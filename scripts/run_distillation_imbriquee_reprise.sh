#!/usr/bin/env bash
# Reprise de RM-56 (fiche 2026-10-05-distillation-imbriquee) : le lot principal a perdu cinq TF-IDF imbriqués (échec aléatoire de sklearn, TypeError NoneType), un encodeur de professeur (panique du tokenizer, code 1 non relançable) et, par ricochet, les élèves du pli 0 (professeur absent).
# Phase A (parallèle au lot, fichiers nouveaux uniquement) : TF-IDF manquants (trois à la fois), encodeur manquant, reconstruction des professeurs, élèves du pli 0.
# Phase B (après TERMINE31) : rattrapage de tout élève encore absent du registre, puis analyse. run_lot (N25) avec le code 1 relançable, trois essais.
set -u
cd "$(dirname "$0")/.."
export HF_HOME="$PWD/artifacts/hf_cache" HF_HUB_OFFLINE=1 PYTHONPATH=artifacts/fla_pkgs TOKENIZERS_PARALLELISM=false RAYON_NUM_THREADS=2 RETRY_CODES="1 134 139" OMP_NUM_THREADS=2
LOGDIR="${LOGDIR:?LOGDIR requis}"
LOG="$LOGDIR/distillation_imbriquee_reprise.log"
source scripts/lib/lot.sh
FICHE=experiments/2026-10-05-distillation-imbriquee.md

tfidf_retry() {  # $1 = j (pli prédit), $2 = k (pli exclu)
  local j="$1" k="$2" a code
  for a in 1 2 3; do
    [ -f "results/predictions/nested-tfidf-k$k-j$j.probs.npz" ] && { echo "$(date -u +%FT%TZ) DEJA nested-tfidf-k$k-j$j" >> "$LOG"; return 0; }
    nice -n 10 .venv/bin/python scripts/nested_tfidf.py "$j" "$k" >> "$LOGDIR/nested_tfidf_reprise_k$k-j$j.out" 2>&1
    code=$?
    echo "$(date -u +%FT%TZ) nested-tfidf-k$k-j$j essai=$a code=$code" >> "$LOG"
    [ "$code" -eq 0 ] && return 0
  done
  echo "$(date -u +%FT%TZ) ECHEC nested-tfidf-k$k-j$j après 3 essais" >> "$LOG"
  return 1
}
export -f tfidf_retry; export LOG LOGDIR

# Paires (pli prédit j, pli exclu k) absentes
PAIRS=""
for k in 0 1 2 3 4; do for j in 0 1 2 3 4; do
  [ "$j" = "$k" ] && continue
  [ -f "results/predictions/nested-tfidf-k$k-j$j.probs.npz" ] || PAIRS="$PAIRS $j,$k"
done; done
echo "$(date -u +%FT%TZ) DEBUT reprise, TF-IDF manquants :$PAIRS" >> "$LOG"
printf '%s\n' $PAIRS | xargs -r -P 3 -I{} bash -c 'IFS=, read j k <<< "{}"; tfidf_retry "$j" "$k"'

# Encodeurs manquants (graines 0 et 1)
for k in 0 1 2 3 4; do for j in 0 1 2 3 4; do
  [ "$j" = "$k" ] && continue
  for s in 0 1; do
    slug="nested-enc-k$k-j$j-s$s"
    [ -f "results/predictions/$slug.probs.npz" ] && continue
    run_lot "$LOG" "$slug" 3 bash -c "timeout 3600 .venv/bin/python scripts/p1_encoder_nested.py almanach/camembert-bio-base --lr 1e-4 --fold $j --exclude-fold $k --epochs 10 --seed $((1000 + s)) --fiche $FICHE --slug $slug --register > $LOGDIR/${slug}_reprise.out 2>&1"
  done
done; done

.venv/bin/python scripts/build_nested_teachers.py --seeds 2 >> "$LOG.out" 2>&1
echo "$(date -u +%FT%TZ) professeurs imbriqués reconstruits code=$?" >> "$LOG"

students() {  # $@ = plis à traiter
  for k in "$@"; do
    T=""
    for j in 0 1 2 3 4; do [ "$j" = "$k" ] && continue; T="$T${T:+,}$j=nested-teacher-k$k-j$j"; done
    [ -f "results/predictions/nested-teacher-k$k-j$([ "$k" = 0 ] && echo 1 || echo 0).probs.npz" ] || continue
    for s in 0 1 2; do
      slug="distill-nested-pli$k-s$s"
      run_lot "$LOG" "$slug" 3 bash -c "timeout 3600 .venv/bin/python scripts/p3_distill.py almanach/camembert-bio-base --teacher '$T' --lr 1e-4 --alpha-kd 0.5 --temperature 2 --fold $k --epochs 10 --seed $((1000 + s)) --fiche $FICHE --slug $slug --register > $LOGDIR/${slug}_reprise.out 2>&1"
    done
  done
}
students 0
echo "$(date -u +%FT%TZ) TERMINE40 (phase A : pli 0 repris)" >> "$LOG"

until grep -q TERMINE31 "$LOGDIR/distillation_imbriquee.log" 2>/dev/null; do sleep 30; done
students 0 1 2 3 4
nice -n 15 .venv/bin/python scripts/distill_analysis.py --register > "$LOGDIR/post_distillation_imbriquee_reprise.out" 2>&1
echo "$(date -u +%FT%TZ) TERMINE41 (phase B : rattrapage et analyse)" >> "$LOG"
