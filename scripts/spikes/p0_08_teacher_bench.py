#!/usr/bin/env python3
"""P0-08 : banc de 10 pas du plus gros professeur candidat en QLoRA 4 bits (NF4), 1 024 tokens, gradient checkpointing.

Mesure la mémoire réservée de pointe et le temps par micro-lot ; le temps par lot effectif de 64 s'en déduit (64 micro-lots).
Écart assumé avec la fiche : 10 pas d'optimiseur avec accumulation de 4 micro-lots, pas de 64 (le temps d'un pas de 64 se
calcule, la mémoire ne dépend pas de l'accumulation). Sortie JSON.
"""
import json
import math
import sys
import time

import torch
from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training
from transformers import AutoModelForSequenceClassification, BitsAndBytesConfig

MODEL = sys.argv[1]
SEQ, MICRO, ACCUM, STEPS, LABELS = 1024, 1, 4, 10, 18
out: dict[str, object] = {"model": MODEL, "seq_len": SEQ, "micro_batch": MICRO, "accumulation": ACCUM, "steps": STEPS, "quant": "nf4 double quant, calcul bf16"}
try:
    t0 = time.time()
    bnb = BitsAndBytesConfig(load_in_4bit=True, bnb_4bit_quant_type="nf4", bnb_4bit_compute_dtype=torch.bfloat16, bnb_4bit_use_double_quant=True)
    model = AutoModelForSequenceClassification.from_pretrained(MODEL, num_labels=LABELS, quantization_config=bnb, device_map={"": 0}, torch_dtype=torch.bfloat16)
    out["loading_class"] = type(model).__name__
    out["load_seconds"] = round(time.time() - t0, 1)
    out["vram_after_load_gib"] = round(torch.cuda.memory_allocated() / 2**30, 2)
    model = prepare_model_for_kbit_training(model, use_gradient_checkpointing=True)
    model = get_peft_model(model, LoraConfig(task_type="SEQ_CLS", r=16, lora_alpha=32, target_modules="all-linear"))
    trainable = [p for p in model.parameters() if p.requires_grad]
    out["trainable_params"] = sum(p.numel() for p in trainable)
    opt = torch.optim.AdamW(trainable, lr=1e-4)
    torch.manual_seed(0)
    ids = torch.randint(1000, 30000, (MICRO, SEQ), device="cuda")
    batch = {"input_ids": ids, "attention_mask": torch.ones_like(ids)}
    y = torch.randint(0, LABELS, (MICRO,), device="cuda")
    torch.cuda.reset_peak_memory_stats()
    micro_times, losses = [], []
    model.train()
    for _ in range(STEPS):
        total = 0.0
        for _ in range(ACCUM):
            s = time.time()
            loss = torch.nn.functional.cross_entropy(model(**batch).logits.float(), y) / ACCUM
            loss.backward()
            torch.cuda.synchronize()
            micro_times.append(time.time() - s)
            total += float(loss)
        opt.step()
        opt.zero_grad(set_to_none=True)
        losses.append(round(total, 4))
    out["losses"] = losses
    out["finite"] = all(math.isfinite(x) for x in losses)
    steady = sorted(micro_times[ACCUM:])  # on écarte les premiers micro-lots (démarrage)
    out["seconds_per_micro_batch_median"] = round(steady[len(steady) // 2], 3)
    out["seconds_per_effective_batch_64"] = round(64 * steady[len(steady) // 2], 1)
    out["vram_peak_allocated_gib"] = round(torch.cuda.max_memory_allocated() / 2**30, 2)
    out["vram_peak_reserved_gib"] = round(torch.cuda.max_memory_reserved() / 2**30, 2)
    out["target_reserved_gib_under"] = 30
    out["status"] = "ok"
except (RuntimeError, OSError, ValueError, KeyError, ImportError, AttributeError) as exc:
    out["status"] = "failed"
    out["error"] = f"{type(exc).__name__}: {str(exc)[:300]}"
print(json.dumps(out, ensure_ascii=False, indent=1))
