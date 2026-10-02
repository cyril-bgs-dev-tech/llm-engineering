"""Chargeur générique : lit un contrat et un adaptateur (id, text, label, author) ; aucune branche propre à une tâche.

Un adaptateur est tout objet doté d'une méthode `load() -> DataFrame` aux colonnes `id`, `text`, `label` (identifiant
de classe du contrat) et `author`. Les partitions se lisent par `load_partitions`, qui compare leur empreinte à la référence.
"""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Protocol

import pandas as pd

from llmft.taskspec import TaskSpec

REQUIRED_COLUMNS = ("id", "text", "label", "author")


class DataError(ValueError):
    """Données ou partitions incohérentes avec le contrat ; le message dit lesquelles."""


class Adapter(Protocol):
    def load(self) -> pd.DataFrame: ...


@dataclass
class Dataset:
    spec: TaskSpec
    frame: pd.DataFrame


def load_dataset(spec: TaskSpec, adapter: Adapter) -> Dataset:
    frame = adapter.load()
    missing = [c for c in REQUIRED_COLUMNS if c not in frame.columns]
    if missing:
        raise DataError(f"colonnes manquantes : {missing} (attendues : {list(REQUIRED_COLUMNS)})")
    if frame["id"].duplicated().any():
        raise DataError(f"identifiants dupliqués : {sorted(frame.loc[frame['id'].duplicated(), 'id'])[:5]}")
    if (frame["text"].fillna("").str.strip() == "").any():
        raise DataError(f"texte vide pour : {sorted(frame.loc[frame['text'].fillna('').str.strip() == '', 'id'])[:5]}")
    unknown = sorted(set(frame["label"]) - set(spec.class_ids))
    if unknown:
        raise DataError(f"étiquettes hors de la liste fermée du contrat {spec.task_id} : {unknown}")
    return Dataset(spec=spec, frame=frame.reset_index(drop=True))


def load_partitions(path: Path | str, reference_sha_path: Path | str) -> dict[str, Any]:
    """Lit un fichier de partitions après avoir comparé son empreinte SHA-256 à celle de la référence versionnée."""
    raw = Path(path).read_bytes()
    expected = Path(reference_sha_path).read_text(encoding="ascii").strip()
    actual = hashlib.sha256(raw).hexdigest()
    if actual != expected:
        raise DataError(f"empreinte des partitions différente de la référence : {actual[:12]} contre {expected[:12]}")
    loaded: dict[str, Any] = json.loads(raw)
    return loaded


def select(dataset: Dataset, partitions: dict[str, Any], fold: int, role: str, key: str = "folds") -> pd.DataFrame:
    """`validation` : le pli `fold` ; `train` : tous les autres plis de développement. La partition scellée n'est jamais renvoyée."""
    folds: list[list[str]] = partitions[key]
    if role == "validation":
        wanted = set(folds[fold])
    elif role == "train":
        wanted = {i for k, f in enumerate(folds) if k != fold for i in f}
    else:
        raise ValueError(f"role inconnu : {role!r} (train ou validation)")
    selected: pd.DataFrame = dataset.frame[dataset.frame["id"].isin(wanted)].reset_index(drop=True)
    return selected
