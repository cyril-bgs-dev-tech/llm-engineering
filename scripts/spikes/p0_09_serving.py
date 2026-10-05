#!/usr/bin/env python3
"""P0-09 (Q9) : latence et débit de service d'un classifieur, runtime Transformers, sur 100 requêtes SYNTHÉTIQUES.

Aucune donnée de patient : des identifiants de tokens tirés au hasard (graine fixe), longueurs tirées d'une loi log-normale
calée sur la moyenne mesurée en P0-21 (environ 1 309 tokens Qwen, plafond 4 096). Le modèle (Qwen3.5-4B, classe de
classification, tête neuve de 18 sorties initialisée à graine fixe) n'est PAS entraîné : seule la **sortie égale** entre
runtimes compte (accord des argmax, écart maximal des logits), pas la qualité.
Protocole de mesure (skill performance-optimization) : 5 requêtes de chauffe, puis 3 passes complètes ; médiane et étendue
des passes pour juger le bruit ; mêmes entrées dans toutes les passes. Plafond dur de 30 Gio de VRAM.
Usage : p0_09_serving.py SORTIE.json
"""
import json
import sys
import time

import numpy as np
import torch
from transformers import AutoModelForSequenceClassification, AutoTokenizer

MODEL, OUT, SEED, N_REQ, MEAN_LEN, MAX_LEN, PASSES, BATCH = "Qwen/Qwen3.5-4B", sys.argv[1], 0, 100, 1309, 4096, 3, 8
torch.cuda.set_per_process_memory_fraction(min(1.0, 30 * 2**30 / torch.cuda.get_device_properties(0).total_memory))
rng = np.random.default_rng(SEED)
lengths = np.clip(rng.lognormal(mean=np.log(MEAN_LEN) - 0.18, sigma=0.6, size=N_REQ).astype(int), 64, MAX_LEN)
inputs = [rng.integers(1000, 30000, size=int(n)).tolist() for n in lengths]
tok = AutoTokenizer.from_pretrained(MODEL)
torch.manual_seed(SEED)
model = AutoModelForSequenceClassification.from_pretrained(MODEL, num_labels=18, dtype=torch.bfloat16, device_map={"": 0})
model.config.pad_token_id = tok.pad_token_id
if hasattr(model.config, "text_config"):
    model.config.text_config.pad_token_id = tok.pad_token_id
model.eval()
out: dict[str, object] = {"runtime": "transformers", "model": MODEL, "n_requests": N_REQ, "lengths_mean": float(lengths.mean()), "lengths_max": int(lengths.max()),
                          "versions": {"torch": torch.__version__, "transformers": __import__("transformers").__version__}}


@torch.no_grad()
def one(ids: list[int]) -> torch.Tensor:
    x = torch.tensor([ids], device="cuda")
    logits: torch.Tensor = model(input_ids=x, attention_mask=torch.ones_like(x)).logits.float()[0].cpu()
    return logits


@torch.no_grad()
def batch(chunk: list[list[int]]) -> torch.Tensor:  # remplissage à droite avec le pad
    m = max(len(c) for c in chunk)
    ids = torch.full((len(chunk), m), tok.pad_token_id, device="cuda")
    att = torch.zeros((len(chunk), m), dtype=torch.long, device="cuda")
    for i, c in enumerate(chunk):
        ids[i, : len(c)] = torch.tensor(c)
        att[i, : len(c)] = 1
    logits: torch.Tensor = model(input_ids=ids, attention_mask=att).logits.float().cpu()
    return logits


for ids in inputs[:5]:
    one(ids)
torch.cuda.synchronize()
torch.cuda.reset_peak_memory_stats()
seq = []
logits_ref = None
for _ in range(PASSES):
    lat, logits = [], []
    for ids in inputs:
        t = time.perf_counter()
        logits.append(one(ids))
        torch.cuda.synchronize()
        lat.append(time.perf_counter() - t)
    seq.append({"p50_ms": round(1000 * float(np.percentile(lat, 50)), 1), "p95_ms": round(1000 * float(np.percentile(lat, 95)), 1),
                "mean_ms": round(1000 * float(np.mean(lat)), 1), "tokens_per_s": round(float(lengths.sum() / np.sum(lat)), 0)})
    logits_ref = torch.stack(logits)
order = np.argsort(lengths)  # lots de longueurs voisines : borne favorable au débit
bat = []
for _ in range(PASSES):
    t = time.perf_counter()
    for i in range(0, N_REQ, BATCH):
        batch([inputs[j] for j in order[i : i + BATCH]])
    torch.cuda.synchronize()
    dt = time.perf_counter() - t
    bat.append({"requests_per_s": round(N_REQ / dt, 2), "tokens_per_s": round(float(lengths.sum() / dt), 0)})
assert logits_ref is not None
batched = torch.cat([batch([inputs[j] for j in order[i : i + BATCH]]) for i in range(0, N_REQ, BATCH)])
inverse = np.empty(N_REQ, int)
inverse[order] = np.arange(N_REQ)
batched = batched[torch.tensor(inverse)]
out["sequential_passes"], out["batched_passes"] = seq, bat
out["batch_size"] = BATCH
out["batched_vs_sequential"] = {"argmax_agreement": float((batched.argmax(1) == logits_ref.argmax(1)).float().mean()), "max_abs_logit_diff": float((batched - logits_ref).abs().max())}
out["vram_peak_gib"] = round(torch.cuda.max_memory_allocated() / 2**30, 2)
out["vram_peak_reserved_gib"] = round(torch.cuda.max_memory_reserved() / 2**30, 2)
torch.save(logits_ref, OUT.replace(".json", ".logits.pt"))
with open(OUT, "w", encoding="utf-8") as handle:
    json.dump(out, handle, ensure_ascii=False, indent=1)
print(json.dumps(out, ensure_ascii=False, indent=1))
