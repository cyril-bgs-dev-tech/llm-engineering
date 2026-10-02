# Micro-tâches : le backlog complet du projet (V6)

Compagnon de `PLAN_PROJET_V6.md`. Ce fichier découpe chaque tâche complexe en micro-tâches, classées par bloc et par phase, avec la catégorie de qualité qu'elles servent (Q1 à Q12, barème de la section 2 du plan V6).

`scripts/check_microtasks.py` vérifie ce fichier : identifiants uniques, dépendances existantes et sans cycle, chemin court (★) fermé sur lui-même, couverture des 12 catégories de qualité à chaque porte. Il se relance après toute modification.

## Règles de découpage

1. **Une micro-tâche = une action et une preuve observable** (fichier, test vert, mesure au registre). Au plus environ 2 h de travail ou 1 h de GPU. Plus gros : on découpe encore.
2. **Types** : `décision` (Cyril tranche), `doc`, `code`, `mesure`, `spike` (essai jetable pour lever un risque), `GPU` (lance un calcul).
3. **Toute micro-tâche `GPU` ou `spike`** passe par : fiche préenregistrée (une ligne suffit pour un spike), `vram-preflight`, `run-registry`.
4. **Le risque d'abord** : les spikes précèdent l'entrée des données, qui précède le code.
5. **Colonne Q** : une ou deux catégories de qualité servies. **Colonne Dép.** : micro-tâches à clore avant ; `*` = toutes les tâches ★ de la phase.
6. **★ = chemin court** (MVP) : l'ensemble ★ est fermé (aucune tâche ★ ne dépend d'une tâche non ★). Il suffit à répondre « oui, voici le protocole et les chiffres ». Dans le chemin court, la référence LoRA est réglée sur le seul taux d'apprentissage ; rang, contexte et époques (P1-14 à P1-16) viennent avec le chemin complet.
7. **Aucun chiffre sans `run_id`** ; aucune note de scorecard sans preuve citée.

## Qui prouve quoi : les notes 2 et 3 par catégorie

Note 2 = satisfait avec preuve dans le dépôt. Note 3 = confirmé de façon indépendante (seconde implémentation, cas piégé, relecture adversariale en contexte neuf, reconstruction à froid, revue externe au code).

| Q | Note 2 apportée par | Note 3 apportée par (confirmation indépendante) | Porte |
|---|---|---|---|
| Q1 Données | P0-14 à P0-23, P0-28, P0-40 | P0-40 (cas piégé qui doit échouer), P2-03 (contrôle hors pli), P2-06 (audit cleanlab et relecture) | 2 dès G-P0, 3 à G-P2 |
| Q2 Protocole | P0-41, P0-45, P0-46 (figé par SHA-256), RM-05, RM-07 | P0-46 (relu en contexte neuf), P3-14 (contre-lecture adversariale des verdicts) | 2 dès G-P0, 3 à G-P3 |
| Q3 Statistique | P0-46 et RM-11 (règles), P1-01, P1-02, P1-19 | P1-02 (vérifié contre SciPy et statsmodels, fausse alerte et puissance simulées), P3-07 | 2 à G-P1, 3 à G-P3 |
| Q4 Erreurs | P1-22, P1-23, P1-24 | P3-13, P4-07 (robustesse et classes hors distribution) | 1 à G-P1, 2 à G-P2, 3 à G-P4 |
| Q5 Incertitude | P1-01 (ECE), P4-04, P4-05, RM-22 | P4-06 (trois mesures de couverture indépendantes) | 1 dès G-P1 (ECE mesurée par le harnais), 3 à G-P4 |
| Q6 Reproductibilité | P0-11, P0-13, P1-26 | P5-09 (reconstruction à froid) | 2 dès G-P0, 3 à G-P5 |
| Q7 Ingénierie | P0-35, P0-42, P0-44 | P5-06 (CI), P5-07, P5-10 (revue indépendante) | 2 dès G-P0, 3 à G-P5 |
| Q8 Efficience | P0-07, P0-08, P0-10, coûts du registre | P4-02, P4-09, P5-02 | 1 dès G-P0, 2 à G-P3, 3 à G-P4 |
| Q9 Déploiement | P0-09 (spike) | P4-02, P4-08, P5-01 à P5-08 | 1 dès G-P0, 2 à G-P4, 3 à G-P5 |
| Q10 Sûreté, éthique | P0-01, P0-12, P0-15, P0-17, P0-20 | P4-10, P5-10 (security-auditor), P5-11 | 2 dès G-P0, 3 à G-P5 |
| Q11 Documentation | P0-47, P2-12 | P5-07 (guide exécuté à blanc) | 1 dès G-P0, 2 à G-P2, 3 à G-P5 |
| Q12 Honnêteté | P0-20, RM-01, RM-12, P1-25 | P3-14 (claim-gate et contre-lecture), P5-12 | 2 dès G-P0, 3 à G-P3 |

## Approche par catégorie de qualité

- **Q1 Données** : unité de découpage = patient ; plis par auteur en contrôle ; quasi-doublons et gabarits par MinHash ; étiquettes dérivées par script déterministe ; probabilités des professeurs strictement hors pli ; audit des étiquettes par confident learning puis relecture d'un échantillon ; aucune étiquette de test modifiée.
- **Q2 Protocole** : préenregistrement figé par empreinte ; références fortes et réglées (TF-IDF, encodeurs français, zéro et few-shot, LoRA réglée) ; budget de réglage égal entre méthodes ; ablation un levier à la fois ; test scellé accessible à un seul script.
- **Q3 Statistique** : cinq graines pour mesurer la variance ; bootstrap apparié d'au moins 2 000 rééchantillonnages ; McNemar ou permutation ; correction de Holm ; verdict en trois valeurs ; un gain doit dépasser deux écarts-types de graines.
- **Q4 Erreurs** : matrice de confusion hiérarchique ; erreurs par spécialité, auteur, longueur, type de document ; courbes d'apprentissage ; perturbations ; spécialité exclue ; relecture d'au moins 50 erreurs.
- **Q5 Incertitude** : ECE ; température ; prédiction conforme LAC, APS, RAPS avec trois implémentations ; abstention chiffrée ; recalibration après quantification ; hypothèse d'échangeabilité énoncée.
- **Q6 Reproductibilité** : `uv.lock`, Docker, graines, déterminisme mesuré, empreintes, reconstruction à froid.
- **Q7 Ingénierie** : contrat validé par Pydantic ; tests avant le code ; types, lint, secrets en continu ; transposabilité testée ; CI ; revue indépendante.
- **Q8 Efficience** : VRAM de pointe, latence p50 et p95, énergie ou coût, front de Pareto, budget par vague.
- **Q9 Déploiement** : service FastAPI lisant le contrat ; vLLM ou Transformers ; ElasticSearch ; composant EDS-NLP ; surveillance de dérive ; retour arrière.
- **Q10 Sûreté, éthique** : licences lues à la source ; usages interdits respectés ; aucune donnée de patient réel ; carte de modèle ; checklist TRIPOD-LLM ; règles de formulation.
- **Q11 Documentation** : wiki à citations vérifiées ; décisions tracées en ADR ; guide de transposition exécuté à blanc.
- **Q12 Honnêteté** : `claim-gate` ; résultats négatifs publiés ; `run_id` partout ; comparaison à l'état de l'art.

