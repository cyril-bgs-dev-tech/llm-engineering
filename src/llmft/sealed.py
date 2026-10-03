"""Porte unique d'accès au test scellé (PROTOCOLE.md section 3, RM-20) : lecture une seule fois, avec une raison écrite."""
from __future__ import annotations

import json
import os
from collections.abc import Callable, Mapping, Sequence
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import pandas as pd

MARKER_PATH = Path("data/splits/sealed_opened.marker")  # chemin fixé par PROTOCOLE.md 6.8
JOURNAL_PATH = Path("data/splits/sealed_access.log")  # une ligne par accès : opération et date, jamais de contenu


def log_access(journal: Path | str | None, operation: str, n_ids: int) -> None:
    """Ajoute une ligne au journal des accès au test scellé (audit GLM C8-A7) ; sans journal, ne fait rien."""
    if journal is None:
        return
    path = Path(journal)
    path.parent.mkdir(parents=True, exist_ok=True)
    record = {"at": datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ"), "operation": operation, "n_ids": n_ids}
    with open(path, "a", encoding="utf-8") as handle:
        handle.write(json.dumps(record, ensure_ascii=False) + "\n")


class AlreadyOpenedError(RuntimeError):
    """Le test scellé a déjà été ouvert : une seconde ouverture invaliderait son statut confirmatoire."""


def open_sealed_test(split: dict[str, Any], marker: Path | str, reason: str) -> list[str]:
    """Renvoie les identifiants du test scellé et laisse une trace d'ouverture ; refuse toute seconde ouverture."""
    if not reason.strip():
        raise ValueError("reason obligatoire : dire pourquoi le test scellé est ouvert")
    path = Path(marker)
    path.parent.mkdir(parents=True, exist_ok=True)
    record = {"opened_at": datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ"), "reason": reason, "n_ids": len(split["test"])}
    try:
        with open(path, "x", encoding="utf-8") as handle:  # échoue si le marqueur existe déjà
            handle.write(json.dumps(record, ensure_ascii=False, indent=1) + "\n")
            handle.flush()
            os.fsync(handle.fileno())
    except FileExistsError as exc:
        raise AlreadyOpenedError(f"test scellé déjà ouvert, voir {path}") from exc
    ids: list[str] = list(split["test"])
    return ids


class ConsumedWithoutResultError(RuntimeError):
    """Le temps B a échoué après l'écriture du marqueur : le test est consommé sans résultat, aucune seconde ouverture."""


def _test_rows(split: dict[str, Any], frame: pd.DataFrame) -> pd.DataFrame:
    ids: list[str] = list(split["test"])
    missing = sorted(set(ids) - set(frame["id"]))
    if missing:
        raise ValueError(f"identifiants du test absents des données : {', '.join(missing)}")
    return pd.DataFrame(frame.set_index("id").loc[ids].reset_index())


def sealed_inputs(split: dict[str, Any], frame: pd.DataFrame, text_col: str, journal: Path | str | None = None) -> pd.DataFrame:
    """Temps A : identifiants et textes du test, AUCUNE colonne d'étiquette, aucun marqueur."""
    rows = _test_rows(split, frame)
    log_access(journal, "inputs", len(rows))
    return pd.DataFrame(rows[["id", text_col]].rename(columns={text_col: "text"}))


def sealed_labels_and_score(
    split: dict[str, Any], frame: pd.DataFrame, label_col: str, predictions: Mapping[str, Any],
    compute: Callable[[Sequence[Any], Sequence[Any]], dict[str, Any]], marker: Path | str, reason: str, out_path: Path | str, rehearsal: bool = False, journal: Path | str | None = None,
) -> dict[str, Any]:
    """Temps B : vérifie la couverture des prédictions, écrit le marqueur, lit les étiquettes, calcule, écrit le résultat par remplacement atomique.

    `rehearsal=True` (répétition générale) : mêmes calculs en mémoire sur les données données, ni marqueur ni fichier. Une panne après l'écriture du marqueur
    le conserve (le test est consommé sans résultat)."""
    ids: list[str] = list(split["test"])
    if set(predictions) != set(ids):
        raise ValueError("les prédictions ne couvrent pas exactement les identifiants du test")
    if not reason.strip():
        raise ValueError("reason obligatoire : dire pourquoi le test scellé est ouvert")
    if rehearsal:
        rows = _test_rows(split, frame)
        log_access(journal, "rehearsal", len(rows))
        return compute(rows[label_col].tolist(), [predictions[i] for i in ids])
    open_sealed_test(split, marker, reason)
    log_access(journal, "open", len(ids))
    try:
        rows = _test_rows(split, frame)
        result = compute(rows[label_col].tolist(), [predictions[i] for i in ids])
        target = Path(out_path)
        tmp = target.with_suffix(target.suffix + ".tmp")
        tmp.write_text(json.dumps(result, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
        os.replace(tmp, target)
    except Exception as exc:
        raise ConsumedWithoutResultError(f"test scellé consommé sans résultat : {exc}") from exc
    return result
