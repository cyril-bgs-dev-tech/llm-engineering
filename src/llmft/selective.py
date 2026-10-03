"""Prédiction sélective (Q5) : courbe risque-couverture, aire sous la courbe (AURC), exactitude à couverture donnée."""
from __future__ import annotations

import numpy as np
from numpy.typing import NDArray


def risk_coverage(conf: NDArray[np.float64], correct: NDArray[np.int_]) -> tuple[NDArray[np.float64], NDArray[np.float64]]:
    """Risque (taux d'erreur) des exemples retenus quand on garde les k plus confiants, pour k = 1 à n."""
    order = np.argsort(-conf, kind="stable")
    err = 1.0 - np.asarray(correct)[order]
    k = np.arange(1, len(conf) + 1)
    return k / len(conf), np.cumsum(err) / k


def aurc(conf: NDArray[np.float64], correct: NDArray[np.int_]) -> float:
    return float(risk_coverage(conf, correct)[1].mean())


def accuracy_at_coverage(conf: NDArray[np.float64], correct: NDArray[np.int_], coverage: float) -> float:
    k = max(1, round(coverage * len(conf)))
    order = np.argsort(-conf, kind="stable")[:k]
    return float(np.asarray(correct)[order].mean())
