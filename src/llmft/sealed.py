"""Porte unique d'accès au test scellé (PROTOCOLE.md section 3, RM-20) : lecture une seule fois, avec une raison écrite."""
from __future__ import annotations

import json
import os
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


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
