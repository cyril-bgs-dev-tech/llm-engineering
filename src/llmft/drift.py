"""Surveillance de dérive à l'entrée (audit GLM C7-A7) : prévalence des chapitres, longueurs, répartition des auteurs, d'un lot de référence à un nouveau lot."""
from collections import Counter
from collections.abc import Mapping, Sequence
from typing import Any

import numpy as np

TV_ALERT = 0.15
KS_ALERT = 0.2


def total_variation(a: Sequence[str], b: Sequence[str]) -> float:
    ca, cb = Counter(a), Counter(b)
    keys = set(ca) | set(cb)
    return 0.5 * sum(abs(ca[k] / len(a) - cb[k] / len(b)) for k in keys)


def _ks(a: Sequence[float], b: Sequence[float]) -> float:
    xa, xb = np.sort(np.asarray(a, dtype=float)), np.sort(np.asarray(b, dtype=float))
    grid = np.concatenate([xa, xb])
    return float(np.max(np.abs(np.searchsorted(xa, grid, side="right") / len(xa) - np.searchsorted(xb, grid, side="right") / len(xb))))


def drift_report(reference: Mapping[str, Sequence[Any]], new: Mapping[str, Sequence[Any]]) -> dict[str, Any]:
    tv_labels = total_variation(reference["labels"], new["labels"])
    ks_len = _ks(reference["lengths"], new["lengths"])
    tv_authors = total_variation(reference["authors"], new["authors"])
    return {"tv_prevalence": tv_labels, "ks_longueur": ks_len, "tv_auteurs": tv_authors,
            "alertes": {"prevalence": tv_labels > TV_ALERT, "longueur": ks_len > KS_ALERT, "auteurs": tv_authors > TV_ALERT}}
