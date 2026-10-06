"""Outils de comparaison appariée (P1-02, ADR-007, PROTOCOLE.md 6.2) : bootstrap hiérarchique, McNemar exact, permutation, Holm, verdict.

Le bootstrap hiérarchique tire d'abord les patients avec remise, **stratifié par classe** et **le même tirage pour les deux recettes** (appariement),
puis tire les graines avec remise, **indépendamment pour chaque recette** ; la statistique est la différence des métriques moyennées sur les graines.
Les unités de l'intervalle sont celles de la métrique (fractions) ; le verdict compare à δ exprimé dans la même unité."""
from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from itertools import product
from math import comb
from typing import Literal

import numpy as np
from numpy.typing import NDArray

DEFAULT_SEED = 20261002
MAX_EXACT_PERMUTATION = 20


@dataclass(frozen=True)
class McNemarResult:
    only_a: int  # patients bien classés par A seulement
    only_b: int
    p_value: float


@dataclass(frozen=True)
class BootResult:
    estimate: float
    lo: float
    hi: float
    width: float
    level: float
    n_boot: int


def mcnemar_exact(a_ok: NDArray[np.bool_], b_ok: NDArray[np.bool_]) -> McNemarResult:
    """Test de McNemar exact (binomial bilatéral) sur les patients où une seule recette a raison."""
    a, b = np.asarray(a_ok, dtype=bool), np.asarray(b_ok, dtype=bool)
    only_a, only_b = int((a & ~b).sum()), int((~a & b).sum())
    n = only_a + only_b
    p = 1.0 if n == 0 else min(1.0, 2 * sum(comb(n, k) for k in range(min(only_a, only_b) + 1)) / 2**n)
    return McNemarResult(only_a, only_b, p)


def holm_adjust(p_values: NDArray[np.float64]) -> NDArray[np.float64]:
    """p-valeurs ajustées de Holm (pas de descente), dans l'ordre d'entrée."""
    p = np.asarray(p_values, dtype=float)
    m = len(p)
    order = np.argsort(p)
    adjusted = np.minimum(1.0, np.maximum.accumulate((m - np.arange(m)) * p[order]))
    out = np.empty(m)
    out[order] = adjusted
    return out


def paired_permutation_pvalue(d: NDArray[np.float64], n_perm: int | None = None, rng: np.random.Generator | None = None) -> float:
    """Test de permutation apparié (inversion de signe) de H0 : moyenne des écarts nulle. `n_perm=None` : énumération exacte (n <= 20)."""
    d = np.asarray(d, dtype=float)
    n = len(d)
    if n == 0:
        raise ValueError("aucun écart apparié : p-valeur indéfinie")
    observed = abs(d.mean())
    tol = 1e-12 * max(observed, 1.0)
    if n_perm is None:
        if n > MAX_EXACT_PERMUTATION:
            raise ValueError(f"énumération exacte limitée à {MAX_EXACT_PERMUTATION} patients ; passer n_perm")
        signs = np.array(list(product((-1.0, 1.0), repeat=n)))
        return float((np.abs(signs @ d / n) >= observed - tol).mean())
    gen = rng if rng is not None else np.random.default_rng(DEFAULT_SEED)
    signs = gen.choice((-1.0, 1.0), size=(n_perm, n))
    return float(((np.abs(signs @ d / n) >= observed - tol).sum() + 1) / (n_perm + 1))


def stratified_weights(truth: NDArray[np.int_], n_boot: int, rng: np.random.Generator) -> NDArray[np.int64]:
    """Multiplicités (n_boot, n) d'un tirage avec remise **dans chaque classe** : l'effectif de chaque classe est conservé."""
    labels = np.asarray(truth)
    weights = np.zeros((n_boot, len(labels)), dtype=np.int64)
    offsets = np.arange(n_boot)[:, None]
    for c in np.unique(labels):
        idx = np.flatnonzero(labels == c)
        draws = rng.integers(0, len(idx), size=(n_boot, len(idx)))
        counts = np.bincount((draws + offsets * len(idx)).ravel(), minlength=n_boot * len(idx)).reshape(n_boot, len(idx))
        weights[:, idx] = counts
    return weights


