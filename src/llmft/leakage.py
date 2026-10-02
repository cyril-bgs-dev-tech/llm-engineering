"""Contrôles anti-fuite (skill leakage-guard) : quasi-doublons, partitions, hors pli, synthétique.

Le seuil de quasi-doublon est une constante du protocole (PROTOCOLE.md section 4) : un échec se corrige à la source,
jamais en relevant le seuil.
"""
from __future__ import annotations

import re
from collections.abc import Iterable, Mapping, Sequence
from typing import Any

import numpy as np
from sklearn.feature_extraction.text import HashingVectorizer

NEAR_DUPLICATE_THRESHOLD = 0.8  # similarité de Jaccard sur les 5-grammes de caractères du texte normalisé
_NGRAM = 5
_BLOCK = 500


def normalize(text: str) -> str:
    """Minuscules, ponctuation retirée, espaces réduits."""
    return re.sub(r"\s+", " ", re.sub(r"[^\w\s]", " ", text.lower())).strip()


def near_duplicate_pairs(texts: Mapping[str, str], threshold: float = NEAR_DUPLICATE_THRESHOLD) -> list[tuple[str, str, float]]:
    """Paires (id, id, similarité) dont la similarité de Jaccard atteint le seuil ; exact, par blocs creux."""
    ids = list(texts)
    if len(ids) < 2:
        return []
    vec = HashingVectorizer(analyzer="char", ngram_range=(_NGRAM, _NGRAM), n_features=2**22, binary=True, norm=None, alternate_sign=False)
    x = vec.transform([normalize(texts[i]) for i in ids]).tocsr().astype(np.float32)
    sizes = np.asarray(x.sum(axis=1)).ravel()
    out: list[tuple[str, str, float]] = []
    for start in range(0, len(ids), _BLOCK):
        inter = (x[start : start + _BLOCK] @ x.T).toarray()
        union = sizes[start : start + _BLOCK, None] + sizes[None, :] - inter
        jac = inter / np.maximum(union, 1)
        for row in range(jac.shape[0]):
            jac[row, : start + row + 1] = 0  # une seule fois par paire, jamais avec soi-même
        for row, col in zip(*np.where(jac >= threshold), strict=True):
            out.append((ids[start + int(row)], ids[int(col)], round(float(jac[row, col]), 4)))
    return out


def clusters(ids: Iterable[str], pairs: Iterable[tuple[str, str, float]]) -> dict[str, int]:
    """Composantes connexes des paires de quasi-doublons : identifiant -> numéro de groupe (tout texte seul a son groupe)."""
    parent = {i: i for i in ids}

    def find(a: str) -> str:
        while parent[a] != a:
            parent[a] = parent[parent[a]]
            a = parent[a]
        return a

    for a, b, _ in pairs:
        parent[find(a)] = find(b)
    numbering: dict[str, int] = {}
    return {i: numbering.setdefault(find(i), len(numbering)) for i in parent}


def cross_partition_pairs(pairs: Iterable[tuple[str, str, float]], partition_of: Mapping[str, Any]) -> list[tuple[str, str, float]]:
    """Paires de quasi-doublons dont les deux textes sont dans des partitions différentes : chacune est une fuite."""
    return [(a, b, s) for a, b, s in pairs if partition_of[a] != partition_of[b]]


def check_out_of_fold(fold_of: Mapping[str, int], teacher_trained_on: Mapping[str, set[int]]) -> list[str]:
    """Le professeur qui a produit les probabilités de l'exemple `i` ne doit pas avoir vu le pli de `i`."""
    return [f"{i} : le professeur a été entraîné sur le pli {fold} de l'exemple" for i, fold in fold_of.items() if fold in teacher_trained_on[i]]


def check_synthetic_sources(generated: Sequence[Mapping[str, Any]], train_ids: set[str]) -> list[str]:
    """Chaque exemple généré porte l'identifiant de sa source, qui doit appartenir à l'entraînement du pli."""
    problems = []
    for g in generated:
        source = g.get("source_id")
        if source is None:
            problems.append(f"{g['id']} : source inconnue")
        elif source not in train_ids:
            problems.append(f"{g['id']} : source {source} hors de l'entraînement")
    return problems
