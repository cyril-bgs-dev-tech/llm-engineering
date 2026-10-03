"""Harnais d'évaluation de la tâche principale (PROTOCOLE.md 6.1, P1-01) : le modèle a K sorties dont une classe exclue de la moyenne.

La macro-F1 porte sur les classes notées seulement ; la classe exclue (`autre`) reste dans l'espace des prédictions (un patient noté
prédit `autre` est un faux négatif de sa classe, un patient `autre` prédit dans une classe notée en est un faux positif) et est
rapportée à part. L'exactitude, la perte logarithmique et l'ECE comptent toutes les sorties, comme le contrat de tâche."""
from __future__ import annotations

from collections.abc import Sequence
from typing import Any

import numpy as np
from numpy.typing import NDArray

from llmft import metrics

VERY_LOW_SUPPORT = 10  # moins de 10 patients de test : « effectif très faible » (PROTOCOLE.md 6.1)


def _prf(truth: NDArray[np.int_], pred: NDArray[np.int_], c: int) -> dict[str, float]:
    tp = float(((truth == c) & (pred == c)).sum())
    fp = float(((truth != c) & (pred == c)).sum())
    fn = float(((truth == c) & (pred != c)).sum())
    return {
        "precision": tp / (tp + fp) if tp + fp else 0.0,
        "recall": tp / (tp + fn) if tp + fn else 0.0,
        "f1": 2 * tp / (2 * tp + fp + fn) if 2 * tp + fp + fn else 0.0,
    }


def chapter_report(y_true: NDArray[np.int_], probs: NDArray[np.float64], labels: Sequence[str], excluded: Sequence[str] = ("autre",)) -> dict[str, Any]:
    """Rapport d'une évaluation : `y_true` (indices dans `labels`), `probs` (une ligne de K probabilités par patient)."""
    missing = [e for e in excluded if e not in labels]
    if missing:
        raise ValueError(f"classe exclue absente de la liste des classes : {', '.join(missing)}")
    truth = np.asarray(y_true, dtype=np.int64)
    pred = np.asarray(probs).argmax(axis=1)
    scored = [lab for lab in labels if lab not in excluded]
    names = [labels[i] for i in truth]
    named_pred = [labels[i] for i in pred]
    per_class: dict[str, dict[str, Any]] = {}
    for lab in scored:
        c = labels.index(lab)
        support = int((truth == c).sum())
        per_class[lab] = {**_prf(truth, pred, c), "support": support, "very_low_support": support < VERY_LOW_SUPPORT}
    apart: dict[str, dict[str, float | int]] = {}
    for lab in excluded:
        c = labels.index(lab)
        stats = _prf(truth, pred, c)
        apart[lab] = {"precision": stats["precision"], "recall": stats["recall"], "support": int((truth == c).sum())}
    return {
        "macro_f1": metrics.macro_f1(names, named_pred, scored),
        "scored_classes": scored,
        "accuracy": metrics.accuracy(names, named_pred),
        "log_loss": metrics.log_loss(np.asarray(probs), truth),
        "ece": metrics.ece(np.asarray(probs), truth),
        "per_class": per_class,
        "excluded": apart,
        "n": len(truth),
    }
