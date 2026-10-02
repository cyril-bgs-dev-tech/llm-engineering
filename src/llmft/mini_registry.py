"""Mini-registre de runs (RM-05) : un fichier JSON par run, écrit une seule fois, bibliothèque standard seule.

Il existe pour que les spikes de P0 puissent consigner leurs résultats avant le registre complet (P0-41).
Le format est un sous-ensemble de celui de P0-41 : les champs en plus viennent s'ajouter sans rien casser.
"""
from __future__ import annotations

import json
import os
import re
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

SCHEMA = "mini-1"
STATUSES = ("ok", "failed", "aborted")
REQUIRED = ("kind", "slug", "status", "summary")
_SLUG = re.compile(r"^[a-z0-9][a-z0-9_-]*$")
MAX_ID_ATTEMPTS = 1000


def _validate(record: dict[str, Any]) -> None:
    for field in REQUIRED:
        if field not in record:
            raise ValueError(f"champ obligatoire manquant : {field}")
    if record["status"] not in STATUSES:
        raise ValueError(f"status doit valoir {STATUSES}, reçu {record['status']!r}")
    if not _SLUG.match(str(record["slug"])):
        raise ValueError(f"slug invalide : {record['slug']!r} (minuscules, chiffres, tiret, tiret bas)")


def register_run(runs_dir: Path | str, record: dict[str, Any]) -> Path:
    """Écrit `<runs_dir>/<run_id>.json` et le renvoie. Refuse d'écraser un run existant (FileExistsError)."""
    _validate(record)
    now = datetime.now(UTC)
    data = dict(record)  # l'argument n'est jamais modifié
    explicit_id = "run_id" in data
    base_id = data.get("run_id") or f"{now:%Y%m%d-%H%M%S}-{record['slug']}"
    data["created_at"] = now.strftime("%Y-%m-%dT%H:%M:%SZ")
    data["schema"] = SCHEMA
    directory = Path(runs_dir)
    directory.mkdir(parents=True, exist_ok=True)
    # Un identifiant généré qui existe déjà (deux runs dans la même seconde) reçoit un suffixe -2, -3, ... ;
    # un identifiant fourni qui existe déjà reste une erreur : on ne renomme jamais un run demandé par son nom.
    for attempt in range(1, MAX_ID_ATTEMPTS + 1):
        data["run_id"] = base_id if attempt == 1 else f"{base_id}-{attempt}"
        path = directory / f"{data['run_id']}.json"
        payload = json.dumps(data, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
        try:
            # Mode « x » : l'ouverture échoue si le fichier existe déjà, sans fenêtre de course.
            with open(path, "x", encoding="utf-8") as handle:
                handle.write(payload)
                handle.flush()
                os.fsync(handle.fileno())
        except FileExistsError:
            if explicit_id or attempt == MAX_ID_ATTEMPTS:
                raise
            continue
        return path
    raise AssertionError("inatteignable")  # pour mypy : la boucle renvoie ou lève


def load_run(path: Path | str) -> dict[str, Any]:
    loaded: dict[str, Any] = json.loads(Path(path).read_text(encoding="utf-8"))
    return loaded


def list_runs(runs_dir: Path | str) -> list[dict[str, Any]]:
    """Tous les runs d'un dossier, triés par run_id."""
    return sorted((load_run(p) for p in Path(runs_dir).glob("*.json")), key=lambda r: r["run_id"])
