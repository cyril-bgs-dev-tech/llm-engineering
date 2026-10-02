"""Vérifie le schéma de preuve des scorecards (`scorecards/*.md`) : une note ne se pose jamais sans preuve.

Le vérificateur contrôle la **présence** et la **cohérence** des preuves (champs, empreinte de l'artefact, degré
d'indépendance) ; il ne prouve pas qu'une note est juste : cela reste le travail de la confirmation indépendante.
"""
from __future__ import annotations

import hashlib
import re
from pathlib import Path
from typing import Any

import yaml

PROOF_FIELDS = ("requirement", "artifact", "command", "expected", "observed", "date", "residual_defect", "justification")
DEGREES = ("code", "données", "méthode", "personne ou contexte", "reconstruction à froid")
_BLOCK = re.compile(r"```yaml\n(.*?)```", re.DOTALL)


def parse_blocks(text: str) -> list[dict[str, Any]]:
    blocks = []
    for raw in _BLOCK.findall(text):
        loaded = yaml.safe_load(raw)
        if isinstance(loaded, dict):
            blocks.append(loaded)
    return blocks


def check_scorecard(path: Path | str, root: Path | str, floors: dict[str, int]) -> list[str]:
    """Liste des défauts du fichier ; liste vide = schéma respecté. `floors` donne le plancher de chaque catégorie."""
    base = Path(root)
    problems: list[str] = []
    seen: set[str] = set()
    for b in parse_blocks(Path(path).read_text(encoding="utf-8")):
        q = str(b.get("q", "?"))
        if q in seen:
            problems.append(f"{q} : catégorie notée deux fois")
        seen.add(q)
        note = b.get("note")
        if not isinstance(note, int) or not 0 <= note <= 3:
            problems.append(f"{q} : note invalide {note!r} (entier de 0 à 3)")
            continue
        if note < floors.get(q, 0) and not str(b.get("remediation", "")).strip():
            problems.append(f"{q} : note {note} sous le plancher {floors[q]} sans plan de rattrapage")
        if note == 0:
            continue
        for field in PROOF_FIELDS:
            if not str(b.get(field, "")).strip():
                problems.append(f"{q} : champ de preuve manquant ou vide : {field}")
        artifact = str(b.get("artifact", "")).strip()
        if artifact:
            target = base / artifact
            if not target.exists():
                problems.append(f"{q} : artefact introuvable : {artifact}")
            elif str(b.get("artifact_sha256", "")).strip() != hashlib.sha256(target.read_bytes()).hexdigest():
                problems.append(f"{q} : empreinte de l'artefact différente de celle consignée ({artifact})")
        if note == 3:
            if not str(b.get("independent_confirmation", "")).strip():
                problems.append(f"{q} : la note 3 exige une confirmation indépendante")
            elif b.get("independence_degree") not in DEGREES:
                problems.append(f"{q} : degré d'indépendance absent ou inconnu (attendu : {', '.join(DEGREES)})")
    return problems
