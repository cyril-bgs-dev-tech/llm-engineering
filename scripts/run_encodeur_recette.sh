#!/usr/bin/env bash
# Recette mûre de l'encodeur (fiche 2026-10-04-encodeur-recette-mure) : trois runs courts, essais multiples sur panne du tokenizer.
set -u
cd "$(dirname "$0")/.."
export HF_HOME="$PWD/artifacts/hf_cache" HF_HUB_OFFLINE=1 PYTHONPATH=artifacts/fla_pkgs TOKENIZERS_PARALLELISM=false RAYON_NUM_THREADS=2
LOGDIR="${LOGDIR:?LOGDIR requis}"
FICHE=experiments/2026-10-04-encodeur-recette-mure.md
run() {  # slug lr epochs
  if ls results/runs | grep -q -- "-$1.json"; then echo "DEJA $1" >> "$LOGDIR/encodeur.log"; return; fi
  for a in 1 2 3 4; do
    timeout 3600 .venv/bin/python scripts/p1_finetune.py almanach/camembert-bio-base --mode full --lr "$2" --epochs "$3" --max-len 508 --micro-batch 16 --effective-batch 32 --fiche "$FICHE" --slug "$1" --register > "$LOGDIR/$1.out" 2>&1
    code=$?; echo "$(date -u +%FT%TZ) $1 essai=$a code=$code" >> "$LOGDIR/encodeur.log"; [ "$code" -eq 0 ] && return
  done
}
run camembert-recette-lr1e-4-ep10 1e-4 10
run camembert-recette-lr2e-4-ep6 2e-4 6
run camembert-recette-lr2e-4-ep10 2e-4 10
echo "$(date -u +%FT%TZ) TERMINE9" >> "$LOGDIR/encodeur.log"
