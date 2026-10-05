#!/usr/bin/env python3
"""Vérifie que tout fichier suivi par git qui commence par un shebang a le mode 100755 dans l'index : sur le disque Windows monté, les fichiers paraissent exécutables et ruff (EXE001)
ne voit rien en local, mais l'intégration continue sous Linux échoue. Correctif : `git update-index --chmod=+x FICHIER`. Périmètre : scripts/, src/ et tests/ (celui de ruff). Usage : check_exec_bits.py"""
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def main() -> int:
    listing = subprocess.run(["git", "ls-files", "-s"], cwd=ROOT, capture_output=True, text=True, check=True).stdout.splitlines()
    bad = []
    for line in listing:
        meta, path = line.split("\t", 1)
        mode = meta.split()[0]
        if mode == "100755" or not path.endswith((".py", ".sh")) or not path.startswith(("scripts/", "src/", "tests/")):
            continue
        p = ROOT / path
        if p.is_file() and p.read_bytes()[:2] == b"#!":
            bad.append(path)
    if bad:
        print(f"{len(bad)} fichier(s) avec shebang sans mode exécutable dans l'index git (git update-index --chmod=+x) :")
        for b in bad[:20]:
            print(" ", b)
        return 1
    print("modes exécutables : conformes")
    return 0


if __name__ == "__main__":
    sys.exit(main())
