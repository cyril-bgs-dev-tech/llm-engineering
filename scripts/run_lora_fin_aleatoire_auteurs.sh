#!/usr/bin/env bash
# LoRA à fin de texte aléatoire en plis groupés par auteur (RM-62, fiche 2026-10-17-lora-fin-aleatoire-plis-auteurs) : cinq plis, robustesse sur le pli évalué de chacun, puis analyse.
# Règles d'arrêt N31 de la fiche : (1) après les plis 0 et 1, recette cassée ; (3) deux tampons de santé non sains de suite : pause. Codes 134 et 139 seuls relancés (N25).
# Lancement subordonné à Q26 (voir la fiche). À lancer sous scripts/run_guarded.sh (N27). Variable LOGDIR requise.
set -u
cd "$(dirname "$0")/.."
export HF_HOME="$PWD/artifacts/hf_cache" HF_HUB_OFFLINE=1 PYTHONPATH=artifacts/fla_pkgs TOKENIZERS_PARALLELISM=false RAYON_NUM_THREADS=2 RETRY_CODES="134 139"
LOGDIR="${LOGDIR:?LOGDIR requis}"
LOG="$LOGDIR/lora_fin_aleatoire_auteurs.log"
source scripts/lib/lot.sh
FICHE=experiments/2026-10-17-lora-fin-aleatoire-plis-auteurs.md
for k in 0 1 2 3 4; do
  SLUG=lora-fin-aleatoire-auteur-pli$k
  run_lot "$LOG" "$SLUG" 3 bash -c "timeout 25200 .venv/bin/python scripts/p1_finetune.py Qwen/Qwen3.5-4B --mode lora --lr 1e-4 --fold $k --fold-key control_folds_by_author --epochs 10 --max-len 4096 --seed 1000 --micro-batch 1 --limit-seconds 22700 --tail-aug 0.5 --fiche $FICHE --slug $SLUG --register > \"$LOGDIR/$SLUG.out\" 2>&1" || exit 1
  .venv/bin/python scripts/lora_author_analysis.py --sante "$k" >> "$LOG" 2>&1; rc=$?
  if [ "$rc" = 11 ]; then echo "$(date -u +%FT%TZ) PAUSE N31 (3) : deux tampons de santé non sains de suite, question à Cyril" >> "$LOG"; exit 3; elif [ "$rc" != 0 ]; then echo "$(date -u +%FT%TZ) ERREUR contrôle de santé code=$rc" >> "$LOG"; exit 1; fi
  run_lot "$LOG" "robustesse-lora-diagnostic-fin-retiree-$SLUG" 2 bash -c "timeout 7200 .venv/bin/python scripts/robustness_lora_diag.py --adapter $SLUG --fold $k --fold-key control_folds_by_author --fiche $FICHE --register > \"$LOGDIR/robustesse_$SLUG.out\" 2>&1" || exit 1
  if [ "$k" = 1 ]; then
    .venv/bin/python scripts/lora_author_analysis.py --regle-arret >> "$LOG" 2>&1; rc=$?
    if [ "$rc" = 10 ]; then echo "$(date -u +%FT%TZ) ARRET N31 (1) : recette cassée aux plis 0 et 1, résultat publié comme échec" >> "$LOG"; exit 2; elif [ "$rc" != 0 ]; then echo "$(date -u +%FT%TZ) ERREUR règle d'arrêt code=$rc" >> "$LOG"; exit 1; fi
  fi
done
run_lot "$LOG" lora-fin-aleatoire-plis-auteurs-analyse 2 bash -c ".venv/bin/python scripts/lora_author_analysis.py --register > \"$LOGDIR/lora_author_analysis.out\" 2>&1"
echo "$(date -u +%FT%TZ) TERMINE" >> "$LOG"
