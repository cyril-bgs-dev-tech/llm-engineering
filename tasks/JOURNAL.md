# Journal de travail

Format : le plus récent en haut. Une entrée par tâche ou par événement, avec la preuve. Voir `CONTRAT_DE_TRAVAIL.md` § 2 et § 10.

## 02/10/2026 : Qwen3.8-27B mesuré (P0-06 et P0-08), Gemma-4-31B en préparation

**Qwen3.8-27B, QLoRA NF4, un seul chargement** (runs `p0-06-qwen3-8-27b-compat` et `p0-08-qwen3-8-27b-qlora-bench`) :
- Voie A : `Qwen3_5ForSequenceClassification` (prédiction juste). Chargement 301 s ; VRAM après chargement 14,3 Gio ; RAM de l'hôte au pic 49,8 Gio.
- Compat, 10 micro-pas de 4 × 1 024 tokens : 7,5 s par micro-pas (546 tokens/s), pic alloué 21,94 Gio.
- **Banc P0-08, 10 pas d'optimiseur, batch effectif 64 : 112 s par pas (585 tokens/s), pic alloué 22,45 Gio, réservé 23,54 Gio, sous les 30 Gio visés.** Pertes finies.
- 1 × 4 096 tokens (longueur du protocole) : 11,4 s, pic 21,97 Gio.
- Les quatre prédictions étaient justes. Les poids ont été supprimés ensuite (51,8 Gio, retéléchargeables en 7 min) pour respecter la règle d'un seul professeur de plus de 50 Gio à la fois.
- **À noter pour P0-45 et RM-16 (non encore une durée annoncée)** : le débit mesuré est de l'ordre de 550 à 600 tokens/s pour ce professeur. Le budget d'un passage sur un pli dépendra de la longueur moyenne d'un patient en tokens (mesure P0-21) ; le calcul est à faire dans P0-45 avec les deux mesures, et sera mis au registre.
- Hypothèse non prouvée sur le crash de WSL : le run de Gemma-4-E4B sans checkpointing a saturé la VRAM (32 Go sur 32 Go) pendant des minutes au moment du crash. Le plafond dur de 30 Gio l'empêche désormais ; la corrélation n'est pas une preuve.

**Gemma-4-31B, prédictions écrites avant le run** (le plus gros professeur candidat, 58 Gio, base de P0-08) :
- Voie B (pas de classe de classification pour `Gemma4Config`, comme le E4B) : probabilité 0,8.
- Pic de VRAM du banc à 1 024 tokens sous 30 Gio : 0,5 (modèle plus gros, vocabulaire de 262 144, tête dernière-couche en plus). Si ce n'est pas le cas, plan B de P0-08 : professeur plus petit ou déclencheur de location, à présenter à Cyril.
- 1 × 4 096 tokens sous 30 Gio : 0,4.

## 02/10/2026 : push GitHub privé et CI (demande explicite de Cyril)

- **Contexte retrouvé** (un niveau au-dessus du projet, sur autorisation de Cyril, GitHub seulement) : compte `cyril-bgs-dev-tech` ; convention existante vitrine publique + dépôt de code privé (`multi-agent-lab` et `multi-agent-lab-code`).
- **Avant l'envoi** : 275 fichiers, aucun de plus de 1 Mo ; gitleaks sur l'arbre et sur tout l'historique (11 commits) : aucun secret ; aucun motif de jeton ; 300 extraits du corpus cherchés dans les fichiers suivis : un seul fichier en contient (`knowledge/raw/parhaf-readme-*.md`, la carte officielle du jeu, CC BY 4.0), restreint au dépôt privé.
- **Fait** : 12 commits atomiques (identité locale au dépôt, adresse noreply GitHub), dépôt **privé** `cyril-bgs-dev-tech/llm-finetuning-code` créé et vérifié `PRIVATE` côté GitHub, `main` poussé.
- **CI** (GitHub Actions, actions épinglées par SHA) : `make check`, `make smoke`, `pip-audit`, audit hebdomadaire, release sur tag `v*`, Dependabot limité aux actions. Premier run **rouge** (20 × EXE001, incohérence de droits entre drvfs et Git, invisible en local) ; reproduit sur un clone neuf ext4, corrigé sans toucher à ruff ; run suivant **vert en 169 s**.
- **Limites dites** : la CI ne couvre ni le GPU ni les 6 tests qui lisent les données ; la protection de branche exige GitHub Pro pour un dépôt privé (403) et n'est pas activée ; `actionlint` non installé, la syntaxe a été validée par le run réel.
- **Écart à signaler** : « local-données » (ADR-004) interdisait qu'un artefact dérivé quitte la machine ; pousser vers un dépôt privé le contredit pour les découpages, empreintes et statistiques. Tracé dans ADR-008 comme décision de Cyril, à confirmer.
- **Vitrine publique** : non créée, en attente de Q9.

