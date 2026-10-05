#!/usr/bin/env python3
"""TF-IDF caractères équilibré (C = 100, aucun réglage) entraîné hors des plis `--fold` et `--exclude-fold`, prédisant `--fold` (professeur imbriqué, RM-56, fiche 2026-10-05-distillation-imbriquee).
Usage : nested_tfidf.py FOLD EXCLUDE_FOLD [--register]   (écrit nested-tfidf-k<EXCLUDE>-j<FOLD>.probs.npz)"""
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent))
import p1_04_06_tfidf
from llmft import tfidf


def main() -> int:
    j, k = int(sys.argv[1]), int(sys.argv[2])
    if j == k:
        raise SystemExit("FOLD et EXCLUDE_FOLD doivent différer")
    texts, y, folds, _, ids = p1_04_06_tfidf.load("chapter")
    labels = sorted(set(y))
    tr = np.where((folds != j) & (folds != k))[0]
    te = np.where(folds == j)[0]
    probs = tfidf.fit_predict_proba([texts[i] for i in tr], [y[i] for i in tr], [texts[i] for i in te], labels, 100.0, (3, 5), "balanced", "char_wb")
    np.savez_compressed(ROOT / f"results/predictions/nested-tfidf-k{k}-j{j}.probs.npz", ids=np.array([ids[i] for i in te]), probs=probs, labels=np.array(labels))
    print(f"nested-tfidf-k{k}-j{j}", probs.shape)
    return 0


if __name__ == "__main__":
    sys.exit(main())
