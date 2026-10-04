# Commandes canoniques (voir docs/COMMANDES.md). Les chemins supposent l'environnement `.venv` de uv.
PY := .venv/bin/python
GITLEAKS := docker run --rm -v "$(CURDIR):/repo:ro" zricethezav/gitleaks:latest dir /repo --config /repo/.gitleaks.toml --redact --no-banner

.PHONY: check-fast check check-full test test-gpu smoke

check-fast:        ## types, lint, plancher, secrets : à chaque édition
	$(PY) -m ruff check .
	$(PY) -m mypy src
	$(PY) scripts/floor_guard.py
	$(GITLEAKS)

test:
	$(PY) -m pytest -q -p no:cacheprovider -m "not gpu" --cov=src/llmft --cov-report=json:artifacts/coverage.json --cov-report=term:skip-covered

check: check-fast test  ## fin de tâche : plus tests, couverture des lignes modifiées, backlog, feuille de route, wiki
	$(PY) scripts/check_changed_coverage.py
	python3 scripts/check_microtasks.py
	python3 scripts/check_roadmap.py
	$(PY) scripts/check_wiki.py
	$(PY) scripts/check_rules_sync.py
	$(PY) scripts/check_wiki_quotes.py
	$(PY) scripts/check_scorecards.py
	$(PY) scripts/check_frozen.py
	$(PY) scripts/budget_alert.py
	$(PY) scripts/check_claims.py

test-gpu:          ## variantes GPU des tests (RTX 5090)
	$(PY) -m pytest -q -p no:cacheprovider -m gpu

smoke:             ## fil synthétique de bout en bout (RM-09)
	$(PY) scripts/smoke.py

check-full: check test-gpu smoke  ## avant tout partage : plus tests GPU, fil complet, audit des dépendances
	$(PY) -m pip_audit --progress-spinner off --ignore-vuln PYSEC-2026-3447  # exception W1 de CONSTRAINTS.md
