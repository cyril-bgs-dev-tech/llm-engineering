#!/usr/bin/env python3
"""Contrôle RM-59 : tout run « ok » enregistré depuis l'entrée en vigueur porte un tampon de santé de la machine au verdict « ok » (`llmft.machine_health`), ou une dérogation écrite (`health_waiver`)."""
import glob
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from llmft import machine_health


def main() -> int:
    runs_dir = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "results/runs"  # dossier de runs : pour prouver le contrôle sur un faux registre (N34)
    records = [json.loads(Path(f).read_text(encoding="utf-8")) for f in sorted(glob.glob(str(runs_dir / "*.json")))]
    bad = machine_health.unhealthy_runs(records)
    for run_id, reason in bad:
        print(f"{run_id} : {reason}", file=sys.stderr)
    print(f"santé de la machine : {len(records)} runs lus, {len(bad)} sans tampon sain depuis {machine_health.HEALTH_REQUIRED_SINCE}")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
