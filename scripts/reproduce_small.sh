#!/usr/bin/env bash
# Reconstruction à froid du chiffre clé de la référence (P5-09, `make reproduce-small` en esprit) : clone neuf du dépôt, environnement verrouillé, téléchargement de PARHAF à la révision
# épinglée vérifié contre le manifeste versionné, TF-IDF caractères équilibré sur cinq plis, comparaison avec le run d'origine (macro-F1 0,7202). Aucun modèle ni artefact copié.
# Usage : scripts/reproduce_small.sh DOSSIER   (nom commençant par llmft-cold ou cold ; dans le dossier de session de préférence). Écrit la durée de chaque étape.
set -u
dest="${1:?dossier requis}"
src="$(cd "$(dirname "$0")/.." && pwd)"
case "$(basename "$dest")" in llmft-cold*|cold*) ;; *) echo "dossier refusé : le nom doit commencer par llmft-cold ou cold : $dest" >&2; exit 2;; esac
rm -rf -- "$dest"
t0=$(date +%s)
step() { local name="$1"; shift; local s; s=$(date +%s); "$@" > "$dest.$name.log" 2>&1; local code=$?; echo "$name code=$code $(( $(date +%s) - s )) s"; return $code; }
git clone -q "$src" "$dest" || exit 1
cd "$dest" || exit 1
echo "commit du clone : $(git log -1 --format=%h) ; données brutes présentes avant téléchargement : $(ls data/raw 2>/dev/null | wc -l) (attendu 0)"
step sync uv sync --frozen || exit 1
step telechargement .venv/bin/python data/scripts/download_parhaf.py || exit 1
step cim10 .venv/bin/python data/scripts/download_cim10.py || exit 1
step tfidf .venv/bin/python scripts/tfidf_variants.py char-balanced --register || exit 1
orig=$(python3 - "$src" <<'PY'
import glob, json, sys
d = json.load(open(sorted(glob.glob(sys.argv[1] + "/results/runs/*-tfidf-variant-char-balanced.json"))[0]))
print(d["metrics"]["macro_f1"])
PY
)
new=$(python3 - <<'PY'
import glob, json
d = json.load(open(sorted(glob.glob("results/runs/*-tfidf-variant-char-balanced.json"))[0]))
print(d["metrics"]["macro_f1"])
PY
)
echo "macro-F1 d'origine : $orig ; reconstruite : $new"
python3 -c "import sys; sys.exit(0 if abs($orig - $new) < 1e-9 else 1)" && echo "IDENTIQUE à 1e-9" || echo "DIFFÉRENT"
echo "total $(( $(date +%s) - t0 )) s"
