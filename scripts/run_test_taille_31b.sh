#!/usr/bin/env bash
# Test de taille : Gemma-4-31B en QLoRA NF4, pli 0, 1e-4, 2 époques (fiche 2026-10-04-test-de-taille-gemma-4-31b). Jusqu'à 3 essais sur panne du tokenizer.
set -u
cd "$(dirname "$0")/.."
export HF_HOME="$PWD/artifacts/hf_cache" HF_HUB_OFFLINE=1 PYTHONPATH=artifacts/fla_pkgs TOKENIZERS_PARALLELISM=false RAYON_NUM_THREADS=2
LOGDIR="${LOGDIR:?LOGDIR requis}"
slug="test-taille-gemma-4-31b-qlora-lr1e-4"
for attempt in 1 2 3; do
  echo "$(date -u +%FT%TZ) DEBUT $slug essai=$attempt" >> "$LOGDIR/test_taille.log"
  timeout 36000 .venv/bin/python scripts/p1_finetune.py google/gemma-4-31B-it --mode lora --quant nf4 --lr 1e-4 --max-len 4096 --micro-batch 1 --effective-batch 32 \
    --limit-seconds 21600 --fiche experiments/2026-10-04-test-de-taille-gemma-4-31b.md --slug "$slug" --register > "$LOGDIR/$slug.out" 2>&1
  code=$?
  echo "$(date -u +%FT%TZ) FIN $slug code=$code" >> "$LOGDIR/test_taille.log"
  if [ "$code" -eq 0 ]; then break; fi
done
echo "$(date -u +%FT%TZ) TERMINE8" >> "$LOGDIR/test_taille.log"
