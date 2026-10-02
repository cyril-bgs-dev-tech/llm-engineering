# Commandes canoniques

Statut : **existe** (fonctionne aujourd'hui), **cible** (à implémenter par la micro-tâche indiquée). Tant que P0-11 n'a pas verrouillé les dépendances, on utilise `.venv/bin/python` ; ensuite `uv run` devient la forme canonique, sans changer le sens des commandes.

La sortie des scripts est forcée en UTF-8 : sous Windows, définir `PYTHONUTF8=1` si besoin.

| Intention | Commande | Statut |
|---|---|---|
| Environnement figé | `uv sync --frozen` | cible (P0-11) |
| Tests | `.venv/bin/python -m pytest` | existe |
| Lint | `.venv/bin/python -m ruff check .` | existe |
| Types | `.venv/bin/python -m mypy src` | existe |
| Contrôle du backlog | `python3 scripts/check_microtasks.py` | existe |
| Contrôle de la feuille de route | `python3 scripts/check_roadmap.py` | existe |
| Régénérer `tasks/` | `python3 scripts/check_roadmap.py --export` | existe |
| Valider un contrat de tâche | `uv run python -m llmft validate-task --spec task_specs/<id>.yaml` | cible (P0-35) |
| Fil synthétique complet (rapport dans `results/smoke_report.md`) | `make smoke` | existe (RM-09) |
| Variantes GPU des tests | `make test-gpu` | existe |
| Chaîne courte sur une tâche (contrat, chargeur, découpage, 10 pas, métriques, registre) | `pipeline.run_chain(spec, adapter, backend="cpu" ou "gpu", steps=10, runs_dir=...)` | existe (P0-44), pas encore de commande en ligne |
| Évaluation finale sur le test scellé | `uv run python -m llmft evaluate --run-id <id> --sealed-test` | cible (RM-20), réservée au script autorisé |
| Contrôle rapide à chaque édition (types, lint, plancher, secrets) | `make check-fast` | existe (CONSTRAINTS.md) |
| Contrôle de fin de tâche (plus tests, couverture des lignes modifiées, backlog, feuille de route, wiki) | `make check` | existe |
| Contrôle avant partage (plus audit des dépendances) | `make check-full` | existe |
| Intégration continue (GitHub Actions) : `make check`, `make smoke`, `pip-audit` sur chaque push et pull request ; release sur tag `vX.Y.Z` | `.github/workflows/` | existe (ADR-008) ; ne couvre ni le GPU ni les tests qui lisent les données |
| Reproduction à froid | `make reproduce-small` | cible (P5-09) |

Les noms exacts des sous-commandes `llmft` sont à approuver à l'écriture de l'interface (P0-35).
