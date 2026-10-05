#!/usr/bin/env python3
"""Vérifie que chaque instantané gelé cité par `experiments/INDEX.md` a bien l'empreinte consignée."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from llmft import frozen


def main() -> int:
    problems = frozen.check_index((ROOT / "experiments/INDEX.md").read_text(encoding="utf-8"), ROOT, frozen.REQUIRED)
    for p in problems:
        print(f"gel : {p}", file=sys.stderr)
    print("gel : " + ("défauts" if problems else "instantanés conformes à l'index"))
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
