"""Règle de puissance RM-17 (PROTOCOLE.md 6.3) : largeur moyenne des intervalles de la différence de macro-F1 entre graines d'une même recette.

Bootstrap sur patients seuls, pool stratifié par classe avec pour tailles de strate les effectifs du test scellé, le même tirage pour les deux graines d'une paire,
percentile à 98,33 %, un seul flux PCG64 de graine 20261002 consommé dans l'ordre lexicographique des paires. Aucune prédiction du test n'est utilisée."""
from collections.abc import Mapping, Sequence

import numpy as np
from numpy.typing import NDArray

SEED = 20261002
N_BOOT = 10_000
LEVEL = 0.9833
THRESHOLD_POINTS = 4.0


def _macro_f1(t: NDArray[np.int_], p: NDArray[np.int_], scored: Sequence[int]) -> NDArray[np.float64]:
    out = np.zeros(t.shape[0])
    for c in scored:
        tp = ((t == c) & (p == c)).sum(1)
        fp = ((t != c) & (p == c)).sum(1)
        fn = ((t == c) & (p != c)).sum(1)
        denom = 2 * tp + fp + fn
        out += np.where(denom > 0, 2 * tp / np.maximum(denom, 1), 0.0)
    return out / len(scored)


def pair_widths(
    truth: NDArray[np.int_], preds: Sequence[NDArray[np.int_]], test_counts: Mapping[int, int], scored: Sequence[int], n_boot: int = N_BOOT, seed: int = SEED
) -> list[float]:
    """Largeur (en points, non arrondie) de l'intervalle de chaque paire de graines (i, j), i < j."""
    rng = np.random.default_rng(seed)
    by_class = {c: np.where(truth == c)[0] for c in test_counts}
    classes = sorted(test_counts)
    alpha = (1.0 - LEVEL) / 2.0
    widths: list[float] = []
    for i in range(len(preds)):
        for j in range(i + 1, len(preds)):
            idx = np.concatenate([by_class[c][rng.integers(0, len(by_class[c]), size=(n_boot, test_counts[c]))] for c in classes], axis=1)
            t = truth[idx]
            diff = _macro_f1(t, preds[i][idx], scored) - _macro_f1(t, preds[j][idx], scored)
            lo, hi = np.percentile(diff, [100 * alpha, 100 * (1 - alpha)])
            widths.append(float(100.0 * (hi - lo)))
    return widths


def mean_width(
    truth: NDArray[np.int_], preds: Sequence[NDArray[np.int_]], test_counts: Mapping[int, int], scored: Sequence[int], n_boot: int = N_BOOT
) -> float | None:
    """Moyenne des largeurs de toutes les paires ; `None` (la règle échoue) avec moins de trois graines."""
    if len(preds) < 3:
        return None
    widths = pair_widths(truth, preds, test_counts, scored, n_boot)
    return float(np.mean(widths))
