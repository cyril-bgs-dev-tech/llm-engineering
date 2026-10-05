#!/usr/bin/env python3
"""Enregistre au registre (ajout seul) la sortie JSON d'un spike : register_json_run.py SORTIE.json SLUG "résumé" [kind]."""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))
from llmft.mini_registry import register_run

ROOT = Path(__file__).resolve().parents[2]
payload = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
record = {"kind": sys.argv[4] if len(sys.argv) > 4 else "measure", "slug": sys.argv[2], "status": "ok", "summary": sys.argv[3], "metrics": payload}
print(register_run(ROOT / "results/runs", record))
