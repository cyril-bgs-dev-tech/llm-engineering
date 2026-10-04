#!/usr/bin/env bash
# Qwen3.5-4B à 10 époques, relance en exclusivité (fiche 2026-10-04-llm-recette-mure-qwen4b-v2). Attend TERMINE14 (runs d'encodeur du pli 1). Un seul essai : un arrêt anticipé est la mesure.
set -u
cd "$(dirname "$0")/.."
export HF_HOME="$PWD/artifacts/hf_cache" HF_HUB_OFFLINE=1 PYTHONPATH=artifacts/fla_pkgs TOKENIZERS_PARALLELISM=false RAYON_NUM_THREADS=2
LOGDIR="${LOGDIR:?LOGDIR requis}"
until grep -q TERMINE14 "$LOGDIR/pli1.log" 2>/dev/null; do sleep 15; done
slug="llm-mur2-qwen3-5-4b-ep10-lr1e-4"
echo "$(date -u +%FT%TZ) DEBUT $slug" >> "$LOGDIR/llm_mur2.log"
timeout 28800 .venv/bin/python scripts/p1_finetune.py Qwen/Qwen3.5-4B --mode lora --lr 1e-4 --epochs 10 --max-len 4096 --micro-batch 1 --effective-batch 32 --limit-seconds 22700 \
  --fiche experiments/2026-10-04-llm-recette-mure-qwen4b-v2.md --slug "$slug" --register > "$LOGDIR/$slug.out" 2>&1
echo "$(date -u +%FT%TZ) FIN $slug code=$?" >> "$LOGDIR/llm_mur2.log"
echo "$(date -u +%FT%TZ) TERMINE15" >> "$LOGDIR/llm_mur2.log"
