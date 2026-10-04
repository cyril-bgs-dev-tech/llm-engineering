#!/usr/bin/env bash
# Témoin d'activité (tasks/SURVEILLEUR_SILENCE.md) : écrit dans results/logs/silence.log chaque minute où le silence dépasse 300 s.
# Activité = dernière modification du journal de nuit, du dernier commit, du dernier run enregistré ou d'un journal de lot (LOGDIR). Arrêt : kill du processus.
set -u
cd "$(dirname "$0")/.."
LOGDIR="${LOGDIR:-}"
mkdir -p results/logs
while true; do
  now=$(date +%s)
  last=$(stat -c %Y tasks/JOURNAL_NUIT_2026-10-02.md 2>/dev/null || echo 0)
  for f in .git/logs/HEAD $(ls -t results/runs/*.json 2>/dev/null | head -1) $( [ -n "$LOGDIR" ] && ls -t "$LOGDIR"/*.log 2>/dev/null | head -3 ); do
    t=$(stat -c %Y "$f" 2>/dev/null || echo 0); [ "$t" -gt "$last" ] && last=$t
  done
  idle=$(( now - last ))
  if [ "$idle" -gt 300 ]; then echo "$(date -u +%FT%TZ) silence=${idle}s" >> results/logs/silence.log; fi
  sleep 60
done
