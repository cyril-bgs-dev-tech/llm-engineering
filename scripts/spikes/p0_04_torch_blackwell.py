#!/usr/bin/env python3
"""Spike P0-04 : PyTorch voit-il la RTX 5090 (sm_120) et exécute-t-il bf16 et attention fusionnée ?

Sortie JSON sur stdout (archivée dans le registre et dans la page wiki `env-blackwell`).
"""
import json
import sys

import torch
import torch.nn.functional as F

out: dict[str, object] = {
    "torch": torch.__version__,
    "cuda_runtime": torch.version.cuda,
    "cuda_available": torch.cuda.is_available(),
    "arch_list": torch.cuda.get_arch_list(),
}
if not torch.cuda.is_available():
    print(json.dumps(out, indent=2))
    sys.exit(1)

props = torch.cuda.get_device_properties(0)
out["device"] = props.name
out["capability"] = f"sm_{props.major}{props.minor}"
out["vram_total_gib"] = round(props.total_memory / 2**30, 2)
out["sm_120_in_arch_list"] = "sm_120" in torch.cuda.get_arch_list()

a = torch.randn(4096, 4096, device="cuda", dtype=torch.bfloat16)
b = torch.randn(4096, 4096, device="cuda", dtype=torch.bfloat16)
c = a @ b
torch.cuda.synchronize()
out["matmul_bf16_ok"] = bool(torch.isfinite(c.float()).all())

q = torch.randn(2, 16, 512, 64, device="cuda", dtype=torch.bfloat16)
k, v = torch.randn_like(q), torch.randn_like(q)
ref = F.scaled_dot_product_attention(q, k, v, is_causal=True)
torch.cuda.synchronize()
out["sdpa_ok"] = bool(torch.isfinite(ref.float()).all())

# Écart numérique entre l'attention fusionnée et un calcul naïf en float32
scores = (q.float() @ k.float().transpose(-1, -2)) / (64**0.5)
mask = torch.triu(torch.ones(512, 512, device="cuda", dtype=torch.bool), diagonal=1)
naive = torch.softmax(scores.masked_fill(mask, float("-inf")), dim=-1) @ v.float()
out["sdpa_max_abs_diff_vs_fp32"] = round(float((ref.float() - naive).abs().max()), 5)

print(json.dumps(out, indent=2))
