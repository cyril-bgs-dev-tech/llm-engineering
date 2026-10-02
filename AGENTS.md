# LLM_finetuning

Affiner et distiller des LLM sur des textes cliniques français, sur une RTX 5090 (location de GPU en option, section 5.2 du plan), pour mesurer ce que chaque technique apporte vraiment. Cible : poste « Ingénieur.e Data Science » du CHU Grenoble Alpes (projet PARTAGES). **La spécification est `PLAN_PROJET_V6.md`** ; V1 à V5 sont l'historique, jamais la référence.

## Avant d'agir

- **Suis `roadmap_unifié.md` : c'est le guide d'exécution** (ordre, portes d'arrêt, skills à charger à chaque étape ; `tasks/todo.md` en est généré). Lis `PLAN_PROJET_V6.md` (sections 0 à 6 et 8), `MICROTACHES.md` (le backlog, identifiants stables) et, dès qu'ils existent, `PROTOCOLE.md` et `CONSTRAINTS.md`. Les outils, dépôts et papiers retenus, avec leur statut de vérification, sont dans `BOITE_A_OUTILS.md`.
- Lis `CONSTRAINTS.md` avant d'écrire du code et ne l'affaiblis jamais pour faire passer un changement : `make check-fast` après chaque édition, `make check` en fin de tâche, `make check-full` avant tout partage.
- Les décisions de la section 10 du plan appartiennent à Cyril : tant qu'une décision est ouverte, propose et attends sa réponse.

## Cycle d'une expérience

`experiment-preregistration` → `dataset-intake` (si nouveau jeu) → `vram-preflight` → code via `lora-classifier-recipe` ou `distillation-pipeline`, en `test-driven-development` → `leakage-guard` → run → `run-registry` → `paired-comparison` → `wiki-ingest` ou `wiki-update` → `model-card-calibration` pour un candidat final → `claim-gate` avant toute sortie du dépôt.

Pour le génie logiciel (spec, découpage, revue, simplification, Git, CI), suis `using-agent-skills`. Les relecteurs `code-reviewer`, `test-engineer` et `security-auditor` sont dans `.codex/agents/`.

## Règles fermes

- **Données** : uniquement publiques, synthétiques ou générées, entrées par `dataset-intake`. Aucune donnée de patient réel, même « pour tester ».
- **Cibles** : chaque tâche est un contrat `task_specs/<task_id>.yaml` (catégories fermées, nommées et définies, format de sortie fixe) ; le code lit le contrat et ne contient rien de propre à une tâche.
- **Qualité** : douze catégories (Q1 à Q12, section 2 du plan). Chaque porte de phase se clôt par une scorecard : une note de 0 à 3 par catégorie, une preuve citée par note, un plan de rattrapage sous le plancher. Une note ne se pose jamais sans preuve.
- **Backlog** : on ne renumérote jamais `MICROTACHES.md` ; après toute modification, `python3 scripts/check_microtasks.py` et `python3 scripts/check_roadmap.py` doivent rester verts.
- **Résultats** : un chiffre sans `run_id` n'existe pas ; `RESULTATS.md` contient les résultats négatifs au même titre que les positifs.
- **Git** : commit, push, création de dépôt distant et changement de visibilité se font sur demande explicite de Cyril.
- **GPU** : un processus que tu n'as pas lancé (Ollama, autre entraînement) se signale à Cyril ; il reste en place.
- **Matériel** : la RTX 5090 est la cible des tests et de la démo ; tout ce qui dépend de la carte passe par un profil de `hardware/`, jamais par le code. Une location de GPU ne se lance que sur un déclencheur de la section 5.2 du plan, avec une fiche préenregistrée et un plafond de dépense validé par Cyril ; idem pour une API payante.
- **Langue** : documentation et wiki en français ; identifiants de code en anglais. Textes de candidature : prose sans tiret cadratin.

## Repères que l'environnement ne dit pas

- Matériel : RTX 5090 (32 Go, Blackwell sm_120), 68 Go de RAM visibles dans WSL (mesuré le 01/10/2026, RM-06 ; l'hôte peut en avoir plus), 32 threads, `/mnt/d` environ 30 fois plus lent que le disque ext4 de WSL (33 Go libres seulement) : voir la page wiki `env-blackwell`. Le support sm_120 de chaque bibliothèque se vérifie avant usage (`vram-preflight`).
- Cyril n'avait encore jamais affiné de LLM avant ce projet : c'est le trou que le projet comble, d'où `claim-gate`.
- Wiki du projet : `knowledge/` (`SCHEMA.md`, liens en style markdown). Le savoir durable (sources, méthodes, décisions, analyses) y va ; le README garde l'installation et les commandes.
- Skills tiers : provenance et exclusions dans `.claude/SKILLS_PROVENANCE.txt`. Leurs hooks n'ont pas été installés. Le mode `wiki-audit strong` et la revue croisée de `doubt-driven-development` envoient du contenu à Codex ou Gemini : demander à Cyril à chaque fois.
