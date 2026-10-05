#!/usr/bin/env bash
# P1-11 : six runs séquentiels (fiche experiments/2026-10-03-p1-11-criblage-eleves.md). Journal par run dans $LOGDIR.
# Limites d'arrêt anticipé = 1,5 fois la projection de la fiche (secondes) : 4B 4630, 9B 7460, Gemma 5630.
set -u
cd "$(dirname "$0")/.."
export HF_HOME="$PWD/artifacts/hf_cache" HF_HUB_OFFLINE=1 PYTHONPATH=artifacts/fla_pkgs
LOGDIR="${LOGDIR:-/tmp}"
FICHE=experiments/2026-10-03-p1-11-criblage-eleves.md
run() {  # modèle slug limite lr
  echo "$(date -u +%FT%TZ) DEBUT $2 lr=$4" >> "$LOGDIR/p1_11.log"
  timeout 14400 .venv/bin/python scripts/p1_finetune.py "$1" --mode lora --lr "$4" --max-len 4096 --micro-batch 1 --effective-batch 32 \
    --limit-seconds "$3" --fiche "$FICHE" --slug "$2-lr$4" --register > "$LOGDIR/$2-lr$4.out" 2>&1
  echo "$(date -u +%FT%TZ) FIN $2 lr=$4 code=$?" >> "$LOGDIR/p1_11.log"
}
for lr in 1e-5 1e-4; do
  run Qwen/Qwen3.5-4B p1-11-qwen3-5-4b 4630 "$lr"
  run google/gemma-4-E4B-it p1-11-gemma-4-e4b 5630 "$lr"
  run Qwen/Qwen3.5-9B p1-11-qwen3-5-9b 7460 "$lr"
done
echo "$(date -u +%FT%TZ) TERMINE" >> "$LOGDIR/p1_11.log"
