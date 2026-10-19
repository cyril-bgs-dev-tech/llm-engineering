#!/usr/bin/env bash
# Témoin mémoire (plantages de WSL du 05/10/2026) : une ligne toutes les INTERVALLE secondes dans results/logs/memoire.log.
# Champs : disponible et utilisé (Mio), swap utilisé, pression mémoire PSI (some avg10), mémoire GPU, trois plus gros processus (RSS en Mio),
# et depuis RM-59 : identifiant de démarrage (8 caractères), segfaults du journal du noyau, puissance GPU (W) : un changement de boot ou de segv date un plantage.
# Une ligne ALERTE est ajoutée quand la mémoire disponible passe sous SEUIL_MIO. Ne tue rien. Arrêt : kill du processus.
set -u
cd "$(dirname "$0")/.."
INTERVALLE="${INTERVALLE:-10}"
SEUIL_MIO="${SEUIL_MIO:-8192}"
OUT="${OUT:-results/logs/memoire.log}"
mkdir -p "$(dirname "$OUT")"
while true; do
  read -r dispo utilise swap < <(free -m | awk '/^Mem:/{d=$7;u=$3} /^Swap:/{s=$3} END{print d, u, s}')
  psi=$(awk '/^some/{sub("avg10=","",$2); print $2}' /proc/pressure/memory 2>/dev/null || echo na)
  gpu=$(nvidia-smi --query-gpu=memory.used --format=csv,noheader,nounits 2>/dev/null | head -1 || echo na)
  top=$(ps -eo rss=,comm= --sort=-rss | head -3 | awk '{printf "%s:%d ", $2, $1/1024}')
  boot=$(cut -c1-8 /proc/sys/kernel/random/boot_id 2>/dev/null || echo na)
  segv=$(dmesg 2>/dev/null | grep -c "segfault at")
  pgpu=$(nvidia-smi --query-gpu=power.draw --format=csv,noheader,nounits 2>/dev/null | head -1 | tr -d " ")
  ts=$(date -u +%FT%TZ)
  echo "$ts dispo=${dispo} utilise=${utilise} swap=${swap} psi=${psi} gpu=${gpu:-na} boot=${boot} segv=${segv:-na} pgpu=${pgpu:-na} top=${top}" >> "$OUT"
  if [ "$dispo" -lt "$SEUIL_MIO" ]; then echo "$ts ALERTE dispo=${dispo} Mio sous le seuil ${SEUIL_MIO}" >> "$OUT"; fi
  sleep "$INTERVALLE"
done
