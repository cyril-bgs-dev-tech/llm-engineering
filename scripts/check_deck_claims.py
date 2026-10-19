#!/usr/bin/env python3
"""Contrôle RM-59 des présentations HTML (`docs/presentation/*.html`) : chaque chiffre balisé `data-claim` est égal à la valeur du registre décrite dans
`docs/presentation/claims.json`, et chaque identifiant de run cité dans un élément `<code>` existe au registre.
Usage : check_deck_claims.py [DOSSIER_DES_PRESENTATIONS]  (le dossier sert à prouver le contrôle sur une copie piégée, N34)."""
import glob
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from llmft import claims

_CODE = re.compile(r"<code>([^<]*)</code>")


def main() -> int:
    deck_dir = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "docs/presentation"
    records = {}
    for f in glob.glob(str(ROOT / "results/runs/*.json")):
        d = json.loads(Path(f).read_text(encoding="utf-8"))
        records[d["run_id"]] = d
    ledger_path = deck_dir / "claims.json"
    ledger = json.loads(ledger_path.read_text(encoding="utf-8")) if ledger_path.exists() else {}
    known = {r["run_id"] for r in records.values()} | {str(r.get("slug")) for r in records.values()}
    known |= {Path(f).stem for f in glob.glob(str(ROOT / "experiments/*.md"))}
    errors, n_spans = [], 0
    for deck in sorted(deck_dir.glob("*.html")):
        html = deck.read_text(encoding="utf-8")
        spans = claims.claim_spans(html)
        n_spans += len(spans)
        errors += [f"{deck.name} : {e}" for e in claims.check_claim_values(spans, ledger, records)]
        cited = " ".join(f"`{c}`" for c in _CODE.findall(html))
        errors += [f"{deck.name} : run cité inconnu du registre : {t}" for t in claims.unknown_run_references(cited, known, set())]
    for e in errors:
        print(e, file=sys.stderr)
    print(f"présentations : {n_spans} chiffres balisés vérifiés contre le registre, {len(errors)} erreur(s)")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
