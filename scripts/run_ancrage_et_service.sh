#!/usr/bin/env bash
# Mesure de service du LoRA, puis zéro-shot du 4B et du 9B (fiche 2026-10-04-ancrage-zero-shot-et-service-lora). Attend TERMINE20 (fin du LoRA des plis 2 à 4). Utilise run_lot (N25).
set -u
cd "$(dirname "$0")/.."
export HF_HOME="$PWD/artifacts/hf_cache" HF_HUB_OFFLINE=1 PYTHONPATH=artifacts/fla_pkgs TOKENIZERS_PARALLELISM=false RAYON_NUM_THREADS=2
LOGDIR="${LOGDIR:?LOGDIR requis}"
source scripts/lib/lot.sh
until grep -q TERMINE20 "$LOGDIR/llm_plis234.log" 2>/dev/null; do sleep 30; done
FICHE=experiments/2026-10-04-ancrage-zero-shot-et-service-lora.md
run_lot "$LOGDIR/ancrage.log" bench-lora-serving-llm-mur2-qwen3-5-4b-ep10-lr1e-4 3 bash -c "timeout 1800 .venv/bin/python scripts/bench_lora_serving.py Qwen/Qwen3.5-4B llm-mur2-qwen3-5-4b-ep10-lr1e-4 --register > $LOGDIR/bench_lora.out 2>&1"
for m in 4B 9B; do
  slug="zero-shot-qwen3-5-$(echo $m | tr 'B' 'b')-pli0"
  run_lot "$LOGDIR/ancrage.log" "$slug" 3 bash -c "timeout 3600 .venv/bin/python scripts/zero_shot.py Qwen/Qwen3.5-$m --slug $slug --fold 0 --fiche $FICHE --register > $LOGDIR/$slug.out 2>&1"
done
echo "$(date -u +%FT%TZ) TERMINE22" >> "$LOGDIR/ancrage.log"
