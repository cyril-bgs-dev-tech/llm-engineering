#!/usr/bin/env python3
"""Construit l'ensemble par moyenne simple des cinq graines d'encodeur d'un pli, et son mélange 50/50 avec le TF-IDF caractères équilibré.

Usage : build_fold_ensemble.py PLI | --pool (concatène les cinq plis dans cinq-plis-*.probs.npz)   (écrit pliK-ensemble-encodeur5.probs.npz et pliK-ensemble-encodeur5-tfidf-charbal.probs.npz ; le pli 0 garde ses noms historiques)."""
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from llmft.ensemble import average_probs

P = ROOT / "results/predictions"


def load(name: str) -> tuple[list[str], np.ndarray, np.ndarray]:
    z = np.load(P / f"{name}.probs.npz", allow_pickle=False)
    return [str(i) for i in z["ids"]], z["probs"].astype(float), z["labels"]


def pool() -> int:
    """Concatène les ensembles des cinq plis (le pli 0 garde ses noms historiques) en un fichier de prédictions hors pli sur 3 586 patients."""
    for suffix in ("ensemble-encodeur5", "ensemble-encodeur5-tfidf-charbal"):
        parts = [load(suffix if k == 0 else f"pli{k}-{suffix}") for k in range(5)]
        ids = [i for p_ids, _, _ in parts for i in p_ids]
        if len(set(ids)) != len(ids):
            raise SystemExit("patients en double entre plis")
        np.savez(P / f"cinq-plis-{suffix}.probs.npz", ids=np.array(ids), probs=np.vstack([p for _, p, _ in parts]), labels=parts[0][2])
        print("écrit", f"cinq-plis-{suffix}", len(ids))
    return 0


def main() -> int:
    if sys.argv[1] == "--pool":
        return pool()
    fold = int(sys.argv[1])
    seeds = [f"camembert-pli{fold}-ep10-s{s}" for s in range(5)]
    missing = [s for s in seeds if not (P / f"{s}.probs.npz").exists()]
    if missing:
        print("manquants :", missing)
        return 1
    loaded = [load(s) for s in seeds]
    labels = loaded[0][2]
    ids, enc = average_probs([(i, p) for i, p, _ in loaded])
    it, pt, _ = load("tfidf-variant-char-balanced")
    pos = {i: k for k, i in enumerate(it)}
    mix = 0.5 * enc + 0.5 * pt[[pos[i] for i in ids]]
    for name, probs in ((f"pli{fold}-ensemble-encodeur5", enc), (f"pli{fold}-ensemble-encodeur5-tfidf-charbal", mix)):
        np.savez(P / f"{name}.probs.npz", ids=np.array(ids), probs=probs, labels=labels)
        print("écrit", name, probs.shape)
    return 0


if __name__ == "__main__":
    sys.exit(main())
