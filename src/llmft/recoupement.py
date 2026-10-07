"""Recoupement d'un chiffre publié par recalcul (règle N36) : compare les probabilités enregistrées à celles d'un recalcul indépendant."""
import hashlib
from typing import Any

import numpy as np
from numpy.typing import NDArray

FLOAT_TOLERANCE = 1e-9


def _digest(probs: NDArray[np.floating]) -> str:
    return hashlib.sha256(np.ascontiguousarray(probs, dtype=np.float64).tobytes()).hexdigest()


def compare_probs(reference: NDArray[np.floating], recomputed: NDArray[np.floating], folds: NDArray[np.integer] | None = None) -> dict[str, Any]:
    """Verdict « concorde » (identique au bit près), « concorde aux flottants près » (écart ≤ 1e-9 et aucune classe prédite ne change) ou « diverge »."""
    if reference.shape != recomputed.shape:
        raise ValueError(f"formes différentes : {reference.shape} contre {recomputed.shape}")
    gap = np.abs(reference - recomputed)
    max_gap = float(gap.max()) if gap.size else 0.0
    changes = int((reference.argmax(1) != recomputed.argmax(1)).sum())
    digest_ref, digest_new = _digest(reference), _digest(recomputed)
    if digest_ref == digest_new:
        verdict = "concorde"
    elif max_gap <= FLOAT_TOLERANCE and changes == 0:
        verdict = "concorde aux flottants près"
    else:
        verdict = "diverge"
    out: dict[str, Any] = {"verdict": verdict, "max_abs_diff": max_gap, "n_class_changes": changes, "digest_reference": digest_ref, "digest_recomputed": digest_new}
    if folds is not None:
        out["max_abs_diff_by_fold"] = {str(int(k)): float(gap[folds == k].max()) for k in np.unique(folds)}
    return out
