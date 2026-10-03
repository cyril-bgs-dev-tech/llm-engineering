#!/usr/bin/env python3
"""Audit GLM v3, C5-A8 : hors distribution par spécialité exclue (leave-one-specialty-out) sur le TF-IDF du chapitre, développement seulement, EXPLORE.

Pour chaque spécialité : entraînement sur toutes les autres, évaluation sur elle ; exactitude et macro-F1 sur les chapitres présents. Usage : glm_v3_loso_tfidf.py"""
import json
import sys
from collections import Counter
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent))
import p1_04_06_tfidf
from llmft import tfidf


def main() -> int:
    run = json.loads(next((ROOT / "results/runs").glob("*-p1-06-tfidf-chapter.json")).read_text(encoding="utf-8"))
    cfg = next(c for c in run["metrics"]["chosen_config_by_fold"] if c["fold"] == 0)
    texts, y, _, excluded, ids = p1_04_06_tfidf.load("chapter")
    meta = pd.read_parquet(p1_04_06_tfidf.PARQUET, columns=["id", "specialty"])
    spec = dict(zip(meta["id"].astype(str), meta["specialty"].str.lower(), strict=True))
    sp = np.array([spec[i] for i in ids])
    labels = sorted(set(y))
    ya = np.array(y)
    out = {}
    for s, n in sorted(Counter(sp.tolist()).items()):
        te, tr = np.where(sp == s)[0], np.where(sp != s)[0]
        probs = tfidf.fit_predict_proba([texts[i] for i in tr], list(ya[tr]), [texts[i] for i in te], labels, cfg["C"], tuple(cfg["ngram"]))
        pred = np.array(labels)[probs.argmax(1)]
        present = [c for c in sorted(set(ya[te])) if c != excluded]
        f1 = []
        for c in present:
            tp, fp, fn = int(((ya[te] == c) & (pred == c)).sum()), int(((ya[te] != c) & (pred == c)).sum()), int(((ya[te] == c) & (pred != c)).sum())
            f1.append(2 * tp / (2 * tp + fp + fn) if 2 * tp + fp + fn else 0.0)
        out[s] = {"n": int(n), "accuracy": round(float((pred == ya[te]).mean()), 4), "macro_f1_classes_presentes": round(float(np.mean(f1)), 4), "chapitres": len(present)}
        print(s, out[s], flush=True)
    (ROOT / "results/measures/glm_v3_loso_tfidf.json").write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
