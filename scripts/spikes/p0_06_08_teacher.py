#!/usr/bin/env python3
"""P0-06 (gros modèle) et P0-08 : compatibilité de classification puis banc de pas d'un professeur en QLoRA 4 bits.

Un seul chargement du modèle (règle de la feuille de route). Trois étapes, un JSON partiel écrit après chacune :
  1. compat : 10 micro-pas, batch 4, 1 024 tokens (même protocole que p0_06_compat.py, mais en NF4) ;
  2. bench P0-08 : 10 pas d'optimiseur, batch effectif 64 = 16 micro-lots de 4 × 1 024 tokens, gradient checkpointing ;
  3. longueur du protocole : 3 micro-pas de 1 × 4 096 tokens (PROTOCOLE.md § 1), pour le budget P0-45.
Plafond dur de 30 Gio de VRAM (vram-preflight) : au-delà, erreur immédiate. Usage : p0_06_08_teacher.py MODELE SORTIE.json
"""
import json
import math
import resource
import sys
import time
import traceback

import torch
from peft import LoraConfig, get_peft_model
from transformers import (
    AutoConfig,
    AutoModelForCausalLM,
    AutoModelForSequenceClassification,
    AutoTokenizer,
    BitsAndBytesConfig,
)

MODEL, OUT_PATH = sys.argv[1], sys.argv[2]
PEAK_LIMIT_GIB = 30.0
LABELS, MICRO_BATCH, SEQ, ACCUM, BENCH_STEPS, COMPAT_STEPS = 18, 4, 1024, 16, 10, 10
LONG_SEQ, LONG_STEPS = 4096, 3
torch.cuda.set_per_process_memory_fraction(min(1.0, PEAK_LIMIT_GIB * 2**30 / torch.cuda.get_device_properties(0).total_memory))
out: dict[str, object] = {"model": MODEL, "quantization": "nf4 4 bits, double quantification, calcul bf16", "labels": LABELS}


def save(stage: str) -> None:
    out["stage_done"] = stage
    out["host_ram_peak_gib"] = round(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 2**20, 1)
    with open(OUT_PATH, "w", encoding="utf-8") as handle:
        json.dump(out, handle, ensure_ascii=False, indent=1)


class LastTokenHead(torch.nn.Module):
    """Voie B : état caché du dernier token réel (remplissage à droite), puis couche linéaire en float32."""

    def __init__(self, base: torch.nn.Module, hidden: int, labels: int) -> None:
        super().__init__()
        self.base, self.head = base, torch.nn.Linear(hidden, labels)

    def forward(self, input_ids: torch.Tensor, attention_mask: torch.Tensor) -> torch.Tensor:
        h = self.base(input_ids=input_ids, attention_mask=attention_mask, output_hidden_states=True, logits_to_keep=1).hidden_states[-1]
        last = attention_mask.sum(dim=1) - 1
        return self.head(h[torch.arange(h.size(0)), last].float())


