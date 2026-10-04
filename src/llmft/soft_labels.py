"""Étiquettes souples pour un classifieur qui n'accepte que des étiquettes dures (régression logistique) : réplication pondérée (RM-46).

Cible mélangée `alpha * one-hot + (1 - alpha) * professeur` ; chaque exemple est répliqué une fois par classe dont la masse dépasse `threshold`, avec cette masse comme poids.
"""
from collections.abc import Sequence

import numpy as np
from numpy.typing import NDArray


def replicate_soft(hard: Sequence[int], teacher: NDArray[np.floating], alpha: float, threshold: float) -> tuple[list[int], list[int], list[float]]:
    """Renvoie (indices des exemples, classes, poids) ; la masse sous le seuil est abandonnée puis le reste renormalisé pour que chaque exemple garde un poids total de 1."""
    if not 0.0 <= alpha <= 1.0 or threshold < 0.0:
        raise ValueError("alpha dans [0, 1] et seuil >= 0")
    n, k = teacher.shape
    if len(hard) != n:
        raise ValueError("autant d'étiquettes dures que de lignes de professeur")
    onehot = np.zeros((n, k))
    onehot[np.arange(n), np.asarray(list(hard), dtype=int)] = 1.0
    target = alpha * onehot + (1.0 - alpha) * np.asarray(teacher, dtype=float)
    rows, classes, weights = [], [], []
    for i in range(n):
        keep = np.flatnonzero(target[i] >= threshold)
        if keep.size == 0:
            keep = np.array([int(hard[i])])
        mass = target[i, keep].sum()
        for c in keep:
            rows.append(i)
            classes.append(int(c))
            weights.append(float(target[i, c] / mass))
    return rows, classes, weights
