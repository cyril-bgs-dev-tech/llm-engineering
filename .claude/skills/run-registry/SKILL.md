---
name: run-registry
description: Enregistre chaque run d'entraînement, d'évaluation ou de banc dans un registre immuable. À utiliser au lancement et à la fin de tout run, pour retrouver la meilleure configuration actuelle, ou avant d'écrire un chiffre dans RESULTATS.md.
---

# Registre des runs

Le **registre** est la seule source de vérité des résultats. Un chiffre qui n'a pas d'identifiant de run n'existe pas.

## Un run = un fichier

`results/<run_id>.json`, avec `run_id = <AAAAMMJJ-HHMMSS>-<slug>`. Écrit une fois, **jamais écrasé ni modifié** : une correction est un nouveau run qui cite l'ancien dans `supersedes`.

Champs obligatoires :
- `run_id`, `experiment` (chemin de la fiche préenregistrée), `supersedes`
- `git_sha` et `git_dirty` (un run sur un arbre modifié non commité est marqué comme tel)
- `config` : la configuration complète résolue (pas seulement le chemin du YAML)
- `data` : jeu, pli, graine, empreintes SHA-256 des fichiers lus
- `env` : versions Python, PyTorch, CUDA, bibliothèques clés, pilote, carte et nombre de GPU, profil `hardware/` utilisé, `local` ou `loué` (avec le coût réel si loué)
- `preflight` : mesures de `vram-preflight`
- `metrics` : par pli et agrégées, avec les prédictions brutes sauvegardées dans `results/preds/<run_id>.parquet` pour permettre les comparaisons appariées
- `cost` : durée, VRAM de pointe, énergie si disponible
- `status` : `ok`, `failed` (avec l'erreur), `aborted` (avec la raison)

Les runs ratés ou interrompus sont enregistrés aussi : ils font partie du coût réel et du récit honnête.

## Usages

- **Meilleure configuration actuelle** : la lire dans le registre, jamais de mémoire.
- **`RESULTATS.md`** est généré ou mis à jour depuis le registre ; chaque chiffre y cite son `run_id`.
- **Le wiki** (`wiki-ingest`, `wiki-update`) cite les runs par leur `run_id` comme source.

**Terminé quand** le fichier JSON du run existe avec tous ses champs, et ses prédictions brutes sont sauvegardées.
