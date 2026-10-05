#!/usr/bin/env python3
"""P0-09 : même banc que p0_09_serving.py (mêmes 100 requêtes synthétiques, graine 0), runtime vLLM, tâche de classification.
À lancer dans l'environnement ISOLÉ de vLLM (jamais dans `.venv`). Compare aux logits de référence Transformers (softmax).
Usage : p0_09_vllm.py DOSSIER_MODELE REFERENCE_LOGITS.pt SORTIE.json"""
import json
import sys
import time

import numpy as np
import torch

MODEL_DIR, REF, OUT = sys.argv[1], sys.argv[2], sys.argv[3]
SEED, N_REQ, MEAN_LEN, MAX_LEN, PASSES = 0, 100, 1309, 4096, 3
rng = np.random.default_rng(SEED)
lengths = np.clip(rng.lognormal(mean=np.log(MEAN_LEN) - 0.18, sigma=0.6, size=N_REQ).astype(int), 64, MAX_LEN)
inputs = [rng.integers(1000, 30000, size=int(n)).tolist() for n in lengths]
import vllm
from vllm import LLM

out: dict[str, object] = {"runtime": "vllm", "vllm_version": vllm.__version__, "torch": torch.__version__, "n_requests": N_REQ}
llm = LLM(model=MODEL_DIR, runner="pooling", convert="classify", dtype="bfloat16", max_model_len=MAX_LEN, gpu_memory_utilization=0.55, enforce_eager=False)
prompts = [{"prompt_token_ids": ids} for ids in inputs]
for p in prompts[:5]:
    llm.classify([p])
seq = []
probs_seq = None
for _ in range(PASSES):
    lat, probs = [], []
    for p in prompts:
        t = time.perf_counter()
        r = llm.classify([p])
        lat.append(time.perf_counter() - t)
        probs.append(torch.tensor(r[0].outputs.probs))
    seq.append({"p50_ms": round(1000 * float(np.percentile(lat, 50)), 1), "p95_ms": round(1000 * float(np.percentile(lat, 95)), 1),
                "mean_ms": round(1000 * float(np.mean(lat)), 1), "tokens_per_s": round(float(lengths.sum() / np.sum(lat)), 0)})
    probs_seq = torch.stack(probs)
bat = []
for _ in range(PASSES):
    t = time.perf_counter()
    llm.classify(prompts)
    dt = time.perf_counter() - t
    bat.append({"requests_per_s": round(N_REQ / dt, 2), "tokens_per_s": round(float(lengths.sum() / dt), 0)})
ref = torch.softmax(torch.load(REF).float(), dim=1)
assert probs_seq is not None
out["sequential_passes"], out["batched_passes"] = seq, bat
out["vs_transformers"] = {"argmax_agreement": float((probs_seq.argmax(1) == ref.argmax(1)).float().mean()), "max_abs_prob_diff": float((probs_seq - ref).abs().max())}
with open(OUT, "w", encoding="utf-8") as handle:
    json.dump(out, handle, ensure_ascii=False, indent=1)
print(json.dumps(out, ensure_ascii=False, indent=1))
