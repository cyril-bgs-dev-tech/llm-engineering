"""Métriques des tâches de classification fermée (macro-F1, exactitude, perte logarithmique, ECE)."""
from __future__ import annotations

from collections.abc import Sequence
from itertools import pairwise

import numpy as np
from numpy.typing import NDArray

_EPS = 1e-12


def macro_f1(y_true: Sequence[str], y_pred: Sequence[str], labels: Sequence[str]) -> float:
    """Moyenne des F1 par classe sur `labels` (une classe sans exemple ni prédiction compte 0)."""
    t, p = np.asarray(y_true), np.asarray(y_pred)
    scores = []
    for label in labels:
        tp = float(((t == label) & (p == label)).sum())
        fp = float(((t != label) & (p == label)).sum())
        fn = float(((t == label) & (p != label)).sum())
        denom = 2 * tp + fp + fn
        scores.append(0.0 if denom == 0 else 2 * tp / denom)
    return float(np.mean(scores))


def accuracy(y_true: Sequence[str], y_pred: Sequence[str]) -> float:
    return float((np.asarray(y_true) == np.asarray(y_pred)).mean())


def log_loss(probs: NDArray[np.float64], y_idx: NDArray[np.int64]) -> float:
    picked = np.clip(probs[np.arange(len(y_idx)), y_idx], _EPS, 1.0)
    return float(-np.log(picked).mean())


def ece(probs: NDArray[np.float64], y_idx: NDArray[np.int64], bins: int = 10) -> float:
    """Erreur de calibration attendue : écart moyen pondéré entre confiance et exactitude par tranche de confiance."""
    conf = probs.max(axis=1)
    correct = (probs.argmax(axis=1) == y_idx).astype(float)
    edges = np.linspace(0.0, 1.0, bins + 1)
    total = 0.0
    for lo, hi in pairwise(edges):
        mask = (conf > lo) & (conf <= hi) if lo > 0 else (conf >= lo) & (conf <= hi)
        if mask.any():
            total += mask.mean() * abs(conf[mask].mean() - correct[mask].mean())
    return float(total)


def compute(names: Sequence[str], probs: NDArray[np.float64], y_idx: NDArray[np.int64], labels: Sequence[str]) -> dict[str, float]:
    pred = [labels[i] for i in probs.argmax(axis=1)]
    truth = [labels[i] for i in y_idx]
    table = {
        "macro_f1": lambda: macro_f1(truth, pred, labels),
        "accuracy": lambda: accuracy(truth, pred),
        "log_loss": lambda: log_loss(probs, y_idx),
        "ece": lambda: ece(probs, y_idx),
    }
    return {n: table[n]() for n in names}
