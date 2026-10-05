#!/usr/bin/env bash
# P1-11, seconde passe : relance les runs absents du registre (segfault du tokenizer le 03/10/2026), avec le vrai code de sortie et jusqu'à 3 essais
# par run en cas de plantage (codes 134, 139). Attend le mot TERMINE dans le journal de la première passe.
set -u
cd "$(dirname "$0")/.."
export HF_HOME="$PWD/artifacts/hf_cache" HF_HUB_OFFLINE=1 PYTHONPATH=artifacts/fla_pkgs TOKENIZERS_PARALLELISM=false RAYON_NUM_THREADS=2
LOGDIR="${LOGDIR:-/tmp}"
FICHE=experiments/2026-10-03-p1-11-criblage-eleves.md
until grep -q TERMINE "$LOGDIR/p1_11.log" 2>/dev/null; do sleep 20; done
run() {  # modèle slug limite lr
  local slug="$2-lr$4"
  if ls results/runs 2>/dev/null | grep -q -- "-$slug.json"; then echo "$(date -u +%FT%TZ) DEJA $slug" >> "$LOGDIR/p1_11.log"; return; fi
  for attempt in 1 2 3; do
    echo "$(date -u +%FT%TZ) DEBUT2 $slug essai=$attempt" >> "$LOGDIR/p1_11.log"
    timeout 14400 .venv/bin/python scripts/p1_finetune.py "$1" --mode lora --lr "$4" --max-len 4096 --micro-batch 1 --effective-batch 32 \
      --limit-seconds "$3" --fiche "$FICHE" --slug "$slug" --register > "$LOGDIR/$slug.out2" 2>&1
    code=$?
    echo "$(date -u +%FT%TZ) FIN2 $slug code=$code" >> "$LOGDIR/p1_11.log"
    if [ "$code" -ne 134 ] && [ "$code" -ne 139 ]; then return; fi
  done
}
for lr in 1e-5 1e-4; do
  run Qwen/Qwen3.5-4B p1-11-qwen3-5-4b 4630 "$lr"
  run google/gemma-4-E4B-it p1-11-gemma-4-e4b 5630 "$lr"
  run Qwen/Qwen3.5-9B p1-11-qwen3-5-9b 7460 "$lr"
done
echo "$(date -u +%FT%TZ) TERMINE2" >> "$LOGDIR/p1_11.log"
