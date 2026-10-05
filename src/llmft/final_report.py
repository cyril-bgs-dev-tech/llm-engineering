"""Calculs du rapport de confirmation (PROTOCOLE_V2.md section 5) : métriques par système, différences avec intervalles par blocs d'auteurs et par patients, verdict en trois valeurs, couverture conforme,
abstention, sensibilité. Fonctions pures, testables sur le développement (répétition générale) avant toute lecture d'étiquettes du test."""
from collections.abc import Mapping, Sequence
from typing import Any

import numpy as np
from numpy.typing import NDArray

from llmft import conformal
from llmft.cluster_bootstrap import cluster_interval
from llmft.power_rule import _macro_f1, pooled_interval


def verdict(lower: float, upper: float, delta: float) -> str:
    """Verdict en trois valeurs d'ADR-007 : gain confirmé si L > delta, absence de gain utile si U < delta, non résolu sinon."""
    if lower > delta:
        return "gain confirmé"
    if upper < delta:
        return "absence de gain utile"
    return "non résolu"


def macro_f1(truth: NDArray[np.int_], pred: NDArray[np.int_], scored: Sequence[int]) -> float:
    return float(_macro_f1(truth[None, :], pred[None, :], scored)[0])


def system_metrics(truth: NDArray[np.int_], probs: NDArray[np.float64], scored: Sequence[int], labels: Sequence[str]) -> dict[str, Any]:
    pred = probs.argmax(1)
    per_class = {}
    for c in scored:
        tp = int(((truth == c) & (pred == c)).sum())
        fp = int(((truth != c) & (pred == c)).sum())
        fn = int(((truth == c) & (pred != c)).sum())
        per_class[labels[c]] = {"n": int((truth == c).sum()), "f1": round(2 * tp / max(2 * tp + fp + fn, 1), 4)}
    return {"macro_f1": round(macro_f1(truth, pred, scored), 4), "accuracy": round(float((pred == truth).mean()), 4), "f1_par_chapitre": per_class}


def compare(truth: NDArray[np.int_], probs_a: NDArray[np.float64], probs_b: NDArray[np.float64], scored: Sequence[int], groups: Sequence[str], n_boot: int = 5000, seed: int = 20261005) -> dict[str, Any]:
    """A moins B : écart observé et IC 95 % par blocs d'auteurs et par patients (points de macro-F1)."""
    d, lo, hi = cluster_interval(truth, probs_a.argmax(1), probs_b.argmax(1), scored, groups, n_boot=n_boot, seed=seed)
    _, lo_p, hi_p = pooled_interval(truth, probs_a.argmax(1), probs_b.argmax(1), scored, n_boot=n_boot, level=0.95)
    return {"difference_points": round(d, 2), "ic95_blocs_auteurs": [round(lo, 2), round(hi, 2)], "ic95_patients": [round(lo_p, 2), round(hi_p, 2)]}


def conformal_report(
    cal_probs: NDArray[np.float64], cal_truth: NDArray[np.int_], test_probs: NDArray[np.float64], test_truth: NDArray[np.int_], family_of_class: Mapping[int, int], alpha: float = 0.10,
) -> dict[str, Any]:
    """Quantiles calibrés sur le développement seulement, appliqués au jeu évalué : couverture et taille, marginales et par famille (Mondrian), couverture minimale par famille."""
    qhat = conformal.fit(cal_probs, cal_truth, alpha)
    marginal = conformal.evaluate(conformal.predict_sets(test_probs, qhat), test_truth)
    q_group = conformal.fit_by_group(cal_probs, cal_truth, family_of_class, alpha)
    sets = conformal.predict_sets_by_group(test_probs, q_group, family_of_class)
    by_family = {}
    fam_arr = np.array([family_of_class[int(c)] for c in test_truth])
    for g in sorted(set(family_of_class.values())):
        sel = fam_arr == g
        if sel.any():
            covered = sum(int(test_truth[i]) in sets[i] for i in np.flatnonzero(sel))
            by_family[int(g)] = {"n": int(sel.sum()), "couverture": round(covered / int(sel.sum()), 3)}
    overall = sum(int(test_truth[i]) in s for i, s in enumerate(sets)) / len(sets)
    return {"niveau_vise": 1 - alpha, "marginal": {"couverture": round(float(marginal["coverage"]), 3), "taille_moyenne": round(float(marginal["mean_set_size"]), 3)},
            "par_famille": {"couverture": round(float(overall), 3), "taille_moyenne": round(float(np.mean([len(s) for s in sets])), 3), "couverture_minimale": min(v["couverture"] for v in by_family.values()), "details": by_family}}


def abstention_table(probs: NDArray[np.float64], truth: NDArray[np.int_], coverages: Sequence[float] = (1.0, 0.9, 0.8, 0.7, 0.5)) -> dict[str, Any]:
    conf, correct = probs.max(1), (probs.argmax(1) == truth).astype(int)
    order = np.argsort(-conf, kind="stable")
    out = {}
    for c in coverages:
        k = max(1, round(c * len(conf)))
        hits = int(correct[order[:k]].sum())
        lo, hi = conformal.wilson(hits, k)
        out[str(c)] = {"n_traites": k, "exactitude": round(hits / k, 3), "wilson95": [round(lo, 3), round(hi, 3)]}
    return out


def full_report(
    truth: NDArray[np.int_], probs_by_model: Mapping[str, NDArray[np.float64]], labels: Sequence[str], other: str, groups: Sequence[str], final: str, reference: str, secondary: Sequence[str],
    delta: float, family_of_class: Mapping[int, int], calibration: Mapping[str, tuple[NDArray[np.float64], NDArray[np.int_]]], n_boot: int = 5000,
) -> dict[str, Any]:
    """Rapport complet : métriques de chaque système, question primaire (final moins référence, verdict), comparaisons secondaires (sans verdict), incertitude du système final, sensibilité."""
    scored = [i for i, c in enumerate(labels) if c != other]
    out: dict[str, Any] = {"n": len(truth), "systemes": {m: system_metrics(truth, p, scored, labels) for m, p in probs_by_model.items()}}
    primary = compare(truth, probs_by_model[final], probs_by_model[reference], scored, groups, n_boot)
    lo, hi = primary["ic95_blocs_auteurs"]
    out["question_primaire"] = {"final": final, "reference": reference, **primary, "delta": delta, "verdict": verdict(lo, hi, delta)}
    out["secondaires_sans_verdict"] = {f"{final} moins {s}": compare(truth, probs_by_model[final], probs_by_model[s], scored, groups, n_boot) for s in secondary}
    cal_p, cal_y = calibration[final]
    out["incertitude_systeme_final"] = {"conforme": conformal_report(cal_p, cal_y, probs_by_model[final], truth, family_of_class), "abstention": abstention_table(probs_by_model[final], truth)}
    sens = {}
    for name, drop in (("sans XVIII", ("XVIII",)), ("sans XVIII ni XXI", ("XVIII", "XXI"))):
        sc = [c for c in scored if labels[c] not in drop]
        sens[name] = {m: round(macro_f1(truth, p.argmax(1), sc), 4) for m, p in probs_by_model.items()}
    out["sensibilite"] = sens
    return out
