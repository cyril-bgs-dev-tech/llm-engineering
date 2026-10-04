#!/usr/bin/env bash
# Après les encodeurs des plis 3 et 4 (fiche 2026-10-04-encodeur-plis-3-et-4) : ensembles, comparaisons appariées contre le TF-IDF, règle de puissance v2.
# Calcul CPU seulement, un thread, priorité basse : ne doit pas ralentir le LoRA qui démarre à la même heure (run_llm_plis_2_3_4.sh).
set -u
cd "$(dirname "$0")/.."
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
LOGDIR="${LOGDIR:?LOGDIR requis}"
until grep -q TERMINE19 "$LOGDIR/plis34.log" 2>/dev/null; do sleep 20; done
P=results/predictions
{
  for fold in 3 4; do
    nice -n 15 .venv/bin/python scripts/build_fold_ensemble.py "$fold"
    code=$?; echo "ensemble pli$fold code=$code"
    nice -n 15 .venv/bin/python scripts/compare_probs.py "$P/tfidf-variant-char-balanced.probs.npz" "$P/pli$fold-ensemble-encodeur5.probs.npz" "$P/pli$fold-ensemble-encodeur5-tfidf-charbal.probs.npz" "pli$fold-encodeur-ensembles" --register
    code=$?; echo "compare pli$fold code=$code"
  done
  nice -n 15 .venv/bin/python scripts/v2_power_preview.py --register
  code=$?; echo "v2_power_preview code=$code"
} > "$LOGDIR/post_plis34.out" 2>&1
echo "$(date -u +%FT%TZ) TERMINE21" >> "$LOGDIR/post_plis34.log"
