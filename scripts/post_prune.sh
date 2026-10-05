#!/usr/bin/env bash
# Après l'encodeur élagué (TERMINE33) : analyse (CPU, un thread, priorité basse).
set -u
cd "$(dirname "$0")/.."
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
LOGDIR="${LOGDIR:?LOGDIR requis}"
until grep -q TERMINE33 "$LOGDIR/encodeur_elague.log" 2>/dev/null; do sleep 60; done
nice -n 15 .venv/bin/python scripts/prune_analysis.py --register > "$LOGDIR/post_prune.out" 2>&1
echo "$(date -u +%FT%TZ) TERMINE34 code=$?" >> "$LOGDIR/post_prune.log"
