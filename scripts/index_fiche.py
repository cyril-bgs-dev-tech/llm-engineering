#!/usr/bin/env python3
"""Hache une fiche préenregistrée et ajoute sa ligne à experiments/INDEX.md en une commande (règle N37) : date et empreinte lues, jamais tapées ;
refus si la fiche contient une heure datée postérieure à maintenant (heure estimée au lieu d'être lue sur l'horloge).
Usage : index_fiche.py experiments/AAAA-MM-JJ-slug.md "Fiche préenregistrée : titre" "déclencheur (premier run de ...)\""""
import hashlib
import sys
from datetime import UTC, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from llmft.fiches import future_times


def index_line(fiche: Path, rel: str, title: str, trigger: str, now: datetime) -> str:
    if "|" in title + trigger:
        raise SystemExit("une barre verticale casserait le tableau de l'index")
    if late := future_times(fiche.read_text(encoding="utf-8"), now):
        raise SystemExit(f"heure postérieure à maintenant ({now:%H:%M}Z) dans la fiche : {', '.join(late)} ; la lire par date -u")
    return f"| {now:%Y-%m-%d} | {title} | `{rel}` | `{hashlib.sha256(fiche.read_bytes()).hexdigest()}` | {trigger} |"


def main() -> int:
    rel, title, trigger = sys.argv[1:4]
    line = index_line(ROOT / rel, rel, title, trigger, datetime.now(UTC))
    with (ROOT / "experiments/INDEX.md").open("a", encoding="utf-8") as index:
        index.write(line + "\n")
    print(line)
    return 0


if __name__ == "__main__":
    sys.exit(main())
