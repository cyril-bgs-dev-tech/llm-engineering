#!/usr/bin/env python3
"""Chaque fiche préenregistrée garde l'empreinte consignée dans experiments/INDEX.md (N29), chaque fiche datée y est citée, et les scripts
qui déclarent DECISION_CONSTANTS n'ont aucune constante absente du texte de leur fiche (N41)."""
import importlib
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))
from llmft.fiches import check_fiche_hashes, missing_constants

DECLARING = ("lora_author_calibration",)  # N41 : tout nouveau script de fiche s'ajoute ici


def main() -> int:
    problems, n = check_fiche_hashes((ROOT / "experiments/INDEX.md").read_text(encoding="utf-8"), ROOT)
    for name in DECLARING:
        module = importlib.import_module(name)
        if missing := missing_constants((ROOT / module.FICHE).read_text(encoding="utf-8"), module.DECISION_CONSTANTS):
            problems.append(f"{name} : constantes absentes de {module.FICHE} : {missing}")
    for p in problems:
        print(f"fiches : {p}", file=sys.stderr)
    print(f"fiches : {n} empreintes vérifiées, {len(DECLARING)} script(s) confronté(s) à sa fiche, " + ("défauts" if problems else "aucun écart"))
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
