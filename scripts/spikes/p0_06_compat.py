#!/usr/bin/env python3
"""P0-06 : compatibilité de classification d'un modèle candidat, avec ses vrais poids.

Voie A : `AutoModelForSequenceClassification` si transformers en fournit une pour ce modèle.
Voie B (repli) : tête linéaire maison sur l'état caché du dernier token d'un `AutoModelForCausalLM`.
Dans les deux cas : LoRA, gradient checkpointing, 10 pas sur des textes synthétiques de 1 024 tokens, bf16.
Sortie JSON : classe de chargement, pad, erreurs, mémoire de pointe, temps par pas.
"""
import json
import math
import sys
import time
import traceback

import torch
from peft import LoraConfig, get_peft_model
from transformers import AutoConfig, AutoModelForCausalLM, AutoModelForSequenceClassification, AutoTokenizer

MODEL = sys.argv[1]
PEAK_LIMIT_GIB = 30.0  # limite du pré-vol (vram-preflight) : au-delà, erreur immédiate plutôt qu'un allocateur qui peine
torch.cuda.set_per_process_memory_fraction(min(1.0, PEAK_LIMIT_GIB * 2**30 / torch.cuda.get_device_properties(0).total_memory))
SEQ, BATCH, STEPS, LABELS = 1024, 4, 10, 18
out: dict[str, object] = {"model": MODEL, "seq_len": SEQ, "batch": BATCH, "labels": LABELS}


class LastTokenHead(torch.nn.Module):
    """Voie B : état caché du dernier token réel, puis couche linéaire (en float32)."""

    def __init__(self, base: torch.nn.Module, hidden: int, labels: int) -> None:
        super().__init__()
        self.base, self.head = base, torch.nn.Linear(hidden, labels)

    def forward(self, input_ids: torch.Tensor, attention_mask: torch.Tensor) -> torch.Tensor:
        # logits_to_keep=1 : on ne lit que l'état caché ; sans lui, les logits sur tout le vocabulaire (262 144 mots pour Gemma 4)
        # de chaque token saturent la VRAM (constaté sur Gemma-4-E4B le 02/10/2026 : 32 Go, 26 minutes sans finir 10 pas).
        h = self.base(input_ids=input_ids, attention_mask=attention_mask, output_hidden_states=True, logits_to_keep=1).hidden_states[-1]
        last = attention_mask.sum(dim=1) - 1  # remplissage à droite : dernier token réel
        return self.head(h[torch.arange(h.size(0)), last].float())


try:
    tok = AutoTokenizer.from_pretrained(MODEL)
    out["pad_token"] = tok.pad_token
    tok.padding_side = "right"
    cfg = AutoConfig.from_pretrained(MODEL)
    t0 = time.time()
    try:
        model = AutoModelForSequenceClassification.from_pretrained(MODEL, num_labels=LABELS, torch_dtype=torch.bfloat16)
        out["route"] = "A: AutoModelForSequenceClassification"
        out["loading_class"] = type(model).__name__
        model.config.pad_token_id = tok.pad_token_id
        if hasattr(model.config, "text_config"):  # modèles multimodaux : la tête de classification lit la configuration du texte
            model.config.text_config.pad_token_id = tok.pad_token_id
            out["pad_set_in_text_config"] = True
        peft_cfg = LoraConfig(task_type="SEQ_CLS", r=16, lora_alpha=32, target_modules="all-linear")
        route_a = True
    except (ValueError, KeyError) as exc:
        out["route_a_error"] = f"{type(exc).__name__}: {str(exc)[:160]}"
        base = AutoModelForCausalLM.from_pretrained(MODEL, torch_dtype=torch.bfloat16)
        hidden = getattr(cfg, "hidden_size", None) or cfg.text_config.hidden_size
        out["route"] = "B: AutoModelForCausalLM + tête maison"
        out["loading_class"] = type(base).__name__
        peft_cfg = LoraConfig(task_type="CAUSAL_LM", r=16, lora_alpha=32, target_modules="all-linear")
        base = get_peft_model(base, peft_cfg)
        model = LastTokenHead(base, hidden, LABELS)
        route_a = False
    if route_a:
        model = get_peft_model(model, peft_cfg)
    out["load_seconds"] = round(time.time() - t0, 1)
    model.to("cuda")
    # Voie B : `model` est un LastTokenHead sans cette méthode ; l'ancien « if hasattr » sautait l'activation sans le dire
    # (cause de l'OOM de Gemma-4-E4B le 02/10/2026). On l'active sur le modèle de base et on consigne l'état réel.
    checkpointed = model if hasattr(model, "gradient_checkpointing_enable") else model.base
    checkpointed.gradient_checkpointing_enable(gradient_checkpointing_kwargs={"use_reentrant": False})
    out["gradient_checkpointing"] = bool(getattr(checkpointed, "is_gradient_checkpointing", False))
    trainable = [p for p in model.parameters() if p.requires_grad]
    out["trainable_params"] = sum(p.numel() for p in trainable)
    out["vram_after_load_gib"] = round(torch.cuda.memory_allocated() / 2**30, 2)
    opt = torch.optim.AdamW(trainable, lr=1e-4)
    torch.manual_seed(0)
    ids = torch.randint(1000, 30000, (BATCH, SEQ), device="cuda")
    batch = {"input_ids": ids, "attention_mask": torch.ones_like(ids)}
    y = torch.randint(0, LABELS, (BATCH,), device="cuda")
    torch.cuda.reset_peak_memory_stats()
    losses, times = [], []
    model.train()
    for _ in range(STEPS):
        s = time.time()
        logits = model(**batch).logits.float() if route_a else model(**batch)
        loss = torch.nn.functional.cross_entropy(logits, y)
        loss.backward()
        opt.step()
        opt.zero_grad(set_to_none=True)
        torch.cuda.synchronize()
        times.append(time.time() - s)
        losses.append(round(float(loss), 4))
    out["losses"] = losses
    out["finite"] = all(math.isfinite(x) and abs(x) < 1e6 for x in losses)
    out["seconds_per_step_median"] = round(sorted(times)[len(times) // 2], 3)
    out["vram_peak_gib"] = round(torch.cuda.max_memory_allocated() / 2**30, 2)
    out["vram_peak_reserved_gib"] = round(torch.cuda.max_memory_reserved() / 2**30, 2)
    out["status"] = "ok"
except (RuntimeError, OSError, ValueError, KeyError, ImportError, AttributeError) as exc:
    out["status"] = "failed"
    out["error"] = f"{type(exc).__name__}: {str(exc)[:300]}"
    out["trace_tail"] = traceback.format_exc().splitlines()[-4:]
print(json.dumps(out, ensure_ascii=False, indent=1))
