#!/usr/bin/env python3
"""Construit les professeurs imbriqués (RM-56) : pour chaque couple (k évalué, j ≠ k), moyenne des graines d'encodeur `nested-enc-k<k>-j<j>-s<s>` puis mélange 50/50 avec `nested-tfidf-k<k>-j<j>`.
Écrit nested-teacher-k<k>-j<j>.probs.npz. Usage : build_nested_teachers.py [--seeds 2]"""
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


def main() -> int:
    n_seeds = int(sys.argv[sys.argv.index("--seeds") + 1]) if "--seeds" in sys.argv else 2
    made = 0
    for k in range(5):
        for j in range(5):
            if j == k:
                continue
            names = [f"nested-enc-k{k}-j{j}-s{s}" for s in range(n_seeds)] + [f"nested-tfidf-k{k}-j{j}"]
            if not all((P / f"{n}.probs.npz").exists() for n in names):
                print("manquant", k, j)
                continue
            loaded = [load(n) for n in names]
            ids, enc = average_probs([(i, p) for i, p, _ in loaded[:-1]])
            tf_ids, tf, labels = loaded[-1]
            pos = {i: m for m, i in enumerate(tf_ids)}
            mix = 0.5 * enc + 0.5 * tf[[pos[i] for i in ids]]
            np.savez(P / f"nested-teacher-k{k}-j{j}.probs.npz", ids=np.array(ids), probs=mix, labels=labels)
            made += 1
    print(made, "professeurs imbriqués construits")
    return 0 if made == 20 else 1


if __name__ == "__main__":
    sys.exit(main())
