#!/usr/bin/env python3
"""Télécharge le ClaML 2019 de la CIM-10 FR (ATIH) et vérifie ses empreintes contre celles de `data/cards/cim10.md` (P5-09 : sans ce script, une reconstruction à froid ne peut pas dériver les étiquettes).

Usage : .venv/bin/python data/scripts/download_cim10.py [--dest DOSSIER]   (défaut : data/raw/cim10)
Source : page ATIH (lien direct relevé le 07/10/2026). Conditions de réutilisation de l'ATIH : mention de l'origine, pas de modification, pas d'usage commercial ; aucun fichier dérivé n'est versionné (voir la fiche).
Seul le XML est conservé (le zip n'est pas rejoué : le XML suffit aux chargeurs)."""
import argparse
import hashlib
import io
import sys
import urllib.request
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
URL = "https://www.atih.sante.fr/sites/default/files/content/documents/cim10classification_internationale_des_maladies_-_cim-10_fr_2019syst_claml_20190211.zip"
EXPECTED = {"cim10fr2019_claml.zip": "a6078fff07e76abf5d319a9643dd2a411d65c47ce2a37b22af492b011d0d9c81", "cim10fr2019.xml": "b835685f4d1359b2f9de41773de254560508ae7351fecfb32836d50eba4e2775"}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--dest", type=Path, default=ROOT / "data" / "raw" / "cim10")
    args = parser.parse_args()
    raw = urllib.request.urlopen(urllib.request.Request(URL, headers={"User-Agent": "Mozilla/5.0"}), timeout=60).read()
    zip_sha = hashlib.sha256(raw).hexdigest()
    if zip_sha != EXPECTED["cim10fr2019_claml.zip"]:
        print(f"ERREUR : empreinte du zip {zip_sha}, attendue {EXPECTED['cim10fr2019_claml.zip']}")
        return 1
    with zipfile.ZipFile(io.BytesIO(raw)) as archive:
        names = [n for n in archive.namelist() if n.lower().endswith(".xml")]
        if len(names) != 1:
            print(f"ERREUR : un seul XML attendu dans le zip, trouvé : {names}")
            return 1
        xml = archive.read(names[0])
    xml_sha = hashlib.sha256(xml).hexdigest()
    if xml_sha != EXPECTED["cim10fr2019.xml"]:
        print(f"ERREUR : empreinte du XML {xml_sha}, attendue {EXPECTED['cim10fr2019.xml']}")
        return 1
    args.dest.mkdir(parents=True, exist_ok=True)
    (args.dest / "cim10fr2019.xml").write_bytes(xml)
    print(f"OK : cim10fr2019.xml ({len(xml)} octets) écrit dans {args.dest}, empreintes du zip et du XML identiques à la fiche.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
