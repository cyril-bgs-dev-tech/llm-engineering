#!/usr/bin/env bash
# Modèles finaux pour le test scellé (fiche 2026-10-05-modeles-finaux). Attend TERMINE31 (fin de la distillation imbriquée : le verdict RM-56 peut ensuite exclure l'élève). run_lot (N25), codes 134 et 139 seuls relancés.
set -u
cd "$(dirname "$0")/.."
export HF_HOME="$PWD/artifacts/hf_cache" HF_HUB_OFFLINE=1 PYTHONPATH=artifacts/fla_pkgs TOKENIZERS_PARALLELISM=false RAYON_NUM_THREADS=2 RETRY_CODES="134 139"
LOGDIR="${LOGDIR:?LOGDIR requis}"
source scripts/lib/lot.sh
until grep -q TERMINE31 "$LOGDIR/distillation_imbriquee.log" 2>/dev/null; do sleep 30; done
FICHE=experiments/2026-10-05-modeles-finaux.md
run_lot "$LOGDIR/modeles_finaux.log" final-tfidf 2 bash -c ".venv/bin/python scripts/final_models.py tfidf --fiche $FICHE --register > \"$LOGDIR/final_tfidf.out\" 2>&1"
for s in 1000 1001 1002 1003 1004; do
  run_lot "$LOGDIR/modeles_finaux.log" final-encoder-s$s 3 bash -c "timeout 3600 .venv/bin/python scripts/final_models.py encoder --seed $s --fiche $FICHE --register > \"$LOGDIR/final_encoder_$s.out\" 2>&1"
done
for s in 1000 1001 1002; do
  run_lot "$LOGDIR/modeles_finaux.log" final-student-s$s 3 bash -c "timeout 3600 .venv/bin/python scripts/final_models.py student --seed $s --fiche $FICHE --register > \"$LOGDIR/final_student_$s.out\" 2>&1"
done
echo "$(date -u +%FT%TZ) TERMINE36" >> "$LOGDIR/modeles_finaux.log"
run_lot "$LOGDIR/modeles_finaux.log" final-lora-s1000 3 bash -c "timeout 25200 .venv/bin/python scripts/final_models.py lora --seed 1000 --fiche $FICHE --register > \"$LOGDIR/final_lora_1000.out\" 2>&1"
echo "$(date -u +%FT%TZ) TERMINE37" >> "$LOGDIR/modeles_finaux.log"
