"""Règle de sélection du système final (RM-50, brouillon `docs/BROUILLON_GEL_SYSTEME_FINAL.md`) : non-infériorité puis coût.

Un candidat est admissible si la borne basse de (candidat moins meilleur) est strictement supérieure à -delta ; le système final est l'admissible le moins cher ;
égalité de coût : le plus haut en macro-F1. La règle est une fonction pure : l'aperçu calculé avant le gel n'engage rien."""
from collections.abc import Sequence
from dataclasses import dataclass


@dataclass(frozen=True)
class Candidate:
    name: str
    cost_rank: int  # 0 = le moins cher
    macro_f1: float
    lower_vs_best_points: float  # borne basse de (candidat moins meilleur), points ; 0.0 pour le meilleur lui-même


def admissible(c: Candidate, delta_points: float = 2.0) -> bool:
    return c.lower_vs_best_points > -delta_points


def select_final(candidates: Sequence[Candidate], delta_points: float = 2.0) -> Candidate:
    if not candidates:
        raise ValueError("aucun candidat")
    ok = [c for c in candidates if admissible(c, delta_points)]
    best = max(candidates, key=lambda c: c.macro_f1)
    if not ok:
        return best
    return min(ok, key=lambda c: (c.cost_rank, -c.macro_f1))
