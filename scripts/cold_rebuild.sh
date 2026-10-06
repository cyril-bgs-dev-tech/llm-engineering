#!/usr/bin/env bash
# Reconstruction à froid (audit GLM C6-A1) : clone neuf du dépôt, environnement verrouillé, contrôles et fil synthétique.
# Usage : scripts/cold_rebuild.sh [dossier]   ; écrit la durée de chaque étape. Ne copie aucune donnée brute (non suivie).
set -u
dest="${1:-/tmp/llmft-cold}"
src="$(cd "$(dirname "$0")/.." && pwd)"
case "$(basename "$dest")" in llmft-cold*|cold*) ;; *) echo "dossier refusé : le nom doit commencer par llmft-cold ou cold (garde contre rm -rf sur un chemin imprévu) : $dest" >&2; exit 2;; esac
rm -rf -- "$dest"
t0=$(date +%s)
step() { local name="$1"; shift; local s; s=$(date +%s); "$@" > "$dest.$name.log" 2>&1; local code=$?; echo "$name code=$code $(( $(date +%s) - s )) s"; return $code; }
git clone -q "$src" "$dest" || exit 1
cd "$dest" || exit 1
echo "données brutes présentes dans le clone : $(ls data/raw 2>/dev/null | wc -l) (attendu 0)"
step sync uv sync --frozen || exit 1
step test .venv/bin/python -m pytest -q -x --ignore=tests/gpu -m "not gpu" || true
step smoke .venv/bin/python scripts/smoke.py || true
echo "total $(( $(date +%s) - t0 )) s"
