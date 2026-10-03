#!/usr/bin/env python3
"""Audit GLM v3, C4-A8 : couverture par classe attendue aux effectifs du test (aucune étiquette de test lue).

Effectifs attendus = prévalence du développement × 633 patients de test. Pour chaque chapitre : demi-largeur de Wilson à 95 % d'une couverture observée de 90 %,
et probabilité qu'une couverture vraie de 90 % soit observée sous 80 % (loi binomiale). Usage : glm_v3_coverage_sim.py"""
import json
import sys
from collections import Counter
from pathlib import Path

from scipy.stats import binom

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent))
import p1_04_06_tfidf
from llmft.conformal import wilson

N_TEST = 633


def main() -> int:
    _, y, _, other, _ = p1_04_06_tfidf.load("chapter")
    counts = Counter(c for c in y if c != other)
    total = sum(counts.values())
    out = {}
    for c, n_dev in sorted(counts.items(), key=lambda kv: kv[1]):
        n = max(round(n_dev / total * N_TEST), 1)
        lo, hi = wilson(round(0.9 * n), n)
        out[c] = {"n_test_attendu": n, "wilson_95_a_90pct": [round(lo, 3), round(hi, 3)], "p_observe_sous_80pct": round(float(binom.cdf(int(0.8 * n - 1e-9), n, 0.9)), 3)}
    path = ROOT / "results/measures/glm_v3_coverage_sim.json"
    path.write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    for c, v in out.items():
        print(c, v)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
