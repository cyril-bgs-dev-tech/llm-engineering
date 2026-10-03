#!/usr/bin/env python3
"""Variantes de recette du TF-IDF sur le chapitre (fiche 2026-10-04-tfidf-variantes-recette) : cinq plis par patient, EXPLORE.
Usage : tfidf_variants.py {balanced|char|char-balanced} [--register]"""
import json
import sys
import time
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent))
import p1_04_06_tfidf
from llmft import evaluation, tfidf
from llmft.mini_registry import register_run

VARIANTS = {"balanced": ("balanced", "word", (1, 2)), "char": (None, "char_wb", (3, 5)), "char-balanced": ("balanced", "char_wb", (3, 5))}
GRID = [(c, None) for c in (10.0, 100.0, 1000.0)]


def main() -> int:
    name = sys.argv[1]
    cw, analyzer, ngram = VARIANTS[name]
    texts, y, folds, excluded, ids = p1_04_06_tfidf.load("chapter")
    labels = sorted(set(y))
    scored = [lab for lab in labels if lab != excluded]
    idx = np.array([labels.index(v) for v in y])
    grid = [(c, ngram) for c, _ in GRID]
    oof = np.zeros((len(y), len(labels)))
    chosen = []
    t0 = time.time()
    for k in range(5):
        tr, te = np.where(folds != k)[0], np.where(folds == k)[0]
        cfg = tfidf.select_config([texts[i] for i in tr], [y[i] for i in tr], folds[tr], (k + 1) % 5, labels, scored, grid, cw, analyzer)
        chosen.append({"fold": k, "C": cfg[0], "ngram": list(cfg[1])})
        oof[te] = tfidf.fit_predict_proba([texts[i] for i in tr], [y[i] for i in tr], [texts[i] for i in te], labels, cfg[0], cfg[1], cw, analyzer)
        print(k, chosen[-1], round(time.time() - t0), "s", flush=True)
    rep = evaluation.chapter_report(idx, oof, labels, excluded=(excluded,))
    out = {"variant": name, "macro_f1": rep["macro_f1"], "accuracy": rep["accuracy"], "log_loss": rep["log_loss"], "chosen": chosen, "seconds": round(time.time() - t0)}
    probs_path = ROOT / f"results/predictions/tfidf-variant-{name}.probs.npz"
    np.savez_compressed(probs_path, ids=np.array(ids), probs=oof, labels=np.array(labels))
    print(json.dumps(out))
    if "--register" in sys.argv:
        print(register_run(ROOT / "results/runs", {"kind": "train", "slug": f"tfidf-variant-{name}", "status": "ok", "summary": f"TF-IDF variante {name} : macro-F1 {rep['macro_f1']:.4f} sur cinq plis",
              "params": {"variant": name, "class_weight": cw, "analyzer": analyzer, "ngram": list(ngram)}, "metrics": out}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
