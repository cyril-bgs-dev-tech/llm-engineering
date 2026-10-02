#!/usr/bin/env python3
"""AGENTS.md (Codex) doit rester la copie de CLAUDE.md, aux chemins de dossiers d'agents près : une seule source de règles (RM-04)."""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def norm(path: Path) -> list[str]:
    return [re.sub(r"\.(claude|codex)\b", ".AGENT", line) for line in path.read_text(encoding="utf-8").splitlines()]


def main() -> int:
    a, b = norm(ROOT / "CLAUDE.md"), norm(ROOT / "AGENTS.md")
    if a == b:
        print("CLAUDE.md et AGENTS.md : alignés")
        return 0
    for i, (x, y) in enumerate(zip(a, b, strict=False), 1):
        if x != y:
            print(f"écart à la ligne {i} :\n  CLAUDE.md : {x[:100]}\n  AGENTS.md : {y[:100]}", file=sys.stderr)
            break
    else:
        print(f"longueurs différentes : {len(a)} contre {len(b)} lignes", file=sys.stderr)
    return 1


if __name__ == "__main__":
    sys.exit(main())
