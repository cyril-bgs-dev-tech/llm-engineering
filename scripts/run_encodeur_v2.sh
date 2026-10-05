#!/usr/bin/env bash
# Recette d'encodeur v2 (fiche 2026-10-05-encodeur-recette-v2) : quatre facteurs, cinq plis, trois graines. Attend TERMINE24 (fin de la distillation). run_lot (N25), codes 134 et 139 seuls relancés.
set -u
cd "$(dirname "$0")/.."
export HF_HOME="$PWD/artifacts/hf_cache" HF_HUB_OFFLINE=1 PYTHONPATH=artifacts/fla_pkgs TOKENIZERS_PARALLELISM=false RAYON_NUM_THREADS=2 RETRY_CODES="134 139"
LOGDIR="${LOGDIR:?LOGDIR requis}"
source scripts/lib/lot.sh
until grep -q TERMINE24 "$LOGDIR/distillation.log" 2>/dev/null; do sleep 30; done
FICHE=experiments/2026-10-05-encodeur-recette-v2.md
for factor in bf16 ls01 ema99 curr2; do
  case "$factor" in
    bf16) OPT="--autocast-bf16";;
    ls01) OPT="--label-smoothing 0.1";;
    ema99) OPT="--ema 0.99";;
    curr2) OPT="--curriculum-epochs 2";;
  esac
  for fold in 0 1 2 3 4; do
    for k in 0 1 2; do
      slug="enc2-$factor-pli$fold-s$k"
      run_lot "$LOGDIR/encodeur_v2.log" "$slug" 3 bash -c "timeout 3600 .venv/bin/python scripts/p1_encoder_v2.py almanach/camembert-bio-base --lr 1e-4 --fold $fold --epochs 10 --seed $((1000 + k)) $OPT --fiche $FICHE --slug $slug --register > $LOGDIR/$slug.out 2>&1"
    done
  done
done
echo "$(date -u +%FT%TZ) TERMINE26" >> "$LOGDIR/encodeur_v2.log"
