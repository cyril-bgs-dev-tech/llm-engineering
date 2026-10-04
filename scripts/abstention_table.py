#!/usr/bin/env python3
"""Audit GLM v4, E-c2 : table d'abstention par modèle (pli 0) : exactitude conditionnelle à la couverture choisie, avec intervalle de Wilson 95 %, et taux de renvoi à l'humain.

Confiance = probabilité maximale brute. Développement seulement. Usage : abstention_table.py NOM=PROBS.npz [NOM=PROBS.npz ...]"""
import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent))
import p1_04_06_tfidf
from llmft.conformal import wilson

COVERAGES = (1.0, 0.9, 0.8, 0.7, 0.5)


def main() -> int:
    _, y, folds, _, ids = p1_04_06_tfidf.load("chapter")
    truth = dict(zip(ids, y, strict=True))
    fold0 = {i for i, g in zip(ids, folds, strict=True) if g == 0}
    out = {}
    for arg in sys.argv[1:]:
        name, path = arg.split("=", 1)
        z = np.load(path, allow_pickle=False)
        labels = [str(c) for c in z["labels"]]
        pid = [str(i) for i in z["ids"]]
        sel = [k for k, i in enumerate(pid) if i in fold0]
        probs = z["probs"][sel].astype(np.float64)
        t = np.array([labels.index(truth[pid[k]]) for k in sel])
        conf, correct = probs.max(1), (probs.argmax(1) == t).astype(int)
        order = np.argsort(-conf, kind="stable")
        rows = {}
        for c in COVERAGES:
            k = max(1, round(c * len(conf)))
            hits = int(correct[order[:k]].sum())
            lo, hi = wilson(hits, k)
            rows[str(c)] = {"n_traites": k, "exactitude": round(hits / k, 3), "wilson95": [round(lo, 3), round(hi, 3)], "taux_de_renvoi": round(1 - c, 2)}
        out[name] = rows
        print(name, {c: (r["exactitude"], r["wilson95"]) for c, r in rows.items()})
    (ROOT / "results/measures/abstention_table.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
