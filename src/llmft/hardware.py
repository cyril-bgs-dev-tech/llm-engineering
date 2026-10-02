"""Profils matériels (`hardware/<nom>.yaml`) : le code lit la carte cible ici, il ne la suppose jamais."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

DEFAULT_DIR = Path(__file__).resolve().parents[2] / "hardware"
REQUIRED = ("name", "compute_capability", "vram_gib", "vram_budget_gib", "precision_default")


@dataclass(frozen=True)
class HardwareProfile:
    name: str
    compute_capability: str
    vram_gib: float
    vram_budget_gib: float
    precision_default: str
    notes: str = ""


def load_profile(name: str, directory: Path | str = DEFAULT_DIR) -> HardwareProfile:
    path = Path(directory) / f"{name}.yaml"
    if not path.exists():
        raise FileNotFoundError(f"profil matériel introuvable : {name} ({path})")
    raw: dict[str, Any] = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    for field in REQUIRED:
        if field not in raw:
            raise ValueError(f"{path.name} : champ obligatoire manquant : {field}")
    if float(raw["vram_budget_gib"]) > float(raw["vram_gib"]):
        raise ValueError(f"{path.name} : vram_budget_gib dépasse vram_gib, le budget doit rester sous la capacité")
    return HardwareProfile(
        name=str(raw["name"]),
        compute_capability=str(raw["compute_capability"]),
        vram_gib=float(raw["vram_gib"]),
        vram_budget_gib=float(raw["vram_budget_gib"]),
        precision_default=str(raw["precision_default"]),
        notes=str(raw.get("notes", "")),
    )
