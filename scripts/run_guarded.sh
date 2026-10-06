#!/usr/bin/env bash
# Lance une commande sous garde : priorité basse, arrêt si la RAM disponible passe sous SEUIL_MIO (défaut 20000) ou si la VRAM dépasse PLAFOND_VRAM_MIO (défaut 30000, règle N12) pendant 20 s d'affilée.
# Le PID gardé est celui de la commande elle-même (lancée en fils direct de ce script) : pas de PID de wrapper. Code de sortie : celui de la commande, 3 si le garde l'a arrêtée.
# Usage : run_guarded.sh COMMANDE [ARGS...]   (à détacher par l'appelant : setsid nohup scripts/run_guarded.sh ... > journal 2>&1 &)
set -u
cd "$(dirname "$0")/.."
SEUIL_MIO="${SEUIL_MIO:-20000}"
PLAFOND_VRAM_MIO="${PLAFOND_VRAM_MIO:-30000}"
nice -n "${NICE:-5}" "$@" &
pid=$!
trop=0
while kill -0 "$pid" 2>/dev/null; do
  dispo=$(free -m | awk '/^Mem:/{print $7}')
  vram=$(nvidia-smi --query-gpu=memory.used --format=csv,noheader,nounits 2>/dev/null | head -1)
  vram="${vram:-0}"
  if [ "$dispo" -lt "$SEUIL_MIO" ]; then raison="RAM disponible ${dispo} Mio sous ${SEUIL_MIO}"; elif [ "$vram" -gt "$PLAFOND_VRAM_MIO" ]; then trop=$((trop + 2)); raison="VRAM ${vram} Mio au-dessus de ${PLAFOND_VRAM_MIO}"; else trop=0; raison=""; fi
  if [ -n "$raison" ] && { [ "$dispo" -lt "$SEUIL_MIO" ] || [ "$trop" -ge 20 ]; }; then
    echo "$(date -u +%FT%TZ) GARDE ${raison} : arrêt de ${pid} ($1)" | tee -a "${MEM_LOG:-results/logs/memoire.log}"
    kill -TERM "$pid" 2>/dev/null; sleep 5; kill -KILL "$pid" 2>/dev/null
    wait "$pid" 2>/dev/null
    exit 3
  fi
  sleep 2
done
wait "$pid"
