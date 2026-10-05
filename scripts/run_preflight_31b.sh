#!/usr/bin/env bash
# Pré-vol du Gemma-4-31B en QLoRA NF4 (3 pas, exemples les plus longs d'abord), après la fin de la reprise P1-12b. Essais multiples sur panne du tokenizer.
set -u
cd "$(dirname "$0")/.."
export HF_HOME="$PWD/artifacts/hf_cache" HF_HUB_OFFLINE=1 PYTHONPATH=artifacts/fla_pkgs TOKENIZERS_PARALLELISM=false RAYON_NUM_THREADS=2
LOGDIR="${LOGDIR:?LOGDIR requis}"
until grep -q TERMINE5 "$LOGDIR/after_p1_12b.log" 2>/dev/null; do sleep 20; done
for attempt in 1 2 3; do
  timeout 3600 .venv/bin/python scripts/p1_finetune.py google/gemma-4-31B-it --mode lora --quant nf4 --lr 1e-4 --max-len 4096 --micro-batch 1 --effective-batch 32 \
    --max-steps 3 --order longest --slug preflight-gemma-4-31b-qlora-4096 --register > "$LOGDIR/preflight-31b.out" 2>&1
  code=$?
  echo "$(date -u +%FT%TZ) PREFLIGHT31B essai=$attempt code=$code" >> "$LOGDIR/preflight31b.log"
  if [ "$code" -eq 0 ]; then break; fi
done
echo "$(date -u +%FT%TZ) TERMINE7" >> "$LOGDIR/preflight31b.log"
