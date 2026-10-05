#!/usr/bin/env python3
"""Différence de macro-F1 entre deux systèmes sur des prédictions hors pli regroupées (règle de puissance v2) : A moins B, IC 95 % et largeur, bootstrap stratifié par classe, même tirage.

Usage : pooled_compare.py A.probs.npz B.probs.npz SLUG [--register]   (les deux fichiers couvrent les mêmes patients ; seul le développement est lu)"""
import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent))
import p1_04_06_tfidf
from llmft.mini_registry import register_run
from llmft.power_rule import pooled_interval


def aligned(path: str, ids: list[str]) -> tuple[np.ndarray, list[str]]:
    z = np.load(path, allow_pickle=False)
    pos = {str(i): k for k, i in enumerate(z["ids"])}
    return z["probs"].astype(np.float64)[[pos[i] for i in ids]], [str(c) for c in z["labels"]]


def main() -> int:
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    path_a, path_b, slug = args
    _, y, _, other, ids_all = p1_04_06_tfidf.load("chapter")
    truth_of = dict(zip(ids_all, y, strict=True))
    za = np.load(path_a, allow_pickle=False)
    ids = [str(i) for i in za["ids"]]
    pa, labels = aligned(path_a, ids)
    pb, labels_b = aligned(path_b, ids)
    if labels != labels_b:
        raise SystemExit("classes différentes")
    truth = np.array([labels.index(truth_of[i]) for i in ids])
    scored = [labels.index(c) for c in labels if c != other]
    d, lo, hi = pooled_interval(truth, pa.argmax(1), pb.argmax(1), scored)
    out = {"n": len(ids), "difference_points": round(d, 2), "ic95_points": [round(lo, 2), round(hi, 2)], "largeur_95": round(hi - lo, 2), "seuil_v2": 4.0}
    print(json.dumps(out))
    if "--register" in sys.argv:
        print(register_run(ROOT / "results/runs", {"kind": "measure", "slug": slug, "status": "ok", "summary": f"{slug} : {out['difference_points']} points [{lo:.2f} ; {hi:.2f}] sur {len(ids)} patients regroupés",
                                                    "params": {"a": Path(path_a).name, "b": Path(path_b).name}, "metrics": out}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
