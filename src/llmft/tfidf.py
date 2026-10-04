"""Référence TF-IDF et régression logistique (P1-04, P1-06) : grille fixée, sélection sur un seul pli de validation."""
from __future__ import annotations

from collections.abc import Sequence
from typing import Any, cast

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression

from llmft import metrics

_Vectorizer: Any = cast(Any, TfidfVectorizer)  # sklearn n'est pas typé assez finement pour le mode strict
_Logistic: Any = cast(Any, LogisticRegression)

GRID: list[tuple[float, tuple[int, int]]] = [(c, ng) for c in (0.1, 1.0, 10.0, 100.0) for ng in ((1, 1), (1, 2))]

GRID_V2: list[tuple[float, tuple[int, int]]] = [(c, ng) for c in (1.0, 10.0, 100.0, 1000.0, 10000.0) for ng in ((1, 1), (1, 2))]  # fiche v2 : C au bord haut de la grille v1


def fit_model(
    train_texts: Sequence[str], train_y: Sequence[str], c: float, ngram: tuple[int, int], class_weight: str | None = None, analyzer: str = "word",
) -> tuple[Any, Any]:
    """Vectoriseur et modèle ajustés (réutilisés par le service d'inférence)."""
    vec = _Vectorizer(sublinear_tf=True, min_df=1 if len(train_texts) < 50 else 2, max_features=200000, ngram_range=ngram, analyzer=analyzer)
    x_train = vec.fit_transform(train_texts)
    model = _Logistic(C=c, max_iter=1000, class_weight=class_weight)
    model.fit(x_train, list(train_y))
    return vec, model


def predict_aligned(vec: Any, model: Any, texts: Sequence[str], labels: Sequence[str]) -> np.ndarray:
    """Probabilités alignées sur `labels` ; une classe absente de l'entraînement garde une colonne à zéro."""
    raw = model.predict_proba(vec.transform(texts))
    out = np.zeros((raw.shape[0], len(labels)))
    index = {lab: i for i, lab in enumerate(labels)}
    for j, cls in enumerate(model.classes_):
        out[:, index[str(cls)]] = raw[:, j]
    return out


def fit_predict_proba(
    train_texts: Sequence[str], train_y: Sequence[str], test_texts: Sequence[str], labels: Sequence[str], c: float, ngram: tuple[int, int],
    class_weight: str | None = None, analyzer: str = "word",
) -> np.ndarray:
    """Probabilités alignées sur `labels` ; une classe absente de l'entraînement garde une colonne à zéro."""
    vec, model = fit_model(train_texts, train_y, c, ngram, class_weight, analyzer)
    return predict_aligned(vec, model, test_texts, labels)


def select_config(
    texts: Sequence[str], y: Sequence[str], folds: np.ndarray, val_fold: int, labels: Sequence[str], scored: Sequence[str],
    grid: Sequence[tuple[float, tuple[int, int]]] | None = None, class_weight: str | None = None, analyzer: str = "word",
) -> tuple[float, tuple[int, int]]:
    """Meilleure macro-F1 sur `val_fold`, entraînement sur les autres plis fournis ; égalité exacte : C le plus bas, puis unigrammes."""
    tr = [i for i in range(len(y)) if folds[i] != val_fold]
    va = [i for i in range(len(y)) if folds[i] == val_fold]
    best: tuple[float, tuple[int, int]] | None = None
    best_score = -1.0
    for c, ng in (GRID if grid is None else grid):
        p = fit_predict_proba([texts[i] for i in tr], [y[i] for i in tr], [texts[i] for i in va], labels, c, ng, class_weight, analyzer)
        pred = [labels[int(k)] for k in p.argmax(1)]
        score = metrics.macro_f1([y[i] for i in va], pred, scored)
        if score > best_score + 1e-12:
            best, best_score = (c, ng), score
    assert best is not None
    return best
