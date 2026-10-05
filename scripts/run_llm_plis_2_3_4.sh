#!/usr/bin/env bash
# LoRA mûr aux plis 2, 3 et 4 (RM-28, fiche 2026-10-04-llm-mur-plis-2-3-4). Attend TERMINE19 (fin des encodeurs des plis 3 et 4). Utilise la fonction partagée run_lot (N25).
set -u
cd "$(dirname "$0")/.."
export HF_HOME="$PWD/artifacts/hf_cache" HF_HUB_OFFLINE=1 PYTHONPATH=artifacts/fla_pkgs TOKENIZERS_PARALLELISM=false RAYON_NUM_THREADS=2
LOGDIR="${LOGDIR:?LOGDIR requis}"
source scripts/lib/lot.sh
until grep -q TERMINE19 "$LOGDIR/plis34.log" 2>/dev/null; do sleep 20; done
for fold in 2 3 4; do
  slug="llm-mur-pli$fold-qwen3-5-4b-ep10-lr1e-4"
  run_lot "$LOGDIR/llm_plis234.log" "$slug" 4 bash -c "timeout 36000 .venv/bin/python scripts/p1_finetune.py Qwen/Qwen3.5-4B --mode lora --fold $fold --lr 1e-4 --epochs 10 --max-len 4096 --micro-batch 1 --effective-batch 32 --limit-seconds 18800 --fiche experiments/2026-10-04-llm-mur-plis-2-3-4.md --slug $slug --register > $LOGDIR/$slug.out 2>&1"
done
echo "$(date -u +%FT%TZ) TERMINE20" >> "$LOGDIR/llm_plis234.log"
