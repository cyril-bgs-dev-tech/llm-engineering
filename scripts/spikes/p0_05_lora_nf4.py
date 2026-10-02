#!/usr/bin/env python3
"""Spike P0-05 : chargement 4 bits NF4 d'un petit modèle et 10 pas LoRA sur la RTX 5090.

Le but est de savoir si la pile (transformers, peft, bitsandbytes) fonctionne sur sm_120, pas d'apprendre quoi que ce soit :
les données sont du texte synthétique répété. Sortie JSON sur stdout.
"""
import json
import math
import sys
import time

import torch
from peft import LoraConfig, get_peft_model
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig

MODEL = sys.argv[1] if len(sys.argv) > 1 else "Qwen/Qwen3-0.6B"
out: dict[str, object] = {"model": MODEL}

tok = AutoTokenizer.from_pretrained(MODEL)
bnb = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_quant_type="nf4",
    bnb_4bit_compute_dtype=torch.bfloat16,
    bnb_4bit_use_double_quant=True,
)
model = AutoModelForCausalLM.from_pretrained(MODEL, quantization_config=bnb, device_map={"": 0})
out["loaded_4bit"] = True
out["vram_after_load_gib"] = round(torch.cuda.memory_allocated() / 2**30, 3)

model.gradient_checkpointing_enable()
model.enable_input_require_grads()
model = get_peft_model(
    model,
    LoraConfig(r=16, lora_alpha=32, lora_dropout=0.0, target_modules="all-linear", task_type="CAUSAL_LM"),
)
trainable = sum(p.numel() for p in model.parameters() if p.requires_grad)
out["trainable_params"] = trainable

text = "Compte rendu d'hospitalisation. Patient de 62 ans admis pour pneumopathie aiguë communautaire. " * 8
batch = tok([text] * 4, return_tensors="pt", truncation=True, max_length=256).to("cuda")
batch["labels"] = batch["input_ids"].clone()

opt = torch.optim.AdamW([p for p in model.parameters() if p.requires_grad], lr=2e-4)
losses, t0 = [], time.time()
model.train()
for step in range(10):
    loss = model(**batch).loss
    loss.backward()
    opt.step()
    opt.zero_grad(set_to_none=True)
    losses.append(round(float(loss), 4))
torch.cuda.synchronize()
out["steps"] = 10
out["losses"] = losses
out["all_finite"] = all(math.isfinite(x) for x in losses)
out["loss_decreased"] = losses[-1] < losses[0]
out["seconds_10_steps"] = round(time.time() - t0, 1)
out["vram_peak_gib"] = round(torch.cuda.max_memory_allocated() / 2**30, 3)
print(json.dumps(out, indent=2))
