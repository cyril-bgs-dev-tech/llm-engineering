#!/usr/bin/env bash
# Encodeur par fenêtres (fiche 2026-10-04-encodeur-par-fenetres) : (a) 6 époques 1e-4 ; (b) meilleure recette de la recette mûre. Attend TERMINE9.
set -u
cd "$(dirname "$0")/.."
export HF_HOME="$PWD/artifacts/hf_cache" HF_HUB_OFFLINE=1 PYTHONPATH=artifacts/fla_pkgs TOKENIZERS_PARALLELISM=false RAYON_NUM_THREADS=2
LOGDIR="${LOGDIR:?LOGDIR requis}"
FICHE=experiments/2026-10-04-encodeur-par-fenetres.md
until grep -q TERMINE9 "$LOGDIR/encodeur.log" 2>/dev/null; do sleep 15; done
run() {  # slug lr epochs
  if ls results/runs | grep -q -- "-$1.json"; then echo "DEJA $1" >> "$LOGDIR/fenetres.log"; return; fi
  for a in 1 2 3 4; do
    timeout 5400 .venv/bin/python scripts/p1_finetune.py almanach/camembert-bio-base --mode full --windows --lr "$2" --epochs "$3" --max-len 4096 --micro-batch 2 --effective-batch 32 --limit-seconds 2700 --fiche "$FICHE" --slug "$1" --register > "$LOGDIR/$1.out" 2>&1
    code=$?; echo "$(date -u +%FT%TZ) $1 essai=$a code=$code" >> "$LOGDIR/fenetres.log"; [ "$code" -eq 0 ] && return
  done
}
run camembert-fenetres-lr1e-4-ep6 1e-4 6
# (b) meilleure macro-F1 parmi les trois runs de la recette mûre (égalité : moins d'époques)
best=$(.venv/bin/python - <<'PY'
import glob, json
rows = []
for f in glob.glob("results/runs/*-camembert-recette-*.json"):
    d = json.load(open(f))
    if d["status"] == "ok":
        p = d["params"]
        rows.append((-round(d["metrics"]["macro_f1"], 4), p["epochs"], p["lr"]))
rows.sort()
print(f"{rows[0][2]} {rows[0][1]}" if rows else "1e-4 10")
PY
)
lr=${best% *}; ep=${best#* }
echo "$(date -u +%FT%TZ) recette retenue pour (b) : lr=$lr epochs=$ep" >> "$LOGDIR/fenetres.log"
run "camembert-fenetres-recette-retenue" "$lr" "$ep"
echo "$(date -u +%FT%TZ) TERMINE10" >> "$LOGDIR/fenetres.log"
