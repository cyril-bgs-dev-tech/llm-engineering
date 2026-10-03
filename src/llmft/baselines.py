"""Bornes de référence sans modèle (P1-03) : classe majoritaire, tirage aléatoire uniforme, tirage selon la prévalence, prior d'entraînement.

Évaluées sur un pli de développement avec les seules étiquettes d'entraînement : jamais le test scellé."""
from __future__ import annotations

from collections import Counter
from collections.abc import Sequence
from typing import Any

import numpy as np

from llmft import metrics

_EPS = 1e-12


def _scores(truth: Sequence[str], pred: Sequence[str], scored: Sequence[str]) -> dict[str, float]:
    return {"macro_f1": metrics.macro_f1(truth, pred, scored), "accuracy": metrics.accuracy(truth, pred)}


def fold_bounds(
    train: Sequence[str], test: Sequence[str], labels: Sequence[str], scored: Sequence[str], n_random: int = 200, rng: np.random.Generator | None = None
) -> dict[str, Any]:
    """Bornes d'un pli : `labels` = toutes les sorties, `scored` = classes de la macro-F1 (la classe exclue reste prédictible)."""
    gen = rng if rng is not None else np.random.default_rng(0)
    counts = Counter(train)
    majority = max(labels, key=lambda lab: (counts.get(lab, 0), lab))
    prior = np.array([counts.get(lab, 0) for lab in labels], dtype=float)
    prior = prior / prior.sum()
    truth = list(test)
    out: dict[str, Any] = {"majority_class": majority, "majority": _scores(truth, [majority] * len(truth), scored), "n_test": len(truth)}
    for name, probs in (("random_uniform", np.full(len(labels), 1 / len(labels))), ("random_prior", prior)):
        draws = [_scores(truth, list(gen.choice(np.array(labels), size=len(truth), p=probs)), scored) for _ in range(n_random)]
        out[name] = {k: float(np.mean([d[k] for d in draws])) for k in ("macro_f1", "accuracy")}
    index = {lab: i for i, lab in enumerate(labels)}
    nll = np.array([-np.log(max(prior[index[t]], _EPS)) for t in truth])
    present = sorted(set(truth))
    out["prior"] = {
        "log_loss": float(nll.mean()),
        "class_balanced_log_loss": float(np.mean([nll[[t == c for t in truth]].mean() for c in present])),
    }
    return out
