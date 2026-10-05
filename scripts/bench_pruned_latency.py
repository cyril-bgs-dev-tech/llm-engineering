#!/usr/bin/env python3
"""Latence d'un encodeur élagué (RM-45) : la latence ne dépend pas des poids appris ; CamemBERT-bio élagué (tête aléatoire) mesuré sur GPU (fp32 et bf16, lot de 1) et sur processeur (8 threads),
sur 100 patients du pli 0 ; comparaison à l'encodeur complet mesuré de la même façon. Usage : bench_pruned_latency.py [--register]"""
import json
import os
import sys
import time
from pathlib import Path

os.environ.setdefault("TOKENIZERS_PARALLELISM", "false")

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent))
import p1_04_06_tfidf
import p1_finetune
from llmft import prune, servicecost
from llmft.mini_registry import register_run


def main() -> int:
    import torch
    from transformers import AutoTokenizer

    texts, y, folds, _, _ = p1_04_06_tfidf.load("chapter")
    labels = sorted(set(y))
    sample = [t for t, g in zip(texts, folds, strict=True) if g == 0][:100]
    tok = AutoTokenizer.from_pretrained("almanach/camembert-bio-base")
    x = p1_finetune.build_inputs(tok, sample, 508)
    out: dict[str, object] = {}
    for every, name in ((1, "12 couches"), (2, "6 couches")):
        for device, dtype, tag in (("cuda", torch.float32, "gpu_fp32"), ("cuda", torch.bfloat16, "gpu_bf16"), ("cpu", torch.float32, "cpu_fp32")):
            torch.manual_seed(0)
            model, _ = p1_finetune.load_model("almanach/camembert-bio-base", "full", len(labels), tok.pad_token_id, 16, 32)
            prune.prune_encoder(model, every)
            model = model.to(device=device, dtype=dtype).eval()
            if device == "cpu":
                torch.set_num_threads(8)
            p1_finetune.predict(model, x[:3], tok.pad_token_id, device, 1, len(labels))
            lat = []
            for xi in x:
                t0 = time.perf_counter()
                p1_finetune.predict(model, [xi], tok.pad_token_id, device, 1, len(labels))
                if device == "cuda":
                    torch.cuda.synchronize()
                lat.append(1000 * (time.perf_counter() - t0))
            out[f"{name} {tag}"] = {**servicecost.latency_summary(lat), "parametres_millions": round(sum(p.numel() for p in model.parameters()) / 1e6, 1)}
            print(name, tag, out[f"{name} {tag}"], flush=True)
            del model
            torch.cuda.empty_cache()
    (ROOT / "results/measures/bench_pruned_latency.json").write_text(json.dumps(out, indent=1, ensure_ascii=False), encoding="utf-8")
    if "--register" in sys.argv:
        print(register_run(ROOT / "results/runs", {"kind": "measure", "slug": "latence-encodeur-elague", "status": "ok", "summary": "Latence de l'encodeur à 6 et 12 couches, GPU et processeur", "params": {"n": len(x)}, "metrics": out}))
    return 0


if __name__ == "__main__":
    np.random.seed(0)
    sys.exit(main())
