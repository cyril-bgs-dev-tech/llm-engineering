#!/usr/bin/env bash
# Enchaîne l'ancrage MorFITT (RM-49) derrière le lot des graines d'encodeur en plis d'auteurs : un seul lot GPU à la fois (règle d'ordonnancement 1). À lancer détaché ; LOGDIR requis.
set -u
cd "$(dirname "$0")/.."
LOGDIR="${LOGDIR:?LOGDIR requis}"
until grep -q "TERMINE (graines : 1 2)" "$LOGDIR/encodeur_auteurs.log" 2>/dev/null; do sleep 30; done
exec scripts/run_guarded.sh bash scripts/run_morfitt.sh
