#!/usr/bin/env bash
# Service de l'encodeur sur GPU (RM-34), après la mesure du LoRA et le zéro-shot (TERMINE22). run_lot (N25).
set -u
cd "$(dirname "$0")/.."
export HF_HOME="$PWD/artifacts/hf_cache" HF_HUB_OFFLINE=1 PYTHONPATH=artifacts/fla_pkgs TOKENIZERS_PARALLELISM=false RAYON_NUM_THREADS=2
LOGDIR="${LOGDIR:?LOGDIR requis}"
source scripts/lib/lot.sh
until grep -q TERMINE22 "$LOGDIR/ancrage.log" 2>/dev/null; do sleep 30; done
run_lot "$LOGDIR/encodeur_gpu.log" bench-encoder-gpu-camembert-deploy-ep10-lr1e-4 3 bash -c "timeout 1800 .venv/bin/python scripts/bench_encoder_gpu.py camembert-deploy-ep10-lr1e-4 --register > \"$LOGDIR/bench_encoder_gpu.out\" 2>&1"
echo "$(date -u +%FT%TZ) TERMINE23" >> "$LOGDIR/encodeur_gpu.log"
