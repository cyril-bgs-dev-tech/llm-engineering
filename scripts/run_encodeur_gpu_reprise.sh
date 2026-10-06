#!/usr/bin/env bash
# Reprise de la mesure de service de l'encodeur sur GPU avec énergie sur 15 secondes de charge (la première mesure durait moins d'une seconde : énergie non fiable). Attend TERMINE28.
set -u
cd "$(dirname "$0")/.."
export HF_HOME="$PWD/artifacts/hf_cache" HF_HUB_OFFLINE=1 PYTHONPATH=artifacts/fla_pkgs TOKENIZERS_PARALLELISM=false RAYON_NUM_THREADS=2 RETRY_CODES="134 139"
LOGDIR="${LOGDIR:?LOGDIR requis}"
source scripts/lib/lot.sh
until grep -q TERMINE28 "$LOGDIR/service_lora_reprise.log" 2>/dev/null; do sleep 30; done
run_lot "$LOGDIR/encodeur_gpu_reprise.log" bench-encoder-gpu-camembert-deploy-ep10-lr1e-4-energie15s 2 bash -c "timeout 1800 .venv/bin/python scripts/bench_encoder_gpu.py camembert-deploy-ep10-lr1e-4 --tag -energie15s --register > \"$LOGDIR/bench_encoder_gpu_reprise.out\" 2>&1"
echo "$(date -u +%FT%TZ) TERMINE29" >> "$LOGDIR/encodeur_gpu_reprise.log"
