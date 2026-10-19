#!/usr/bin/env bash
# Entrée de journal de nuit (règle N37) : en-tête horodaté par date -u, corps lu sur l'entrée standard et écrit tel quel (aucune expansion).
# Usage : scripts/journal_entry.sh "titre" <<'FIN' ... FIN   (variable JOURNAL : fichier visé, par défaut tasks/JOURNAL_NUIT_2026-10-02.md)
set -eu
title="${1:-}"
[ -n "$title" ] || { echo "titre requis" >&2; exit 2; }
journal="${JOURNAL:-$(dirname "$0")/../tasks/JOURNAL_NUIT_2026-10-02.md}"
body="$(cat; echo .)"
printf '\n### %s : %s\n\n%s' "$(date -u +%FT%TZ)" "$title" "${body%.}" >> "$journal"
