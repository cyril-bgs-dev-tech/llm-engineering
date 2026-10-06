#!/usr/bin/env bash
# LoRA avec fin de texte aléatoirement coupée (fiche 2026-10-07-lora-fin-aleatoire) : entraînement au pli 0 puis robustesse en inférence. run_lot (N25), codes 134 et 139 seuls relancés.
# À lancer sous scripts/run_guarded.sh (N27). Variable LOGDIR requise.
set -u
cd "$(dirname "$0")/.."
export HF_HOME="$PWD/artifacts/hf_cache" HF_HUB_OFFLINE=1 PYTHONPATH=artifacts/fla_pkgs TOKENIZERS_PARALLELISM=false RAYON_NUM_THREADS=2 RETRY_CODES="134 139"
LOGDIR="${LOGDIR:?LOGDIR requis}"
LOG="$LOGDIR/lora_fin_aleatoire.log"
source scripts/lib/lot.sh
FICHE=experiments/2026-10-07-lora-fin-aleatoire.md
SLUG=lora-fin-aleatoire-pli0
run_lot "$LOG" "$SLUG" 3 bash -c "timeout 25200 .venv/bin/python scripts/p1_finetune.py Qwen/Qwen3.5-4B --mode lora --lr 1e-4 --fold 0 --epochs 10 --max-len 4096 --seed 1000 --micro-batch 1 --limit-seconds 22700 --tail-aug 0.5 --fiche $FICHE --slug $SLUG --register > \"$LOGDIR/$SLUG.out\" 2>&1" && \
run_lot "$LOG" "robustesse-lora-diagnostic-fin-retiree-$SLUG" 2 bash -c "timeout 7200 .venv/bin/python scripts/robustness_lora_diag.py --adapter $SLUG --register > \"$LOGDIR/robustesse_$SLUG.out\" 2>&1"
echo "$(date -u +%FT%TZ) TERMINE" >> "$LOG"
