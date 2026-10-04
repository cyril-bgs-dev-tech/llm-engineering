#!/usr/bin/env python3
"""Audit GLM v4, F-c1 : leave-one-author-out sur le TF-IDF du chapitre (estimation « nouveaux auteurs »), développement seulement, EXPLORE.

Pour chaque auteur d'au moins 20 patients : entraînement sur tous les autres patients du développement, prédiction de ses patients. Les prédictions hors auteur sont regroupées
(macro-F1 sur 17 chapitres) et comparées aux estimations par patient (0,6844) et par plis d'auteurs (0,6457). Configuration fixe C = 100, n-grammes (1, 2).
Usage : loao_tfidf.py [--register]"""
import json
import sys
import time
from collections import Counter
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent))
import p1_04_06_tfidf
from llmft import evaluation, tfidf
from llmft.mini_registry import register_run


def main() -> int:
    texts, y, _, excluded, ids = p1_04_06_tfidf.load("chapter")
    meta = pd.read_parquet(p1_04_06_tfidf.PARQUET, columns=["id", "author"])
    author = dict(zip(meta["id"].astype(str), meta["author"], strict=True))
    au = np.array([author[i] for i in ids])
    labels = sorted(set(y))
    idx = np.array([labels.index(v) for v in y])
    big = [a for a, n in Counter(au.tolist()).items() if n >= 20]
    keep = np.flatnonzero(np.isin(au, big))
    oof = np.zeros((len(y), len(labels)))
    t0 = time.time()
    for k, a in enumerate(sorted(big)):
        te = np.flatnonzero(au == a)
        tr = np.flatnonzero(au != a)
        oof[te] = tfidf.fit_predict_proba([texts[i] for i in tr], [y[i] for i in tr], [texts[i] for i in te], labels, 100.0, (1, 2))
        print(k + 1, "/", len(big), round(time.time() - t0), "s", flush=True)
    rep = evaluation.chapter_report(idx[keep], oof[keep], labels, excluded=(excluded,))
    out = {"n_auteurs": len(big), "n_patients": len(keep), "macro_f1": rep["macro_f1"], "accuracy": rep["accuracy"], "log_loss": rep["log_loss"], "seconds": round(time.time() - t0)}
    np.savez_compressed(ROOT / "results/predictions/tfidf-loao.probs.npz", ids=np.array([ids[i] for i in keep]), probs=oof[keep], labels=np.array(labels))
    print(json.dumps(out))
    if "--register" in sys.argv:
        print(register_run(ROOT / "results/runs", {"kind": "train", "slug": "tfidf-loao", "status": "ok", "summary": f"TF-IDF leave-one-author-out ({len(big)} auteurs) : macro-F1 {rep['macro_f1']:.4f}", "params": {"c": 100.0, "ngram": [1, 2]}, "metrics": out}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
