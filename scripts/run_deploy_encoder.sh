#!/usr/bin/env bash
# Candidat de déploiement : CamemBERT-bio 10 époques 1e-4 (recette de la fiche 2026-10-04-encodeur-recette-mure, graine 1000) avec sauvegarde des poids, puis mesure INT8 en CPU.
set -u
cd "$(dirname "$0")/.."
export HF_HOME="$PWD/artifacts/hf_cache" HF_HUB_OFFLINE=1 PYTHONPATH=artifacts/fla_pkgs TOKENIZERS_PARALLELISM=false RAYON_NUM_THREADS=2
LOGDIR="${LOGDIR:?LOGDIR requis}"
slug="camembert-deploy-ep10-lr1e-4"
for a in 1 2 3 4; do
  if ls results/runs | grep -q -- "-$slug.json"; then break; fi
  timeout 3600 .venv/bin/python scripts/p1_finetune.py almanach/camembert-bio-base --mode full --lr 1e-4 --epochs 10 --max-len 508 --micro-batch 16 --effective-batch 32 --save-model \
    --fiche experiments/2026-10-04-encodeur-recette-mure.md --slug "$slug" --register > "$LOGDIR/$slug.out" 2>&1
  code=$?; echo "$(date -u +%FT%TZ) $slug essai=$a code=$code" >> "$LOGDIR/deploy.log"; [ "$code" -eq 0 ] && break
done
.venv/bin/python scripts/quantize_eval_encoder.py "$slug" --threads 8 --n 200 --register > "$LOGDIR/quantize.out" 2>&1
echo "$(date -u +%FT%TZ) TERMINE13 code=$?" >> "$LOGDIR/deploy.log"
