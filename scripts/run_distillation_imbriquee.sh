#!/usr/bin/env bash
# Distillation à professeur imbriqué (RM-56, fiche 2026-10-05-distillation-imbriquee). Attend TERMINE29 (fin des reprises de service). run_lot (N25), codes 134 et 139 seuls relancés.
set -u
cd "$(dirname "$0")/.."
export HF_HOME="$PWD/artifacts/hf_cache" HF_HUB_OFFLINE=1 PYTHONPATH=artifacts/fla_pkgs TOKENIZERS_PARALLELISM=false RAYON_NUM_THREADS=2 RETRY_CODES="134 139" OMP_NUM_THREADS=2
LOGDIR="${LOGDIR:?LOGDIR requis}"
source scripts/lib/lot.sh
until grep -q TERMINE29 "$LOGDIR/encodeur_gpu_reprise.log" 2>/dev/null; do sleep 30; done
FICHE=experiments/2026-10-05-distillation-imbriquee.md
for k in 0 1 2 3 4; do
  for j in 0 1 2 3 4; do
    [ "$j" = "$k" ] && continue
    for s in 0 1; do
      slug="nested-enc-k$k-j$j-s$s"
      run_lot "$LOGDIR/distillation_imbriquee.log" "$slug" 3 bash -c "timeout 3600 .venv/bin/python scripts/p1_encoder_nested.py almanach/camembert-bio-base --lr 1e-4 --fold $j --exclude-fold $k --epochs 10 --seed $((1000 + s)) --fiche $FICHE --slug $slug --register > $LOGDIR/$slug.out 2>&1"
    done
    if ! ls results/predictions | grep -q "^nested-tfidf-k$k-j$j.probs.npz$"; then
      nice -n 10 .venv/bin/python scripts/nested_tfidf.py "$j" "$k" >> "$LOGDIR/distillation_imbriquee.out" 2>&1
      echo "$(date -u +%FT%TZ) nested-tfidf-k$k-j$j code=$?" >> "$LOGDIR/distillation_imbriquee.log"
    fi
  done
done
.venv/bin/python scripts/build_nested_teachers.py --seeds 2 >> "$LOGDIR/distillation_imbriquee.out" 2>&1
echo "$(date -u +%FT%TZ) professeurs imbriqués code=$?" >> "$LOGDIR/distillation_imbriquee.log"
for k in 0 1 2 3 4; do
  T=""
  for j in 0 1 2 3 4; do [ "$j" = "$k" ] && continue; T="$T${T:+,}$j=nested-teacher-k$k-j$j"; done
  for s in 0 1 2; do
    slug="distill-nested-pli$k-s$s"
    run_lot "$LOGDIR/distillation_imbriquee.log" "$slug" 3 bash -c "timeout 3600 .venv/bin/python scripts/p3_distill.py almanach/camembert-bio-base --teacher '$T' --lr 1e-4 --alpha-kd 0.5 --temperature 2 --fold $k --epochs 10 --seed $((1000 + s)) --fiche $FICHE --slug $slug --register > $LOGDIR/$slug.out 2>&1"
  done
done
nice -n 15 .venv/bin/python scripts/distill_analysis.py --register > "$LOGDIR/post_distillation_imbriquee.out" 2>&1
echo "$(date -u +%FT%TZ) TERMINE31" >> "$LOGDIR/distillation_imbriquee.log"
