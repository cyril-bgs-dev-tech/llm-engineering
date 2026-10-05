#!/usr/bin/env python3
"""Vérifie que les identifiants de runs cités dans RESULTATS.md, docs/*.md et la présentation existent au registre (ou sont une fiche de `experiments/`, une page du wiki ou une exception connue)."""
import glob
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from llmft import claims

ALLOW = {"claim-gate", "audit-hebdomadaire.yml"}


def main() -> int:
    known: set[str] = set()
    for f in glob.glob(str(ROOT / "results/runs/*.json")):
        d = json.loads(Path(f).read_text(encoding="utf-8"))
        known |= {d["slug"], d["run_id"]}
    known |= {Path(f).stem for f in glob.glob(str(ROOT / "experiments/*.md"))}
    known |= {Path(f).stem for f in glob.glob(str(ROOT / "knowledge/wiki/pages/*.md"))}
    known |= {Path(f).name for f in glob.glob(str(ROOT / ".claude/skills/*"))}
    docs = [ROOT / "RESULTATS.md", *map(Path, glob.glob(str(ROOT / "docs/*.md"))), *map(Path, glob.glob(str(ROOT / "docs/presentation/*.md")))]
    bad = {}
    for d in docs:
        unknown = claims.unknown_run_references(d.read_text(encoding="utf-8"), known, ALLOW)
        if unknown:
            bad[str(d.relative_to(ROOT))] = unknown
    for d, tokens in bad.items():
        print(f"{d} : identifiants inconnus du registre : {', '.join(tokens)}", file=sys.stderr)
    print("claim-gate : références de runs vérifiées" if not bad else "claim-gate : défauts")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
