#!/usr/bin/env bash
# Copie les journaux de lot (petits, texte) du répertoire de session vers results/logs/lots/ (audit GLM v4, G-c3) : traçabilité des relances et des codes de sortie dans le dépôt.
# Usage : archive_logs.sh REPERTOIRE_DES_JOURNAUX   (copie les *.log ; les sorties détaillées *.out restent hors dépôt)
set -eu
src="${1:?répertoire des journaux requis}"
dest="$(dirname "$0")/../results/logs/lots"
mkdir -p "$dest"
for f in "$src"/*.log; do
  [ -e "$f" ] || continue
  cp "$f" "$dest/$(basename "$f")"
done
echo "journaux archivés dans $dest : $(ls "$dest" | wc -l)"
