#!/usr/bin/env python3
"""Entraînement débiaisé par auteur du TF-IDF (fiche 2026-10-04-debiaisage-auteur-tfidf, EXPLORE) : poids d'exemples décroissants avec le volume de l'auteur.

Modes de poids : none, inv, invsqrt ; schémas : patient (StratifiedKFold) et auteur (StratifiedGroupKFold) ; cinq plis, graine 1, TF-IDF mots (1, 2), C = 100. Développement seulement.
Usage : author_debias_tfidf.py [--register]"""
import json
import sys
import time
from collections import Counter
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.model_selection import StratifiedGroupKFold, StratifiedKFold

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent))
import p1_04_06_tfidf
from llmft import tfidf
from llmft.mini_registry import register_run
from llmft.power_rule import _macro_f1


def weights(authors: np.ndarray, mode: str) -> np.ndarray | None:
    if mode == "none":
        return None
    counts = Counter(authors.tolist())
    n = np.array([counts[a] for a in authors], dtype=float)
    w = n.mean() / n
    if mode == "invsqrt":
        w = np.sqrt(w)
    return w / w.mean()


def main() -> int:
    texts, y, _, other, ids = p1_04_06_tfidf.load("chapter")
    meta = pd.read_parquet(p1_04_06_tfidf.PARQUET, columns=["id", "author"])
    author = dict(zip(meta["id"].astype(str), meta["author"], strict=True))
    groups = np.array([author[i] for i in ids])
    labels = sorted(set(y))
    t = np.array([labels.index(v) for v in y])
    scored = [labels.index(c) for c in labels if c != other]
    out: dict = {}
    t0 = time.time()
    for scheme in ("patient", "auteur"):
        splitter = StratifiedKFold(5, shuffle=True, random_state=1) if scheme == "patient" else StratifiedGroupKFold(5, shuffle=True, random_state=1)
        splits = list(splitter.split(np.zeros(len(y)), t, groups))
        for mode in ("none", "inv", "invsqrt"):
            oof = np.zeros((len(y), len(labels)))
            for tr, te in splits:
                sw = weights(groups[tr], mode)
                oof[te] = tfidf.fit_predict_proba([texts[i] for i in tr], [y[i] for i in tr], [texts[i] for i in te], labels, 100.0, (1, 2), sample_weight=sw)
            mf = float(_macro_f1(t[None, :], oof.argmax(1)[None, :], scored)[0])
            out[f"{scheme}-{mode}"] = round(mf, 4)
            np.savez_compressed(ROOT / f"results/predictions/tfidf-debias-{scheme}-{mode}.probs.npz", ids=np.array(ids), probs=oof, labels=np.array(labels))
            print(scheme, mode, round(mf, 4), round(time.time() - t0), "s", flush=True)
    out["ecart_patient_moins_auteur"] = {m: round(100 * (out[f"patient-{m}"] - out[f"auteur-{m}"]), 2) for m in ("none", "inv", "invsqrt")}
    (ROOT / "results/measures/author_debias_tfidf.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
    print(json.dumps(out))
    if "--register" in sys.argv:
        print(register_run(ROOT / "results/runs", {"kind": "measure", "slug": "author-debias-tfidf", "status": "ok", "summary": f"Débiaisage par auteur du TF-IDF : écarts patient moins auteur {out['ecart_patient_moins_auteur']}", "params": {"seed": 1}, "metrics": out}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
