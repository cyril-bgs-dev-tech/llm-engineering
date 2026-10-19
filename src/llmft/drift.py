"""Surveillance de dérive à l'entrée (audit GLM C7-A7) : prévalence des chapitres, longueurs, répartition des auteurs, d'un lot de référence à un nouveau lot.
Signaux sans étiquette d'un lot reçu par le service (P5-08, fiche 2026-10-17-simulation-derive) : baisse de la part servie par E seul, prévalence des chapitres prédits, longueurs ;
seuils d'alerte mesurés sur des lots tirés de la référence (centile haut), taux de détection sur des lots tirés d'un scénario de dérive."""
from collections import Counter
from collections.abc import Hashable, Mapping, Sequence
from typing import Any

import numpy as np

TV_ALERT = 0.15
KS_ALERT = 0.2


def total_variation(a: Sequence[Hashable], b: Sequence[Hashable]) -> float:
    ca, cb = Counter(a), Counter(b)
    keys = set(ca) | set(cb)
    return 0.5 * sum(abs(ca[k] / len(a) - cb[k] / len(b)) for k in keys)


def ks_statistic(a: Sequence[float] | np.ndarray, b: Sequence[float] | np.ndarray) -> float:
    xa, xb = np.sort(np.asarray(a, dtype=float)), np.sort(np.asarray(b, dtype=float))
    grid = np.concatenate([xa, xb])
    return float(np.max(np.abs(np.searchsorted(xa, grid, side="right") / len(xa) - np.searchsorted(xb, grid, side="right") / len(xb))))


def drift_report(reference: Mapping[str, Sequence[Any]], new: Mapping[str, Sequence[Any]]) -> dict[str, Any]:
    tv_labels = total_variation(reference["labels"], new["labels"])
    ks_len = ks_statistic(reference["lengths"], new["lengths"])
    tv_authors = total_variation(reference["authors"], new["authors"])
    return {"tv_prevalence": tv_labels, "ks_longueur": ks_len, "tv_auteurs": tv_authors,
            "alertes": {"prevalence": tv_labels > TV_ALERT, "longueur": ks_len > KS_ALERT, "auteurs": tv_authors > TV_ALERT}}


def confident_share(probs: np.ndarray, tau: float) -> float:
    """Part des lignes dont la probabilité maximale atteint τ (inclus, comme la cascade) : la part servie par E seul."""
    return float(np.mean(probs.max(axis=1) >= tau))


def draw_lots(n_items: int, n: int, draws: int, seed: int, weights: np.ndarray | None = None) -> np.ndarray:
    """`draws` lots de `n` indices tirés sans remise parmi `n_items` ; avec `weights`, tirage pondéré (poids nul : jamais tiré)."""
    rng = np.random.default_rng(seed)
    p = None if weights is None else np.asarray(weights, dtype=float) / float(np.sum(weights))
    return np.stack([rng.choice(n_items, size=n, replace=False, p=p) for _ in range(draws)])


def lot_signals(probs: np.ndarray, lengths: np.ndarray, ref_probs: np.ndarray, ref_lengths: np.ndarray, tau: float) -> dict[str, float]:
    """S1 : baisse de la part servie par E seul ; S2 : variation totale des chapitres prédits ; S3 : Kolmogorov-Smirnov des longueurs ; lot contre référence."""
    k = ref_probs.shape[1]
    p_lot = np.bincount(probs.argmax(axis=1), minlength=k) / len(probs)
    p_ref = np.bincount(ref_probs.argmax(axis=1), minlength=k) / len(ref_probs)
    return {"s1_baisse_part_e": confident_share(ref_probs, tau) - confident_share(probs, tau),
            "s2_tv_prevalence_predite": float(0.5 * np.abs(p_lot - p_ref).sum()),
            "s3_ks_longueur": ks_statistic(lengths, ref_lengths)}


def alert_threshold(null_values: np.ndarray, q: float) -> float:
    return float(np.quantile(np.asarray(null_values, dtype=float), q))


def detection_rate(values: np.ndarray, threshold: float) -> float:
    """Part des lots dont la statistique dépasse strictement le seuil."""
    return float(np.mean(np.asarray(values, dtype=float) > threshold))


def low_tail_power(null_values: np.ndarray, alt_values: np.ndarray, alpha: float) -> tuple[float, float]:
    """Seuil d'alerte d'une métrique de qualité (centile `alpha` des lots de référence) et part des lots d'un scénario strictement sous ce seuil (puissance)."""
    threshold = float(np.quantile(np.asarray(null_values, dtype=float), alpha))
    return threshold, float(np.mean(np.asarray(alt_values, dtype=float) < threshold))
