#!/usr/bin/env bash
# Ancrage MorFITT (RM-49, fiche 2026-10-05-ancrage-morfitt) : réglage sur validation puis cinq graines évaluées une fois sur le test public. Attend l'ouverture du test scellé de PARHAF (marqueur) et un GPU libre
# (fin de TERMINE33). run_lot (N25), codes 134 et 139 seuls relancés.
set -u
cd "$(dirname "$0")/.."
export HF_HOME="$PWD/artifacts/hf_cache" HF_HUB_OFFLINE=1 PYTHONPATH=artifacts/fla_pkgs TOKENIZERS_PARALLELISM=false RAYON_NUM_THREADS=2 RETRY_CODES="134 139"
LOGDIR="${LOGDIR:?LOGDIR requis}"
source scripts/lib/lot.sh
until [ -f data/splits/sealed_opened.marker ] && grep -q TERMINE33 "$LOGDIR/encodeur_elague.log" 2>/dev/null; do sleep 60; done
FICHE=experiments/2026-10-05-ancrage-morfitt.md
run_lot "$LOGDIR/morfitt.log" morfitt-reglage-validation 2 bash -c ".venv/bin/python scripts/morfitt_run.py tune --register --fiche $FICHE > \"$LOGDIR/morfitt_tune.out\" 2>&1"
run_lot "$LOGDIR/morfitt.log" morfitt-final-resume 2 bash -c ".venv/bin/python scripts/morfitt_run.py final --register --fiche $FICHE > \"$LOGDIR/morfitt_final.out\" 2>&1"
echo "$(date -u +%FT%TZ) TERMINE35" >> "$LOGDIR/morfitt.log"