---

## Phase P0 : Socle (47 micro-tâches)

### Bloc P0-A : décisions de Cyril

| ID | ★ | Type | Micro-tâche | Q | Skill ou outil | Preuve de fin | Dép. |
|---|---|---|---|---|---|---|---|
| P0-01 | ★ | décision | Cyril accepte ou écarte les conditions d'accès des modèles conditionnés (Gemma 4, MedGemma) sur Hugging Face | Q10 | interview-me | ADR-001 : liste des modèles autorisés ; aucun jeton dans le dépôt | - |
| P0-02 | ★ | décision | Trancher emplacement du dossier, dépôt Git, périmètre (chemin court ou complet), date limite CHUGA, démo locale ou publique (décisions 1 à 5 du plan V6) | Q11 | interview-me, documentation-and-adrs | ADR-002 : une ligne par décision, réponse datée de Cyril | - |
| P0-03 | ★ | décision | Fixer fournisseur et plafond de location, règle de revue croisée externe, limite de la relecture d'étiquettes (décisions 7 à 9) | Q10 | interview-me | ADR-003 ; « non décidé » accepté si daté | P0-02 |

### Bloc P0-B : environnement et spikes Blackwell (le risque d'abord)

| ID | ★ | Type | Micro-tâche | Q | Skill ou outil | Preuve de fin | Dép. |
|---|---|---|---|---|---|---|---|
| P0-04 | ★ | spike | Installer PyTorch (cu128 puis cu130) dans un environnement jetable ; vérifier que `sm_120` figure dans `torch.cuda.get_arch_list()`, qu'un produit matriciel bf16 et un `scaled_dot_product_attention` s'exécutent | Q6 | vram-preflight | Sortie archivée dans le wiki (page `env-blackwell`), versions avec suffixe `+cuXXX` | RM-05 |
| P0-05 | ★ | spike | Installer transformers v5, peft, trl, accelerate, bitsandbytes ; charger un modèle de 1 milliard de paramètres au plus en 4 bits NF4 et faire 10 pas LoRA | Q6 | vram-preflight, debugging-and-error-recovery | Journal de 10 pas sans erreur ; tableau bibliothèque, version, sm_120 oui ou non | P0-04 |
| P0-06 | ★ | spike | Pour chaque candidat (Qwen3.5 4B et 9B, Qwen3.8-27B, Gemma 4 E4B et 31B, MedGemma 4B), vérifier la classe de chargement réellement utilisable (les cartes officielles de Qwen3.8-27B et de Gemma 4 31B recommandent `AutoModelForMultimodalLM` et ne mentionnent aucune classification), que `pad_token` est défini, qu'un passage avant et arrière tient ; élèves d'abord, gros professeur chargé une seule fois (compatibilité puis 10 pas de P0-08) | Q7 | lora-classifier-recipe, vram-preflight | Tableau de compatibilité par modèle (classe de chargement, pad, tête, erreurs) dans le wiki ; repli « verbaliseur » consigné pour tout modèle sans tête de classification utilisable | P0-05, P0-01 |
| P0-07 |  | spike | Mesurer débit et mémoire de SDPA contre FlashAttention 2 (et Liger-Kernel si installable) sur SM120 | Q8 | performance-optimization, vram-preflight | Courbes débit et mémoire pour 3 longueurs ; décision écrite | P0-05 |
| P0-08 | ★ | spike | Banc de 10 pas du plus gros professeur candidat en QLoRA 4 bits, 1 024 tokens, gradient checkpointing, batch effectif 64 par accumulation | Q8 | vram-preflight | Pic de mémoire réservée (cible sous 30 Go) et temps par pas au registre ; sinon plan B écrit (professeur plus petit ou déclencheur de location) | P0-06, RM-05 |
| P0-09 |  | spike | Servir un classifieur avec vLLM (ou documenter l'échec) et comparer à Transformers et FastAPI sur 100 requêtes | Q9 | performance-optimization, vram-preflight | Décision écrite : vLLM utilisable pour la classification, oui ou non, version incluse | P0-05 |
| P0-10 |  | spike | Quantifier un petit modèle dense en INT8 (bitsandbytes), FP8 et NVFP4 (llm-compressor) ; vérifier chargement et prédiction sur SM120 | Q8 | performance-optimization, vram-preflight | Tableau format, charge, prédit, VRAM, latence ; NVFP4 marqué utilisable ou non | P0-05 |
| P0-11 | ★ | code | Verrouiller l'environnement (`uv.lock`), écrire le Dockerfile, créer `hardware/rtx5090.yaml` | Q6 | ci-cd-and-automation | `docker build` et `uv sync --frozen` réussissent sur machine propre ; profil lu par un test | P0-04, P0-05 |
| P0-12 | ★ | doc | Auditer la licence de chaque dépendance et dépôt consulté (TRL, PEFT, MAPIE, TorchCP en LGPL, cleanlab, EDS-NLP, DistiLLM-2...) | Q10 | security-and-hardening | `docs/LICENCES.md` : licence, usage, compatibilité | P0-11 |
| P0-13 | ★ | code | Lancement par `accelerate launch` sur 1 GPU, avec point de sauvegarde et reprise vérifiés | Q6 | incremental-implementation | Un run interrompu puis repris retrouve la même perte dans la tolérance fixée | P0-05 |

### Bloc P0-C : entrée des données

| ID | ★ | Type | Micro-tâche | Q | Skill ou outil | Preuve de fin | Dép. |
|---|---|---|---|---|---|---|---|
| P0-14 | ★ | code | Script de téléchargement de PARHAF avec révision épinglée et empreintes SHA-256 | Q1 | dataset-intake | Rejoué sur machine propre : mêmes empreintes ; `data/` ignoré par Git | P0-11, RM-03 |
| P0-15 | ★ | doc | Lire à la source la licence et les usages permis ou interdits de PARHAF ; consigner le texte exact | Q10 | dataset-intake | Section licence de `data/cards/parhaf.md` avec URL et citations littérales | P0-14 |
| P0-16 | ★ | doc | Fiche du jeu PARHAF : provenance, découpage officiel, distribution, longueurs, biais connus, ce que le jeu ne représente pas | Q1 | dataset-intake | `data/cards/parhaf.md` complète, chaque champ tiré d'une mesure de P0-21 | P0-15, P0-21 |
| P0-17 | ★ | mesure | Chercher des motifs de données personnelles sur 200 documents (noms, dates complètes, numéros, adresses) | Q10 | security-and-hardening | Rapport : zéro, ou liste des cas douteux signalés à Cyril | P0-14 |
| P0-18 |  | doc | Entrée des sous-ensembles annotés PARHAF (conclusion, pseudo, biomarqueurs, infectiologie, réponse au traitement) : licences et fiches, sans les utiliser avant P6 | Q1 | dataset-intake | Cinq fiches courtes | P0-15 |
| P0-19 |  | doc | Entrée de PARCOMED : choisir la version (commerciale CC BY ou research only), fiche, taille de l'échantillon utilisable | Q1 | dataset-intake | Fiche et décision écrite sur la version | P0-12 |
| P0-20 | ★ | doc | Déduire des conditions d'usage de PARHAF les règles de formulation (CV, LinkedIn, démo, publication) | Q10 Q12 | claim-gate | Page `regles-de-formulation` consultée par claim-gate | P0-15 |
| P0-21 | ★ | mesure | Compter dans les données : patients, documents, spécialités, types de documents, longueurs en tokens de chaque tokenizer candidat | Q1 | dataset-intake | Tableau versionné ; chaque chiffre cite sa source, la révision épinglée (sha du dépôt HF) et son périmètre (publié, embargo, total) ; divergences des sources (4 254 ou 4 259 patients, 18 ou 20 spécialités, 6 185 ou 6 190 documents) tranchées par la donnée | P0-14 |
| P0-22 | ★ | mesure | Mesurer la présence du diagnostic principal CIM-10 dans `suggested_scenario` : taux par pool et spécialité, formats rencontrés | Q1 | dataset-intake | Tableau de présence ; liste des patients sans étiquette ; décision sur leur exclusion | P0-14 |
| P0-23 | ★ | mesure | Distribution des classes CIM-10 aux trois niveaux (chapitre, bloc, trois caractères) et seuil minimal d'exemples par classe | Q1 | dataset-intake | Histogrammes ; nombre de classes sous le seuil par niveau | P0-22, P0-27 |
| P0-24 |  | doc | Entrée de MorFITT : licence à la source, fiche, contrat `morfitt_specialites` (multilabel) | Q1 Q7 | dataset-intake | Fiche et YAML valide au schéma | P0-12, P0-35 |
| P0-25 |  | doc | Entrée de CLISTER : licence à la source, fiche, niveaux de similarité nommés et définis, contrat `clister_similarite` (pair_ordinal) | Q1 Q7 | dataset-intake | Fiche et YAML valide ; si la licence interdit l'usage, tâche retirée par ADR | P0-12, P0-35 |
| P0-26 |  | doc | Entrée de DiaMED (repli) : licence et fiche seulement | Q1 | dataset-intake | Fiche courte | P0-12 |
| P0-27 | ★ | code | Obtenir la nomenclature CIM-10 officielle (conditions de réutilisation lues) ; en tirer noms et hiérarchie chapitre, bloc, code | Q1 | source-driven-development | Fichier versionné ; test de cohérence (chaque code a son bloc et son chapitre) | P0-12 |

### Bloc P0-D : découpage et règles de données

| ID | ★ | Type | Micro-tâche | Q | Skill ou outil | Preuve de fin | Dép. |
|---|---|---|---|---|---|---|---|
| P0-28 | ★ | code | Découpage par patient : test interne scellé et 5 plis stratifiés, graine fixée | Q1 | leakage-guard, test-driven-development | Fichiers d'identifiants et SHA-256 ; test : aucun patient dans deux partitions | P0-22, P0-33, RM-07 |
| P0-29 | ★ | code | Plis groupés par auteur, second découpage de contrôle | Q1 | leakage-guard | Fichier d'identifiants ; test : aucun auteur dans deux plis | P0-28 |
| P0-30 | ★ | mesure | Mesurer le raccourci d'auteur : un modèle simple (TF-IDF et régression logistique) prédit spécialité et chapitre à partir du seul trigramme de l'auteur et d'un échantillon de style | Q4 | leakage-guard | Score face au seuil chiffré fixé par RM-07 avant observation ; si le seuil est dépassé, les plis par auteur deviennent la métrique principale (ADR) | P0-28, RM-07 |
| P0-31 | ★ | mesure | Vérifier l'état de l'ouverture du test embargoé (page du jeu, CodaBench) ; consigner règles et calendrier | Q2 | dataset-intake | Note datée ; nouvelle vérification planifiée en P3-15 | P0-15 |
| P0-32 | ★ | décision | Choisir l'unité d'entrée : un document, ou un patient (documents concaténés par type, ordre fixe) ; règle de troncature | Q2 | experiment-preregistration | Règle dans `PROTOCOLE.md` appuyée par les longueurs de P0-21 | P0-21 |
| P0-33 | ★ | décision | Politique des classes rares : seuil minimal, regroupement hiérarchique, classe « autre » | Q2 | experiment-preregistration | Règle écrite et appliquée par script | P0-23 |
| P0-34 | ★ | doc | Définir l'accès au test scellé : un seul script d'évaluation finale peut le charger | Q2 | leakage-guard | Test automatique qui échoue si un autre module le lit | P0-28 |

### Bloc P0-E : contrats de tâche

| ID | ★ | Type | Micro-tâche | Q | Skill ou outil | Preuve de fin | Dép. |
|---|---|---|---|---|---|---|---|
| P0-35 | ★ | code | Schéma Pydantic du contrat de tâche (type, entrées, classes, hiérarchie, format de sortie, métriques, abstention) avec ses tests | Q7 | test-driven-development | Tests verts ; un contrat invalide est rejeté avec un message clair | P0-11 |
| P0-36 | ★ | doc | Contrat de la tâche de contrôle `parhaf_doctype` | Q7 | dataset-intake | YAML valide ; chaque classe nommée et définie | P0-35, P0-21 |
| P0-37 | ★ | doc | Contrat `parhaf_specialty` | Q7 | dataset-intake | YAML valide ; chaque classe nommée et définie | P0-35, P0-21 |
| P0-38 | ★ | doc | Contrat `parhaf_cim10_chapter` : noms officiels et définitions opérationnelles des chapitres | Q1 | dataset-intake, doubt-driven-development | YAML valide ; définitions relues en contexte neuf | P0-27, P0-35, P0-23 |
| P0-39 | ★ | doc | Tâche jouet synthétique (deux classes, 50 exemples) avec son contrat | Q7 | test-driven-development | YAML valide et données générées par un script déterministe | P0-35 |

### Bloc P0-F : garde-fous, protocole, clôture

| ID | ★ | Type | Micro-tâche | Q | Skill ou outil | Preuve de fin | Dép. |
|---|---|---|---|---|---|---|---|
| P0-40 | ★ | code | Tests `leakage-guard` : patient, quasi-doublons et gabarits (MinHash), test scellé, hors pli | Q1 | leakage-guard | `tests/test_leakage.py` vert ; un cas piégé volontairement fait échouer le test | P0-28, P0-29 |
| P0-41 | ★ | code | Squelette du registre de runs : écriture immuable, schéma des champs, validateur | Q2 | run-registry, test-driven-development | Un second écrasement échoue ; un run sans `env` est refusé | P0-11 |
| P0-42 | ★ | doc | `CONSTRAINTS.md` et `make check` (types, lint, tests, gitleaks, couverture des lignes modifiées) | Q7 | constraint-driven-development | `make check` vert ; chaque seuil a sa raison ; gitleaks actif dès le premier commit | P0-11 |
| P0-43 | ★ | code | Chargeur de données générique : lit le contrat et un adaptateur (identifiant, texte, étiquette) | Q7 | api-and-interface-design | Deux tâches chargées sans branche propre à l'une d'elles ; l'empreinte des partitions est comparée à une référence versionnée à chaque chargement | P0-35, P0-36 |
| P0-44 | ★ | code | Test de transposabilité : la tâche jouet et `parhaf_doctype` passent par la même chaîne (chargement, 10 pas, évaluation, registre) sans une ligne propre à l'une ; le test existe en deux variantes, `backend=cpu` (petit modèle, CI sans GPU) et `backend=gpu` | Q7 | test-driven-development | Test vert dans les deux variantes ; ajouter une tâche de même famille ne modifie pas le noyau (seuls un YAML et un adaptateur dans un répertoire autorisé changent), coût d'ajout mesuré en fichiers, lignes et durée | P0-43, P0-41, P0-39 |
| P0-45 | ★ | doc | Budget de calcul par vague (heures GPU), arrêt anticipé, règle de repli | Q8 | experiment-preregistration | Tableau dans `PROTOCOLE.md` | P0-08 |
| P0-46 | ★ | doc | Rédiger `PROTOCOLE.md` : métriques, tests statistiques, seuils de décision, graines, niveau conforme, règles de gel ; chaque expérience porte l'étiquette REP (vérification d'un mécanisme exact de la recette source), ADAPT (transfert au clinique français) ou EXPLORE ; développement sur plis, confirmation sur le test scellé ouvert une seule fois ; relecture adversariale en contexte neuf ; calcul de son SHA-256 | Q2 Q3 | experiment-preregistration, doubt-driven-development | Fichier figé, empreinte consignée avant tout run de P1 et dans une page wiki datée, constats de la relecture classés | P0-32, P0-33, P0-34, P0-41, P0-44, P0-45, RM-02, RM-07, RM-11, RM-12 |
| P0-47 | ★ | doc | Ingérer au wiki trois papiers du Lot A (A4 PARHAF, A5, A6 ; voir `BOITE_A_OUTILS.md`) ; A1, A2, A3 et A7 par RM-18, A8 par RM-23 | Q11 | wiki-ingest | Trois pages sources à citations par lignes ; `wiki-lint` sans erreur | - |
| G-P0 | ★ | doc | Scorecard G-P0 : note Q1 à Q12, une preuve par note, plan de rattrapage pour toute note sous le plancher du plan V6 | Q12 | claim-gate, wiki-lint | `scorecards/G-P0.md` | * |

