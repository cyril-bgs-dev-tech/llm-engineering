#!/usr/bin/env python3
"""Audit GLM v4, E-c1 (version par familles de chapitres) : couverture conforme LAC à 90 % par famille avec Wilson, TF-IDF, étalonnage croisé par plis par patient, développement seulement.
Usage : coverage_by_family.py [--register]"""
import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent))
import glm_v3_families
import p1_04_06_tfidf
from llmft import conformal
from llmft.mini_registry import register_run


def main() -> int:
    _, y, folds, _, ids = p1_04_06_tfidf.load("chapter")
    z = np.load(ROOT / "results/predictions/p1-06-tfidf-chapter.probs.npz", allow_pickle=False)
    labels = [str(c) for c in z["labels"]]
    pos = {str(i): k for k, i in enumerate(z["ids"])}
    probs = z["probs"][[pos[i] for i in ids]]
    t = np.array([labels.index(v) for v in y])
    f = np.asarray(folds)
    covered = np.zeros(len(t), dtype=bool)
    for k in range(5):
        cal, te = f != k, np.flatnonzero(f == k)
        q = conformal.fit(probs[cal], t[cal], 0.10, "lac")
        sets = conformal.predict_sets(probs[te], q, "lac")
        covered[te] = [t[i] in s for i, s in zip(te, sets, strict=True)]
    fam = {c: name for name, cs in glm_v3_families.FAMILIES.items() for c in cs}
    out = {}
    for name in glm_v3_families.FAMILIES:
        sel = np.array([fam[v] == name for v in y])
        n, hits = int(sel.sum()), int(covered[sel].sum())
        lo, hi = conformal.wilson(hits, n)
        out[name] = {"n": n, "couverture": round(hits / n, 3), "wilson95": [round(lo, 3), round(hi, 3)]}
        print(name, out[name])
    (ROOT / "results/measures/coverage_by_family.json").write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    if "--register" in sys.argv:
        print(register_run(ROOT / "results/runs", {"kind": "measure", "slug": "coverage-by-family-tfidf", "status": "ok", "summary": "Couverture conforme LAC 90 % par famille de chapitres (TF-IDF, développement)", "params": {"alpha": 0.1}, "metrics": out}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
