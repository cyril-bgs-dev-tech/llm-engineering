#!/usr/bin/env python3
"""Piste « hiérarchie comme supervision » (EXPLORE) : TF-IDF entraîné sur les blocs CIM-10 (plus fins que le chapitre), probabilités agrégées par chapitre.

Cinq plis par patient, configuration fixe C = 100, n-grammes (1, 2) (celle de la référence), poids équilibrés ou non. Développement seulement.
Usage : hier_supervision_tfidf.py {plain|balanced} [--register]"""
import json
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent))
import p1_04_06_tfidf as base
from llmft import cim10, evaluation, loader, splits, tfidf
from llmft.mini_registry import register_run


def main() -> int:
    mode = sys.argv[1]
    parts = loader.load_partitions(base.PART, base.SHA)
    fold_of = {pid: k for k, ids in enumerate(parts["folds"]) for pid in ids}
    df = pd.read_parquet(base.PARQUET, columns=["id", "suggested_scenario", "documents"])
    df = df[df["id"].isin(fold_of)].copy()
    h = cim10.load_claml(base.CLAML)
    res = df["suggested_scenario"].map(lambda s: h.lookup(s["primary_diagnosis"]["code"][0]))
    df = df[res.notna()].copy()
    res = res[res.notna()]
    df["chapter"] = splits.apply_rare_class_policy(res.map(lambda r: r.chapter))
    df["block"] = res.map(lambda r: r.block).to_numpy()
    df["fold"] = df["id"].map(fold_of)
    texts = [base.patient_text(d) for d in df["documents"]]
    y_ch = df["chapter"].tolist()
    blocks = df["block"].tolist()
    folds = df["fold"].to_numpy()
    ids = df["id"].astype(str).tolist()
    labels = sorted(set(y_ch))
    block_to_chapter = {b: c for b, c in zip(blocks, y_ch, strict=True)}
    blabels = sorted(set(blocks))
    cw = "balanced" if mode == "balanced" else None
    oof = np.zeros((len(y_ch), len(labels)))
    t0 = time.time()
    for k in range(5):
        tr, te = np.where(folds != k)[0], np.where(folds == k)[0]
        vec, model = tfidf.fit_model([texts[i] for i in tr], [blocks[i] for i in tr], 100.0, (1, 2), cw)
        pb = tfidf.predict_aligned(vec, model, [texts[i] for i in te], blabels)
        for j, b in enumerate(blabels):
            oof[te, labels.index(block_to_chapter[b])] += pb[:, j]
        print(k, round(time.time() - t0), "s", len(blabels), "blocs", flush=True)
    idx = np.array([labels.index(v) for v in y_ch])
    rep = evaluation.chapter_report(idx, oof, labels, excluded=("AUTRE",))
    out = {"mode": mode, "macro_f1": rep["macro_f1"], "accuracy": rep["accuracy"], "log_loss": rep["log_loss"], "n_blocs": len(blabels), "seconds": round(time.time() - t0)}
    np.savez_compressed(ROOT / f"results/predictions/tfidf-hier-{mode}.probs.npz", ids=np.array(ids), probs=oof, labels=np.array(labels))
    print(json.dumps(out))
    if "--register" in sys.argv:
        print(register_run(ROOT / "results/runs", {"kind": "train", "slug": f"tfidf-hier-{mode}", "status": "ok", "summary": f"TF-IDF supervisé sur les blocs CIM-10, agrégé par chapitre ({mode}) : macro-F1 {rep['macro_f1']:.4f}", "params": {"mode": mode}, "metrics": out}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
