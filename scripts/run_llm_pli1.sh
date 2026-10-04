#!/usr/bin/env bash
# Qwen3.5-4B LoRA à 10 époques au pli 1 (fiche 2026-10-04-llm-mur-pli1). Code de sortie capturé avant affichage ; essais consignés (N25), un arrêt anticipé enregistré n'est pas relancé.
set -u
cd "$(dirname "$0")/.."
export HF_HOME="$PWD/artifacts/hf_cache" HF_HUB_OFFLINE=1 PYTHONPATH=artifacts/fla_pkgs TOKENIZERS_PARALLELISM=false RAYON_NUM_THREADS=2
LOGDIR="${LOGDIR:?LOGDIR requis}"
slug="llm-mur-pli1-qwen3-5-4b-ep10-lr1e-4"
for a in 1 2 3 4; do
  if ls results/runs | grep -q -- "-$slug.json"; then break; fi
  echo "$(date -u +%FT%TZ) DEBUT $slug essai=$a" >> "$LOGDIR/llm_pli1.log"
  timeout 36000 .venv/bin/python scripts/p1_finetune.py Qwen/Qwen3.5-4B --mode lora --fold 1 --lr 1e-4 --epochs 10 --max-len 4096 --micro-batch 1 --effective-batch 32 --limit-seconds 18800 \
    --fiche experiments/2026-10-04-llm-mur-pli1.md --slug "$slug" --register > "$LOGDIR/$slug.out" 2>&1
  code=$?
  echo "$(date -u +%FT%TZ) FIN $slug essai=$a code=$code" >> "$LOGDIR/llm_pli1.log"
  [ "$code" -eq 0 ] && break
done
echo "$(date -u +%FT%TZ) TERMINE16" >> "$LOGDIR/llm_pli1.log"
