#!/usr/bin/env bash
# Encodeur en plis groupés par auteur (fiche 2026-10-06-encodeur-plis-auteurs) : graine 1000 aux cinq plis, puis règle d'arrêt anticipé écrite dans la fiche, puis graines 1001 et 1002.
# run_lot (N25), codes 134 et 139 seuls relancés. À lancer sous scripts/run_guarded.sh (N27). Variable LOGDIR requise.
set -u
cd "$(dirname "$0")/.."
export HF_HOME="$PWD/artifacts/hf_cache" HF_HUB_OFFLINE=1 PYTHONPATH=artifacts/fla_pkgs TOKENIZERS_PARALLELISM=false RAYON_NUM_THREADS=2 RETRY_CODES="134 139"
LOGDIR="${LOGDIR:?LOGDIR requis}"
LOG="$LOGDIR/encodeur_auteurs.log"
source scripts/lib/lot.sh
FICHE=experiments/2026-10-06-encodeur-plis-auteurs.md
for k in ${SEEDS:-0}; do
  for fold in 0 1 2 3 4; do
    slug="enc-auteur-pli$fold-s$k"
    run_lot "$LOG" "$slug" 3 bash -c "timeout 3600 .venv/bin/python scripts/p1_encoder_v2.py almanach/camembert-bio-base --lr 1e-4 --fold $fold --fold-key control_folds_by_author --epochs 10 --seed $((1000 + k)) --autocast-bf16 --fiche $FICHE --slug $slug --register > \"$LOGDIR/$slug.out\" 2>&1"
  done
done
echo "$(date -u +%FT%TZ) TERMINE (graines : ${SEEDS:-0})" >> "$LOG"
