"""Calibration des probabilités (Q5) : température, ECE globale et par classe, perte logarithmique, Brier, tableau de fiabilité.

`metrics.py` (périmètre gelé) garde l'ECE du protocole ; ce module ajoute les variantes de diagnostic sans y toucher."""
from __future__ import annotations

import math

import numpy as np
from numpy.typing import NDArray

_EPS = 1e-12
_GOLDEN = (math.sqrt(5) - 1) / 2


def nll(probs: NDArray[np.float64], y: NDArray[np.int_]) -> float:
    return float(-np.log(np.clip(probs[np.arange(len(y)), y], _EPS, 1.0)).mean())


def apply_temperature(probs: NDArray[np.float64], temperature: float) -> NDArray[np.float64]:
    z = np.log(np.clip(probs, _EPS, 1.0)) / temperature
    e = np.exp(z - z.max(axis=1, keepdims=True))
    return np.asarray(e / e.sum(axis=1, keepdims=True))


def fit_temperature(probs: NDArray[np.float64], y: NDArray[np.int_], lo: float = 0.05, hi: float = 20.0, tol: float = 1e-4) -> float:
    """Température qui minimise la perte logarithmique (recherche par section dorée sur log T ; la perte est convexe en 1/T)."""
    a, b = math.log(lo), math.log(hi)
    c, d = b - _GOLDEN * (b - a), a + _GOLDEN * (b - a)
    fc, fd = nll(apply_temperature(probs, math.exp(c)), y), nll(apply_temperature(probs, math.exp(d)), y)
    while b - a > tol:
        if fc < fd:
            b, d, fd = d, c, fc
            c = b - _GOLDEN * (b - a)
            fc = nll(apply_temperature(probs, math.exp(c)), y)
        else:
            a, c, fc = c, d, fd
            d = a + _GOLDEN * (b - a)
            fd = nll(apply_temperature(probs, math.exp(d)), y)
    return math.exp((a + b) / 2)


def reliability_bins(conf: NDArray[np.float64], hit: NDArray[np.float64], bins: int = 15) -> list[dict[str, float]]:
    """Par intervalle de confiance : effectif, confiance moyenne, fréquence observée."""
    edges = np.linspace(0, 1, bins + 1)
    idx = np.clip(np.digitize(conf, edges[1:-1]), 0, bins - 1)
    out = []
    for b in range(bins):
        m = idx == b
        if m.any():
            out.append({"n": int(m.sum()), "confidence": float(conf[m].mean()), "frequency": float(hit[m].mean())})
    return out


def _ece_from_bins(rows: list[dict[str, float]], n: int) -> float:
    return float(sum(r["n"] / n * abs(r["confidence"] - r["frequency"]) for r in rows))


def ece(probs: NDArray[np.float64], y: NDArray[np.int_], bins: int = 15) -> float:
    conf, pred = probs.max(axis=1), probs.argmax(axis=1)
    return _ece_from_bins(reliability_bins(conf, (pred == y).astype(float), bins), len(y))


def classwise_ece(probs: NDArray[np.float64], y: NDArray[np.int_], bins: int = 15) -> dict[int, float]:
    """ECE un contre tous pour chaque classe présente (probabilité de la classe contre sa fréquence réelle)."""
    return {int(c): _ece_from_bins(reliability_bins(probs[:, c], (y == c).astype(float), bins), len(y)) for c in np.unique(y)}


def brier(probs: NDArray[np.float64], y: NDArray[np.int_]) -> float:
    onehot = np.eye(probs.shape[1])[y]
    return float(((probs - onehot) ** 2).sum(axis=1).mean())
