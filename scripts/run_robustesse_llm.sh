#!/usr/bin/env bash
# Robustesse du LoRA mûr (pli 0) par inférence sur adaptateur sauvegardé ; essais consignés, code de sortie capturé avant affichage.
set -u
cd "$(dirname "$0")/.."
export HF_HOME="$PWD/artifacts/hf_cache" HF_HUB_OFFLINE=1 PYTHONPATH=artifacts/fla_pkgs TOKENIZERS_PARALLELISM=false RAYON_NUM_THREADS=2
LOGDIR="${LOGDIR:?LOGDIR requis}"
for a in 1 2 3; do
  timeout 3600 .venv/bin/python scripts/robustness_llm.py Qwen/Qwen3.5-4B llm-mur2-qwen3-5-4b-ep10-lr1e-4 --fold 0 --register > "$LOGDIR/robustesse_llm.out" 2>&1
  code=$?; echo "$(date -u +%FT%TZ) robustesse essai=$a code=$code" >> "$LOGDIR/robustesse.log"; [ "$code" -eq 0 ] && break
done
echo "$(date -u +%FT%TZ) TERMINE17" >> "$LOGDIR/robustesse.log"
