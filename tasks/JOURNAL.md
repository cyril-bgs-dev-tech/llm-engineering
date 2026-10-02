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

## 02/10/2026 : rapport de fin de session (R4 close, G-P0 en attente de Cyril)

**Coché avec preuve (48 tâches sur 165)**
- R4 : P0-06 (5 registres `p0-06-*-compat`), P0-08 (`p0-08-*-qlora-bench`), P0-45 (`p0-45-budget-hypotheses`), RM-13 (ADR-009). Synthèse : page wiki `compatibilite-modeles-p0-06`.
- Dépôt privé GitHub + CI verte (ADR-008), run 169 s ; `make check` vert à la fin (165 tests).
- Test `test_adding_a_task_of_the_same_family…` : écrit désormais sa mesure dans `tmp_path`, plus dans le fichier suivi `results/measures/task_addition_cost.json` (qui n'est plus modifié à chaque exécution). Changement non commité.

**Prouvé / non prouvé**
- Prouvé : chargement, passage avant-arrière et mémoire des 5 modèles sur la RTX 5090 ; le plus gros professeur tient sous 30 Gio (pic réservé 26,41 Gio).
- Non prouvé : qualité de classification de tout modèle ; padding à longueurs variables ; MedGemma ; effet isolé de `logits_to_keep=1` ; budget total (hypothèses à recaler par RM-16).

**Portes**
- G-P0 : bloquée par Q5 (B, N, K, δ). P0-46 (gel de `PROTOCOLE.md`), RM-11 (ADR-007) et tout run comparatif attendent.
- R0 : P0-02 (Q4), RM-04 (Q3) ; RM-03 : commit initial fait sur demande explicite, case à cocher à la validation de Cyril.

**Questions, par priorité** : Q5, Q3, Q1, Q4, Q6, Q7, Q8 (défauts dans `QUESTIONS_POUR_CYRIL.md`).

**Ressources** : Ollama (pid 204, ~1,4 Go VRAM) laissé en place ; aucun processus à moi sur le GPU. Disque : `artifacts/hf_cache` pèse 102 Go sur `/mnt/d` (85 Go libres), dont les poids Gemma-4-31B (~58 Go) ; aucune location, aucune API payante.

**Ce que je ne fais pas sans toi** : fixer B/N/K/δ, geler le protocole, lancer un run comparatif, créer la vitrine publique, écrire aux auteurs de PARHAF, accepter les conditions de MedGemma.

## 02/10/2026 : brouillon de la section 6 de PROTOCOLE.md (P0-46, non gelé)

- Ajouté : métriques (macro-F1 sur 17 classes, `AUTRE` hors moyenne mais dans les prédictions), renvoi à ADR-007 pour les tests et le verdict, tableau des seuils, graines (`s_k = 1000 + k`, graine défaillante non remplacée), niveau conforme 90 % proposé, étiquettes REP/ADAPT/EXPLORE, séparation développement/confirmation, procédure de relecture adversariale, règles de gel.
- **Trois marques `[À FIXER Q5]` restent** (δ, K, niveau conforme) ; B et N ne sont pas dans cette section (budget, section 5). Le gel est interdit tant qu'une marque subsiste. Rien n'est figé, aucune empreinte posée, `experiments/INDEX.md` inchangé.
- Point de vigilance : `macro_f1` reçoit `labels` de l'appelant ; l'exclusion d'`AUTRE` n'est donc pas imposée par le code. À verrouiller par un test dans P1-01 (tâche suivante, après G-P0).
- Preuve : `make check` vert. Non commité.

## 02/10/2026 : RM-18 partiel (A7 et A1 ingérés, A2 et A3 bloqués)
- Pages créées : `limited-impact-medical-adaptation` (A7, texte intégral du PDF, 11 notes à lignes) et `lmsys-first-place-distillation-readme` (A1, **README du dépôt**, pas le texte de la solution ; dit en tête de page). `overview`, `log`, index et lien retour mis à jour ; `check_wiki` et `check_wiki_quotes` verts.
- Bloqué : A2 et A3 sont des pages Kaggle rendues par JavaScript ; curl ne rapporte que le titre et WebFetch n'a reçu aucun texte. Je n'ai ni résumé ni contenu de seconde main dans le wiki (un résumé de moteur de recherche n'est pas une source citable). Question Q10.
- Écart au skill `wiki-ingest` : l'étape 3 demande d'attendre l'avis de Cyril avant d'écrire ; j'ai écrit sans emphase particulière (contrat : travail autonome) ; les points à retenir sont dans les pages.
- RM-18 **non coché** : il exige quatre pages.

## 02/10/2026 : RM-23 clos (TRIPOD-LLM ingéré)
- Page `tripod-llm-reporting-guideline` (A8) : 17 notes à lignes, tableau des items qui touchent une étude de fine-tuning pour la classification (5, 6, 7, 12, 13, 14c-f, 16, 19b, 19d). Texte brut `raw/pmc-12104976-tripod-llm.txt` (page PMC du manuscrit d'auteur, nettoyée de ses balises). Licence de réutilisation non vérifiée : items résumés, pas recopiés.
- Preuve : `lint-mechanical.py` sans constat (orphelins corrigés par liens retour), `check_wiki` et `check_wiki_quotes` verts. **Aucune conformité TRIPOD-LLM n'est revendiquée** : la page liste ce qu'il faudra rapporter.
- Progression : 49 tâches cochées sur 165. RM-18 reste ouvert (A2 et A3, Q10).

## 02/10/2026 : valeurs de Cyril enregistrées, relecture de cohérence, alerte de puissance
- Valeurs fixées par Cyril : δ = 2,0 ; K = 5 ; B = 90 h (réponse à `AskUserQuestion`). Commits `4b74439`, `e0f6374`, `feb7f11`, `4dbf597` poussés, CI verte.
- Relecture de cohérence de `PROTOCOLE.md` § 6 contre ADR-007 (par moi, **pas** la relecture adversariale en contexte neuf de P0-46, qui reste à faire avant le gel) : deux défauts corrigés. (1) La lettre B désignait à la fois le budget de GPU et les 10 000 répliques de bootstrap : ADR-007 parle maintenant de R. (2) § 6.4 admettait un verdict avec 3 graines ou plus alors qu'ADR-007 impose la présentation « non combiné » sous K = 5 : § 6.4 s'aligne sur ADR-007.
- **Alerte** : esquisse de puissance enregistrée (`scripts/spikes/power_sketch.py`, run `20261002-200851-power-sketch-ic-width`). Sur 628 patients simulés, l'IC apparié à 98,33 % fait 7,5 à 13,5 points de large pour 4 admis. Prédictions simulées, borne basse : à confirmer ou infirmer par RM-15. Question Q12. Non commité.

## 03/10/2026 : relecture adversariale de PROTOCOLE.md (P0-46), constats classés, gel NON fait
Relecteur : sous-agent `code-reviewer` du dépôt, contexte neuf, lecture seule, rien envoyé hors machine (autorisé par Cyril le 03/10). Verdict : **ne pas geler en l'état** (4 bloquants). J'ai vérifié ses chiffres avant d'agir (effectifs du test, 2,9 h contre 5,8 h, plis de contrôle, raccourci d'auteur) : tous exacts.

| # | Gravité | Sujet | Classement | Où |
|---|---|---|---|---|
| 1 | bloquant | verdict impossible avec δ = 2,0 ; repli laissé libre | **accepté, décision de Cyril (C1)** : repli écrit (EXPLORE si largeur > 4 points, δ inchangé) | 6.3 |
| 2 | bloquant | B = 90 h ne finance pas le réglage égal des variantes ; criblage compté 2,9 h au lieu de 5,8 h | **accepté, corrigé** (section 5 : 51 à 76 h sans réglage des variantes, 76 à 122 h avec 3 graines de réglage, 54 à 81 h avec 1 graine) ; **décision de Cyril (C2)** | 5, 6.10 |
| 3 | bloquant | mentions de brouillon et de proposition dans le fichier haché ; ADR-009 provisoire | **accepté, corrigé** (liste de mentions, grep au gel) ; ratification d'ADR-009 = **C3** | 6.10 |
| 4 | bloquant | empreinte de fichier entier invérifiable ; section 5 condamnée à changer | **accepté, corrigé** : instantané dans `experiments/frozen/`, exception de la section 5 | 6.10 |
| 5 | important | « une seule ouverture » contre couverture conforme, candidat final | **accepté, corrigé** : un seul script, « consommé sans résultat » défini | 6.8 |
| 6 | important | graine défaillante : « non résolu d'office » contredit ADR-007 | **accepté, corrigé** : panne relancée, divergence non remplacée, K < 5 = pas de verdict | 6.4 |
| 7 | important | recettes confirmatoires non définies, règle de choix du taux absente | **accepté, corrigé** (professeur, α, T, pré-entraînement fixés avant ; départage ; bord de grille) | 6.5 |
| 8 | important | paramètres statistiques indéfinis (type d'intervalle, niveau EXPLORE, Wilson, Holm, générateur) | **accepté, corrigé** | 6.2 |
| 9 | important | REP/ADAPT/EXPLORE se recouvrent | **accepté, corrigé** (précédence, statut séparé) | 6.7 |
| 10 | important | contradictions avec P2-08, P3-07, candidat final du plan | **accepté** : estimations exploratoires, TF-IDF et encodeurs EXPLORE ; **confirmation de Cyril (C5)** | 6.2 |
| 11 | important | valeurs des sections 1 à 4 « proposées par Claude » | **accepté** : confirmation de Cyril (**C4**) | 6.10 |
| 12 | important | traitement d'`AUTRE` non uniforme | **accepté, corrigé** (18 sorties, macro-F1 sur 17 ; ADR-009 corrigée) | 6.1 |
| 13 | mineur | raccourci d'auteur conditionnel alors que mesuré | **accepté, corrigé** (−0,86 point, non signalé) | 6.8 |
| 14 | mineur | effectifs du test faux dans ADR-007 ; ADR-006 périmée | **accepté, corrigé** (champ `test_class_counts` ajouté à `make_splits`, partition inchangée, empreinte 5c06b068 ; esquisse de puissance refaite : run `20261002-221006-power-sketch-ic-width-v2`, 7,8 à 13,7 points ; erratum) | 6.1, 6.11, ADR-007 |
| 15 | mineur | unité de δ (points ou 0 à 1) | **accepté, corrigé** | 6.1 |
| 16 | mineur | fuite professeur/élève en développement ; échangeabilité conforme ; égalité à trois candidats ; même graine ; facteur (K−1)/K | **accepté en partie** : fuite bornée dite (6.8), échangeabilité dite (6.6) ; **non traité** : règle d'égalité d'ADR-009 avec un troisième candidat indiscernable, facteur (K−1)/K (négligeable devant les patients) | 6.6, 6.8 |

**Ma première esquisse était fausse sur un point** : elle utilisait des effectifs de test proportionnels (15 % des effectifs de classe) que ADR-007 décrivait comme « réels ». Corrigé ci-dessus ; l'ancien run reste au registre (ajout seul) et est cité comme tel.
**À signaler honnêtement** : le relecteur dit avoir recalculé les effectifs par classe du test depuis le parquet et les identifiants de split, donc lu les étiquettes de la partition scellée **hors de la porte d'accès** (comptes agrégés, aucun usage pour un choix). Je les ai reproduits par `scripts/make_splits.py` (module autorisé à fabriquer les partitions), et ils sont maintenant publiés dans `splits_summary.json`. Les prochaines relectures n'ont pas à toucher aux étiquettes du test.
**Gel** : non fait. Il manque C1 à C5 de Cyril, puis une seconde relecture de la version corrigée.

## 03/10/2026 : seconde relecture adversariale (version corrigée), constats classés, gel NON fait
Relecteur : second sous-agent `code-reviewer`, contexte neuf, lecture seule, **sans lecture d'aucune étiquette** (consigne respectée). Verdict : ne pas geler (3 bloquants, 8 importants, mineurs). Ses recalculs de la section 5 concordent avec les miens ; la simulation et les effectifs aussi.

| # | Gravité | Constat | Classement |
|---|---|---|---|
| 1 | bloquant | l'extension de grille 2e-4 casse l'ordre du backlog (référence gelée avant les variantes) et fait passer N de 4 à 5 | **accepté, règle supprimée** : grille jamais étendue, risque de sous-réglage signalé au bord (6.5) |
| 2 | bloquant | règle de puissance inapplicable (source des prédictions, sous-échantillonnage infaisable sur un pli, paramètres, mauvaise porte, graines) | **accepté, réécrite** : porte RM-17, cinq graines de P1-19, bootstrap dans le pool du pli 0 aux effectifs du test, 10 paires, moyenne des largeurs, seuil strict 4,0, sortie anticipée ; ADR-007 et backlog alignés (6.3) |
| 3 | bloquant | arrêt anticipé (section 5) contre pannes (6.4) ; une divergence tue tous les verdicts | **accepté, réécrit** : une définition (`failed`), classement par le code, risque dit à Cyril (**C8**) |
| 4 | important | budget incomplet (puissance, 2e-4, P2-01, P1-26, RM-19, P1-07, P2-07), « pessimiste » seulement pour les professeurs | **accepté** : run `20261002-223418-budget-v2-premier-cycle` (57,6 à 86,3 h ; 65,8 à 97,5 h) ; postes non comptés listés ; **décision de Cyril (C7)** |
| 5 | important | conflits restants avec backlog et plan | **accepté** : cellules de P1-13, P2-08, P3-07, RM-17, RM-20 mises à jour, `todo.md` régénéré, **ADR-010** |
| 6 | important | P3-07 et P2-08 sans évaluation possible hors RM-20 | **accepté** : « entraînent sans évaluer » (6.8) |
| 7 | important | branches réussite et échec de 6.3 incomplètes | **accepté** : porte, consignation du basculement, pas un changement de famille (6.3, 6.10) |
| 8 | important | test consommé sans résultat, cas non prévus | **accepté** : condition préalable (K = 5 complet), deux temps A et B (6.8) |
| 9 | important | verdict résolu rare en cas favorable | **accepté, vérifié** (≈ 12 % pour un vrai gain de 3 points à largeur 4) ; dit en 6.3 ; **C8** |
| 10 | important | règles de gel incomplètes (grep, périmètre, errata dans le fichier haché, pas de contrôle de l'instantané) | **accepté** : grep insensible à la casse, périmètre élargi, errata hors fichier (`experiments/ERRATA-PROTOCOLE.md`), `scripts/check_frozen.py` dans `make check`, « avant P1-03 » |
| 11 | important | valeurs implicites (époques, plafond de vague, candidat final, fiches) | **accepté** : 2 époques pour toutes les recettes (**C6**), plafond = B avec alerte à 80 %, candidat final désigné par Cyril, empreinte datée des fiches |
| 12 | important | fuite des candidats distillés dans la calibration conforme | **accepté** : dite et rapportée avec réserve (6.6), pas de professeurs imbriqués |
| 13 à 18 | mineur | chiffres ADR-007, départage, relance micro-lot, repli (3) et « local », minimum 5,7, facteur (K−1)/K | **acceptés et traités**, sauf (K−1)/K et couverture de l'intervalle à 83 répliques par queue : **à vérifier en P1-02** |

**Écart de méthode à dire** : `src/llmft/frozen.py` et son test ont été écrits dans le même geste, pas test d'abord en rouge. Les 4 tests passent ; ils couvrent les quatre cas.
**Gel** : non fait. Il manque C6, C7, C8 de Cyril, puis une dernière passe limitée aux lignes modifiées depuis la seconde relecture (6.9), puis les empreintes. Non commité depuis `4dbf597`.

## 03/10/2026 : troisième relecture traitée, PROTOCOLE.md GELÉ (P0-46 coché)
- Relecteur 3 : 20 constats (2 bloquants). **Traités** : sortie anticipée de la règle de puissance supprimée (contradiction avec la moyenne) ; 6.4 et 6.8 alignés par comparaison (une graine divergente ne perd que sa comparaison) ; règle de puissance entièrement spécifiée (R = 10 000, PCG64, graine 20261002, paires, seuil strict, cas à moins de 5 graines) ; temps A et B de l'ouverture du test précisés (deux fonctions dans `sealed.py`, marqueur à chemin fixe, répétition générale) ; couverture conforme abandonnée si P4-04 et P4-05 ne sont pas prêts ; dépendances P3-07 et RM-20 sans boucle ; ADR-007 et ADR-010 alignées (6.3 prévaut) ; budget v3 corrigé (P2-01 au débit pessimiste ; run `20261002-230546-budget-v3-premier-cycle` : 57,6 à 99,8 h selon élève et professeur) ; périmètre du gel élargi à 9 fichiers, errata bornés, `check_frozen` durci (tests d'abord, 7 verts) ; règle 5 étendue ; repli (3) déclaré ouvert.
- **Non traité par du code** : classement des échecs par le registre, `sealed.py` à deux temps, répétition générale du temps B : portés par P1-19 et RM-20 (cellules du backlog mises à jour).
- **Limite dite** : ces corrections n'ont été relues que par moi.
- **Gel** : instantanés dans `experiments/frozen/`, neuf empreintes dans `experiments/INDEX.md` et la page wiki `protocole-gele-2026-10-03` ; PROTOCOLE.md SHA-256 `aba89842a1c7da2c…` (instantané `PROTOCOLE-2026-10-03.md`). Mentions d'ouverture restantes jugées admises : « hypothèse » (budget par nature), « défaut » (expression « pas un défaut à cacher »), définition de « local » d'ADR-004 (ne touche aucune règle), motif de recherche de la règle de gel.
- **Écart de méthode** : mon cahier pour GLM avait des défauts de conception (renvois à des fichiers que GLM ne lit pas, format de réponse ajouté après coup, missions sans étapes ni gabarit) : refait en version autonome.
- Non commité depuis `0996e55`.

## 03/10/2026 : contrat de nuit écrit (`tasks/CONTRAT_NUIT.md`)
- Sources lues, sur le chemin donné par Cyril (`/mnt/d/POJECT_Tune_The_Swarm_v1`, WSL) : `AGENTS.md` (R1 à R33), `docs/JOURNAL_NUIT_2026-09-30.md` et `2026-10-01.md` (contrats, délégations, file ordonnée, prolongations, conditions d'arrêt), `docs/RESUME_NUIT_2026-09-30.md`. Rien d'autre n'a été lu ; aucun identifiant ouvert.
- Transposition : 20 règles N1 à N20, interdits propres à ce dépôt (test scellé, protocole gelé, push, envoi hors machine, GPU, `~`), file par défaut dans l'état actuel, réserve perpétuelle, gabarit de journal, table des skills à charger. Le défaut constaté dans l'autre projet (contrats trop maigres, arrêt avant le réveil) est traité par la prolongation obligatoire de la file.
- Écart assumé avec l'autre projet : là-bas l'assistant commite pendant la nuit ; ici `CLAUDE.md` exige une demande explicite : commits locaux seulement si Cyril les délègue à la question de départ.
- Non commité. `CLAUDE.md` n'est pas modifié (fichier de Cyril) : à lui d'ajouter une ligne « mode nuit » s'il le veut.
