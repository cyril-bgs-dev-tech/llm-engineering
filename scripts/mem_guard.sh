#!/usr/bin/env bash
# Garde-fou mémoire pour un calcul CPU lourd lancé à côté d'un lot GPU (plantages de WSL du 05/10/2026).
# Usage : mem_guard.sh PID [SEUIL_MIO=20000] : tue PID (et ses fils) si la mémoire disponible passe sous le seuil, consigne dans results/logs/memoire.log, s'arrête quand PID finit.
# Ne vise jamais qu'un PID donné : le lot GPU et le témoin mem_watch.sh ne sont pas touchés.
set -u
cd "$(dirname "$0")/.."
pid="${1:?PID requis}"
seuil="${2:-20000}"
while kill -0 "$pid" 2>/dev/null; do
  dispo=$(free -m | awk '/^Mem:/{print $7}')
  if [ "$dispo" -lt "$seuil" ]; then
    echo "$(date -u +%FT%TZ) GARDE dispo=${dispo} Mio sous ${seuil} : arrêt de ${pid}" >> results/logs/memoire.log
    pkill -TERM -P "$pid" 2>/dev/null
    kill -TERM "$pid" 2>/dev/null
    sleep 5
    kill -KILL "$pid" 2>/dev/null
    exit 3
  fi
  sleep 2
done
