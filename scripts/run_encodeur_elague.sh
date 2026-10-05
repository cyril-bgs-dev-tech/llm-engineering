#!/usr/bin/env bash
# Encodeur élagué (RM-45, fiche 2026-10-05-encodeur-elague) : 30 runs puis latence. Attend TERMINE31 (fin de la distillation imbriquée). run_lot (N25), codes 134 et 139 seuls relancés.
set -u
cd "$(dirname "$0")/.."
export HF_HOME="$PWD/artifacts/hf_cache" HF_HUB_OFFLINE=1 PYTHONPATH=artifacts/fla_pkgs TOKENIZERS_PARALLELISM=false RAYON_NUM_THREADS=2 RETRY_CODES="134 139"
LOGDIR="${LOGDIR:?LOGDIR requis}"
source scripts/lib/lot.sh
until grep -q TERMINE31 "$LOGDIR/distillation_imbriquee.log" 2>/dev/null; do sleep 30; done
FICHE=experiments/2026-10-05-encodeur-elague.md
ENS="0=ensemble-encodeur5-tfidf-charbal,1=pli1-ensemble-encodeur5-tfidf-charbal,2=pli2-ensemble-encodeur5-tfidf-charbal,3=pli3-ensemble-encodeur5-tfidf-charbal,4=pli4-ensemble-encodeur5-tfidf-charbal"
for arm in plain distill; do
  for fold in 0 1 2 3 4; do
    for k in 0 1 2; do
      slug="prune-$arm-pli$fold-s$k"
      if [ "$arm" = distill ]; then OPT="--teacher '$ENS'"; else OPT=""; fi
      run_lot "$LOGDIR/encodeur_elague.log" "$slug" 3 bash -c "timeout 3600 .venv/bin/python scripts/p1_encoder_pruned.py almanach/camembert-bio-base --lr 1e-4 --every 2 $OPT --fold $fold --epochs 10 --seed $((1000 + k)) --fiche $FICHE --slug $slug --register > $LOGDIR/$slug.out 2>&1"
    done
  done
done
run_lot "$LOGDIR/encodeur_elague.log" latence-encodeur-elague 2 bash -c "timeout 1800 .venv/bin/python scripts/bench_pruned_latency.py --register > $LOGDIR/latence_elague.out 2>&1"
echo "$(date -u +%FT%TZ) TERMINE33" >> "$LOGDIR/encodeur_elague.log"
