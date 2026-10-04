"""Moyenne de probabilités de plusieurs modèles sur les mêmes patients (ensemble par moyenne simple)."""
import numpy as np


def average_probs(members: list[tuple[list[str], np.ndarray]], weights: list[float] | None = None) -> tuple[list[str], np.ndarray]:
    """Moyenne (pondérée) des probabilités, alignées sur l'ordre des identifiants du premier membre.

    Refuse des membres qui ne couvrent pas exactement les mêmes identifiants ou des poids non positifs.
    """
    if not members:
        raise ValueError("aucun membre")
    ids = list(members[0][0])
    w = np.ones(len(members)) if weights is None else np.asarray(weights, dtype=float)
    if len(w) != len(members) or (w <= 0).any():
        raise ValueError("poids invalides")
    acc = np.zeros_like(members[0][1], dtype=float)
    for (mids, probs), wi in zip(members, w, strict=True):
        if set(mids) != set(ids) or len(mids) != len(ids):
            raise ValueError("les membres ne couvrent pas les mêmes identifiants")
        pos = {i: k for k, i in enumerate(mids)}
        acc += wi * probs[[pos[i] for i in ids]]
    return ids, acc / w.sum()
