#!/usr/bin/env bash
# Confirmation de l'ensemble au pli 1 (fiche 2026-10-04-confirmation-ensemble-pli1) : cinq encodeurs, graines 1000 à 1004, en parallèle du LoRA (mémoire GPU suffisante).
set -u
cd "$(dirname "$0")/.."
export HF_HOME="$PWD/artifacts/hf_cache" HF_HUB_OFFLINE=1 PYTHONPATH=artifacts/fla_pkgs TOKENIZERS_PARALLELISM=false RAYON_NUM_THREADS=2
LOGDIR="${LOGDIR:?LOGDIR requis}"
for k in 0 1 2 3 4; do
  slug="camembert-pli1-ep10-s$k"
  for a in 1 2 3 4; do
    if ls results/runs | grep -q -- "-$slug.json"; then break; fi
    timeout 3600 .venv/bin/python scripts/p1_finetune.py almanach/camembert-bio-base --mode full --fold 1 --lr 1e-4 --epochs 10 --seed "$((1000 + k))" --max-len 508 --micro-batch 16 --effective-batch 32 \
      --fiche experiments/2026-10-04-confirmation-ensemble-pli1.md --slug "$slug" --register > "$LOGDIR/$slug.out" 2>&1
    code=$?; echo "$(date -u +%FT%TZ) $slug essai=$a code=$code" >> "$LOGDIR/pli1.log"; [ "$code" -eq 0 ] && break
  done
done
echo "$(date -u +%FT%TZ) TERMINE14" >> "$LOGDIR/pli1.log"
