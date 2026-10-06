#!/usr/bin/env python3
"""Télécharge MorFITT (Dr-BERT/MORFITT, format parquet) à une révision épinglée et vérifie ses empreintes (RM-49, dataset-intake).

Usage :
  .venv/bin/python data/scripts/download_morfitt.py --dest DOSSIER   # rejeu dans un dossier propre, vérifié contre le manifeste versionné
  .venv/bin/python data/scripts/download_morfitt.py --build          # construit le manifeste depuis data/raw/morfitt (déjà téléchargé le 05/10/2026), après vérification de l'identité avec un téléchargement propre
Seuls le README et les trois parquet `source/` sont téléchargés. Conditions d'usage : voir data/cards/morfitt.md (licence à vérifier à la source, deux déclarations divergentes)."""
import argparse
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from llmft import manifest as mf

REPO_ID = "Dr-BERT/MORFITT"
# Révision observée le 06/10/2026 (dépôt modifié le 15/01/2026) ; le jeu local a été téléchargé le 05/10/2026 : son identité avec cette révision est vérifiée par --build.
PINNED_REVISION = "5f381299bb113fdba325538d65ef412650a4d98e"
ALLOW = ["README.md", "source/*"]
MANIFEST = ROOT / "data" / "manifests" / "morfitt.json"
LOCAL = ROOT / "data" / "raw" / "morfitt"


def fetch(dest: Path) -> None:
    from huggingface_hub import snapshot_download

    snapshot_download(repo_id=REPO_ID, repo_type="dataset", revision=PINNED_REVISION, local_dir=str(dest), allow_patterns=ALLOW)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--dest", type=Path)
    parser.add_argument("--build", action="store_true")
    args = parser.parse_args()
    if args.build:
        with tempfile.TemporaryDirectory() as tmp:
            fetch(Path(tmp))
            fresh = mf.build_manifest(tmp, source=REPO_ID, revision=PINNED_REVISION)
        local = mf.build_manifest(LOCAL, source=REPO_ID, revision=PINNED_REVISION)
        ignored = {f["path"] for f in local["files"]} - {f["path"] for f in fresh["files"]}
        local["files"] = [f for f in local["files"] if f["path"] in {g["path"] for g in fresh["files"]}]
        if local["files"] != fresh["files"]:
            print("ERREUR : le jeu local diffère du téléchargement propre à la révision épinglée")
            return 1
        mf.write_manifest(fresh, MANIFEST)
        print(f"Manifeste créé : {MANIFEST} ({len(fresh['files'])} fichiers, identiques au jeu local ; fichiers locaux hors périmètre ignorés : {sorted(ignored)})")
        return 0
    dest = args.dest or LOCAL
    fetch(dest)
    problems = mf.verify_manifest(dest, mf.load_manifest(MANIFEST))
    for p in problems:
        print(" -", p)
    print("OK : identique au manifeste versionné" if not problems else "ERREUR : écarts avec le manifeste")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
