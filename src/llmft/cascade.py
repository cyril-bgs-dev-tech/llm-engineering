"""Cascade par seuil de confiance (RM-40) : le premier modèle répond quand sa probabilité maximale atteint le seuil, sinon le cas passe au second ; choix du seuil hors du pli évalué."""
from collections.abc import Callable, Sequence

import numpy as np
from numpy.typing import NDArray


def cascade_probs(first: NDArray[np.floating], second: NDArray[np.floating], tau: float) -> tuple[NDArray[np.floating], NDArray[np.bool_]]:
    """Probabilités de la cascade et masque des cas traités par le premier modèle."""
    keep = first.max(axis=1) >= tau
    return np.where(keep[:, None], first, second), keep


def choose_threshold(
    first: NDArray[np.floating], second: NDArray[np.floating], score: Callable[[NDArray[np.floating]], float], grid: Sequence[float], tolerance: float,
) -> float | None:
    """Plus petit seuil (donc le plus grand nombre de cas traités par le modèle bon marché) dont le score reste à `tolerance` près de celui du second modèle seul ; None si aucun seuil ne convient.

    `score` reçoit des probabilités et renvoie une métrique à maximiser (macro-F1). Le choix ne doit utiliser que des données d'étalonnage, jamais le pli évalué.
    """
    reference = score(second)
    for tau in sorted(grid):
        probs, _ = cascade_probs(first, second, tau)
        if score(probs) >= reference - tolerance:
            return float(tau)
    return None
