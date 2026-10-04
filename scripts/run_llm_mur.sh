#!/usr/bin/env bash
# Qwen3.5-4B à 10 époques (fiche 2026-10-04-llm-recette-mure-qwen4b). Attend TERMINE11 (graines de l'encodeur).
set -u
cd "$(dirname "$0")/.."
export HF_HOME="$PWD/artifacts/hf_cache" HF_HUB_OFFLINE=1 PYTHONPATH=artifacts/fla_pkgs TOKENIZERS_PARALLELISM=false RAYON_NUM_THREADS=2
LOGDIR="${LOGDIR:?LOGDIR requis}"
until grep -q TERMINE11 "$LOGDIR/graines.log" 2>/dev/null; do sleep 15; done
slug="llm-mur-qwen3-5-4b-ep10-lr1e-4"
for a in 1 2 3 4; do
  if ls results/runs | grep -q -- "-$slug.json"; then break; fi
  echo "$(date -u +%FT%TZ) DEBUT $slug essai=$a" >> "$LOGDIR/llm_mur.log"
  timeout 28800 .venv/bin/python scripts/p1_finetune.py Qwen/Qwen3.5-4B --mode lora --lr 1e-4 --epochs 10 --max-len 4096 --micro-batch 1 --effective-batch 32 --limit-seconds 22700 \
    --fiche experiments/2026-10-04-llm-recette-mure-qwen4b.md --slug "$slug" --register > "$LOGDIR/$slug.out" 2>&1
  code=$?; echo "$(date -u +%FT%TZ) FIN $slug code=$code" >> "$LOGDIR/llm_mur.log"
  [ "$code" -eq 0 ] && break
done
echo "$(date -u +%FT%TZ) TERMINE12" >> "$LOGDIR/llm_mur.log"
