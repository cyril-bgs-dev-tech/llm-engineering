#!/usr/bin/env python3
"""Fin estimée d'un lot depuis son journal (règle N39) : un cycle va du premier DEBUT d'un run qui ouvre un cycle (motif) au premier DEBUT du suivant,
contrôles, robustesse et relances comprises ; fin = début du cycle en cours + durée moyenne des cycles mesurés × cycles restants. Estimation, méthode écrite.
Usage : eta_lot.py JOURNAL MOTIF TOTAL   (ex. : results/logs/lots/lora_fin_aleatoire_auteurs.log 'lora-fin-aleatoire-auteur-pli\\d+' 5)"""
import re
import sys
from datetime import UTC, datetime
from itertools import pairwise
from pathlib import Path
from typing import Any

_LINE = re.compile(r"^(\S+Z) DEBUT (\S+) essai=1$")


def project(log_text: str, pattern: str, total: int) -> dict[str, Any]:
    starts = [datetime.strptime(m[1], "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=UTC).timestamp()
              for line in log_text.splitlines() if (m := _LINE.match(line)) and re.fullmatch(pattern, m[2])]
    cycles = [b - a for a, b in pairwise(starts)]
    remaining = total - len(cycles)
    end = starts[-1] + remaining * sum(cycles) / len(cycles) if cycles else None
    return {"cycles_mesures_s": cycles, "cycles_restants": remaining, "fin_estimee": end}


def main() -> int:
    log, pattern, total = sys.argv[1], sys.argv[2], int(sys.argv[3])
    p = project(Path(log).read_text(encoding="utf-8"), pattern, total)
    if p["fin_estimee"] is None:
        print("aucun cycle terminé : pas de projection")
        return 0
    mean = sum(p["cycles_mesures_s"]) / len(p["cycles_mesures_s"])
    print(f"estimation (N39) : cycles mesurés {[round(c / 3600, 2) for c in p['cycles_mesures_s']]} h, moyenne {mean / 3600:.2f} h, "
          f"{p['cycles_restants']} cycle(s) restant(s) dont l'actuel : fin vers {datetime.fromtimestamp(p['fin_estimee'], UTC):%Y-%m-%dT%H:%MZ}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
