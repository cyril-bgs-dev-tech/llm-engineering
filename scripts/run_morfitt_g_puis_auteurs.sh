#!/usr/bin/env bash
# RM-61 (G gelé sur MorFITT, fiche 2026-10-17-g-gele-morfitt) puis le lot de RM-62 (scripts/run_lora_fin_aleatoire_auteurs.sh), à la suite sur la même carte.
# Lancement autorisé par écrit par Cyril le 17/10/2026 malgré l'instabilité (réponse « vas-y » à Q26) ; chaque run porte le tampon de santé.
# À lancer sous scripts/run_guarded.sh (N27). Variable LOGDIR requise. Code de sortie : celui du lot de RM-62.
set -u
cd "$(dirname "$0")/.."
export HF_HOME="$PWD/artifacts/hf_cache" HF_HUB_OFFLINE=1 PYTHONPATH=artifacts/fla_pkgs TOKENIZERS_PARALLELISM=false RAYON_NUM_THREADS=2 RETRY_CODES="134 139"
LOGDIR="${LOGDIR:?LOGDIR requis}"
LOG="$LOGDIR/morfitt_g.log"
source scripts/lib/lot.sh
run_lot "$LOG" morfitt-g-gele 3 bash -c "timeout 9000 .venv/bin/python scripts/morfitt_g.py --register > \"$LOGDIR/morfitt_g.out\" 2>&1"
echo "$(date -u +%FT%TZ) RM-61 terminé code=$? ; lot de RM-62 ensuite" >> "$LOG"
bash scripts/run_lora_fin_aleatoire_auteurs.sh
