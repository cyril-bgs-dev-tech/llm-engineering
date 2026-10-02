#!/usr/bin/env python3
"""Télécharge PARHAF (HealthDataHub/PARHAF) à une révision épinglée et vérifie ses empreintes (P0-14).

Usage :
  .venv/bin/python data/scripts/download_parhaf.py             # télécharge ; crée le manifeste s'il n'existe pas, sinon le vérifie
  .venv/bin/python data/scripts/download_parhaf.py --dest /tmp/x  # rejeu dans un dossier propre, vérifié contre le manifeste versionné

Les données vont dans data/raw/ (ignoré par Git). Le manifeste data/manifests/parhaf.json est versionné.
Conditions d'usage : voir data/cards/parhaf.md (usages cliniques, de déploiement et de généralisation exclus).
"""
import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from llmft import manifest as mf

REPO_ID = "HealthDataHub/PARHAF"
# Révision observée le 01/10/2026 (dépôt modifié le 09/06/2026). Une révision n'est jamais « la dernière » : elle est épinglée.
PINNED_REVISION = "60426ccdbbbb335e0281f2e5c236b89100ffbd42"
MANIFEST = ROOT / "data" / "manifests" / "parhaf.json"
DEFAULT_DEST = ROOT / "data" / "raw" / "parhaf"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--revision", default=PINNED_REVISION)
    parser.add_argument("--dest", type=Path, default=DEFAULT_DEST)
    args = parser.parse_args()

    from huggingface_hub import HfApi, snapshot_download

    head = HfApi().dataset_info(REPO_ID).sha
    if head != args.revision:
        print(f"Note : la dernière révision du dépôt est {head}, on reste sur la révision épinglée {args.revision}.")
    local = snapshot_download(repo_id=REPO_ID, repo_type="dataset", revision=args.revision, local_dir=str(args.dest))
    print(f"Téléchargé dans {local}")

    if MANIFEST.exists():
        reference = mf.load_manifest(MANIFEST)
        if reference["revision"] != args.revision:
            print(f"ERREUR : le manifeste est à la révision {reference['revision']}, pas {args.revision}.")
            return 1
        problems = mf.verify_manifest(args.dest, reference)
        if problems:
            print("ERREUR : écarts avec le manifeste versionné :")
            for p in problems:
                print(" -", p)
            return 1
        print(f"OK : {len(reference['files'])} fichiers identiques au manifeste versionné.")
    else:
        built = mf.build_manifest(args.dest, source=REPO_ID, revision=args.revision)
        mf.write_manifest(built, MANIFEST)
        print(f"Manifeste créé : {MANIFEST} ({len(built['files'])} fichiers).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
