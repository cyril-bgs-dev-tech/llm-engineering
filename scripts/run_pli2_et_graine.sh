#!/usr/bin/env bash
# Fiche 2026-10-04-confirmation-pli2-et-graine-lora : (a) cinq encodeurs au pli 2, (b) LoRA mûr graine 1001 au pli 0. Code de sortie capturé avant affichage ; essais consignés.
set -u
cd "$(dirname "$0")/.."
export HF_HOME="$PWD/artifacts/hf_cache" HF_HUB_OFFLINE=1 PYTHONPATH=artifacts/fla_pkgs TOKENIZERS_PARALLELISM=false RAYON_NUM_THREADS=2
LOGDIR="${LOGDIR:?LOGDIR requis}"
FICHE=experiments/2026-10-04-confirmation-pli2-et-graine-lora.md
run() {  # slug puis arguments
  local slug="$1"; shift
  for a in 1 2 3 4; do
    if ls results/runs | grep -q -- "-$slug.json"; then return; fi
    timeout 36000 .venv/bin/python scripts/p1_finetune.py "$@" --fiche "$FICHE" --slug "$slug" --register > "$LOGDIR/$slug.out" 2>&1
    code=$?; echo "$(date -u +%FT%TZ) $slug essai=$a code=$code" >> "$LOGDIR/pli2.log"; [ "$code" -eq 0 ] && return
  done
}
for k in 0 1 2 3 4; do
  run "camembert-pli2-ep10-s$k" almanach/camembert-bio-base --mode full --fold 2 --lr 1e-4 --epochs 10 --seed "$((1000 + k))" --max-len 508 --micro-batch 16 --effective-batch 32
done
run "llm-mur-s1001-qwen3-5-4b-ep10-lr1e-4" Qwen/Qwen3.5-4B --mode lora --lr 1e-4 --epochs 10 --seed 1001 --max-len 4096 --micro-batch 1 --effective-batch 32 --limit-seconds 18800
echo "$(date -u +%FT%TZ) TERMINE18" >> "$LOGDIR/pli2.log"
