#!/usr/bin/env bash
# Plis 3 et 4 de l'encodeur (fiche 2026-10-04-encodeur-plis-3-et-4). Attend TERMINE18 (fin du LoRA graine 1001). Code de sortie capturé avant affichage ; essais consignés.
set -u
cd "$(dirname "$0")/.."
export HF_HOME="$PWD/artifacts/hf_cache" HF_HUB_OFFLINE=1 PYTHONPATH=artifacts/fla_pkgs TOKENIZERS_PARALLELISM=false RAYON_NUM_THREADS=2
LOGDIR="${LOGDIR:?LOGDIR requis}"
until grep -q TERMINE18 "$LOGDIR/pli2.log" 2>/dev/null; do sleep 20; done
for fold in 3 4; do
  for k in 0 1 2 3 4; do
    slug="camembert-pli$fold-ep10-s$k"
    for a in 1 2 3 4; do
      if ls results/runs | grep -q -- "-$slug.json"; then break; fi
      timeout 3600 .venv/bin/python scripts/p1_finetune.py almanach/camembert-bio-base --mode full --fold "$fold" --lr 1e-4 --epochs 10 --seed "$((1000 + k))" --max-len 508 --micro-batch 16 --effective-batch 32 \
        --fiche experiments/2026-10-04-encodeur-plis-3-et-4.md --slug "$slug" --register > "$LOGDIR/$slug.out" 2>&1
      code=$?; echo "$(date -u +%FT%TZ) $slug essai=$a code=$code" >> "$LOGDIR/plis34.log"; [ "$code" -eq 0 ] && break
    done
  done
done
echo "$(date -u +%FT%TZ) TERMINE19" >> "$LOGDIR/plis34.log"
