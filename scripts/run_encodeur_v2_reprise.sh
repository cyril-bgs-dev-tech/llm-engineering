#!/usr/bin/env bash
# Reprise du run manquant de la recette d'encodeur v2 (enc2-curr2-pli3-s0 : panique du tokenizer, code 1, non relancé car RETRY_CODES ne contenait pas 1) puis nouvelle analyse. Attend TERMINE33 (GPU libre).
# run_lot (N25) avec le code 1 relançable (cap de trois essais, consignés).
set -u
cd "$(dirname "$0")/.."
export HF_HOME="$PWD/artifacts/hf_cache" HF_HUB_OFFLINE=1 PYTHONPATH=artifacts/fla_pkgs TOKENIZERS_PARALLELISM=false RAYON_NUM_THREADS=2 RETRY_CODES="1 134 139"
LOGDIR="${LOGDIR:?LOGDIR requis}"
source scripts/lib/lot.sh
until grep -q TERMINE33 "$LOGDIR/encodeur_elague.log" 2>/dev/null; do sleep 30; done
FICHE=experiments/2026-10-05-encodeur-recette-v2.md
slug=enc2-curr2-pli3-s0
run_lot "$LOGDIR/encodeur_v2_reprise.log" "$slug" 3 bash -c "timeout 3600 .venv/bin/python scripts/p1_encoder_v2.py almanach/camembert-bio-base --lr 1e-4 --fold 3 --epochs 10 --seed 1000 --curriculum-epochs 2 --fiche $FICHE --slug $slug --register > $LOGDIR/$slug.out 2>&1"
OMP_NUM_THREADS=1 nice -n 15 .venv/bin/python scripts/enc2_analysis.py --register > "$LOGDIR/post_enc2_reprise.out" 2>&1
echo "$(date -u +%FT%TZ) TERMINE39" >> "$LOGDIR/encodeur_v2_reprise.log"
