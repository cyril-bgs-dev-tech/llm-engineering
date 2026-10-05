#!/usr/bin/env bash
# Temps A du test scellé (PROTOCOLE_V2.md section 5) : prédictions de chaque modèle final sur les TEXTES du test, aucune étiquette lue. Attend TERMINE37 (fin des modèles finaux). Une écriture unique par modèle.
# run_lot (N25) ; un modèle déjà écrit n'est jamais remplacé (le script refuse).
set -u
cd "$(dirname "$0")/.."
export HF_HOME="$PWD/artifacts/hf_cache" HF_HUB_OFFLINE=1 PYTHONPATH=artifacts/fla_pkgs TOKENIZERS_PARALLELISM=false RAYON_NUM_THREADS=2 RETRY_CODES="134 139"
LOGDIR="${LOGDIR:?LOGDIR requis}"
source scripts/lib/lot.sh
until grep -q TERMINE37 "$LOGDIR/modeles_finaux.log" 2>/dev/null; do sleep 30; done
for m in tfidf encoder-s1000 encoder-s1001 encoder-s1002 encoder-s1003 encoder-s1004 student-s1000 student-s1001 student-s1002 lora-s1000; do
  run_lot "$LOGDIR/temps_a.log" "temps-a-$m" 2 bash -c "timeout 3600 .venv/bin/python scripts/sealed_evaluation.py inputs $m > $LOGDIR/temps_a_$m.out 2>&1"
done
echo "$(date -u +%FT%TZ) TERMINE38" >> "$LOGDIR/temps_a.log"
