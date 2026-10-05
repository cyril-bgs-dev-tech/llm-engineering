#!/usr/bin/env python3
"""Aperçu de la règle de puissance du protocole v2 (brouillon) : largeur de l'IC de la différence appariée « ensemble encodeur + TF-IDF moins TF-IDF » sur les plis dont les encodeurs sont entraînés.

Lit les probabilités hors pli par pli (encodeur moyenné sur cinq graines, TF-IDF caractères et poids équilibrés), forme les prédictions regroupées, calcule la largeur à 95 % (comparaison primaire unique)
et à 98,33 % (trois comparaisons). Développement seulement. Usage : v2_power_preview.py [--register]"""
import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent))
import p1_04_06_tfidf
from llmft.mini_registry import register_run
from llmft.power_rule import pooled_interval, pooled_width

P = ROOT / "results/predictions"
FOLDS = {0: ("ensemble-encodeur5", None), 1: ("pli1-ensemble-encodeur5", None), 2: ("pli2-ensemble-encodeur5", None), 3: ("pli3-ensemble-encodeur5", None), 4: ("pli4-ensemble-encodeur5", None)}


def load(name: str) -> tuple[list[str], np.ndarray, list[str]]:
    z = np.load(P / f"{name}.probs.npz", allow_pickle=False)
    return [str(i) for i in z["ids"]], z["probs"].astype(float), [str(c) for c in z["labels"]]


def main() -> int:
    _, y, _, other, ids = p1_04_06_tfidf.load("chapter")
    truth_of = dict(zip(ids, y, strict=True))
    it, pt, labels = load("tfidf-variant-char-balanced")
    pos_t = {i: k for k, i in enumerate(it)}
    all_ids, p_enc, p_tf = [], [], []
    used = []
    for fold, (name, _) in FOLDS.items():
        if not (P / f"{name}.probs.npz").exists():
            continue
        ie, pe, _ = load(name)
        all_ids += ie
        p_enc.append(pe)
        p_tf.append(pt[[pos_t[i] for i in ie]])
        used.append(fold)
    enc, tf = np.vstack(p_enc), np.vstack(p_tf)
    truth = np.array([labels.index(truth_of[i]) for i in all_ids])
    scored = [labels.index(c) for c in labels if c != other]
    ens = 0.5 * enc + 0.5 * tf
    out = {"plis": used, "n": len(all_ids), "largeur_ensemble_moins_tfidf_95": round(pooled_width(truth, ens.argmax(1), tf.argmax(1), scored, level=0.95), 2),
           "largeur_ensemble_moins_tfidf_98_33": round(pooled_width(truth, ens.argmax(1), tf.argmax(1), scored), 2),
           "largeur_encodeur_moins_tfidf_95": round(pooled_width(truth, enc.argmax(1), tf.argmax(1), scored, level=0.95), 2), "seuil": 4.0}
    d_e, lo_e, hi_e = pooled_interval(truth, ens.argmax(1), tf.argmax(1), scored, level=0.95)
    d_c, lo_c, hi_c = pooled_interval(truth, enc.argmax(1), tf.argmax(1), scored, level=0.95)
    out.update({"ensemble_moins_tfidf_points": round(d_e, 2), "ic95_ensemble_moins_tfidf": [round(lo_e, 2), round(hi_e, 2)], "encodeur_moins_tfidf_points": round(d_c, 2), "ic95_encodeur_moins_tfidf": [round(lo_c, 2), round(hi_c, 2)]})
    print(json.dumps(out))
    (ROOT / "results/measures/v2_power_preview.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
    if "--register" in sys.argv:
        print(register_run(ROOT / "results/runs", {"kind": "measure", "slug": f"v2-power-preview-{len(used)}-plis", "status": "ok", "summary": f"Largeur de l'IC ensemble moins TF-IDF sur {len(used)} plis : {out['largeur_ensemble_moins_tfidf_95']} points", "params": {"plis": used}, "metrics": out}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
