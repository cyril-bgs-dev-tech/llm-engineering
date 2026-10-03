"""Déterminisme d'un rejeu (P1-26) : écart entre deux historiques de perte et deux listes de prédictions de même graine."""
from collections.abc import Sequence
from typing import Any


def compare(loss_a: Sequence[float], loss_b: Sequence[float], pred_a: Sequence[str], pred_b: Sequence[str]) -> dict[str, Any]:
    if len(loss_a) != len(loss_b):
        raise ValueError(f"nombre de pas différent : {len(loss_a)} contre {len(loss_b)}")
    if len(pred_a) != len(pred_b):
        raise ValueError("nombre de prédictions différent")
    drift = max((abs(x - y) for x, y in zip(loss_a, loss_b, strict=True)), default=0.0)
    different = sum(1 for x, y in zip(pred_a, pred_b, strict=True) if x != y)
    return {"pas": len(loss_a), "loss_identique": drift == 0.0, "ecart_perte_max": drift, "predictions_identiques": different == 0, "predictions_differentes": different, "n": len(pred_a)}
