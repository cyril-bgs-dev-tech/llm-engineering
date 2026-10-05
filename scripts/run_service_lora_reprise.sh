#!/usr/bin/env bash
# Reprise de la mesure de service du LoRA fusionné (RM-34) après correction du jeton de remplissage (échec du lot du 05/10 à 03h : lots de plus d'un patient). Attend TERMINE26 (fin de la recette d'encodeur v2). run_lot (N25), codes 134 et 139 seuls relancés.
set -u
cd "$(dirname "$0")/.."
export HF_HOME="$PWD/artifacts/hf_cache" HF_HUB_OFFLINE=1 PYTHONPATH=artifacts/fla_pkgs TOKENIZERS_PARALLELISM=false RAYON_NUM_THREADS=2 RETRY_CODES="134 139"
LOGDIR="${LOGDIR:?LOGDIR requis}"
source scripts/lib/lot.sh
until grep -q TERMINE26 "$LOGDIR/encodeur_v2.log" 2>/dev/null; do sleep 30; done
run_lot "$LOGDIR/service_lora_reprise.log" bench-lora-serving-llm-mur2-qwen3-5-4b-ep10-lr1e-4 2 bash -c "timeout 1800 .venv/bin/python scripts/bench_lora_serving.py Qwen/Qwen3.5-4B llm-mur2-qwen3-5-4b-ep10-lr1e-4 --register > $LOGDIR/bench_lora_reprise.out 2>&1"
echo "$(date -u +%FT%TZ) TERMINE28" >> "$LOGDIR/service_lora_reprise.log"
