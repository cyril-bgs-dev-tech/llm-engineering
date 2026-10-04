#!/usr/bin/env python3
"""Efficience de l'encodeur déployable : macro-F1 du pli 0 et latence par patient en CPU, flottant 32 bits contre quantification dynamique INT8 (PyTorch, sans dépendance de plus).

Usage : quantize_eval_encoder.py SLUG_DU_MODELE_SAUVEGARDE [--threads 8] [--n 200] [--register]   (modèle sous artifacts/models/<slug>, développement seulement)"""
import json
import sys
import time
from pathlib import Path

import numpy as np
import torch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent))
from transformers import AutoModelForSequenceClassification, AutoTokenizer

import p1_04_06_tfidf
import p1_finetune
from llmft import evaluation
from llmft.mini_registry import register_run


def arg(name: str, default: int) -> int:
    return int(sys.argv[sys.argv.index(name) + 1]) if name in sys.argv else default


def main() -> int:
    slug = sys.argv[1]
    torch.set_num_threads(arg("--threads", 8))
    n_lat = arg("--n", 200)
    model_dir = ROOT / "artifacts/models" / slug
    texts, y, folds, excluded, _ = p1_04_06_tfidf.load("chapter")
    labels = sorted(set(y))
    idx = np.array([labels.index(v) for v in y])
    te = np.where(folds == 0)[0]
    tok = AutoTokenizer.from_pretrained(model_dir)
    x = p1_finetune.build_inputs(tok, [texts[i] for i in te], 508)
    pad = tok.pad_token_id
    results = {}
    base = AutoModelForSequenceClassification.from_pretrained(model_dir, torch_dtype=torch.float32).eval()
    variants = {"fp32": base, "int8_dynamique": torch.quantization.quantize_dynamic(AutoModelForSequenceClassification.from_pretrained(model_dir, torch_dtype=torch.float32).eval(), {torch.nn.Linear}, dtype=torch.qint8)}
    for name, model in variants.items():
        probs = p1_finetune.predict(model, x, pad, "cpu", 16, len(labels))
        rep = evaluation.chapter_report(idx[te], probs, labels, excluded=(excluded,))
        lat = []
        with torch.no_grad():
            for ids in x[:n_lat]:
                t = torch.tensor([ids])
                s = time.perf_counter()
                model(input_ids=t, attention_mask=torch.ones_like(t))
                lat.append(1000 * (time.perf_counter() - s))
        size_mb = sum(p.numel() * (1 if name.startswith("int8") else 4) for p in model.parameters()) / 1e6
        results[name] = {"macro_f1": round(rep["macro_f1"], 4), "accuracy": round(rep["accuracy"], 4), "latence_ms_p50": round(float(np.percentile(lat, 50)), 1), "latence_ms_p95": round(float(np.percentile(lat, 95)), 1), "taille_approx_mo": round(size_mb)}
        print(name, results[name], flush=True)
    out = {"modele": slug, "threads": torch.get_num_threads(), "n_latence": n_lat, **results}
    (ROOT / "results/measures" / f"quantization_{slug}.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
    if "--register" in sys.argv:
        print(register_run(ROOT / "results/runs", {"kind": "measure", "slug": f"quantization-{slug}", "status": "ok", "summary": f"Encodeur {slug} : fp32 contre INT8 dynamique en CPU", "params": {"threads": out["threads"]}, "metrics": out}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
