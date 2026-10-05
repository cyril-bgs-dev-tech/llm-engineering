#!/usr/bin/env python3
"""Heures de GPU consommées d'après le registre contre B = 90 h ; code de sortie 1 à 80 % de B (alerte du protocole)."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from llmft.budget import BUDGET_HOURS, alert, consumed_hours


def main() -> int:
    hours = consumed_hours(ROOT / "results/runs")
    print(f"{hours:.2f} h de durée d'entraînement et de tokenisation enregistrées sur B = {BUDGET_HOURS:.0f} h ({100 * hours / BUDGET_HOURS:.1f} %)")
    return 1 if alert(hours) else 0


if __name__ == "__main__":
    raise SystemExit(main())
