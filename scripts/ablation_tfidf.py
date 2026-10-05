#!/usr/bin/env python3
"""Perturbations de forme et ablations de contenu sur le TF-IDF caractères et poids équilibrés (même recette que le service), pli 0, entraînement sur les plis 1 à 4, développement seulement, EXPLORE.
Usage : ablation_tfidf.py [--register]"""
import json
import random
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent))
import p1_04_06_tfidf
from llmft import evaluation, tfidf
from llmft.mini_registry import register_run
from llmft.perturb import ABLATIONS, PERTURBATIONS


def main() -> int:
    texts, y, folds, excluded, _ = p1_04_06_tfidf.load("chapter")
    labels = sorted(set(y))
    idx = np.array([labels.index(v) for v in y])
    tr, te = np.where(folds != 0)[0], np.where(folds == 0)[0]
    variants = {"propre": [texts[i] for i in te]}
    for name, fn in {**PERTURBATIONS, **ABLATIONS}.items():
        rng = random.Random(1000)
        variants[name] = [fn(texts[i], rng) for i in te]
    flat = [t for v in variants.values() for t in v]
    probs = tfidf.fit_predict_proba([texts[i] for i in tr], [y[i] for i in tr], flat, labels, 10.0, (3, 5), "balanced", "char_wb")
    out = {}
    for k, name in enumerate(variants):
        rep = evaluation.chapter_report(idx[te], probs[k * len(te) : (k + 1) * len(te)], labels, excluded=(excluded,))
        out[name] = {"macro_f1": round(rep["macro_f1"], 4), "accuracy": round(rep["accuracy"], 4)}
        print(name, out[name], flush=True)
    (ROOT / "results/measures/ablation_tfidf.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
    if "--register" in sys.argv:
        print(register_run(ROOT / "results/runs", {"kind": "measure", "slug": "ablation-tfidf-charbal-fold0", "status": "ok", "summary": "Perturbations et ablations du TF-IDF caractères et poids (pli 0)", "params": {"c": 10.0}, "metrics": out}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
