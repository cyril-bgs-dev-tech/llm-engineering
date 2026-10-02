"""Manifeste d'empreintes d'un jeu de données téléchargé (P0-14), bibliothèque standard seule.

Les données restent hors de Git ; seul le manifeste (chemins, tailles, SHA-256, révision) est versionné.
Il permet de vérifier qu'un nouveau téléchargement redonne exactement les mêmes octets.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

SCHEMA = "manifest-1"
_SKIP_DIRS = {".cache"}  # métadonnées locales de huggingface_hub, non reproductibles


def sha256_file(path: Path | str, chunk: int = 1 << 20) -> str:
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for block in iter(lambda: handle.read(chunk), b""):
            digest.update(block)
    return digest.hexdigest()


def _files(root: Path) -> list[Path]:
    return sorted(
        (p for p in root.rglob("*") if p.is_file() and not (set(p.relative_to(root).parts) & _SKIP_DIRS)),
        key=lambda p: p.relative_to(root).as_posix(),
    )


def build_manifest(root: Path | str, source: str, revision: str) -> dict[str, Any]:
    if not revision:
        raise ValueError("la revision doit être épinglée (identifiant de commit du dépôt source)")
    base = Path(root)
    return {
        "schema": SCHEMA,
        "source": source,
        "revision": revision,
        "files": [
            {"path": p.relative_to(base).as_posix(), "bytes": p.stat().st_size, "sha256": sha256_file(p)}
            for p in _files(base)
        ],
    }


def verify_manifest(root: Path | str, manifest: dict[str, Any]) -> list[str]:
    """Liste les écarts entre un dossier et son manifeste ; liste vide = identique."""
    base = Path(root)
    problems: list[str] = []
    expected = {f["path"]: f for f in manifest["files"]}
    present = {p.relative_to(base).as_posix() for p in _files(base)}
    for path, entry in expected.items():
        target = base / path
        if path not in present:
            problems.append(f"{path} : fichier manquant")
        elif sha256_file(target) != entry["sha256"]:
            problems.append(f"{path} : empreinte différente")
    for path in sorted(present - set(expected)):
        problems.append(f"{path} : fichier inattendu")
    return problems


def write_manifest(manifest: dict[str, Any], target: Path | str) -> None:
    Path(target).write_text(json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def load_manifest(path: Path | str) -> dict[str, Any]:
    loaded: dict[str, Any] = json.loads(Path(path).read_text(encoding="utf-8"))
    return loaded
