#!/usr/bin/env python3
"""Audit GLM v3, C5-A4 : robustesse du TF-IDF aux perturbations de texte, pli 0 (entraînement sur les plis 1 à 4, configuration choisie au pli 0 par P1-06).

Les perturbations ne touchent que le texte du pli évalué. Développement seulement. Usage : glm_v3_perturb_tfidf.py"""
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
from llmft.perturb import PERTURBATIONS

SEED = 1000


def main() -> int:
    run = json.loads(next((ROOT / "results/runs").glob("*-p1-06-tfidf-chapter.json")).read_text(encoding="utf-8"))
    cfg = next(c for c in run["metrics"]["chosen_config_by_fold"] if c["fold"] == 0)
    texts, y, folds, excluded, _ = p1_04_06_tfidf.load("chapter")
    labels = sorted(set(y))
    idx = np.array([labels.index(v) for v in y])
    tr, te = np.where(folds != 0)[0], np.where(folds == 0)[0]
    variants = {"propre": [texts[i] for i in te]}
    for name, fn in PERTURBATIONS.items():
        rng = random.Random(SEED)
        variants[name] = [fn(texts[i], rng) for i in te]
    flat = [t for v in variants.values() for t in v]
    probs = tfidf.fit_predict_proba([texts[i] for i in tr], [y[i] for i in tr], flat, labels, cfg["C"], tuple(cfg["ngram"]))
    out = {"config": cfg, "n": len(te)}
    for k, name in enumerate(variants):
        p = probs[k * len(te) : (k + 1) * len(te)]
        rep = evaluation.chapter_report(idx[te], p, labels, excluded=(excluded,))
        out[name] = {"macro_f1": round(rep["macro_f1"], 4), "accuracy": round(rep["accuracy"], 4)}
        print(name, out[name])
    (ROOT / "results/measures/glm_v3_perturb_tfidf.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
