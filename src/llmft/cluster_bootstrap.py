"""Bootstrap par blocs (auteurs) de la différence de macro-F1 entre deux systèmes sur des prédictions regroupées (audit GLM v6, levier 1).

Tirage avec remise des **auteurs** (tous les patients d'un auteur tiré entrent ensemble, autant de fois que l'auteur est tiré), même tirage pour les deux systèmes : l'appariement par patient
est conservé et la corrélation des erreurs au sein d'un auteur est respectée. Calcul vectorisé par comptes vrais positifs, faux positifs et faux négatifs par auteur et par classe."""
from collections.abc import Sequence

import numpy as np
from numpy.typing import NDArray


def _counts(truth: NDArray[np.int_], pred: NDArray[np.int_], group_index: NDArray[np.int_], n_groups: int, scored: Sequence[int]) -> NDArray[np.float64]:
    """Tableau (auteurs, 3 * classes évaluées) des comptes tp, fp, fn par auteur."""
    out = np.zeros((n_groups, 3, len(scored)))
    for k, c in enumerate(scored):
        t, p = truth == c, pred == c
        np.add.at(out[:, 0, k], group_index, (t & p).astype(float))
        np.add.at(out[:, 1, k], group_index, (~t & p).astype(float))
        np.add.at(out[:, 2, k], group_index, (t & ~p).astype(float))
    return out.reshape(n_groups, -1)


def _macro_from_counts(totals: NDArray[np.float64], n_scored: int) -> NDArray[np.float64]:
    tp, fp, fn = (totals[:, i * n_scored : (i + 1) * n_scored] for i in range(3))
    denom = 2 * tp + fp + fn
    return np.where(denom > 0, 2 * tp / np.maximum(denom, 1), 0.0).mean(axis=1)


def cluster_interval(
    truth: NDArray[np.int_], pred_a: NDArray[np.int_], pred_b: NDArray[np.int_], scored: Sequence[int], groups: Sequence[str], n_boot: int = 5000, seed: int = 20261005, level: float = 0.95,
) -> tuple[float, float, float]:
    """(différence observée, borne basse, borne haute) en points de macro-F1 de A moins B, bootstrap d'auteurs."""
    uniq = sorted(set(groups))
    if len(uniq) < 2:
        raise ValueError("le bootstrap d'auteurs exige au moins deux auteurs : avec un seul, l'intervalle est de largeur nulle")
    index = {g: i for i, g in enumerate(uniq)}
    gi = np.array([index[g] for g in groups])
    ca = _counts(truth, pred_a, gi, len(uniq), scored)
    cb = _counts(truth, pred_b, gi, len(uniq), scored)
    rng = np.random.default_rng(seed)
    weights = rng.multinomial(len(uniq), np.full(len(uniq), 1.0 / len(uniq)), size=n_boot).astype(float)
    diff = _macro_from_counts(weights @ ca, len(scored)) - _macro_from_counts(weights @ cb, len(scored))
    observed = _macro_from_counts(ca.sum(0, keepdims=True), len(scored))[0] - _macro_from_counts(cb.sum(0, keepdims=True), len(scored))[0]
    alpha = (1.0 - level) / 2.0
    lo, hi = np.percentile(diff, [100 * alpha, 100 * (1 - alpha)])
    return float(100 * observed), float(100 * lo), float(100 * hi)
