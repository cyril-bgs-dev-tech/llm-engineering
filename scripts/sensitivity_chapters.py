#!/usr/bin/env python3
"""Sensibilité de la macro-F1 regroupée à l'exclusion des chapitres XVIII (symptômes) et XXI (facteurs), à la suite de l'audit des erreurs confiantes (descriptif, EXPLORE).
Usage : sensitivity_chapters.py [--register]"""
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent))
import p1_04_06_tfidf
from llmft.cluster_bootstrap import cluster_interval
from llmft.mini_registry import register_run
from llmft.power_rule import _macro_f1

P = ROOT / "results/predictions"


def load(name: str) -> tuple[list[str], np.ndarray, list[str]]:
    z = np.load(P / f"{name}.probs.npz", allow_pickle=False)
    return [str(i) for i in z["ids"]], z["probs"].astype(np.float64), [str(c) for c in z["labels"]]


def main() -> int:
    _, y, _, other, ids_all = p1_04_06_tfidf.load("chapter")
    truth_of = dict(zip(ids_all, y, strict=True))
    meta = pd.read_parquet(p1_04_06_tfidf.PARQUET, columns=["id", "author"])
    author_of = dict(zip(meta["id"].astype(str), meta["author"], strict=True))
    ids, enc, labels = load("cinq-plis-ensemble-encodeur5")
    pos = {i: k for k, i in enumerate(load("tfidf-variant-char-balanced")[0])}
    tf = load("tfidf-variant-char-balanced")[1][[pos[i] for i in ids]]
    mix = 0.5 * enc + 0.5 * tf
    truth = np.array([labels.index(truth_of[i]) for i in ids])
    groups = [author_of[i] for i in ids]
    base = [labels.index(c) for c in labels if c != other]
    variants = {"17 chapitres": base, "sans XVIII": [c for c in base if labels[c] != "XVIII"], "sans XVIII ni XXI": [c for c in base if labels[c] not in ("XVIII", "XXI")]}
    out: dict[str, object] = {}
    for vname, scored in variants.items():
        row: dict[str, object] = {}
        for sysname, probs in (("tfidf", tf), ("encodeur", enc), ("ensemble", mix)):
            row[sysname] = round(float(_macro_f1(truth[None, :], probs.argmax(1)[None, :], scored)[0]), 4)
        d, lo, hi = cluster_interval(truth, mix.argmax(1), tf.argmax(1), scored, groups)
        row["ensemble_moins_tfidf_points"] = [round(d, 2), round(lo, 2), round(hi, 2)]
        out[vname] = row
        print(vname, row, flush=True)
    f1 = {}
    for name in ("XVIII", "XXI"):
        c = labels.index(name)
        tp = int(((truth == c) & (mix.argmax(1) == c)).sum())
        fp = int(((truth != c) & (mix.argmax(1) == c)).sum())
        fn = int(((truth == c) & (mix.argmax(1) != c)).sum())
        f1[name] = {"n": int((truth == c).sum()), "f1_ensemble": round(2 * tp / max(2 * tp + fp + fn, 1), 3)}
    out["f1_chapitres"] = f1
    print(f1)
    (ROOT / "results/measures/sensitivity_chapters.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
    if "--register" in sys.argv:
        print(register_run(ROOT / "results/runs", {"kind": "measure", "slug": "sensibilite-xviii-xxi", "status": "ok", "summary": "Sensibilité de la macro-F1 à l'exclusion des chapitres XVIII et XXI (descriptif)", "params": {}, "metrics": out}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
