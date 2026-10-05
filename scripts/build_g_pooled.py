#!/usr/bin/env python3
"""Probabilités hors pli regroupées du système G (ensemble LoRA 4B + encodeur moyenné + TF-IDF, parts égales, retenu par la règle après RM-56) : écrit cinq-plis-ensemble-g.probs.npz.
Développement seulement. Usage : build_g_pooled.py"""
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
P = ROOT / "results/predictions"
PARTS = ["cinq-plis-llm-mur", "cinq-plis-ensemble-encodeur5", "tfidf-variant-char-balanced"]


def main() -> int:
    ref = np.load(P / f"{PARTS[0]}.probs.npz", allow_pickle=False)
    ids = [str(i) for i in ref["ids"]]
    labels = [str(c) for c in ref["labels"]]
    mats = []
    for name in PARTS:
        z = np.load(P / f"{name}.probs.npz", allow_pickle=False)
        if [str(c) for c in z["labels"]] != labels:
            raise SystemExit(f"classes différentes : {name}")
        pos = {str(i): k for k, i in enumerate(z["ids"])}
        mats.append(z["probs"].astype(np.float64)[[pos[i] for i in ids]])
    probs = np.mean(mats, axis=0)
    np.savez_compressed(P / "cinq-plis-ensemble-g.probs.npz", ids=np.array(ids), probs=probs, labels=np.array(labels))
    print("cinq-plis-ensemble-g", probs.shape)
    return 0


if __name__ == "__main__":
    sys.exit(main())
