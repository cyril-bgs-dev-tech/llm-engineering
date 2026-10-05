#!/usr/bin/env bash
# Reprise après P1-12 : relance les runs absents du registre (panique ou segfault du tokenizer Rust, codes 1, 134, 139), jusqu'à 4 essais ; ordre : rejeu P1-26 d'abord.
# grille complète de taux (2e-5, 5e-5), exploration Q19 sur le 4B. Essais multiples sur segfault du tokenizer (134, 139).
set -u
cd "$(dirname "$0")/.."
export HF_HOME="$PWD/artifacts/hf_cache" HF_HUB_OFFLINE=1 PYTHONPATH=artifacts/fla_pkgs TOKENIZERS_PARALLELISM=false RAYON_NUM_THREADS=2
LOGDIR="${LOGDIR:?LOGDIR requis}"
LOG="$LOGDIR/after_p1_12b.log"
until grep -q TERMINE4 "$LOGDIR/after_p1_12.log" 2>/dev/null; do sleep 20; done
run() {
  local slug="$1"; shift
  if ls results/runs 2>/dev/null | grep -q -- "-$slug.json"; then echo "$(date -u +%FT%TZ) DEJA $slug" >> "$LOG"; return; fi
  for attempt in 1 2 3 4; do
    echo "$(date -u +%FT%TZ) DEBUT $slug essai=$attempt" >> "$LOG"
    timeout 14400 .venv/bin/python scripts/p1_finetune.py "$@" --slug "$slug" --register > "$LOGDIR/$slug.out" 2>&1
    code=$?
    echo "$(date -u +%FT%TZ) FIN $slug code=$code" >> "$LOG"
    if [ "$code" -eq 0 ]; then return; fi
  done
}
CAM=experiments/2026-10-03-camembert-epoques-diagnostic.md
GRID=experiments/2026-10-03-p1-13-grille-eleve-qwen4b.md
COMMON=(Qwen/Qwen3.5-4B --mode lora --max-len 4096 --micro-batch 1 --effective-batch 32 --limit-seconds 4650)


run "p1-26-rejeu-qwen3-5-4b-lr1e-4" "${COMMON[@]}" --lr 1e-4 --fiche "$GRID"
run "p1-13-qwen3-5-4b-lr5e-5" "${COMMON[@]}" --lr 5e-5 --fiche "$GRID"
run "p1-13-qwen3-5-4b-lr2e-5" "${COMMON[@]}" --lr 2e-5 --fiche "$GRID"
run "q19-qwen3-5-4b-lr1e-4-perte-ponderee" "${COMMON[@]}" --lr 1e-4 --class-weights inv-sqrt --fiche experiments/2026-10-03-q19-perte-ponderee-qwen4b.md
echo "$(date -u +%FT%TZ) TERMINE5" >> "$LOG"