---

## Phase P1 : Références (26 micro-tâches)

### Bloc P1-A : harnais de mesure

| ID | ★ | Type | Micro-tâche | Q | Skill ou outil | Preuve de fin | Dép. |
|---|---|---|---|---|---|---|---|
| P1-01 | ★ | code | Harnais d'évaluation : accuracy, macro-F1, log loss, ECE, Spearman | Q3 Q5 | test-driven-development | Valeurs exactes sur 5 cas construits à la main | P0-41 |
| P1-02 | ★ | code | Outils de comparaison appariée : bootstrap, McNemar, permutation, correction de Holm ; vérifiés contre SciPy et statsmodels | Q3 | paired-comparison | Fausse alerte au plus 5 % sur données sans effet ; détection d'un effet injecté ; accord avec les bibliothèques | P1-01 |
| P1-03 | ★ | mesure | Bornes : classe majoritaire et tirage aléatoire sur les trois tâches | Q2 | experiment-preregistration | Lignes au registre | P1-01 |

### Bloc P1-B : références classiques et encodeurs

| ID | ★ | Type | Micro-tâche | Q | Skill ou outil | Preuve de fin | Dép. |
|---|---|---|---|---|---|---|---|
| P1-04 | ★ | mesure | TF-IDF et régression logistique sur `parhaf_doctype`, réglage de C et des n-grammes sur validation | Q2 | experiment-preregistration | Run au registre avec intervalle de confiance | P1-03 |
| P1-05 |  | mesure | TF-IDF et régression logistique sur `parhaf_specialty` | Q2 | experiment-preregistration | Run au registre | P1-04 |
| P1-06 | ★ | mesure | TF-IDF et régression logistique sur `parhaf_cim10_chapter` | Q2 | experiment-preregistration | Run au registre | P1-04, P0-38 |
| P1-07 | ★ | GPU | DrBERT ou CamemBERT-bio affiné sur `parhaf_cim10_chapter`, taux d'apprentissage réglé sur 4 valeurs | Q2 | experiment-preregistration, vram-preflight | Run au registre ; nombre d'essais de réglage consigné | P1-06 |
| P1-08 |  | GPU | doctomodernbert-fr (contexte long) sur la même tâche | Q2 | experiment-preregistration, vram-preflight | Run au registre | P1-07 |
| P1-09 |  | GPU | LLM candidat en zéro-shot, invite avec noms et définitions des classes | Q2 | experiment-preregistration, vram-preflight | Run et invite figée | P0-38, P0-06 |
| P1-10 |  | GPU | Même modèle en few-shot (3 puis 8 exemples tirés de l'entraînement seulement) | Q2 | leakage-guard, vram-preflight | Run ; contrôle : exemples hors test | P1-09 |

### Bloc P1-C : choix de l'élève et réglage de la LoRA de référence

| ID | ★ | Type | Micro-tâche | Q | Skill ou outil | Preuve de fin | Dép. |
|---|---|---|---|---|---|---|---|
| P1-11 | ★ | GPU | Criblage des points de départ : un pli, réglages identiques, deux à trois candidats fixés par RM-13 (au moins un généraliste) ; criblage de quatre à six modèles au chemin complet | Q2 | lora-classifier-recipe, vram-preflight | Un run par modèle au registre | P0-06, P1-06, P0-43, RM-13 |
| P1-12 | ★ | décision | Choisir l'élève selon la règle écrite avant le criblage (meilleur macro-F1 sous contrainte de VRAM et de latence) | Q2 | experiment-preregistration | ADR-élève ; règle datée avant P1-11 | P1-11 |
| P1-13 | ★ | GPU | Balayage du taux d'apprentissage LoRA (1e-5, 2e-5, 5e-5, 1e-4), trois graines | Q3 | lora-classifier-recipe, vram-preflight | 12 runs ; courbe taux contre macro-F1 | P1-12 |
| P1-14 |  | GPU | Balayage du rang et d'alpha autour du meilleur taux | Q3 | lora-classifier-recipe, vram-preflight | Runs au registre | P1-13 |
| P1-15 |  | GPU | Balayage de la longueur de contexte et de la troncature (milieu, tête et fin) | Q3 | lora-classifier-recipe, vram-preflight | Runs au registre | P1-13 |
| P1-16 |  | GPU | Nombre d'époques et ordonnanceur | Q3 | lora-classifier-recipe, vram-preflight | Runs au registre | P1-13 |
| P1-17 |  | GPU | Tête de classification contre verbaliseur | Q2 | paired-comparison, vram-preflight | Verdict en trois valeurs | P1-14 |
| P1-18 |  | GPU | Pooling (dernier, moyenne, max) avec et sans masque bidirectionnel | Q2 | paired-comparison, vram-preflight | Verdicts en trois valeurs | P1-14 |
| P1-19 | ★ | GPU | Variance entre graines : cinq graines de la configuration réglée | Q3 | paired-comparison, vram-preflight | Écart-type publié ; règle de décision de RM-11 appliquée | P1-13 |
| P1-20 | ★ | doc | Geler la configuration de référence (LoRA réglée) : fichier de config et run_id | Q2 | run-registry | `configs/reference.yaml` citant le run_id | P1-19 |
| P1-21 |  | doc | Documenter le budget de réglage par méthode (essais, heures) pour garantir un budget égal | Q2 | run-registry | Tableau méthode, essais, heures | P1-20 |

### Bloc P1-D : analyse et clôture

| ID | ★ | Type | Micro-tâche | Q | Skill ou outil | Preuve de fin | Dép. |
|---|---|---|---|---|---|---|---|
| P1-22 |  | GPU | Courbe d'apprentissage de la référence à 10, 25, 50, 100 % de l'entraînement | Q4 | run-registry, vram-preflight | Courbe et runs | P1-20 |
| P1-23 | ★ | mesure | Analyse d'erreurs initiale : matrice de confusion hiérarchique, par spécialité, longueur, type de document | Q4 | paired-comparison | Tableaux et 20 erreurs relues | P1-20 |
| P1-24 |  | mesure | Raccourcis : même modèle avec plis par patient contre plis par auteur ; comparaison au modèle témoin de P0-30 | Q4 | leakage-guard | Verdict apparié ; ADR si l'écart est significatif | P1-20, P0-29, P0-30 |
| P1-25 | ★ | doc | Page d'analyse V0 dans le wiki et premier `RESULTATS.md` (positifs et négatifs) | Q12 | wiki-ingest, claim-gate | Chaque chiffre cite un run_id ; `wiki-lint` vert | P1-23, RM-14 |
| P1-26 | ★ | GPU | Rejouer le run de référence avec la même graine ; mesurer le déterminisme | Q6 | run-registry, vram-preflight | Prédictions identiques ou écart borné, consigné | P1-20 |
| G-P1 | ★ | doc | Scorecard G-P1 | Q12 | claim-gate | `scorecards/G-P1.md` | * |

---

## Phase P2 : Professeurs et données (12 micro-tâches)

| ID | ★ | Type | Micro-tâche | Q | Skill ou outil | Preuve de fin | Dép. |
|---|---|---|---|---|---|---|---|
| P2-01 | ★ | GPU | Professeur 1 : réglage minimal du taux sur un pli (QLoRA) | Q3 | lora-classifier-recipe, vram-preflight | Run au registre | P0-08, P1-20 |
| P2-02 | ★ | GPU | Professeur 1 en cinq plis ; probabilités hors pli en Parquet avec manifeste | Q1 | distillation-pipeline, vram-preflight | Fichiers et manifeste, un fichier par pli | P2-01 |
| P2-03 | ★ | code | Contrôle hors pli : chaque exemple n'est prédit que par le professeur qui ne l'a pas vu | Q1 | leakage-guard | Test vert sur les logits stockés | P2-02, P0-40 |
| P2-04 |  | GPU | Professeur 2 d'une autre famille en cinq plis | Q2 | distillation-pipeline, vram-preflight | Fichiers et manifeste | P2-03 |
| P2-05 |  | mesure | Score hors pli de chaque professeur et de leur moyenne ; accord entre professeurs | Q3 | paired-comparison | Tableau et kappa | P2-04 |
| P2-06 | ★ | mesure | Audit des étiquettes : cleanlab sur les probabilités hors pli, file de relecture, relecture de 100 cas pour cohérence avec les définitions | Q1 | distillation-pipeline | `relabel_queue.csv` et rapport ; aucune étiquette de test modifiée | P2-02 |
| P2-07 | ★ | GPU | Pré-entraînement sur tâche voisine (`parhaf_specialty`, MorFITT en option), fusion de la LoRA, tête neuve | Q2 | lora-classifier-recipe, vram-preflight | Runs et point de contrôle fusionné | P1-20, P0-37 |
| P2-08 | ★ | mesure | Gain de la tâche voisine contre la référence, test apparié, trois graines | Q3 | paired-comparison | Verdict en trois valeurs | P2-07, P1-19 |
| P2-09 |  | GPU | Pré-entraînement continu léger sur un échantillon de PARCOMED, puis mesure | Q2 | paired-comparison, vram-preflight | Verdict | P0-19, P1-20 |
| P2-10 |  | GPU | Données synthétiques par les professeurs, amorcées sur des exemples d'entraînement seulement, avec identifiant de source ; contrôle de fuite | Q1 | leakage-guard, vram-preflight | Fichier avec lignée ; test vert | P2-02 |
| P2-11 |  | GPU | Tâches multi-étiquettes (MorFITT) et sur paires (CLISTER) de bout en bout avec le même code | Q7 | test-driven-development, vram-preflight | Deux runs au registre sans branche propre à une tâche | P0-24, P0-25, P1-20 |
| P2-12 |  | doc | Pages wiki des professeurs, de la qualité des étiquettes et de la tâche voisine | Q11 | wiki-update | Pages et `wiki-lint` vert | P2-08 |
| G-P2 | ★ | doc | Scorecard G-P2 | Q12 | claim-gate | `scorecards/G-P2.md` | * |

---

## Phase P3 : Distillation et leviers (15 micro-tâches)

| ID | ★ | Type | Micro-tâche | Q | Skill ou outil | Preuve de fin | Dép. |
|---|---|---|---|---|---|---|---|
| P3-01 | ★ | code | Perte de distillation `alpha·CE + (1 - alpha)·T²·KL` avec tests de gradient et cas limites | Q7 | distillation-pipeline, test-driven-development | alpha=1 retrouve la CE ; KL nulle si les distributions sont égales | P1-20 |
| P3-02 | ★ | GPU | Élève distillé d'un professeur, alpha et T par défaut | Q2 | distillation-pipeline, vram-preflight | Run au registre | P3-01, P2-03 |
| P3-03 |  | GPU | Balayage d'alpha et de T | Q3 | distillation-pipeline, vram-preflight | Runs au registre | P3-02 |
| P3-04 |  | GPU | Plusieurs professeurs : moyenne des probabilités contre pondération par score hors pli | Q2 | paired-comparison, vram-preflight | Verdict | P2-05, P3-02 |
| P3-05 |  | GPU | Direction de la KL (directe, inverse, asymétrique) | Q2 | paired-comparison, vram-preflight | Verdict | P3-02 |
| P3-06 |  | GPU | Distillation des justifications : tâche auxiliaire de génération | Q2 | distillation-pipeline, vram-preflight | Verdict ; l'explication n'est jamais une preuve de qualité | P3-02 |
| P3-07 | ★ | mesure | Verdict apparié V1 : distillation, tâche voisine, les deux, contre la référence | Q3 | paired-comparison | Table de verdicts avec intervalles | P3-02, P2-08 |
| P3-08 |  | GPU | Variantes LoRA (DoRA, rsLoRA, PiSSA, LoRA+), chacune avec son propre balayage de taux | Q2 | lora-classifier-recipe, vram-preflight | Verdicts ; protocole conforme à arXiv 2602.04998 | P1-20 |
| P3-09 |  | GPU | Pondération de classes, perte focale, lissage d'étiquettes | Q2 | paired-comparison, vram-preflight | Verdicts | P1-20 |
| P3-10 |  | GPU | Courbes d'apprentissage de l'élève distillé à 10, 25, 50, 100 % | Q4 | run-registry, vram-preflight | Courbe | P3-07 |
| P3-11 |  | GPU | Étiquettes nettoyées contre brutes : impact du nettoyage | Q1 | paired-comparison, vram-preflight | Verdict | P2-06 |
| P3-12 |  | GPU | Niveaux bloc et trois caractères avec la meilleure recette | Q4 | run-registry, vram-preflight | Tableau par niveau | P3-07 |
| P3-13 |  | mesure | Analyse d'erreurs approfondie : spécialité, auteur, longueur, classes rares | Q4 | paired-comparison | Rapport avec 50 erreurs relues | P3-07 |
| P3-14 |  | doc | Consolider verdicts, `RESULTATS.md`, pages wiki (méthodes, résultats négatifs), tableau coût contre qualité ; contre-lecture adversariale des verdicts | Q2 Q12 | wiki-update, claim-gate, doubt-driven-development | Cohérence vérifiée ; constats de la contre-lecture classés | P3-13 |
| P3-15 |  | mesure | Revérifier l'ouverture du test embargoé de PARHAF ; si ouvert, préparer la soumission unique | Q2 | dataset-intake | Note datée ; soumission préenregistrée si possible | P0-31 |
| G-P3 | ★ | doc | Scorecard G-P3 | Q12 | claim-gate | `scorecards/G-P3.md` | * |

---

## Phase P4 : Compression et sûreté (10 micro-tâches)

| ID | ★ | Type | Micro-tâche | Q | Skill ou outil | Preuve de fin | Dép. |
|---|---|---|---|---|---|---|---|
| P4-01 |  | GPU | Fusion des LoRA des cinq plis contre ensemble des cinq | Q2 | paired-comparison, vram-preflight | Verdict | P3-07 |
| P4-02 |  | GPU | Quantification : INT8 bitsandbytes, GPTQ, FP8, NVFP4 ; qualité, latence, VRAM sur la tâche | Q8 Q9 | performance-optimization, vram-preflight | Tableau format contre métriques, runs au registre | P4-01, P0-10 |
| P4-03 |  | GPU | Augmentation au test (troncature, ordre des documents) | Q2 | paired-comparison, vram-preflight | Verdict | P4-01 |
| P4-04 | ★ | code | Calibration par température et ECE avant et après | Q5 | model-card-calibration | Diagramme de fiabilité | P3-07 |
| P4-05 | ★ | code | Prédiction conforme avec MAPIE (LAC, APS, RAPS) ; couverture empirique contre niveau visé | Q5 | model-card-calibration | Couverture mesurée sur le test (hypothèse d'échangeabilité énoncée) ; validation de RM-22 | P4-04 |
| P4-06 |  | code | Vérification croisée des implémentations (MAPIE, TorchCP, maison) : contrôle d'implémentation, pas validation des hypothèses | Q5 | doubt-driven-development | Trois couvertures dans la même tolérance | P4-05 |
| P4-07 |  | mesure | Robustesse : perturbations (fautes, abréviations, coupures, ordre des sections) et spécialité exclue de l'entraînement | Q4 | paired-comparison | Courbes de dégradation | P4-01 |
| P4-08 | ★ | code | Politique d'abstention et courbe automatisation contre exactitude ; recalibration si un modèle quantifié est retenu | Q5 Q9 | model-card-calibration | Courbe et point de fonctionnement | P4-05 |
| P4-09 |  | mesure | Front de Pareto qualité contre coût (VRAM, latence, énergie) | Q8 | performance-optimization | Graphique et tableau | P4-02 |
| P4-10 | ★ | doc | Carte de modèle et checklist TRIPOD-LLM remplie | Q10 | model-card-calibration | `model_cards/<modèle>.md` et checklist des 19 items | P4-08 |
| G-P4 | ★ | doc | Scorecard G-P4 | Q12 | claim-gate | `scorecards/G-P4.md` | * |

---

## Phase P5 : Industrialisation (12 micro-tâches)

| ID | ★ | Type | Micro-tâche | Q | Skill ou outil | Preuve de fin | Dép. |
|---|---|---|---|---|---|---|---|
| P5-01 |  | code | Service FastAPI qui lit le contrat : prédiction, ensemble conforme, abstention | Q9 | api-and-interface-design | Tests d'API verts | P4-08 |
| P5-02 |  | mesure | Charge et latence p50 et p95 du service sur la 5090 | Q8 | performance-optimization | Rapport | P5-01 |
| P5-03 |  | mesure | Backend vLLM (si validé en P0-09) contre Transformers : débit | Q8 | performance-optimization | Tableau | P5-01, P0-09 |
| P5-04 |  | code | Indexation ElasticSearch (texte et prédictions) en conteneur local | Q9 | api-and-interface-design | Requête de test | P5-01 |
| P5-05 |  | code | Composant EDS-NLP exposant le classifieur ; test d'interopérabilité | Q9 | source-driven-development | Pipeline EDS-NLP de test vert | P5-01 |
| P5-06 |  | code | CI GitLab : tests, types, lint, secrets, test de transposabilité | Q7 | ci-cd-and-automation | Pipeline vert | P0-42 |
| P5-07 |  | doc | `docs/TRANSPOSER_AU_CHU.md` exécuté à blanc sur une tâche factice | Q11 Q7 | documentation-and-adrs | La tâche factice tourne en suivant le guide seul | P5-06 |
| P5-08 |  | doc | Surveillance de dérive, règles de maintenance, seuils de réentraînement, retour arrière | Q9 | observability-and-instrumentation, shipping-and-launch | Document et simulation de dérive | P5-01 |
| P5-09 | ★ | mesure | Reconstruction à froid : clone neuf puis `make reproduce-small` | Q6 | ci-cd-and-automation | Chiffre clé reproduit dans la tolérance | P0-11, P0-42, P1-20 |
| P5-10 |  | doc | Revue indépendante : code-reviewer, security-auditor, test-engineer ; doubt-driven sur les décisions clés | Q7 Q10 | code-review-and-quality | Rapports ; aucun envoi externe sans accord de Cyril | P5-09 |
| P5-11 |  | code | Démo locale avec bannière « données fictives, pas d'usage clinique » | Q10 | shipping-and-launch | Script de démo | P5-01, P0-20 |
| P5-12 | ★ | doc | Rapport final et textes sortants (CV, LinkedIn, lettre) passés par `claim-gate` | Q12 | claim-gate | Tableau de preuve joint | P4-10, P5-09 |
| G-P5 | ★ | doc | Scorecard G-P5 | Q12 | claim-gate | `scorecards/G-P5.md` | * |

---

## Phase P6 : piste générative (option, 8 micro-tâches)

| ID | ★ | Type | Micro-tâche | Q | Skill ou outil | Preuve de fin | Dép. |
|---|---|---|---|---|---|---|---|
| P6-01 |  | doc | Contrat génératif de la tâche « conclusion » (entrée : corps du compte rendu ; sortie : texte ; champs fermés pour l'évaluation) | Q7 | dataset-intake | `task_specs/parhaf_conclusion.yaml` valide | P0-18, P0-35 |
| P6-02 |  | GPU | Baseline : LLM zéro-shot et few-shot | Q2 | experiment-preregistration, vram-preflight | Run au registre | P6-01 |
| P6-03 |  | GPU | SFT LoRA de l'élève | Q2 | lora-classifier-recipe, vram-preflight | Run au registre | P6-02 |
| P6-04 |  | code | Métrique de faits atomiques bidirectionnelle (extraction, appariement) validée sur 50 paires relues | Q3 | test-driven-development | Accord avec la relecture mesuré | P6-01 |
| P6-05 |  | mesure | LLM-juge distinct du générateur, validé sur un échantillon annoté à la main, stabilité mesurée | Q3 | doubt-driven-development | Accord juge et humain, stabilité consignés | P6-04 |
| P6-06 |  | GPU | Distillation sur politique avec `DistillationTrainer` (vocabulaire commun vérifié) | Q2 | distillation-pipeline, vram-preflight | Run au registre | P6-03 |
| P6-07 |  | GPU | GRPO à récompense vérifiable (F1 d'extraction, validité du JSON) sur la tâche d'extraction dérivée des spans | Q2 | experiment-preregistration, vram-preflight | Run et récompense testée | P6-03 |
| P6-08 |  | GPU | Décodage contraint (xgrammar, llguidance) : validité et latence | Q9 | performance-optimization, vram-preflight | Tableau | P6-03 |

---

## Option R : location de GPU (5 micro-tâches, seulement sur déclencheur)

| ID | ★ | Type | Micro-tâche | Q | Skill ou outil | Preuve de fin | Dép. |
|---|---|---|---|---|---|---|---|
| R-01 |  | décision | Fiche préenregistrée de location : question scientifique, déclencheur (section 5.2 du plan), durée, plafond | Q10 | experiment-preregistration | Fiche figée et accord de Cyril sur le plafond | - |
| R-02 |  | doc | Choisir le fournisseur ; vérifier que les licences des données permettent l'hébergement tiers ; aucun secret dans l'image | Q10 | dataset-intake, security-and-hardening | Note et liste des fichiers autorisés | R-01 |
| R-03 |  | spike | Profil `hardware/<carte>.yaml` et pré-vol sur la machine louée | Q8 | vram-preflight | Pré-vol vert | R-02 |
| R-04 |  | GPU | Exécuter, rapatrier les artefacts, enregistrer le coût réel | Q8 | run-registry, vram-preflight | Runs « loué » au registre avec le coût | R-03 |
| R-05 |  | mesure | Comparer à protocole égal et présenter à côté des résultats 5090 | Q3 | paired-comparison, claim-gate | Verdict ; matériel signalé | R-04 |

---

## Phase RM : additions issues des audits de GLM 5.3 et de ChatGPT 5.6 (24 micro-tâches)

Ces tâches viennent du point fait le 01/10/2026 (voir `roadmap_unifié.md`, section 1). Elles sont toutes ★ : ce sont des garde-fous, des décisions et des portes d'arrêt, pour la plupart petites. Leur ordre d'exécution est celui de la feuille de route.

| ID | ★ | Type | Micro-tâche | Q | Skill ou outil | Preuve de fin | Dép. |
|---|---|---|---|---|---|---|---|
| RM-01 | ★ | doc | Archiver l'offre CHUGA : texte intégral fourni par Cyril, URL ou PDF, date de consultation, SHA-256, dans `docs/offre/` | Q12 | claim-gate | Fichier archivé et empreinte consignée ; tout le périmètre cite cette archive et non la mémoire | - |
| RM-02 | ★ | décision | Fixer le cap du premier cycle : budget B (heures GPU) et N (essais de réglage par famille), métrique primaire, seuil « pratiquement utile », définition de « local » (données, calcul, démonstration), objectif neutre quant au vainqueur | Q2 | interview-me, documentation-and-adrs | ADR-004 avec les valeurs de Cyril, ou valeur provisoire datée ; B et N obligatoires avant P0-46 | P0-02 |
| RM-03 | ★ | code | `git init` local, `.gitignore` (data/, models/, artifacts/, .venv/, caches, sorties de runs lourdes), commit d'amorçage présenté à Cyril | Q10 | git-workflow-and-versioning | `git check-ignore data/x` confirme l'exclusion ; aucun commit sans l'accord de Cyril ; aucun dépôt distant créé | P0-02 |
| RM-04 | ★ | doc | `SPEC-P0.md` courte (objectifs, commandes canoniques via `uv run` avec sortie UTF-8, structure, style, tests, limites toujours, demander, jamais, critères de succès) ; une seule source de règles pour CLAUDE.md et AGENTS.md | Q7 | spec-driven-development | SPEC-P0 validée par Cyril ; `docs/COMMANDES.md` ; AGENTS.md aligné sur CLAUDE.md, chemins en `.codex` | RM-03, RM-02 |
| RM-05 | ★ | code | Mini-registre de runs : fichier JSON en ajout seul, bibliothèque standard, validateur, sans dépendance, avant tout spike | Q2 | run-registry, test-driven-development | Test : un écrasement est refusé ; format compatible avec P0-41 | RM-03 |
| RM-06 | ★ | mesure | Mesurer la machine telle que WSL la voit : RAM visible, disque libre, pilote et mémoire GPU, un chargement de poids sur ext4 contre `/mnt/d`, emplacement de `HF_HOME` et des points de sauvegarde | Q8 Q6 | vram-preflight | Page wiki `env-blackwell` et un run au registre ; écart avec « environ 96 Go de RAM » de CLAUDE.md consigné | P0-05, RM-05 |
| RM-07 | ★ | décision | Préenregistrer les règles de split : unité de split et de bootstrap, groupement par auteur contre stratification (règle si incompatibles), tolérance de déséquilibre, auteurs présents dans une seule classe, seuil chiffré du « raccourci d'auteur » fixé avant son observation, statut confirmatoire ou exploratoire de chaque split | Q1 Q2 | experiment-preregistration | Section « splits » de `PROTOCOLE.md` en brouillon daté, antérieure à P0-30 | P0-23, P0-32, P0-33 |
| RM-08 | ★ | décision | Porte go/no-go sur la viabilité des données : continuer, simplifier la cible (niveau chapitre, regroupements) ou changer de tâche | Q2 | doubt-driven-development | Décision datée appuyée par les chiffres de P0-22, P0-23, P0-28, P0-29, P0-30 | P0-22, P0-23, P0-28, P0-29, P0-30 |
| RM-09 | ★ | mesure | Fil synthétique de bout en bout : une commande (`make smoke`) enchaîne contrat, chargeur, split, modèle trivial sur CPU, métriques, registre, reprise, rapport ; rejouée dans un environnement propre | Q6 Q7 | test-driven-development | Sortie archivée ; un cas de fuite piégé est détecté ; reconstruction depuis un clone ou un environnement neuf réussie | P0-35, P0-39, P0-40, P0-41, P0-43, P0-13 |
| RM-10 | ★ | code | Renforcer `check_microtasks.py` (GPU et spike citent `vram-preflight`, comptes ★ du plan lus depuis le script, skills cités existants) et brancher `check_microtasks`, `check_roadmap` et `wiki-lint` sur `make check` | Q7 | constraint-driven-development | Tests des trois contrôles ; `make check` les exécute | P0-42 |
| RM-11 | ★ | décision | Définir l'estimand (différence de macro-F1 entre recettes sous variation de graine), le rééchantillonnage hiérarchique (exemples ou patients, puis graines) ou la présentation séparée, la famille de comparaisons de Holm, la taille d'effet minimale utile | Q3 | paired-comparison | Section statistique de `PROTOCOLE.md`, remplaçant la règle ad hoc des deux écarts-types | P0-32, RM-02 |
| RM-12 | ★ | doc | Schéma de preuve des scorecards (exigence, artefact et empreinte, commande de reproduction, attendu et observé, confirmation indépendante avec son degré, date, défaut résiduel, justification) et degrés d'indépendance (code, données, méthode, personne ou contexte, reconstruction à froid) | Q12 Q7 | claim-gate | `scorecards/TEMPLATE.md` ; règles dans `PROTOCOLE.md` | P0-42 |
| RM-13 | ★ | décision | Présélectionner l'élève du premier cycle (deux à trois candidats, règle écrite avant lecture des résultats) à partir du spike de compatibilité | Q2 | experiment-preregistration | ADR-élève daté avant tout run comparatif | P0-06 |
| RM-14 | ★ | mesure | Raccourcis sur les références : TF-IDF et régression logistique avec plis par patient contre plis par auteur, comparés au modèle témoin de P0-30 | Q4 | leakage-guard, paired-comparison | Verdict apparié ; ADR si l'écart est significatif | P1-06, P0-29, P0-30 |
| RM-15 | ★ | décision | Porte go/no-go après les références : la comparaison est-elle informative (variance, puissance, raccourcis), ou faut-il arrêter ou simplifier avant le LLM | Q2 | doubt-driven-development | Décision datée avec les chiffres de P1-04, P1-06, P1-07 et RM-14 | P1-04, P1-06, P1-07, RM-14 |
| RM-16 | ★ | GPU | Mesure pilote de débit : un pli, une configuration LoRA, 100 pas ; recaler budgets et calendrier (hypothèse, mesure, marge) | Q8 | vram-preflight, run-registry | Tableau hypothèse, mesure, marge ; `PROTOCOLE.md` complété ; aucune durée annoncée avant cette mesure | P1-12 |
| RM-17 | ★ | décision | Porte go/no-go après la LoRA de référence : la distillation se poursuit comme question scientifique, ou comme expérience d'apprentissage limitée si la LoRA est dominée par l'encodeur | Q2 | doubt-driven-development | Décision datée | P1-20, P1-26 |
| RM-18 | ★ | doc | Ingérer au wiki les papiers A1, A2, A3 et A7 du Lot A avant leur première utilisation | Q11 | wiki-ingest | Quatre pages sources à citations par lignes ; `wiki-lint` vert | P0-47 |
| RM-19 | ★ | GPU | Spike de distillation miniature : un pli ou un sous-échantillon, une paire professeur élève, perte CE et KL ; écart avec la recette LMSYS exacte documenté (CE, deux KL, deux pertes cosinus) ; coût du run complet estimé ; règle go/no-go préenregistrée | Q2 Q8 | distillation-pipeline, vram-preflight | Run au registre ; coût mesuré ; décision écrite | P2-01, P3-01, P1-20, RM-18 |
| RM-20 | ★ | mesure | Ouverture unique du test scellé pour la comparaison confirmatoire, via le seul script autorisé | Q2 | leakage-guard | Un seul accès journalisé ; verdict confirmatoire en trois valeurs | P3-07, P0-34 |
| RM-21 | ★ | décision | Porte go/no-go après le verdict de distillation : le meilleur candidat mérite-t-il calibration et robustesse, ou le budget manque-t-il pour lever l'incertitude | Q2 | doubt-driven-development | Décision datée | RM-20 |
| RM-22 | ★ | code | Valider la prédiction conforme au-delà de la proximité des trois outils : cas jouets analytiques, invariants, couverture conditionnelle (par classe, par spécialité), test sous rupture d'échangeabilité | Q5 | test-driven-development | Tests verts ; couverture conditionnelle rapportée avec ses limites | P4-05 |
| RM-23 | ★ | doc | Ingérer au wiki TRIPOD-LLM (A8) avant la carte de modèle | Q11 | wiki-ingest | Page source à citations ; `wiki-lint` vert | P0-47 |
| RM-24 | ★ | doc | Générer `tasks/plan.md` et `tasks/todo.md` depuis la feuille de route ; relancer les deux vérificateurs | Q11 Q7 | planning-and-task-breakdown | `check_microtasks.py` et `check_roadmap.py` verts ; todo généré sans identifiant manquant | - |

---

## Mode d'emploi pour l'agent

- **L'ordre d'exécution est celui de `roadmap_unifié.md`**, qui place chaque micro-tâche une fois et vérifie les dépendances (`scripts/check_roadmap.py`). `tasks/todo.md` en est généré.
- Une tâche se clôt sur sa preuve de fin, jamais sur une impression. Une preuve manquante laisse la tâche ouverte.
- Relancer `python scripts/check_microtasks.py` après toute modification de ce fichier.
