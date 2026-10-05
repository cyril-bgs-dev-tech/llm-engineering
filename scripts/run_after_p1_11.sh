#!/usr/bin/env bash
# Après P1-11 (seconde passe terminée) : diagnostic d'époques de CamemBERT-bio, rejeu du 9B à 1e-4 (déterminisme P1-26 et conservation des probabilités
# et de l'adaptateur), exploration Q19 (perte pondérée). Essais multiples en cas de segfault du tokenizer (134, 139). Journal : $LOGDIR/after_p1_11.log
set -u
cd "$(dirname "$0")/.."
export HF_HOME="$PWD/artifacts/hf_cache" HF_HUB_OFFLINE=1 PYTHONPATH=artifacts/fla_pkgs TOKENIZERS_PARALLELISM=false RAYON_NUM_THREADS=2
LOGDIR="${LOGDIR:?LOGDIR requis}"
LOG="$LOGDIR/after_p1_11.log"
until grep -q TERMINE2 "$LOGDIR/p1_11.log" 2>/dev/null; do sleep 20; done
run() {  # slug puis arguments de p1_finetune.py
  local slug="$1"; shift
  if ls results/runs 2>/dev/null | grep -q -- "-$slug.json"; then echo "$(date -u +%FT%TZ) DEJA $slug" >> "$LOG"; return; fi
  for attempt in 1 2 3; do
    echo "$(date -u +%FT%TZ) DEBUT $slug essai=$attempt" >> "$LOG"
    timeout 14400 .venv/bin/python scripts/p1_finetune.py "$@" --slug "$slug" --register > "$LOGDIR/$slug.out" 2>&1
    code=$?
    echo "$(date -u +%FT%TZ) FIN $slug code=$code" >> "$LOG"
    if [ "$code" -ne 134 ] && [ "$code" -ne 139 ]; then return; fi
  done
}
CAM=experiments/2026-10-03-camembert-epoques-diagnostic.md
for ep in 4 6; do
  run "camembert-epoques-lr1e-4-ep$ep" almanach/camembert-bio-base --mode full --lr 1e-4 --max-len 508 --micro-batch 16 --effective-batch 32 --epochs "$ep" --fiche "$CAM"
done
run "p1-26-rejeu-qwen3-5-9b-lr1e-4" Qwen/Qwen3.5-9B --mode lora --lr 1e-4 --max-len 4096 --micro-batch 1 --effective-batch 32 --limit-seconds 7460 --fiche experiments/2026-10-03-p1-11-criblage-eleves.md
run "q19-qwen3-5-9b-lr1e-4-perte-ponderee" Qwen/Qwen3.5-9B --mode lora --lr 1e-4 --max-len 4096 --micro-batch 1 --effective-batch 32 --limit-seconds 5500 --class-weights inv-sqrt --fiche experiments/2026-10-03-q19-perte-ponderee-qwen9b.md
echo "$(date -u +%FT%TZ) TERMINE3" >> "$LOG"
