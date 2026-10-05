#!/usr/bin/env bash
# Post-traitement du LoRA mûr aux plis 2 à 4 (fiche 2026-10-04-llm-mur-plis-2-3-4) : incertitude et comparaisons appariées pli par pli dès qu'un run est enregistré, puis agrégat à cinq plis.
# CPU seulement, un thread, priorité basse (ne gêne pas la chaîne GPU).
set -u
cd "$(dirname "$0")/.."
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
LOGDIR="${LOGDIR:?LOGDIR requis}"
P=results/predictions
for fold in 2 3 4; do
  slug="llm-mur-pli$fold-qwen3-5-4b-ep10-lr1e-4"
  until [ -f "$P/$slug.probs.npz" ] || grep -q "ECHEC $slug\|ARRET $slug" "$LOGDIR/llm_plis234.log" 2>/dev/null; do sleep 60; done
  [ -f "$P/$slug.probs.npz" ] || { echo "$(date -u +%FT%TZ) pli$fold sans probabilités" >> "$LOGDIR/post_lora.log"; continue; }
  nice -n 15 .venv/bin/python scripts/q5_uncertainty.py "$P/$slug.probs.npz" "$slug" --register > "$LOGDIR/q5_$slug.out" 2>&1
  echo "$(date -u +%FT%TZ) q5 pli$fold code=$?" >> "$LOGDIR/post_lora.log"
  nice -n 15 .venv/bin/python scripts/compare_probs.py "$P/tfidf-variant-char-balanced.probs.npz" "$P/$slug.probs.npz" "pli$fold-llm-mur" --register > "$LOGDIR/cmp_tfidf_pli$fold.out" 2>&1
  echo "$(date -u +%FT%TZ) compare tfidf pli$fold code=$?" >> "$LOGDIR/post_lora.log"
  enc="pli$fold-ensemble-encodeur5"
  nice -n 15 .venv/bin/python scripts/compare_probs.py "$P/$enc.probs.npz" "$P/$slug.probs.npz" "pli$fold-llm-mur-vs-encodeur" --register > "$LOGDIR/cmp_enc_pli$fold.out" 2>&1
  echo "$(date -u +%FT%TZ) compare encodeur pli$fold code=$?" >> "$LOGDIR/post_lora.log"
done
if [ -f "$P/llm-mur-pli4-qwen3-5-4b-ep10-lr1e-4.probs.npz" ] && [ -f "$P/llm-mur-pli3-qwen3-5-4b-ep10-lr1e-4.probs.npz" ] && [ -f "$P/llm-mur-pli2-qwen3-5-4b-ep10-lr1e-4.probs.npz" ]; then
  nice -n 15 .venv/bin/python scripts/build_fold_ensemble.py --pool-files cinq-plis-llm-mur llm-mur2-qwen3-5-4b-ep10-lr1e-4 llm-mur-pli1-qwen3-5-4b-ep10-lr1e-4 llm-mur-pli2-qwen3-5-4b-ep10-lr1e-4 llm-mur-pli3-qwen3-5-4b-ep10-lr1e-4 llm-mur-pli4-qwen3-5-4b-ep10-lr1e-4 >> "$LOGDIR/post_lora.out" 2>&1
  for ref in tfidf-variant-char-balanced cinq-plis-ensemble-encodeur5 cinq-plis-ensemble-encodeur5-tfidf-charbal; do
    nice -n 15 .venv/bin/python scripts/pooled_compare.py "$P/cinq-plis-llm-mur.probs.npz" "$P/$ref.probs.npz" "cinq-plis-llm-mur-moins-$ref" --register >> "$LOGDIR/post_lora.out" 2>&1
  done
  nice -n 15 .venv/bin/python scripts/q5_uncertainty.py "$P/cinq-plis-llm-mur.probs.npz" "cinq-plis-llm-mur" --register >> "$LOGDIR/post_lora.out" 2>&1
  nice -n 15 .venv/bin/python scripts/conformal_by_family.py "llm5=$P/cinq-plis-llm-mur.probs.npz" --register >> "$LOGDIR/post_lora.out" 2>&1
  nice -n 15 .venv/bin/python scripts/abstention_table.py --all --register "llm=$P/cinq-plis-llm-mur.probs.npz" >> "$LOGDIR/post_lora.out" 2>&1
fi
echo "$(date -u +%FT%TZ) TERMINE25" >> "$LOGDIR/post_lora.log"
