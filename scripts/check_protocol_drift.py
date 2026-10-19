#!/usr/bin/env python3
"""Contrôle de dérive documentaire (réserve R-a du contrat de nuit) : les valeurs gelées du protocole (δ, K, B, N), lues dans `PROTOCOLE.md`,
ne doivent être contredites dans aucun document de référence (backlog, plan, feuille de route, contraintes, résultats, protocole v2, ADR, `docs/`).
Usage : check_protocol_drift.py [RACINE]  (la racine sert à prouver le contrôle sur une copie piégée, N34) ; code 1 si une valeur dérive."""
import glob
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOCUMENTS = ["MICROTACHES.md", "PLAN_PROJET_V6.md", "roadmap_unifié.md", "CONSTRAINTS.md", "RESULTATS.md", "PROTOCOLE.md", "PROTOCOLE_V2.md", "CLAUDE.md", "docs/decisions/ADR-*.md", "docs/*.md"]
MENTIONS = {
    "delta": re.compile(r"δ\s*=\s*([0-9]+(?:,[0-9]+)?)"),
    "B": re.compile(r"\bB\s*=\s*([0-9]+(?:,[0-9]+)?)\s*h\b"),
    "K": re.compile(r"\bK\s*=\s*([0-9]+)\b"),
    "N": re.compile(r"\bN\s*=\s*([0-9]+)\b"),
}
REFERENCE = {  # lignes du protocole gelé (section 6, tableau des valeurs ; section 5 pour N)
    "delta": re.compile(r"\| δ, [^|]*\| \*\*([0-9]+(?:,[0-9]+)?) points\*\*"),
    "K": re.compile(r"\| K, [^|]*\| \*\*([0-9]+)\*\*"),
    "B": re.compile(r"\| B, [^|]*\| \*\*([0-9]+) h\*\*"),
    "N": re.compile(r"nombre d'essais \*\*N\*\* est fixé à \*\*([0-9]+)\*\*"),
}


def _number(text: str) -> float:
    return float(text.replace(",", "."))


def reference_values(protocol_text: str) -> dict[str, float]:
    out = {}
    for name, rx in REFERENCE.items():
        m = rx.search(protocol_text)
        if m is None:
            raise ValueError(f"valeur de référence {name} introuvable dans PROTOCOLE.md")
        out[name] = _number(m.group(1))
    return out


def drift(text: str, reference: dict[str, float]) -> list[tuple[int, str, str]]:
    """(ligne, nom, extrait) pour chaque mention « δ = x », « B = x h », « K = x », « N = x » dont la valeur diffère de la référence."""
    found = []
    for name, rx in MENTIONS.items():
        for m in rx.finditer(text):
            if _number(m.group(1)) != reference[name]:
                found.append((text.count("\n", 0, m.start()) + 1, name, m.group(0)))
    return sorted(found)


def main(argv: list[str]) -> int:
    root = Path(argv[0]) if argv else ROOT
    reference = reference_values((root / "PROTOCOLE.md").read_text(encoding="utf-8"))
    paths = sorted({Path(p) for pattern in DOCUMENTS for p in glob.glob(str(root / pattern))})
    errors = [f"{p.relative_to(root)}:{line} : {excerpt} (protocole gelé : {name} = {reference[name]:g})"
              for p in paths for line, name, excerpt in drift(p.read_text(encoding="utf-8"), reference)]
    for e in errors:
        print(e, file=sys.stderr)
    print(f"dérive documentaire : {len(paths)} documents lus, valeurs gelées {reference}, {len(errors)} écart(s)")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
