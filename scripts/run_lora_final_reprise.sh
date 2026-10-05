#!/usr/bin/env bash
# Reprise du LoRA final de G (fiche 2026-10-05-modeles-finaux) : le lot principal a échoué en une minute par une panique aléatoire du tokenizer (code 1, non relancé). Attend TERMINE38 (GPU libre), relance avec le code 1 relançable (trois essais, consignés), puis le temps A du LoRA. Les lots d'élagage et de MorFITT attendent TERMINE42.
set -u
cd "$(dirname "$0")/.."
export HF_HOME="$PWD/artifacts/hf_cache" HF_HUB_OFFLINE=1 PYTHONPATH=artifacts/fla_pkgs TOKENIZERS_PARALLELISM=false RAYON_NUM_THREADS=2 RETRY_CODES="1 134 139"
LOGDIR="${LOGDIR:?LOGDIR requis}"
LOG="$LOGDIR/lora_final_reprise.log"
source scripts/lib/lot.sh
until grep -q TERMINE38 "$LOGDIR/temps_a.log" 2>/dev/null; do sleep 20; done
FICHE=experiments/2026-10-05-modeles-finaux.md
run_lot "$LOG" final-lora-s1000 3 bash -c "timeout 25200 .venv/bin/python scripts/final_models.py lora --seed 1000 --fiche $FICHE --register > $LOGDIR/final_lora_1000_reprise.out 2>&1"
run_lot "$LOG" temps-a-lora-s1000 2 bash -c "timeout 3600 .venv/bin/python scripts/sealed_evaluation.py inputs lora-s1000 > $LOGDIR/temps_a_lora-s1000_reprise.out 2>&1"
echo "$(date -u +%FT%TZ) TERMINE42" >> "$LOG"
