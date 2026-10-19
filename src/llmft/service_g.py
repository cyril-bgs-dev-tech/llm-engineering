"""Service du système final G d'un seul tenant (RM-35, RM-48) : composition des probabilités, cascade E puis G (RM-60), latence modélisée d'une cascade, critère d'acceptation d'une mesure répétée."""
from collections.abc import Callable, Sequence
from typing import Any

import numpy as np
from numpy.typing import NDArray


def combine_g(lora: NDArray[np.floating], encoders: Sequence[NDArray[np.floating]], tfidf: NDArray[np.floating]) -> NDArray[np.floating]:
    """G = moyenne à parts égales du LoRA, de la moyenne des encodeurs et du TF-IDF (composition du gel, ADR-016)."""
    if not encoders:
        raise ValueError("aucun encodeur fourni")
    if any(e.shape != lora.shape for e in encoders) or tfidf.shape != lora.shape:
        raise ValueError("formes différentes entre composantes")
    enc = np.mean(np.stack(list(encoders)), axis=0)
    return np.mean(np.stack([lora, enc, tfidf]), axis=0)


def combine_e(encoders: Sequence[NDArray[np.floating]], tfidf: NDArray[np.floating]) -> NDArray[np.floating]:
    """E = moyenne à parts égales de la moyenne des encodeurs et du TF-IDF (composition de `scripts/build_fold_ensemble.py`)."""
    if not encoders:
        raise ValueError("aucun encodeur fourni")
    enc = np.mean(np.stack(list(encoders)), axis=0)
    if enc.shape != tfidf.shape:
        raise ValueError("formes différentes entre composantes")
    return 0.5 * enc + 0.5 * tfidf


def cascade_predict(
    text: str, first: Callable[[str], tuple[list[NDArray[np.floating]], NDArray[np.floating]]], lora: Callable[[str], NDArray[np.floating]], labels: Sequence[str], tau: float,
) -> dict[str, Any]:
    """Cascade E puis G (RM-60) : E répond seul si sa probabilité maximale atteint `tau` (seuil inclusif, comme `llmft.cascade.cascade_probs`) ; sinon le LoRA est calculé et G complet répond."""
    encoders, tfidf = first(text)
    e = combine_e(encoders, tfidf).reshape(-1)
    if float(e.max()) >= tau:
        probs, stage = e, "E"
    else:
        probs, stage = combine_g(lora(text), encoders, tfidf).reshape(-1), "G"
    k = int(probs.argmax())
    return {"label": labels[k], "probability": float(probs[k]), "stage": stage}


def cascade_mean_latency(first_ms: float, second_ms: float, share_first: float) -> float:
    """Latence moyenne d'une cascade : le premier étage répond à tous, le second s'ajoute pour la part escaladée."""
    if not 0.0 <= share_first <= 1.0:
        raise ValueError("la part du premier étage doit être dans [0, 1]")
    return first_ms + (1.0 - share_first) * second_ms


def passes_accepted(p50_a: float, p50_b: float, *, same_classes: bool, tolerance: float = 0.10) -> bool:
    """Deux passages sont acceptés si leurs p50 diffèrent de moins de `tolerance` (relatif au plus petit) et si les classes prédites sont identiques."""
    low = min(p50_a, p50_b)
    return same_classes and low > 0 and abs(p50_a - p50_b) / low < tolerance


def latency_percentiles(latencies_ms: Sequence[float]) -> dict[str, float]:
    a = np.asarray(latencies_ms, dtype=float)
    if a.size == 0:
        raise ValueError("aucune latence")
    return {"p50_ms": round(float(np.percentile(a, 50)), 1), "p95_ms": round(float(np.percentile(a, 95)), 1), "p99_ms": round(float(np.percentile(a, 99)), 1), "moyenne_ms": round(float(a.mean()), 1)}
