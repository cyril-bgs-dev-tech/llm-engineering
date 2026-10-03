#!/usr/bin/env python3
"""Q5 : fiabilité de l'incertitude d'un modèle sur le chapitre, à partir de probabilités hors pli (développement seulement ; test scellé jamais lu).

Par validation croisée sur les plis : pour chaque pli k, la température et les quantiles conformes sont ajustés sur les plis ≠ k, appliqués au pli k.
Rapporte : ECE (15 intervalles), ECE par classe, Brier, perte logarithmique avant et après température ; conforme (LAC et APS, marginal et par classe,
niveaux 90 % et 80 %) : couverture marginale et par classe avec Wilson, taille moyenne des ensembles ; prédiction sélective (AURC, exactitude à 90, 80, 70 %
de couverture). Option `--shift AUTRE.probs.npz` : étalonner sur ce modèle (plis par patient) et évaluer sur AUTRE (plis par auteur), même patients.
Usage : q5_uncertainty.py PROBS.npz SLUG [--shift PROBS_AUTEUR.npz] [--register]"""
import json
import sys
from pathlib import Path
from typing import Any

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent))
import p1_04_06_tfidf
from llmft import calibration, conformal, selective
from llmft.mini_registry import register_run


def load_probs(path: str) -> tuple[list[str], np.ndarray, list[str]]:
    z = np.load(path, allow_pickle=False)
    return [str(i) for i in z["ids"]], z["probs"].astype(np.float64), [str(c) for c in z["labels"]]


def summarize(sets: list[set[int]], y: np.ndarray, n_classes: int) -> dict[str, Any]:
    r = conformal.evaluate(sets, y)
    cov = r["coverage_by_class"]
    return {"coverage": round(r["coverage"], 4), "mean_set_size": round(r["mean_set_size"], 3), "singleton_rate": round(r["singleton_rate"], 3),
            "min_class_coverage": round(min(cov.values()), 3), "n": r["n"], "by_class": {str(k): round(v, 3) for k, v in cov.items()}}


def main() -> int:
    path, slug = sys.argv[1], sys.argv[2]
    ids, probs, labels = load_probs(path)
    _, y_all, fold_arr, _, ids_all = p1_04_06_tfidf.load("chapter")
    truth = dict(zip(ids_all, y_all, strict=True))
    lab_idx = {lab: i for i, lab in enumerate(labels)}
    y = np.array([lab_idx[truth[i]] for i in ids])
    fold_map = dict(zip(ids_all, fold_arr, strict=True))
    folds = np.array([fold_map[i] for i in ids])
    n_cls = len(labels)
    out: dict[str, Any] = {"n": len(ids), "classes": n_cls}
    # --- calibration croisée : température ajustée hors du pli évalué ---
    q = np.zeros_like(probs)
    temps = []
    for k in range(5):
        cal, te = folds != k, folds == k
        t = calibration.fit_temperature(probs[cal], y[cal])
        temps.append(round(t, 3))
        q[te] = calibration.apply_temperature(probs[te], t)
    out["calibration"] = {
        "temperatures_by_fold": temps,
        "before": {"ece": round(calibration.ece(probs, y), 4), "classwise_ece_mean": round(float(np.mean(list(calibration.classwise_ece(probs, y).values()))), 4),
                   "brier": round(calibration.brier(probs, y), 4), "nll": round(calibration.nll(probs, y), 4)},
        "after_cross_fitted_temperature": {"ece": round(calibration.ece(q, y), 4), "classwise_ece_mean": round(float(np.mean(list(calibration.classwise_ece(q, y).values()))), 4),
                                           "brier": round(calibration.brier(q, y), 4), "nll": round(calibration.nll(q, y), 4)}}
    # --- conforme croisé ---
    conf_out: dict[str, Any] = {}
    for alpha in (0.10, 0.20):
        for method in ("lac", "aps"):
            marg_sets: list[set[int]] = [set() for _ in ids]
            cls_sets: list[set[int]] = [set() for _ in ids]
            for k in range(5):
                cal, te = np.flatnonzero(folds != k), np.flatnonzero(folds == k)
                qh = conformal.fit(probs[cal], y[cal], alpha, method)
                qc = conformal.fit_by_class(probs[cal], y[cal], alpha, method, n_cls)
                for i, s in zip(te, conformal.predict_sets(probs[te], qh, method), strict=True):
                    marg_sets[i] = s
                for i, s in zip(te, conformal.predict_sets_by_class(probs[te], qc, method), strict=True):
                    cls_sets[i] = s
            conf_out[f"{method}_alpha{alpha:.2f}"] = {"marginal": summarize(marg_sets, y, n_cls), "by_class": summarize(cls_sets, y, n_cls), "target": round(1 - alpha, 2)}
    out["conformal"] = conf_out
    # --- sélectif ---
    conf, correct = probs.max(axis=1), (probs.argmax(axis=1) == y).astype(int)
    out["selective"] = {"aurc": round(selective.aurc(conf, correct), 4), "error_rate": round(1 - float(correct.mean()), 4),
                        "accuracy_at_coverage": {str(c): round(selective.accuracy_at_coverage(conf, correct, c), 4) for c in (1.0, 0.9, 0.8, 0.7)}}
    # --- décalage : étalonner sur ce modèle (plis par patient), évaluer sur l'autre (plis par auteur) ---
    if "--shift" in sys.argv:
        ids2, probs2, labels2 = load_probs(sys.argv[sys.argv.index("--shift") + 1])
        assert labels2 == labels
        pos = {i: j for j, i in enumerate(ids2)}
        probs2 = probs2[[pos[i] for i in ids]]
        shift: dict[str, Any] = {}
        for method in ("lac", "aps"):
            qh = conformal.fit(probs, y, 0.10, method)
            qc = conformal.fit_by_class(probs, y, 0.10, method, n_cls)
            shift[method] = {"marginal_on_author_folds": summarize(conformal.predict_sets(probs2, qh, method), y, n_cls),
                             "by_class_on_author_folds": summarize(conformal.predict_sets_by_class(probs2, qc, method), y, n_cls),
                             "marginal_same_scheme_reference": summarize(conformal.predict_sets(probs, qh, method), y, n_cls)}
        out["shift_patient_to_author_folds"] = shift
    print(json.dumps(out, ensure_ascii=False, indent=1))
    if "--register" in sys.argv:
        print(register_run(ROOT / "results/runs", {"kind": "measure", "slug": slug, "status": "ok",
              "summary": f"Fiabilité de l'incertitude (calibration, conforme, sélectif) de {Path(path).name} sur le développement, validation croisée par pli",
              "params": {"probs": Path(path).name, "alphas": [0.1, 0.2], "cross_fitted": True}, "metrics": out}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
