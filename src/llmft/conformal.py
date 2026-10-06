"""Prédiction conforme pour la classification (Q5, PROTOCOLE.md 6.6) : LAC et APS déterministes, marginale ou par classe (Mondrian), évaluation.

Quantile fini : k = ceil((n + 1)(1 - alpha)) ; si k > n le quantile est infini (la garantie exige trop d'exemples de calibration), donc la classe
est toujours incluse, par prudence. Les effectifs de calibration par classe sont ceux de la calibration, jamais du test."""
from __future__ import annotations

import math
from collections.abc import Mapping, Sequence
from typing import Any

import numpy as np
from numpy.typing import NDArray


def conformal_quantile(scores: NDArray[np.float64], alpha: float) -> float:
    if not 0.0 < alpha < 1.0:
        raise ValueError(f"alpha doit être dans ]0, 1[, reçu {alpha}")
    n = len(scores)
    k = math.ceil((n + 1) * (1 - alpha))
    return float("inf") if k > n or n == 0 else float(np.sort(scores)[k - 1])


def _scores_all(probs: NDArray[np.float64], method: str) -> NDArray[np.float64]:
    """Score de non-conformité de chaque classe pour chaque exemple (grand = peu conforme)."""
    if method == "lac":
        return np.asarray(1.0 - probs)
    if method == "aps":  # masse cumulée des classes au moins aussi probables, la classe comprise
        order = np.argsort(-probs, axis=1)
        cum = np.cumsum(np.take_along_axis(probs, order, axis=1), axis=1)
        scores = np.empty_like(probs)
        np.put_along_axis(scores, order, cum, axis=1)
        # classes à égalité de probabilité : même score (la plus grande masse cumulée)
        for i in range(len(probs)):
            for v in np.unique(probs[i]):
                m = probs[i] == v
                if m.sum() > 1:
                    scores[i, m] = scores[i, m].max()
        return scores
    raise ValueError(f"méthode inconnue : {method!r} (lac ou aps)")


def fit(probs: NDArray[np.float64], y: NDArray[np.int_], alpha: float, method: str = "lac") -> float:
    if not np.isfinite(probs).all():
        raise ValueError("probabilités non finies (NaN ou infini) : calibration refusée")
    s = _scores_all(probs, method)[np.arange(len(y)), y]
    return conformal_quantile(s, alpha)


def fit_by_class(probs: NDArray[np.float64], y: NDArray[np.int_], alpha: float, method: str, n_classes: int) -> dict[int, float]:
    s = _scores_all(probs, method)[np.arange(len(y)), y]
    return {c: conformal_quantile(s[y == c], alpha) for c in range(n_classes)}


def fit_by_group(probs: NDArray[np.float64], y: NDArray[np.int_], group_of_class: Mapping[int, int], alpha: float, method: str = "lac") -> dict[int, float]:
    """Quantile par groupe de classes (famille) : calibré sur les exemples dont la **vraie** classe est dans le groupe ; le groupe sans exemple reçoit un quantile infini."""
    s = _scores_all(probs, method)[np.arange(len(y)), y]
    groups = np.array([group_of_class[int(c)] for c in y])
    return {g: conformal_quantile(s[groups == g], alpha) for g in set(group_of_class.values())}


def predict_sets_by_group(probs: NDArray[np.float64], qhats: Mapping[int, float], group_of_class: Mapping[int, int], method: str = "lac") -> list[set[int]]:
    """La classe candidate c est dans l'ensemble si son score est sous le quantile du groupe de c (aucune étiquette de test n'intervient)."""
    s = _scores_all(probs, method)
    return [{c for c in range(s.shape[1]) if row[c] <= qhats[group_of_class[c]]} for row in s]


def predict_sets(probs: NDArray[np.float64], qhat: float, method: str = "lac") -> list[set[int]]:
    s = _scores_all(probs, method)
    return [set(np.flatnonzero(row <= qhat).tolist()) for row in s]


def predict_sets_by_class(probs: NDArray[np.float64], qhats: Mapping[int, float], method: str = "lac") -> list[set[int]]:
    s = _scores_all(probs, method)
    return [{c for c in range(s.shape[1]) if row[c] <= qhats[c]} for row in s]


def wilson(k: int, n: int, z: float = 1.96) -> tuple[float, float]:
    if n == 0:
        return 0.0, 1.0
    p = k / n
    d = 1 + z * z / n
    centre = (p + z * z / (2 * n)) / d
    half = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return max(0.0, centre - half), min(1.0, centre + half)


def evaluate(sets: Sequence[set[int]], y: NDArray[np.int_]) -> dict[str, Any]:
    hit = np.array([int(t) in s for s, t in zip(sets, y, strict=True)])
    sizes = np.array([len(s) for s in sets])
    by_class = {int(c): float(hit[y == c].mean()) for c in np.unique(y)}
    wilson_by_class = {int(c): wilson(int(hit[y == c].sum()), int((y == c).sum())) for c in np.unique(y)}
    return {"coverage": float(hit.mean()), "coverage_by_class": by_class, "coverage_by_class_wilson": wilson_by_class, "mean_set_size": float(sizes.mean()),
            "singleton_rate": float((sizes == 1).mean()), "empty_rate": float((sizes == 0).mean()), "n": len(y)}