def run_steps(model, route_a, trainable, batch, seq, n_opt, accum, label):
    """`n_opt` pas d'optimiseur de `accum` micro-lots ; renvoie pertes, temps par pas, pics de mémoire."""
    opt = torch.optim.AdamW(trainable, lr=1e-4)
    torch.manual_seed(0)
    ids = torch.randint(1000, 30000, (batch, seq), device="cuda")
    feed = {"input_ids": ids, "attention_mask": torch.ones_like(ids)}
    y = torch.randint(0, LABELS, (batch,), device="cuda")
    torch.cuda.empty_cache()
    torch.cuda.reset_peak_memory_stats()
    losses, times = [], []
    model.train()
    for step in range(n_opt):
        start = time.time()
        for _ in range(accum):
            logits = model(**feed).logits.float() if route_a else model(**feed)
            loss = torch.nn.functional.cross_entropy(logits, y) / accum
            loss.backward()
        opt.step()
        opt.zero_grad(set_to_none=True)
        torch.cuda.synchronize()
        times.append(time.time() - start)
        losses.append(round(float(loss.detach()) * accum, 4))
        print(f"[{label}] pas {step + 1}/{n_opt} : {times[-1]:.1f} s", file=sys.stderr, flush=True)
    return {
        "optimizer_steps": n_opt, "micro_batches_per_step": accum, "micro_batch": batch, "seq_len": seq,
        "losses": losses, "finite": all(math.isfinite(x) and abs(x) < 1e6 for x in losses),
        "seconds_per_optimizer_step_median": round(sorted(times)[len(times) // 2], 2),
        "seconds_per_micro_batch_median": round(sorted(times)[len(times) // 2] / accum, 3),
        "vram_peak_gib": round(torch.cuda.max_memory_allocated() / 2**30, 2),
        "vram_peak_reserved_gib": round(torch.cuda.max_memory_reserved() / 2**30, 2),
    }


try:
    tok = AutoTokenizer.from_pretrained(MODEL)
    out["pad_token"] = tok.pad_token
    cfg = AutoConfig.from_pretrained(MODEL)
    bnb = BitsAndBytesConfig(load_in_4bit=True, bnb_4bit_quant_type="nf4", bnb_4bit_use_double_quant=True, bnb_4bit_compute_dtype=torch.bfloat16)
    t0 = time.time()
    try:
        model = AutoModelForSequenceClassification.from_pretrained(
            MODEL, num_labels=LABELS, dtype=torch.bfloat16, quantization_config=bnb, device_map={"": 0})
        out["route"] = "A: AutoModelForSequenceClassification"
        model.config.pad_token_id = tok.pad_token_id
        if hasattr(model.config, "text_config"):
            model.config.text_config.pad_token_id = tok.pad_token_id
            out["pad_set_in_text_config"] = True
        route_a, hidden = True, 0
    except (ValueError, KeyError) as exc:
        out["route_a_error"] = f"{type(exc).__name__}: {str(exc)[:160]}"
        model = AutoModelForCausalLM.from_pretrained(MODEL, dtype=torch.bfloat16, quantization_config=bnb, device_map={"": 0})
        out["route"] = "B: AutoModelForCausalLM + tête maison"
        route_a, hidden = False, (getattr(cfg, "hidden_size", None) or cfg.text_config.hidden_size)
    out["loading_class"] = type(model).__name__
    out["load_seconds"] = round(time.time() - t0, 1)
    out["vram_after_load_gib"] = round(torch.cuda.memory_allocated() / 2**30, 2)
    model.gradient_checkpointing_enable(gradient_checkpointing_kwargs={"use_reentrant": False})
    out["gradient_checkpointing"] = bool(getattr(model, "is_gradient_checkpointing", False))
    peft_cfg = LoraConfig(task_type="SEQ_CLS" if route_a else "CAUSAL_LM", r=16, lora_alpha=32, target_modules="all-linear")
    model = get_peft_model(model, peft_cfg)
    if not route_a:
        model = LastTokenHead(model, hidden, LABELS).to("cuda")
    trainable = [p for p in model.parameters() if p.requires_grad]
    out["trainable_params"] = sum(p.numel() for p in trainable)
    save("chargement")

    out["stage1_compat"] = run_steps(model, route_a, trainable, MICRO_BATCH, SEQ, COMPAT_STEPS, 1, "compat")
    out["status"] = "ok"
    save("compat")
    out["stage2_bench_p0_08"] = run_steps(model, route_a, trainable, MICRO_BATCH, SEQ, BENCH_STEPS, ACCUM, "bench")
    save("bench_p0_08")
    out["stage3_longueur_4096"] = run_steps(model, route_a, trainable, 1, LONG_SEQ, LONG_STEPS, 1, "4096")
    save("longueur_4096")
except (RuntimeError, OSError, ValueError, KeyError, ImportError, AttributeError) as exc:
    out["status"] = "failed" if "stage1_compat" not in out else "partial"
    out["error"] = f"{type(exc).__name__}: {str(exc)[:400]}"
    out["trace_tail"] = traceback.format_exc().splitlines()[-4:]
    save("erreur")
print(json.dumps(out, ensure_ascii=False, indent=1))
