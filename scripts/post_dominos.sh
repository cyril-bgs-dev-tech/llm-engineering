#!/usr/bin/env bash
# Après le post-traitement du LoRA à cinq plis (TERMINE25) : aperçu de la règle de sélection du système final (RM-50 brouillon) et cascade validée hors pli (RM-40, fiche cascade-cinq-plis).
# CPU seulement, un thread, priorité basse.
set -u
cd "$(dirname "$0")/.."
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
LOGDIR="${LOGDIR:?LOGDIR requis}"
until grep -q TERMINE25 "$LOGDIR/post_lora.log" 2>/dev/null; do sleep 60; done
P=results/predictions
{
  nice -n 15 .venv/bin/python scripts/final_selection_preview.py --register
  echo "selection code=$?"
  nice -n 15 .venv/bin/python scripts/cascade_cv.py "$P/cinq-plis-ensemble-encodeur5.probs.npz" "$P/cinq-plis-llm-mur.probs.npz" cascade-cinq-plis-encodeur-lora --register
  echo "cascade encodeur code=$?"
  nice -n 15 .venv/bin/python scripts/cascade_cv.py "$P/tfidf-variant-char-balanced.probs.npz" "$P/cinq-plis-llm-mur.probs.npz" cascade-cinq-plis-tfidf-lora --register
  echo "cascade tfidf code=$?"
} > "$LOGDIR/post_dominos.out" 2>&1
echo "$(date -u +%FT%TZ) TERMINE27" >> "$LOGDIR/post_dominos.log"
