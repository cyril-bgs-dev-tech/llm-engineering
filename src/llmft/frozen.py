"""Contrôle des instantanés gelés : chaque ligne de `experiments/INDEX.md` qui cite un fichier de `experiments/frozen/` doit
correspondre à son empreinte SHA-256 (PROTOCOLE.md 6.10, règle 2). Les lignes plus anciennes, sans instantané, sont ignorées.
Une ligne qui cite `experiments/frozen/` sans être lisible est un défaut ; dès qu'un instantané existe, toutes les entrées
obligatoires (`REQUIRED`) doivent figurer dans l'index."""
from __future__ import annotations

import hashlib
import re
from collections.abc import Sequence
from pathlib import Path

_ROW = re.compile(r"^\|[^|]*\|[^|]*\|\s*`(experiments/frozen/[^`]+)`[^|]*\|\s*`([0-9a-f]{64})`")
REQUIRED = ("PROTOCOLE", "ADR-004", "ADR-007", "ADR-009", "ADR-010", "parhaf_cim10_chapter.yaml", "metrics", "splits_summary", "parhaf_cim10_chapter.sha256")


def check_index(index_text: str, root: Path, required: Sequence[str] = ()) -> list[str]:
    problems = []
    cited: list[str] = []
    for line in index_text.splitlines():
        match = _ROW.match(line)
        if not match:
            if "experiments/frozen/" in line and line.startswith("|"):
                problems.append(f"ligne d'instantané illisible : {line[:80]}")
            continue
        rel, expected = match.groups()
        cited.append(rel)
        target = root / rel
        if not target.is_file():
            problems.append(f"instantané absent : {rel}")
        elif hashlib.sha256(target.read_bytes()).hexdigest() != expected:
            problems.append(f"empreinte différente de l'index : {rel}")
    if cited:
        problems += [f"entrée obligatoire absente de l'index : {name}" for name in required if not any(name in c for c in cited)]
    return problems