def _metric_per_replicate(w: NDArray[np.int64], truth: NDArray[np.int_], pred: NDArray[np.int_], k: int, scored: Sequence[int], metric: str) -> NDArray[np.float64]:
    if metric == "accuracy":
        return np.asarray((w @ (pred == truth).astype(np.int64)) / w.sum(axis=1), dtype=float)
    predicted = w @ np.eye(k, dtype=np.int64)[pred]
    f1 = np.zeros((w.shape[0], len(scored)))
    for j, c in enumerate(scored):
        mask = truth == c
        tp = w[:, mask] @ (pred[mask] == c).astype(np.int64)
        support = w[:, mask].sum(axis=1)
        fp, fn = predicted[:, c] - tp, support - tp
        denom = 2 * tp + fp + fn
        f1[:, j] = np.where(denom > 0, 2 * tp / np.maximum(denom, 1), 0.0)
    return np.asarray(f1.mean(axis=1))


def _point(truth: NDArray[np.int_], preds: NDArray[np.int_], k: int, scored: Sequence[int], metric: str) -> float:
    ones = np.ones((1, len(truth)), dtype=np.int64)
    return float(np.mean([_metric_per_replicate(ones, truth, p, k, scored, metric)[0] for p in preds]))


def hierarchical_bootstrap(
    truth: NDArray[np.int_],
    preds_a: NDArray[np.int_],
    preds_b: NDArray[np.int_],
    k_classes: int,
    scored: Sequence[int],
    metric: Literal["macro_f1", "accuracy"] = "macro_f1",
    stratify: bool = True,
    resample_seeds: bool = True,
    n_boot: int = 10000,
    level: float = 1 - 0.05 / 3,
    rng: np.random.Generator | None = None,
) -> BootResult:
    """Différence A moins B de la métrique, intervalle percentile à `level`. `preds_*` : (graines, patients), indices de classe."""
    t, a, b = np.asarray(truth), np.asarray(preds_a), np.asarray(preds_b)
    gen = rng if rng is not None else np.random.default_rng(DEFAULT_SEED)
    w = stratified_weights(t if stratify else np.zeros(len(t), dtype=int), n_boot, gen)
    per_a = np.stack([_metric_per_replicate(w, t, s, k_classes, scored, metric) for s in a], axis=1)
    per_b = np.stack([_metric_per_replicate(w, t, s, k_classes, scored, metric) for s in b], axis=1)
    rows = np.arange(n_boot)[:, None]
    if resample_seeds:
        mean_a = per_a[rows, gen.integers(0, a.shape[0], size=(n_boot, a.shape[0]))].mean(axis=1)
        mean_b = per_b[rows, gen.integers(0, b.shape[0], size=(n_boot, b.shape[0]))].mean(axis=1)
    else:
        mean_a, mean_b = per_a.mean(axis=1), per_b.mean(axis=1)
    diff = mean_a - mean_b
    lo, hi = np.percentile(diff, [100 * (1 - level) / 2, 100 * (1 + level) / 2])
    return BootResult(_point(t, a, k_classes, scored, metric) - _point(t, b, k_classes, scored, metric), float(lo), float(hi), float(hi - lo), level, n_boot)


def verdict(lo: float, hi: float, delta: float) -> str:
    """Verdict en trois valeurs d'ADR-007 : gain confirmé si lo > δ, absence de gain utile si hi < δ, sinon non résolu."""
    if lo > delta:
        return "gain confirmé"
    if hi < delta:
        return "absence de gain utile"
    return "non résolu"


def bonferroni_level(m: int, alpha: float = 0.05) -> float:
    """Niveau de l'intervalle pour une famille de `m` comparaisons (ADR-007, point 3)."""
    return 1 - alpha / m
