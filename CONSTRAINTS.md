# Constraints

Dernière revue : 02/10/2026, par Claude en autonomie (aucune réponse de Cyril à l'entretien du skill : les défauts du skill s'appliquent, à confirmer). Lire avant d'écrire du code. **Ne pas affaiblir ce fichier pour faire passer un changement** ; un seuil relâché est un événement signalé par `scripts/floor_guard.py`.

## Plancher (toujours appliqué)

- Aucune suppression de contrôle ajoutée : `# noqa`, `# type: ignore`, `# pragma: no cover`, `gitleaks:allow`, `nosemgrep`.
- Aucun travail inachevé : `raise NotImplementedError`, `except ...: pass`, `TODO`, `FIXME`.
- Aucun test sauté, supprimé ou vidé de ses assertions sans raison écrite dans le message de commit.
- Aucun secret dans le code (rapporté par règle et emplacement, jamais par valeur : `--redact`).
- Ce fichier ne se relâche pas pour faire passer un changement.

## Appliqué avec des chiffres

| Dimension | Règle | Vérifié par | S'exécute | Raison du seuil |
|---|---|---|---|---|
| Types | Zéro erreur, mode strict sur `src/` | `.venv/bin/python -m mypy src` | à chaque édition, `make check-fast` | Le code d'évaluation doit être sûr : une erreur de type sur une métrique fausse un résultat publié |
| Lint | Zéro erreur | `.venv/bin/python -m ruff check .` | à chaque édition, `make check-fast` | Règles par défaut de ruff ; les dossiers de skills tiers sont exclus de la configuration |
| Secrets | Zéro secret | gitleaks par Docker : `dir . --config .gitleaks.toml --redact` | à chaque édition et avant tout commit | Un jeton Hugging Face ou GitLab dans le dépôt est irréversible une fois publié |
| Plancher | Zéro violation dans le diff | `.venv/bin/python scripts/floor_guard.py` | à chaque édition, `make check-fast` | Détecte les voies faciles vers le vert (suppression, stub, test affaibli, seuil relâché) |
| Tests | Tous verts, y compris les cas de fuite piégés | `.venv/bin/python -m pytest` | fin de tâche, `make check` | Un test de fuite qui ne peut pas échouer ne prouve rien |
| Couverture | Lignes modifiées de `src/` couvertes à 80 % ou plus | `scripts/check_changed_coverage.py` (rapport de `pytest --cov`) | fin de tâche, `make check` | Assez haut pour exiger un test, assez bas pour une ligne de configuration ; sans commit, toutes les lignes comptent |
| Backlog | `check_microtasks` et `check_roadmap` verts | `python3 scripts/check_microtasks.py`, `python3 scripts/check_roadmap.py` | fin de tâche, `make check` | L'ordre et les preuves du plan sont vérifiés mécaniquement |
| Wiki | Aucun lien cassé, frontmatter complet, aucune collision de slug | `.venv/bin/python scripts/check_wiki.py` | fin de tâche, `make check` | Un lien inventé est l'échec que la discipline du wiki existe pour éviter |
| Citations du wiki | Toute citation littérale retrouvée mot pour mot dans les lignes citées du fichier brut | `.venv/bin/python scripts/check_wiki_quotes.py` | fin de tâche, `make check` | Une citation approximative est pire que pas de citation (règle du wiki) |
| Scorecards | Aucune note sans preuve, empreinte d'artefact exacte | `.venv/bin/python scripts/check_scorecards.py` | fin de tâche, `make check` | Une note sans preuve est une affirmation ; le vérificateur ne prouve pas la note, seulement la preuve |
| Dépendances | Aucune vulnérabilité connue, hors exception W1 | `.venv/bin/python -m pip_audit --ignore-vuln PYSEC-2026-3447` | `make check-full`, avant tout partage | **Contrainte externe** : lit une base de vulnérabilités que le projet ne contrôle pas |

Budget de temps : `make check-fast` doit rester sous 90 secondes (mesuré à l'écriture : voir « Mesuré »). Limite connue de l'audit : torch, dont la version locale `+cu128` n'existe pas sur PyPI, n'est pas auditable par pip-audit. Les contrôles de performance de page et d'accessibilité sont **écartés** : le projet n'a ni page web ni URL à interroger.

## Mesuré, pas encore appliqué (cliquet)

| Mesure | Aujourd'hui | Direction |
|---|---|---|
| Couverture de `src/llmft` | 97 % (567 instructions, 19 non couvertes) le 02/10/2026 | ne doit pas baisser de plus de 0.5 point |
| Durée de `make check-fast` | à mesurer à la première exécution complète | ne doit pas croître |

## Exceptions

| ID | Règle | Chemin | Raison | Responsable | Expire |
|---|---|---|---|---|---|
| W1 | Dépendances sans vulnérabilité connue | `PYSEC-2026-3447` (setuptools 81.0.0) | torch 2.11.0+cu128, la pile validée par les spikes P0-04, P0-05 et P0-13, exige setuptools inférieur à 82 ; la faille (CVE-2026-59890) ne touche que la fabrication d'archives sources sur macOS avec des noms de fichiers Unicode, hors de notre usage (Linux, aucune archive publiée). Rétrograder torch à 2.10 invaliderait les preuves | Claude, à confirmer par Cyril | 2026-12-31 |
