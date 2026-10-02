"""Tâche jouet synthétique (P0-39) : deux classes, texte généré de façon déterministe, aucune donnée réelle."""
from __future__ import annotations

import numpy as np
import pandas as pd

_POSITIVE = ["Très satisfait du service", "Excellent accueil", "Résultat parfait", "Je recommande vivement", "Équipe remarquable"]
_NEGATIVE = ["Très déçu du service", "Accueil désagréable", "Résultat décevant", "Je déconseille fortement", "Équipe injoignable"]
_FILLER = ["lors de ma visite de mardi", "pour la seconde fois", "après une longue attente", "malgré mes attentes", "au guichet principal"]


def make_toy(n: int = 50, seed: int = 0) -> pd.DataFrame:
    """`n` exemples équilibrés (n pair) ; colonnes id, text, label, author. Même (n, seed), mêmes données."""
    if n % 2:
        raise ValueError("n doit être pair pour équilibrer les deux classes")
    rng = np.random.default_rng(seed)
    labels = np.array(["positif", "negatif"] * (n // 2))
    rng.shuffle(labels)
    rows = []
    for i, label in enumerate(labels):
        core = _POSITIVE if label == "positif" else _NEGATIVE
        text = f"{core[rng.integers(len(core))]} {_FILLER[rng.integers(len(_FILLER))]}."
        rows.append({"id": f"toy{i:04d}", "text": text, "label": str(label), "author": f"a{rng.integers(10):02d}"})
    return pd.DataFrame(rows)


class ToyAdapter:
    """Adaptateur du chargeur générique pour la tâche jouet."""

    def __init__(self, n: int = 50, seed: int = 0) -> None:
        self.n, self.seed = n, seed

    def load(self) -> pd.DataFrame:
        return make_toy(self.n, self.seed)