## 02/10/2026 : P0-06 et P0-08, gros professeur Qwen3.8-27B (prédictions avant le run)

**Élèves validés (P0-06)** : Qwen3.5-4B et 9B en voie A (`Qwen3_5ForSequenceClassification`), Gemma-4-E4B en voie B (aucune classe de classification pour `Gemma4Config`). Runs `p0-06-*-compat` au registre. Trois prédictions écrites avant, trois confirmées. **Cause de l'OOM de Gemma prouvée** : le gradient checkpointing n'était pas activé en voie B (le `if hasattr` sautait sans bruit) ; la part de `logits_to_keep` dans le gain n'est pas isolée, les deux corrections ont été appliquées ensemble.

**Téléchargement** : Qwen3.8-27B, 51 Gio, 437 s (environ 100 Mo/s), vers `artifacts/hf_cache`. Disque `/mnt/d` : environ 92 Go libres ensuite : un seul gros professeur à la fois (ADR-001).

**Spike** `scripts/spikes/p0_06_08_teacher.py` (QLoRA NF4, un seul chargement) : étape 1 compat (10 micro-pas, 1 024 tokens), étape 2 banc P0-08 (10 pas d'optimiseur, 16 micro-lots de 4, batch effectif 64), étape 3 un lot de 1 × 4 096 tokens. Plafond dur de 30 Gio de VRAM ; JSON partiel après chaque étape.

**Prédictions écrites avant le run :**
- Voie A réussit comme pour le 4B et le 9B, même architecture `Qwen3_5` (probabilité 0,8).
- Pic de VRAM à l'étape 2 sous 30 Gio (0,7) ; un lot de 1 × 4 096 tokens sous 30 Gio (0,7).
- RAM de l'hôte au pic sous 60 Go pendant le chargement (0,7).
- Hypothèse de durée, non annoncée comme fait : l'étape 2 prend plusieurs dizaines de minutes ; la mesure remplace cette hypothèse (RM-16).

## 02/10/2026 : P0-06, résultats partiels et incident Gemma-4-E4B

- **Qwen3.5-4B : prédiction confirmée.** Voie A, classe `Qwen3_5ForSequenceClassification`, pad écrit dans `text_config`, 10 pas finis et finis en valeurs, pic alloué 11,87 Gio (réservé 12,42), 1,79 s par pas médian (`artifacts/spikes/p0_06/Qwen_Qwen3.5-4B.json`). Les pertes tombent vers 0 car le banc réentraîne un lot synthétique fixe : ce n'est pas un résultat d'apprentissage.
- **Gemma-4-E4B : incident.** Le run est resté 26 minutes à 32 Go sur 32 Go de VRAM (100 % d'utilisation) sans finir 10 pas : pré-vol violé (limite 30 Go). Cause probable : la voie B calculait les logits sur tout le vocabulaire (262 144) à chaque token. J'ai **arrêté mes propres processus** (pids 6542 et 6751 ; aucun processus étranger touché), puis corrigé le spike : `logits_to_keep=1` et plafond dur de 30 Gio (`set_per_process_memory_fraction`), `timeout` de 20 minutes par modèle. Cause à confirmer par le résultat de la relance, elle n'est pas encore prouvée.
- Relance : `artifacts/spikes/run_p0_06b.sh` (Gemma-4-E4B puis Qwen3.5-9B).
- Mesure réseau faite à la demande de Cyril (non enregistrée au registre) : 20 à 21 ms vers l'extérieur, environ 59 Mo/s, DNS de WSL2 à environ 40 ms par résolution.

## 02/10/2026 : P0-06 repris (compatibilité de classification des élèves)

**Constat** : P0-06 était en cours au moment du crash. Le résultat de Qwen3.5-4B (échec « no padding token ») est **périmé** : le script `scripts/spikes/p0_06_compat.py` a été corrigé à 00:56 (pad écrit aussi dans `text_config`), après ce run (00:55). Le run de Gemma-4-E4B a été tué par le crash (JSON vide). Qwen3.5-9B n'a jamais tourné. Anciens fichiers conservés en `*.perime*`.

**Prédictions écrites avant le relancement** (voir `vram-preflight` et `experiment-preregistration`) :
- Qwen3.5-4B : voie A (classe `Qwen3_5ForSequenceClassification`) réussit avec le correctif du pad, 10 pas finis, pic bien sous 30 Go (probabilité 0,8).
- Gemma-4-E4B : pas de classe de classification pour `Gemma4ForConditionalGeneration` ; repli voie B, ou échec (probabilité 0,6 de repli).
- Qwen3.5-9B : voie A comme le 4B ; pic sous 30 Go en bf16 avec LoRA (probabilité 0,6, c'est le plus incertain).
- Ollama occupe 1,4 Go : compté, non touché.

## 02/10/2026 : RM-09 clos (fil synthétique rejoué sur environnement propre)

**Défaut trouvé par `make smoke` en place** : deux runs enregistrés dans la même seconde recevaient le même `run_id` généré, et le registre immuable refusait le second (`FileExistsError`). Le rapport d'hier n'avait passé que par chance de timing.
- Test d'abord (rouge), puis correctif dans `src/llmft/mini_registry.py` : un identifiant **généré** déjà pris reçoit un suffixe `-2`, `-3` ; un identifiant **fourni** déjà pris reste une erreur. Aucun run n'est jamais écrasé.
- Preuve : `make check` vert (162 tests), `make smoke` vert en place (9,7 s).

**Environnement propre** : copie du dépôt sans `.venv`, caches, `.git`, `data/raw`, `artifacts` ; `uv sync --frozen` en 40 s ; `scripts/smoke.py` vert (contrat invalide rejeté, rejeu identique, deux fuites piégées détectées) ; 156 tests passés, 6 ignorés (ils ont besoin de `data/raw`, absent de la copie). Sortie archivée : `results/measures/smoke_clean_env.txt` ; run `rm-09-smoke-clean-env` au registre.

**Limite** : la copie vient du dossier de travail, pas d'un clone Git (aucun commit n'existe encore). La reconstruction depuis un clone est P5-09.

**Prochain pas** : R3 est close. R4 : P0-06 (compatibilité de classification des modèles, `vram-preflight` d'abord), RM-13, P0-08, P0-45.

## 02/10/2026 : point de vérification après le crash de WSL

**Constat (mesuré à la reprise)**
- Machine : RTX 5090 visible, 1 386 Mo de VRAM occupés par `ollama serve` (pid 204, lancé au démarrage de WSL, pas par moi : signalé, laissé en place, question Q8) ; RAM 68 Go dont 65 libres ; ext4 677 Go libres, `/mnt/d` 161 Go libres.
- Dépôt : `git init` fait (01:01), **aucun commit**, tout est non suivi. Aucun fichier tronqué trouvé : le dernier écrit, `results/measures/task_addition_cost.json`, est un JSON valide.
- Progression : 43 tâches cochées sur 165 (R0 à R3 sauf P0-02, RM-03, RM-04, RM-09). `check_microtasks.py` et `check_roadmap.py` verts (159 micro-tâches, 92 ★).
- `make check-fast` : ruff, mypy, floor-guard et gitleaks verts (aucun secret).
- `make check` : **1 test rouge sur 159**, `test_no_other_module_reads_the_sealed_partition`. Cause : `scripts/smoke.py` (RM-09, écrit juste avant le crash) lisait `leaked.test[0]` pour piéger une fuite sur la tâche jouet. Le garde-fou du test scellé avait raison.

**Correction (sans affaiblir le garde-fou)**
- Test d'abord (rouge) : `tests/test_splits.py::test_plant_leak_returns_a_copy_with_one_patient_in_test_and_fold_0`.
- `splits.plant_leak(s)` ajoutée dans `src/llmft/splits.py` (module autorisé à fabriquer les partitions) ; `scripts/smoke.py` l'appelle au lieu de lire `.test`. La liste d'autorisation du test n'est pas modifiée.

**Documents créés**
- `tasks/CONTRAT_DE_TRAVAIL.md` (en attente de validation, § 11), `tasks/QUESTIONS_POUR_CYRIL.md` (Q1 à Q8).

**Prochain pas** : relancer `make check` jusqu'au vert, puis RM-09 (rejouer `make smoke` sur environnement propre), puis R4 dans l'ordre.
