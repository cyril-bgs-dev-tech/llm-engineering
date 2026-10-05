#!/usr/bin/env python3
"""Mesures sans GPU de l'audit GLM v3 (C2-A3, C2-A5, C5-A3) : effectifs par pli et classe, macro/pondérée/micro, destination des erreurs.

Développement seulement, agrégats seulement. Usage : glm_v3_cpu_measures.py"""
import json
import sys
from collections import Counter
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(Path(__file__).resolve().parent))
import p1_04_06_tfidf

OUT = ROOT / "results/measures/glm_v3_cpu.json"
PREDS = {"tfidf": "p1-06-tfidf-chapter", "qwen3.5-9b-1e-4": "p1-11-qwen3-5-9b-lr1e-4", "gemma-4-e4b-1e-4": "p1-11-gemma-4-e4b-lr1e-4"}


def f1s(t: np.ndarray, p: np.ndarray, classes: list[str]) -> dict[str, float]:
    out = {}
    for c in classes:
        tp, fp, fn = int(((t == c) & (p == c)).sum()), int(((t != c) & (p == c)).sum()), int(((t == c) & (p != c)).sum())
        out[c] = 2 * tp / (2 * tp + fp + fn) if 2 * tp + fp + fn else 0.0
    return out


def main() -> int:
    _, y, folds, other, ids = p1_04_06_tfidf.load("chapter")
    classes = sorted(c for c in set(y) if c != other)
    counts = {int(f): dict(Counter(c for c, g in zip(y, folds, strict=True) if g == f)) for f in sorted(set(folds.tolist()))}
    truth = dict(zip(ids, y, strict=True))
    fold0 = {i for i, g in zip(ids, folds, strict=True) if g == 0}
    result: dict = {"effectifs_par_pli_et_classe": counts, "modeles": {}}
    for name, slug in PREDS.items():
        pred = json.loads((ROOT / f"results/predictions/{slug}.json").read_text(encoding="utf-8"))
        pm = dict(zip(pred["ids"], pred["pred"], strict=True))
        sel = [i for i in pm if i in fold0]
        t, p = np.array([truth[i] for i in sel]), np.array([pm[i] for i in sel])
        f = f1s(t, p, classes)
        support = {c: int((t == c).sum()) for c in classes}
        w = sum(f[c] * support[c] for c in classes) / max(sum(support.values()), 1)
        zero = [c for c in classes if f[c] == 0.0 and support[c] > 0]
        dest = {c: dict(Counter(p[t == c]).most_common(4)) for c in zero}
        result["modeles"][name] = {"n": len(sel), "macro_f1": round(float(np.mean([f[c] for c in classes])), 4), "weighted_f1": round(w, 4),
                                   "micro_f1_accuracy": round(float((t == p).mean()), 4), "f1_nulle": zero, "destination_des_erreurs_f1_nulle": dest,
                                   "f1_par_classe": {c: round(f[c], 3) for c in classes}}
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(result, ensure_ascii=False, indent=1), encoding="utf-8")
    for n, m in result["modeles"].items():
        print(n, {k: m[k] for k in ("n", "macro_f1", "weighted_f1", "micro_f1_accuracy", "f1_nulle")})
    print(json.dumps(result["effectifs_par_pli_et_classe"][0], ensure_ascii=False))
    print(json.dumps(result["modeles"]["qwen3.5-9b-1e-4"]["destination_des_erreurs_f1_nulle"], ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
