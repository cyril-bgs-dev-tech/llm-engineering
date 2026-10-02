#!/usr/bin/env python3
"""Vérifie chaque `scorecards/G-P<n>.md` : schéma de preuve (RM-12) et plancher de la porte lu dans PLAN_PROJET_V6.md."""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from llmft import scorecard


def floors_for(gate: int) -> dict[str, int]:
    out = {}
    for line in (ROOT / "PLAN_PROJET_V6.md").read_text(encoding="utf-8").splitlines():
        m = re.match(r"^\| (Q\d+) [^|]*\|((?: \d+ \|){6})\s*$", line)
        if m:
            out[m.group(1)] = int(m.group(2).replace("|", " ").split()[gate])
    return out


def main() -> int:
    cards = sorted((ROOT / "scorecards").glob("G-P[0-5].md"))
    if not cards:
        print("scorecards : aucune porte à vérifier")
        return 0
    failed = False
    for card in cards:
        floors = floors_for(int(card.stem[-1]))
        if len(floors) != 12:
            print(f"{card.name} : planchers illisibles dans le plan ({len(floors)} catégories)", file=sys.stderr)
            return 2
        problems = scorecard.check_scorecard(card, ROOT, floors)
        for p in problems:
            print(f"{card.name} : {p}", file=sys.stderr)
        failed = failed or bool(problems)
        print(f"{card.name} : {'défauts' if problems else 'schéma respecté'}")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
