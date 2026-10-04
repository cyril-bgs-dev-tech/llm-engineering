#!/usr/bin/env python3
"""Élève TF-IDF à étiquettes souples (RM-46, fiche 2026-10-04-tfidf-souple) : cinq plis, professeur strictement hors pli, aucun réglage.

Usage : tfidf_soft.py PROFESSEUR_CINQ_PLIS.probs.npz SLUG [--register]   (développement seulement)"""
import json
import sys
import time
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent))
import p1_04_06_tfidf
from llmft import distill, evaluation, soft_labels, tfidf
from llmft.mini_registry import register_run

C_BY_FOLD = {0: 100.0, 1: 10.0, 2: 1000.0, 3: 100.0, 4: 10.0}  # repris du run tfidf-variant-char-balanced
ALPHA, THRESHOLD = 0.5, 0.05


def main() -> int:
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    teacher_path, slug = args
    texts, y, folds, excluded, ids = p1_04_06_tfidf.load("chapter")
    labels = sorted(set(y))
    idx = np.array([labels.index(v) for v in y])
    fold_of = dict(zip(ids, folds.tolist(), strict=True))
    z = np.load(teacher_path, allow_pickle=False)
    if [str(c) for c in z["labels"]] != labels:
        raise SystemExit("classes différentes du professeur")
    t_ids = [str(i) for i in z["ids"]]
    t_probs = z["probs"].astype(np.float64)
    oof = np.zeros((len(y), len(labels)))
    t0 = time.time()
    for k in range(5):
        tr, te = np.where(folds != k)[0], np.where(folds == k)[0]
        by_fold = {f: ([i for i in t_ids if fold_of[i] == f], None) for f in range(5) if f != k}
        files = {f: (ids_f, np.stack([t_probs[t_ids.index(i)] for i in ids_f])) for f, (ids_f, _) in by_fold.items()}
        tmap = distill.oof_teacher_map(files, fold_of)
        teacher = distill.require_teacher([ids[i] for i in tr], tmap)
        rows, classes, weights = soft_labels.replicate_soft([int(idx[i]) for i in tr], teacher, ALPHA, THRESHOLD)
        x_texts = [texts[tr[r]] for r in rows]
        x_y = [labels[c] for c in classes]
        oof[te] = tfidf.fit_predict_proba(x_texts, x_y, [texts[i] for i in te], labels, C_BY_FOLD[k], (3, 5), "balanced", "char_wb", weights)
        print(k, len(rows), "lignes répliquées", round(time.time() - t0), "s", flush=True)
    rep = evaluation.chapter_report(idx, oof, labels, excluded=(excluded,))
    out = {"macro_f1": rep["macro_f1"], "accuracy": rep["accuracy"], "log_loss": rep["log_loss"], "seconds": round(time.time() - t0), "alpha": ALPHA, "seuil": THRESHOLD, "c_par_pli": C_BY_FOLD}
    np.savez_compressed(ROOT / f"results/predictions/{slug}.probs.npz", ids=np.array(ids), probs=oof, labels=np.array(labels))
    print(json.dumps(out))
    if "--register" in sys.argv:
        print(register_run(ROOT / "results/runs", {"kind": "train", "slug": slug, "status": "ok", "summary": f"{slug} : macro-F1 {rep['macro_f1']:.4f} sur cinq plis (TF-IDF à étiquettes souples)", "params": {"teacher": Path(teacher_path).name, "alpha": ALPHA, "threshold": THRESHOLD}, "metrics": out}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
