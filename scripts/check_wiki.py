#!/usr/bin/env python3
"""Branche le lint mécanique du wiki sur `make check` : échec sur lien cassé, frontmatter manquant ou collision de slug."""
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BLOCKING = ("broken_links", "missing_frontmatter", "slug_collisions")


def main() -> int:
    proc = subprocess.run([sys.executable, "bin/lint-mechanical.py"], cwd=ROOT / "knowledge", capture_output=True, text=True, check=False)
    try:
        report = json.loads(proc.stdout)
    except json.JSONDecodeError:
        print("wiki : sortie du lint illisible", file=sys.stderr)
        print(proc.stderr[-400:], file=sys.stderr)
        return 2
    findings = report.get("findings")
    if not isinstance(findings, dict) or not all(k in findings for k in BLOCKING):
        print(f"wiki : format de rapport inattendu, clés vues : {list(report)}", file=sys.stderr)
        return 2  # un rapport qu'on ne sait pas lire n'est jamais « propre »
    problems = {k: findings[k] for k in BLOCKING if findings[k]}
    for key, value in problems.items():
        print(f"wiki : {key} : {value}", file=sys.stderr)
    print("wiki : propre" if not problems else "wiki : échec")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
