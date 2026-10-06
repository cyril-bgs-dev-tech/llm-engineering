#!/usr/bin/env python3
"""Analyse de l'encodeur en plis groupés par auteur (RM-39, fiche 2026-10-06-encodeur-plis-auteurs) : moyenne des graines disponibles par pli, prédictions regroupées sur 3 586 patients,
comparaison avec le TF-IDF caractères équilibré en plis d'auteurs (bootstrap par blocs d'auteurs, verdict à trois valeurs de la fiche, δ = 2,0), perte par rapport aux plis par patient.
Usage : encoder_author_analysis.py [--register]. Développement seulement."""
import glob
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent))
import p1_04_06_tfidf
from llmft import evaluation
from llmft.cluster_bootstrap import cluster_interval
from llmft.mini_registry import register_run
from llmft.power_rule import _macro_f1

DELTA = 2.0
TFIDF_AUTHOR_FILE = "tfidf-variant-char-balanced-author"
TFIDF_PATIENT = 0.7202
ENCODER_PATIENT_BF16 = 0.7598
TFIDF_LOSS = 4.6


def verdict(lo: float, hi: float) -> str:
    return "gain confirmé" if lo > DELTA else ("absence de gain utile" if hi < DELTA else "non résolu")


def loss_reading(loss: float) -> str:
    return "plus faible" if loss < TFIDF_LOSS - 1.0 else ("comparable" if loss <= TFIDF_LOSS + 1.0 else "plus fort")


def main() -> int:
    _, y, _, other, ids_all = p1_04_06_tfidf.load("chapter", "control_folds_by_author")
    labels = sorted(set(y))
    idx = {i: labels.index(v) for i, v in zip(ids_all, y, strict=True)}
    meta = pd.read_parquet(p1_04_06_tfidf.PARQUET, columns=["id", "author"])
    author_of = dict(zip(meta["id"].astype(str), meta["author"], strict=True))
    seeds = sorted({int(f.split("-s")[-1].split(".")[0]) for f in glob.glob(str(ROOT / "results/predictions/enc-auteur-pli*-s*.probs.npz"))})
    ids_pooled: list[str] = []
    parts: list[np.ndarray] = []
    for k in range(5):
        mats, ref_ids = [], None
        for s in seeds:
            z = np.load(ROOT / f"results/predictions/enc-auteur-pli{k}-s{s}.probs.npz", allow_pickle=False)
            ids = [str(i) for i in z["ids"]]
            ref_ids = ref_ids or ids
            pos = {i: j for j, i in enumerate(ids)}
            mats.append(z["probs"].astype(np.float64)[[pos[i] for i in ref_ids]])
        ids_pooled += ref_ids or []
        parts.append(np.mean(mats, axis=0))
    probs = np.vstack(parts)
    truth = np.array([idx[i] for i in ids_pooled])
    scored = [labels.index(c) for c in labels if c != other]
    groups = [author_of[i] for i in ids_pooled]
    z = np.load(ROOT / f"results/predictions/{TFIDF_AUTHOR_FILE}.probs.npz", allow_pickle=False)
    pos = {str(i): j for j, i in enumerate(z["ids"])}
    tf = z["probs"].astype(np.float64)[[pos[i] for i in ids_pooled]]
    f1_enc = float(_macro_f1(truth[None, :], probs.argmax(1)[None, :], scored)[0]) * 100
    f1_tf = float(_macro_f1(truth[None, :], tf.argmax(1)[None, :], scored)[0]) * 100
    d, lo, hi = cluster_interval(truth, probs.argmax(1), tf.argmax(1), scored, groups)
    rep = evaluation.chapter_report(truth, probs, labels, excluded=(other,) if other else ())
    loss = ENCODER_PATIENT_BF16 * 100 - f1_enc
    out = {"graines": seeds, "n_patients": len(ids_pooled), "macro_f1_encodeur_plis_auteurs": round(f1_enc / 100, 4), "macro_f1_tfidf_plis_auteurs": round(f1_tf / 100, 4),
           "a_encodeur_moins_tfidf_points": [round(d, 2), round(lo, 2), round(hi, 2)], "a_verdict": verdict(lo, hi),
           "b_perte_encodeur_points": round(loss, 2), "b_perte_tfidf_points": round((TFIDF_PATIENT * 100) - f1_tf, 2), "b_lecture": loss_reading(loss),
           "exactitude": round(rep["accuracy"], 4), "log_loss": round(rep["log_loss"], 4), "ece": round(rep["ece"], 4)}
    print(json.dumps(out, ensure_ascii=False, indent=1))
    (ROOT / "results/measures/encoder_author_analysis.json").write_text(json.dumps(out, indent=1, ensure_ascii=False), encoding="utf-8")
    if "--register" in sys.argv:
        print(register_run(ROOT / "results/runs", {"kind": "measure", "slug": "encodeur-plis-auteurs-analyse", "status": "ok", "summary": f"Encodeur en plis d'auteurs contre TF-IDF : {out['a_verdict']}, perte {out['b_perte_encodeur_points']} points ({out['b_lecture']})",
                                                    "params": {"fiche": "experiments/2026-10-06-encodeur-plis-auteurs.md", "delta": DELTA}, "metrics": out}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
