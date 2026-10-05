#!/usr/bin/env bash
# Après la distillation (TERMINE24) : analyse regroupée (CPU, un thread, priorité basse).
set -u
cd "$(dirname "$0")/.."
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
LOGDIR="${LOGDIR:?LOGDIR requis}"
until grep -q TERMINE24 "$LOGDIR/distillation.log" 2>/dev/null; do sleep 60; done
nice -n 15 .venv/bin/python scripts/distill_analysis.py --register > "$LOGDIR/post_distillation.out" 2>&1
echo "$(date -u +%FT%TZ) TERMINE30 code=$?" >> "$LOGDIR/post_distillation.log"
