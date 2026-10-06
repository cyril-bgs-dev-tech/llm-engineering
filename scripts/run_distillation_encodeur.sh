#!/usr/bin/env bash
# Distillation vers l'encodeur (RM-32, fiche 2026-10-04-distillation-vers-encodeur). Attend TERMINE23 (fin du service de l'encodeur) ; exige les cinq plis du LoRA. run_lot (N25) : seuls les codes 134 et 139 (tokenizer) sont relancés.
set -u
cd "$(dirname "$0")/.."
export HF_HOME="$PWD/artifacts/hf_cache" HF_HUB_OFFLINE=1 PYTHONPATH=artifacts/fla_pkgs TOKENIZERS_PARALLELISM=false RAYON_NUM_THREADS=2 RETRY_CODES="134 139"
LOGDIR="${LOGDIR:?LOGDIR requis}"
source scripts/lib/lot.sh
until grep -q TERMINE23 "$LOGDIR/encodeur_gpu.log" 2>/dev/null; do sleep 30; done
FICHE=experiments/2026-10-04-distillation-vers-encodeur.md
LORA="0=llm-mur2-qwen3-5-4b-ep10-lr1e-4,1=llm-mur-pli1-qwen3-5-4b-ep10-lr1e-4,2=llm-mur-pli2-qwen3-5-4b-ep10-lr1e-4,3=llm-mur-pli3-qwen3-5-4b-ep10-lr1e-4,4=llm-mur-pli4-qwen3-5-4b-ep10-lr1e-4"
ENS="0=ensemble-encodeur5-tfidf-charbal,1=pli1-ensemble-encodeur5-tfidf-charbal,2=pli2-ensemble-encodeur5-tfidf-charbal,3=pli3-ensemble-encodeur5-tfidf-charbal,4=pli4-ensemble-encodeur5-tfidf-charbal"
for arm in lora ens; do
  if [ "$arm" = lora ]; then T="$LORA"; else T="$ENS"; fi
  for fold in 0 1 2 3 4; do
    for k in 0 1 2; do
      slug="distill-$arm-pli$fold-s$k"
      run_lot "$LOGDIR/distillation.log" "$slug" 3 bash -c "timeout 3600 .venv/bin/python scripts/p3_distill.py almanach/camembert-bio-base --teacher '$T' --lr 1e-4 --alpha-kd 0.5 --temperature 2 --fold $fold --epochs 10 --seed $((1000 + k)) --fiche $FICHE --slug $slug --register > \"$LOGDIR/$slug.out\" 2>&1"
    done
  done
done
echo "$(date -u +%FT%TZ) TERMINE24" >> "$LOGDIR/distillation.log"
