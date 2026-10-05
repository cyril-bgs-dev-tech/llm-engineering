#!/usr/bin/env bash
# Saturation et graines de l'encodeur (fiche 2026-10-04-encodeur-saturation-et-graines). Attend TERMINE10 (encodeur par fenêtres).
set -u
cd "$(dirname "$0")/.."
export HF_HOME="$PWD/artifacts/hf_cache" HF_HUB_OFFLINE=1 PYTHONPATH=artifacts/fla_pkgs TOKENIZERS_PARALLELISM=false RAYON_NUM_THREADS=2
LOGDIR="${LOGDIR:?LOGDIR requis}"
FICHE=experiments/2026-10-04-encodeur-saturation-et-graines.md
until grep -q TERMINE10 "$LOGDIR/fenetres.log" 2>/dev/null; do sleep 15; done
run() {  # slug epochs seed
  if ls results/runs | grep -q -- "-$1.json"; then echo "DEJA $1" >> "$LOGDIR/graines.log"; return; fi
  for a in 1 2 3 4; do
    timeout 3600 .venv/bin/python scripts/p1_finetune.py almanach/camembert-bio-base --mode full --lr 1e-4 --epochs "$2" --seed "$3" --max-len 508 --micro-batch 16 --effective-batch 32 --fiche "$FICHE" --slug "$1" --register > "$LOGDIR/$1.out" 2>&1
    code=$?; echo "$(date -u +%FT%TZ) $1 essai=$a code=$code" >> "$LOGDIR/graines.log"; [ "$code" -eq 0 ] && return
  done
}
run camembert-saturation-ep15 15 1000
run camembert-saturation-ep20 20 1000
best=$(.venv/bin/python - <<'PY'
import glob, json
rows = []
for f in glob.glob("results/runs/*-camembert-saturation-ep*.json") + glob.glob("results/runs/*-camembert-recette-lr1e-4-ep10.json"):
    d = json.load(open(f))
    if d["status"] == "ok":
        rows.append((-round(d["metrics"]["macro_f1"], 4), d["params"]["epochs"]))
rows.sort()
print(rows[0][1] if rows else 10)
PY
)
echo "$(date -u +%FT%TZ) recette retenue pour les graines : epochs=$best" >> "$LOGDIR/graines.log"
for k in 1 2 3 4; do run "camembert-graine-ep$best-s$k" "$best" "$((1000 + k))"; done
echo "$(date -u +%FT%TZ) TERMINE11" >> "$LOGDIR/graines.log"
