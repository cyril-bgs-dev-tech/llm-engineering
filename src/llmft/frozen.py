"""Contrôle des instantanés gelés : chaque ligne de `experiments/INDEX.md` qui cite un fichier de `experiments/frozen/` doit
correspondre à son empreinte SHA-256 (PROTOCOLE.md 6.10, règle 2). Les lignes plus anciennes, sans instantané, sont ignorées."""
from __future__ import annotations

import hashlib
import re
from pathlib import Path

_ROW = re.compile(r"^\|[^|]*\|[^|]*\|\s*`(experiments/frozen/[^`]+)`[^|]*\|\s*`([0-9a-f]{64})`")


def check_index(index_text: str, root: Path) -> list[str]:
    problems = []
    for line in index_text.splitlines():
        match = _ROW.match(line)
        if not match:
            continue
        rel, expected = match.groups()
        target = root / rel
        if not target.is_file():
            problems.append(f"instantané absent : {rel}")
        elif hashlib.sha256(target.read_bytes()).hexdigest() != expected:
            problems.append(f"empreinte différente de l'index : {rel}")
    return problems
