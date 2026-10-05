#!/usr/bin/env bash
# Après la recette d'encodeur v2 (TERMINE26) : analyse par facteur (CPU, un thread, priorité basse).
set -u
cd "$(dirname "$0")/.."
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
LOGDIR="${LOGDIR:?LOGDIR requis}"
until grep -q TERMINE26 "$LOGDIR/encodeur_v2.log" 2>/dev/null; do sleep 60; done
nice -n 15 .venv/bin/python scripts/enc2_analysis.py --register > "$LOGDIR/post_enc2.out" 2>&1
echo "$(date -u +%FT%TZ) TERMINE32 code=$?" >> "$LOGDIR/post_enc2.log"
