"""Règle de choix de l'élève (ADR-009, P1-12) : plus haute macro-F1 sous contrainte de mémoire ; si l'intervalle apparié à 95 % de la différence
entre les deux meilleurs contient 0, on retient le moins coûteux des deux."""
from __future__ import annotations

from collections.abc import Callable, Mapping
from typing import Any


def choose_student(candidates: Mapping[str, Mapping[str, Any]], ci_for: Callable[[str, str], tuple[float, float]], max_peak_gib: float) -> tuple[str, str]:
    """`candidates[nom]` : macro_f1, cost_s (secondes d'entraînement), peak_gib ; `ci_for(a, b)` : IC 95 % de macro-F1(a) moins macro-F1(b)."""
    ok = {n: c for n, c in candidates.items() if c["peak_gib"] <= max_peak_gib}
    if not ok:
        raise ValueError(f"aucun candidat sous {max_peak_gib} Gio")
    ranked = sorted(ok, key=lambda n: (-ok[n]["macro_f1"], ok[n]["cost_s"]))
    if len(ranked) == 1:
        return ranked[0], "seul candidat admissible"
    first, second = ranked[0], ranked[1]
    lo, hi = ci_for(first, second)
    if lo <= 0 <= hi:
        cheaper = min((first, second), key=lambda n: ok[n]["cost_s"])
        return cheaper, f"égalité apparié ({first} contre {second}, IC contient 0) : le moins coûteux"
    return first, f"plus haute macro-F1 ({first}, écart résolu contre {second})"
