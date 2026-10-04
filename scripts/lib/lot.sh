#!/usr/bin/env bash
# Lancement partagé des runs de lot (règle N25) : code de sortie capturé AVANT tout affichage, essais plafonnés et consignés, run déjà au registre sauté.
# Usage : source scripts/lib/lot.sh ; run_lot JOURNAL SLUG ESSAIS_MAX COMMANDE...   (variables : RUNS_DIR, RETRY_CODES="1 134 139")
# Code de retour : 0 si le run a abouti ou était déjà au registre, sinon le dernier code de sortie (le lot décide de la suite).
run_lot() {
  local log="$1" slug="$2" max="$3"; shift 3
  local runs_dir="${RUNS_DIR:-results/runs}" retry="${RETRY_CODES:-1 134 139}" attempt code=0
  for attempt in $(seq 1 "$max"); do
    if ls "$runs_dir" 2>/dev/null | grep -q -- "-$slug.json"; then echo "$(date -u +%FT%TZ) DEJA $slug" >> "$log"; return 0; fi
    echo "$(date -u +%FT%TZ) DEBUT $slug essai=$attempt" >> "$log"
    "$@"
    code=$?
    echo "$(date -u +%FT%TZ) FIN $slug essai=$attempt code=$code" >> "$log"
    if [ "$code" -eq 0 ]; then return 0; fi
    case " $retry " in *" $code "*) ;; *) echo "$(date -u +%FT%TZ) ARRET $slug code=$code non relançable" >> "$log"; return "$code";; esac
  done
  echo "$(date -u +%FT%TZ) ECHEC $slug après $max essais, dernier code=$code (défaut à corriger, pas une panne aléatoire)" >> "$log"
  return "$code"
}
