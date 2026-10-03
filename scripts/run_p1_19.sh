#!/usr/bin/env bash
# P1-19 : quatre graines supplémentaires (1001 à 1004) du Qwen3.5-4B à 1e-4 ; la graine 1000 est le run P1-11 existant (s_0). Attend TERMINE5 de la reprise.
# Essais multiples en cas de panne du tokenizer Rust (tout code non nul), jusqu'à 4.
set -u
cd "$(dirname "$0")/.."
export HF_HOME="$PWD/artifacts/hf_cache" HF_HUB_OFFLINE=1 PYTHONPATH=artifacts/fla_pkgs TOKENIZERS_PARALLELISM=false RAYON_NUM_THREADS=2
LOGDIR="${LOGDIR:?LOGDIR requis}"
LOG="$LOGDIR/p1_19.log"
until grep -q TERMINE5 "$LOGDIR/after_p1_12b.log" 2>/dev/null; do sleep 20; done
FICHE=experiments/2026-10-03-p1-19-cinq-graines-qwen4b.md
for k in 1 2 3 4; do
  slug="p1-19-s$k"
  if ls results/runs 2>/dev/null | grep -q -- "-$slug.json"; then echo "$(date -u +%FT%TZ) DEJA $slug" >> "$LOG"; continue; fi
  for attempt in 1 2 3 4; do
    echo "$(date -u +%FT%TZ) DEBUT $slug essai=$attempt" >> "$LOG"
    timeout 14400 .venv/bin/python scripts/p1_finetune.py Qwen/Qwen3.5-4B --mode lora --lr 1e-4 --max-len 4096 --micro-batch 1 --effective-batch 32 \
      --limit-seconds 4650 --seed "$((1000 + k))" --fiche "$FICHE" --slug "$slug" --register > "$LOGDIR/$slug.out" 2>&1
    code=$?
    echo "$(date -u +%FT%TZ) FIN $slug code=$code" >> "$LOG"
    if [ "$code" -eq 0 ]; then break; fi
  done
done
echo "$(date -u +%FT%TZ) TERMINE6" >> "$LOG"
