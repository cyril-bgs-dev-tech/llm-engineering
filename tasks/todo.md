# Liste de tâches (générée)

Fichier généré par `python3 scripts/check_roadmap.py --export` depuis `roadmap_unifié.md` et `MICROTACHES.md`.
Ne pas l'éditer à la main hors des cases à cocher ; toute autre modification se fait dans le backlog ou la feuille de route.

## Étape R0 : cadrage et fondations légères

- [x] RM-24 (doc) : Générer `tasks/plan.md` et `tasks/todo.md` depuis la feuille de route ; relancer les deux vérificateurs
  - Preuve de fin : `check_microtasks.py` et `check_roadmap.py` verts ; todo généré sans identifiant manquant
  - Skills : planning-and-task-breakdown ; dépendances : aucune
- [x] RM-01 (doc) : Archiver l'offre CHUGA : texte intégral fourni par Cyril, URL ou PDF, date de consultation, SHA-256, dans `docs/offre/`
  - Preuve de fin : Fichier archivé et empreinte consignée ; tout le périmètre cite cette archive et non la mémoire
  - Skills : claim-gate ; dépendances : aucune
- [ ] P0-02 (décision) : Trancher emplacement du dossier, dépôt Git, périmètre (chemin court ou complet), date limite CHUGA, démo locale ou publique (décisions 1 à 5 du plan V6)
  - Preuve de fin : ADR-002 : une ligne par décision, réponse datée de Cyril
  - Skills : interview-me, documentation-and-adrs ; dépendances : aucune
- [x] RM-02 (décision) : Fixer le cap du premier cycle : budget B (heures GPU) et N (essais de réglage par famille), métrique primaire, seuil « pratiquement utile », définition de « local » (données, calcul, démonstration), objectif neutre quant au vainqueur
  - Preuve de fin : ADR-004 avec les valeurs de Cyril, ou valeur provisoire datée ; B et N obligatoires avant P0-46
  - Skills : interview-me, documentation-and-adrs ; dépendances : P0-02
- [ ] RM-03 (code) : `git init` local, `.gitignore` (data/, models/, artifacts/, .venv/, caches, sorties de runs lourdes), commit d'amorçage présenté à Cyril
  - Preuve de fin : `git check-ignore data/x` confirme l'exclusion ; aucun commit sans l'accord de Cyril ; aucun dépôt distant créé
  - Skills : git-workflow-and-versioning ; dépendances : P0-02
- [ ] RM-04 (doc) : `SPEC-P0.md` courte (objectifs, commandes canoniques via `uv run` avec sortie UTF-8, structure, style, tests, limites toujours, demander, jamais, critères de succès) ; une seule source de règles pour CLAUDE.md et AGENTS.md
  - Preuve de fin : SPEC-P0 validée par Cyril ; `docs/COMMANDES.md` ; AGENTS.md aligné sur CLAUDE.md, chemins en `.codex`
  - Skills : spec-driven-development ; dépendances : RM-03, RM-02

## Étape R1 : socle machine minimal

- [x] RM-05 (code) : Mini-registre de runs : fichier JSON en ajout seul, bibliothèque standard, validateur, sans dépendance, avant tout spike
  - Preuve de fin : Test : un écrasement est refusé ; format compatible avec P0-41
  - Skills : run-registry, test-driven-development ; dépendances : RM-03
- [x] P0-04 (spike) : Installer PyTorch (cu128 puis cu130) dans un environnement jetable ; vérifier que `sm_120` figure dans `torch.cuda.get_arch_list()`, qu'un produit matriciel bf16 et un `scaled_dot_product_attention` s'exécutent
  - Preuve de fin : Sortie archivée dans le wiki (page `env-blackwell`), versions avec suffixe `+cuXXX`
  - Skills : vram-preflight ; dépendances : RM-05
- [x] P0-05 (spike) : Installer transformers v5, peft, trl, accelerate, bitsandbytes ; charger un modèle de 1 milliard de paramètres au plus en 4 bits NF4 et faire 10 pas LoRA
  - Preuve de fin : Journal de 10 pas sans erreur ; tableau bibliothèque, version, sm_120 oui ou non
  - Skills : vram-preflight, debugging-and-error-recovery ; dépendances : P0-04
- [x] RM-06 (mesure) : Mesurer la machine telle que WSL la voit : RAM visible, disque libre, pilote et mémoire GPU, un chargement de poids sur ext4 contre `/mnt/d`, emplacement de `HF_HOME` et des points de sauvegarde
  - Preuve de fin : Page wiki `env-blackwell` et un run au registre ; écart avec « environ 96 Go de RAM » de CLAUDE.md consigné
  - Skills : vram-preflight ; dépendances : P0-05, RM-05
- [x] P0-11 (code) : Verrouiller l'environnement (`uv.lock`), écrire le Dockerfile, créer `hardware/rtx5090.yaml`
  - Preuve de fin : `docker build` et `uv sync --frozen` réussissent sur machine propre ; profil lu par un test
  - Skills : ci-cd-and-automation ; dépendances : P0-04, P0-05
- [x] P0-12 (doc) : Auditer la licence de chaque dépendance et dépôt consulté (TRL, PEFT, MAPIE, TorchCP en LGPL, cleanlab, EDS-NLP, DistiLLM-2...)
  - Preuve de fin : `docs/LICENCES.md` : licence, usage, compatibilité
  - Skills : security-and-hardening ; dépendances : P0-11

## Étape R2 : viabilité des données (CPU seulement)

- [x] P0-14 (code) : Script de téléchargement de PARHAF avec révision épinglée et empreintes SHA-256
  - Preuve de fin : Rejoué sur machine propre : mêmes empreintes ; `data/` ignoré par Git
  - Skills : dataset-intake ; dépendances : P0-11, RM-03
- [x] P0-15 (doc) : Lire à la source la licence et les usages permis ou interdits de PARHAF ; consigner le texte exact
  - Preuve de fin : Section licence de `data/cards/parhaf.md` avec URL et citations littérales
  - Skills : dataset-intake ; dépendances : P0-14
- [x] P0-21 (mesure) : Compter dans les données : patients, documents, spécialités, types de documents, longueurs en tokens de chaque tokenizer candidat
  - Preuve de fin : Tableau versionné ; chaque chiffre cite sa source, la révision épinglée (sha du dépôt HF) et son périmètre (publié, embargo, total) ; divergences des sources (4 254 ou 4 259 patients, 18 ou 20 spécialités, 6 185 ou 6 190 documents) tranchées par la donnée
  - Skills : dataset-intake ; dépendances : P0-14
- [x] P0-22 (mesure) : Mesurer la présence du diagnostic principal CIM-10 dans `suggested_scenario` : taux par pool et spécialité, formats rencontrés
  - Preuve de fin : Tableau de présence ; liste des patients sans étiquette ; décision sur leur exclusion
  - Skills : dataset-intake ; dépendances : P0-14
- [x] P0-17 (mesure) : Chercher des motifs de données personnelles sur 200 documents (noms, dates complètes, numéros, adresses)
  - Preuve de fin : Rapport : zéro, ou liste des cas douteux signalés à Cyril
  - Skills : security-and-hardening ; dépendances : P0-14
- [x] P0-27 (code) : Obtenir la nomenclature CIM-10 officielle (conditions de réutilisation lues) ; en tirer noms et hiérarchie chapitre, bloc, code
  - Preuve de fin : Fichier versionné ; test de cohérence (chaque code a son bloc et son chapitre)
  - Skills : source-driven-development ; dépendances : P0-12
- [x] P0-23 (mesure) : Distribution des classes CIM-10 aux trois niveaux (chapitre, bloc, trois caractères) et seuil minimal d'exemples par classe
  - Preuve de fin : Histogrammes ; nombre de classes sous le seuil par niveau
  - Skills : dataset-intake ; dépendances : P0-22, P0-27
- [x] P0-20 (doc) : Déduire des conditions d'usage de PARHAF les règles de formulation (CV, LinkedIn, démo, publication)
  - Preuve de fin : Page `regles-de-formulation` consultée par claim-gate
  - Skills : claim-gate ; dépendances : P0-15
- [x] P0-31 (mesure) : Vérifier l'état de l'ouverture du test embargoé (page du jeu, CodaBench) ; consigner règles et calendrier
  - Preuve de fin : Note datée ; nouvelle vérification planifiée en P3-15
  - Skills : dataset-intake ; dépendances : P0-15
- [x] P0-16 (doc) : Fiche du jeu PARHAF : provenance, découpage officiel, distribution, longueurs, biais connus, ce que le jeu ne représente pas
  - Preuve de fin : `data/cards/parhaf.md` complète, chaque champ tiré d'une mesure de P0-21
  - Skills : dataset-intake ; dépendances : P0-15, P0-21
- [x] P0-32 (décision) : Choisir l'unité d'entrée : un document, ou un patient (documents concaténés par type, ordre fixe) ; règle de troncature
  - Preuve de fin : Règle dans `PROTOCOLE.md` appuyée par les longueurs de P0-21
  - Skills : experiment-preregistration ; dépendances : P0-21
- [x] P0-33 (décision) : Politique des classes rares : seuil minimal, regroupement hiérarchique, classe « autre »
  - Preuve de fin : Règle écrite et appliquée par script
  - Skills : experiment-preregistration ; dépendances : P0-23
- [x] RM-07 (décision) : Préenregistrer les règles de split : unité de split et de bootstrap, groupement par auteur contre stratification (règle si incompatibles), tolérance de déséquilibre, auteurs présents dans une seule classe, seuil chiffré du « raccourci d'auteur » fixé avant son observation, statut confirmatoire ou exploratoire de chaque split
  - Preuve de fin : Section « splits » de `PROTOCOLE.md` en brouillon daté, antérieure à P0-30
  - Skills : experiment-preregistration ; dépendances : P0-23, P0-32, P0-33
- [x] P0-28 (code) : Découpage par patient : test interne scellé et 5 plis stratifiés, graine fixée
  - Preuve de fin : Fichiers d'identifiants et SHA-256 ; test : aucun patient dans deux partitions
  - Skills : leakage-guard, test-driven-development ; dépendances : P0-22, P0-33, RM-07
- [x] P0-29 (code) : Plis groupés par auteur, second découpage de contrôle
  - Preuve de fin : Fichier d'identifiants ; test : aucun auteur dans deux plis
  - Skills : leakage-guard ; dépendances : P0-28
- [x] P0-30 (mesure) : Mesurer le raccourci d'auteur : un modèle simple (TF-IDF et régression logistique) prédit spécialité et chapitre à partir du seul trigramme de l'auteur et d'un échantillon de style
  - Preuve de fin : Score face au seuil chiffré fixé par RM-07 avant observation ; si le seuil est dépassé, les plis par auteur deviennent la métrique principale (ADR)
  - Skills : leakage-guard ; dépendances : P0-28, RM-07
- [x] P0-34 (doc) : Définir l'accès au test scellé : un seul script d'évaluation finale peut le charger
  - Preuve de fin : Test automatique qui échoue si un autre module le lit
  - Skills : leakage-guard ; dépendances : P0-28
- [x] RM-08 (décision) : Porte go/no-go sur la viabilité des données : continuer, simplifier la cible (niveau chapitre, regroupements) ou changer de tâche
  - Preuve de fin : Décision datée appuyée par les chiffres de P0-22, P0-23, P0-28, P0-29, P0-30
  - Skills : doubt-driven-development ; dépendances : P0-22, P0-23, P0-28, P0-29, P0-30

## Étape R3 : fil synthétique de bout en bout

- [x] P0-35 (code) : Schéma Pydantic du contrat de tâche (type, entrées, classes, hiérarchie, format de sortie, métriques, abstention) avec ses tests
  - Preuve de fin : Tests verts ; un contrat invalide est rejeté avec un message clair
  - Skills : test-driven-development ; dépendances : P0-11
- [x] P0-36 (doc) : Contrat de la tâche de contrôle `parhaf_doctype`
  - Preuve de fin : YAML valide ; chaque classe nommée et définie
  - Skills : dataset-intake ; dépendances : P0-35, P0-21
- [x] P0-37 (doc) : Contrat `parhaf_specialty`
  - Preuve de fin : YAML valide ; chaque classe nommée et définie
  - Skills : dataset-intake ; dépendances : P0-35, P0-21
- [x] P0-39 (doc) : Tâche jouet synthétique (deux classes, 50 exemples) avec son contrat
  - Preuve de fin : YAML valide et données générées par un script déterministe
  - Skills : test-driven-development ; dépendances : P0-35
- [x] P0-38 (doc) : Contrat `parhaf_cim10_chapter` : noms officiels et définitions opérationnelles des chapitres
  - Preuve de fin : YAML valide ; définitions relues en contexte neuf
  - Skills : dataset-intake, doubt-driven-development ; dépendances : P0-27, P0-35, P0-23
- [x] P0-41 (code) : Squelette du registre de runs : écriture immuable, schéma des champs, validateur
  - Preuve de fin : Un second écrasement échoue ; un run sans `env` est refusé
  - Skills : run-registry, test-driven-development ; dépendances : P0-11
- [x] P0-43 (code) : Chargeur de données générique : lit le contrat et un adaptateur (identifiant, texte, étiquette)
  - Preuve de fin : Deux tâches chargées sans branche propre à l'une d'elles ; l'empreinte des partitions est comparée à une référence versionnée à chaque chargement
  - Skills : api-and-interface-design ; dépendances : P0-35, P0-36
- [x] P0-40 (code) : Tests `leakage-guard` : patient, quasi-doublons et gabarits (MinHash), test scellé, hors pli
  - Preuve de fin : `tests/test_leakage.py` vert ; un cas piégé volontairement fait échouer le test
  - Skills : leakage-guard ; dépendances : P0-28, P0-29
- [x] P0-42 (doc) : `CONSTRAINTS.md` et `make check` (types, lint, tests, gitleaks, couverture des lignes modifiées)
  - Preuve de fin : `make check` vert ; chaque seuil a sa raison ; gitleaks actif dès le premier commit
  - Skills : constraint-driven-development ; dépendances : P0-11
- [x] P0-13 (code) : Lancement par `accelerate launch` sur 1 GPU, avec point de sauvegarde et reprise vérifiés
  - Preuve de fin : Un run interrompu puis repris retrouve la même perte dans la tolérance fixée
  - Skills : incremental-implementation ; dépendances : P0-05
- [x] P0-44 (code) : Test de transposabilité : la tâche jouet et `parhaf_doctype` passent par la même chaîne (chargement, 10 pas, évaluation, registre) sans une ligne propre à l'une ; le test existe en deux variantes, `backend=cpu` (petit modèle, CI sans GPU) et `backend=gpu`
  - Preuve de fin : Test vert dans les deux variantes ; ajouter une tâche de même famille ne modifie pas le noyau (seuls un YAML et un adaptateur dans un répertoire autorisé changent), coût d'ajout mesuré en fichiers, lignes et durée
  - Skills : test-driven-development ; dépendances : P0-43, P0-41, P0-39
- [x] RM-09 (mesure) : Fil synthétique de bout en bout : une commande (`make smoke`) enchaîne contrat, chargeur, split, modèle trivial sur CPU, métriques, registre, reprise, rapport ; rejouée dans un environnement propre
  - Preuve de fin : Sortie archivée ; un cas de fuite piégé est détecté ; reconstruction depuis un clone ou un environnement neuf réussie
  - Skills : test-driven-development ; dépendances : P0-35, P0-39, P0-40, P0-41, P0-43, P0-13
- [x] RM-10 (code) : Renforcer `check_microtasks.py` (GPU et spike citent `vram-preflight`, comptes ★ du plan lus depuis le script, skills cités existants) et brancher `check_microtasks`, `check_roadmap` et `wiki-lint` sur `make check`
  - Preuve de fin : Tests des trois contrôles ; `make check` les exécute
  - Skills : constraint-driven-development ; dépendances : P0-42

## Étape R4 : compatibilité des modèles et budget

- [x] P0-01 (décision) : Cyril accepte ou écarte les conditions d'accès des modèles conditionnés (Gemma 4, MedGemma) sur Hugging Face
  - Preuve de fin : ADR-001 : liste des modèles autorisés ; aucun jeton dans le dépôt
  - Skills : interview-me ; dépendances : aucune
- [x] P0-03 (décision) : Fixer fournisseur et plafond de location, règle de revue croisée externe, limite de la relecture d'étiquettes (décisions 7 à 9)
  - Preuve de fin : ADR-003 ; « non décidé » accepté si daté
  - Skills : interview-me ; dépendances : P0-02
- [x] P0-06 (spike) : Pour chaque candidat (Qwen3.5 4B et 9B, Qwen3.8-27B, Gemma 4 E4B et 31B, MedGemma 4B), vérifier la classe de chargement réellement utilisable (les cartes officielles de Qwen3.8-27B et de Gemma 4 31B recommandent `AutoModelForMultimodalLM` et ne mentionnent aucune classification), que `pad_token` est défini, qu'un passage avant et arrière tient ; élèves d'abord, gros professeur chargé une seule fois (compatibilité puis 10 pas de P0-08)
  - Preuve de fin : Tableau de compatibilité par modèle (classe de chargement, pad, tête, erreurs) dans le wiki ; repli « verbaliseur » consigné pour tout modèle sans tête de classification utilisable
  - Skills : lora-classifier-recipe, vram-preflight ; dépendances : P0-05, P0-01
- [x] RM-13 (décision) : Présélectionner l'élève du premier cycle (deux à trois candidats, règle écrite avant lecture des résultats) à partir du spike de compatibilité
  - Preuve de fin : ADR-élève daté avant tout run comparatif
  - Skills : experiment-preregistration ; dépendances : P0-06
- [x] P0-08 (spike) : Banc de 10 pas du plus gros professeur candidat en QLoRA 4 bits, 1 024 tokens, gradient checkpointing, batch effectif 64 par accumulation
  - Preuve de fin : Pic de mémoire réservée (cible sous 30 Go) et temps par pas au registre ; sinon plan B écrit (professeur plus petit ou déclencheur de location)
  - Skills : vram-preflight ; dépendances : P0-06, RM-05
- [x] P0-45 (doc) : Budget de calcul par vague (heures GPU), arrêt anticipé, règle de repli
  - Preuve de fin : Tableau dans `PROTOCOLE.md`
  - Skills : experiment-preregistration ; dépendances : P0-08

## Étape R5 : geler le protocole

- [ ] RM-11 (décision) : Définir l'estimand (différence de macro-F1 entre recettes sous variation de graine), le rééchantillonnage hiérarchique (exemples ou patients, puis graines) ou la présentation séparée, la famille de comparaisons de Holm, la taille d'effet minimale utile
  - Preuve de fin : Section statistique de `PROTOCOLE.md`, remplaçant la règle ad hoc des deux écarts-types
  - Skills : paired-comparison ; dépendances : P0-32, RM-02
- [x] RM-12 (doc) : Schéma de preuve des scorecards (exigence, artefact et empreinte, commande de reproduction, attendu et observé, confirmation indépendante avec son degré, date, défaut résiduel, justification) et degrés d'indépendance (code, données, méthode, personne ou contexte, reconstruction à froid)
  - Preuve de fin : `scorecards/TEMPLATE.md` ; règles dans `PROTOCOLE.md`
  - Skills : claim-gate ; dépendances : P0-42
- [x] P0-47 (doc) : Ingérer au wiki trois papiers du Lot A (A4 PARHAF, A5, A6 ; voir `BOITE_A_OUTILS.md`) ; A1, A2, A3 et A7 par RM-18, A8 par RM-23
  - Preuve de fin : Trois pages sources à citations par lignes ; `wiki-lint` sans erreur
  - Skills : wiki-ingest ; dépendances : aucune
- [ ] P0-46 (doc) : Rédiger `PROTOCOLE.md` : métriques, tests statistiques, seuils de décision, graines, niveau conforme, règles de gel ; chaque expérience porte l'étiquette REP (vérification d'un mécanisme exact de la recette source), ADAPT (transfert au clinique français) ou EXPLORE ; développement sur plis, confirmation sur le test scellé ouvert une seule fois ; relecture adversariale en contexte neuf ; calcul de son SHA-256
  - Preuve de fin : Fichier figé, empreinte consignée avant tout run de P1 et dans une page wiki datée, constats de la relecture classés
  - Skills : experiment-preregistration, doubt-driven-development ; dépendances : P0-32, P0-33, P0-34, P0-41, P0-44, P0-45, RM-02, RM-07, RM-11, RM-12
- [ ] G-P0 (doc) : Scorecard G-P0 : note Q1 à Q12, une preuve par note, plan de rattrapage pour toute note sous le plancher du plan V6
  - Preuve de fin : `scorecards/G-P0.md`
  - Skills : claim-gate, wiki-lint ; dépendances : *

## Étape R6 : références sur la tâche principale

- [ ] P1-01 (code) : Harnais d'évaluation : accuracy, macro-F1, log loss, ECE, Spearman
  - Preuve de fin : Valeurs exactes sur 5 cas construits à la main
  - Skills : test-driven-development ; dépendances : P0-41
- [ ] P1-02 (code) : Outils de comparaison appariée : bootstrap, McNemar, permutation, correction de Holm ; vérifiés contre SciPy et statsmodels
  - Preuve de fin : Fausse alerte au plus 5 % sur données sans effet ; détection d'un effet injecté ; accord avec les bibliothèques
  - Skills : paired-comparison ; dépendances : P1-01
- [ ] P1-03 (mesure) : Bornes : classe majoritaire et tirage aléatoire sur les trois tâches
  - Preuve de fin : Lignes au registre
  - Skills : experiment-preregistration ; dépendances : P1-01
- [ ] P1-04 (mesure) : TF-IDF et régression logistique sur `parhaf_doctype`, réglage de C et des n-grammes sur validation
  - Preuve de fin : Run au registre avec intervalle de confiance
  - Skills : experiment-preregistration ; dépendances : P1-03
- [ ] P1-06 (mesure) : TF-IDF et régression logistique sur `parhaf_cim10_chapter`
  - Preuve de fin : Run au registre
  - Skills : experiment-preregistration ; dépendances : P1-04, P0-38
- [ ] P1-07 (GPU) : DrBERT ou CamemBERT-bio affiné sur `parhaf_cim10_chapter`, taux d'apprentissage réglé sur 4 valeurs
  - Preuve de fin : Run au registre ; nombre d'essais de réglage consigné
  - Skills : experiment-preregistration, vram-preflight ; dépendances : P1-06
- [ ] RM-14 (mesure) : Raccourcis sur les références : TF-IDF et régression logistique avec plis par patient contre plis par auteur, comparés au modèle témoin de P0-30
  - Preuve de fin : Verdict apparié ; ADR si l'écart est significatif
  - Skills : leakage-guard, paired-comparison ; dépendances : P1-06, P0-29, P0-30
- [ ] RM-15 (décision) : Porte go/no-go après les références : la comparaison est-elle informative (variance, puissance, raccourcis), ou faut-il arrêter ou simplifier avant le LLM
  - Preuve de fin : Décision datée avec les chiffres de P1-04, P1-06, P1-07 et RM-14
  - Skills : doubt-driven-development ; dépendances : P1-04, P1-06, P1-07, RM-14

## Étape R7 : une LoRA de référence (jalon A)

- [ ] P1-11 (GPU) : Criblage des points de départ : un pli, réglages identiques, deux à trois candidats fixés par RM-13 (au moins un généraliste) ; criblage de quatre à six modèles au chemin complet
  - Preuve de fin : Un run par modèle au registre
  - Skills : lora-classifier-recipe, vram-preflight ; dépendances : P0-06, P1-06, P0-43, RM-13
- [ ] P1-12 (décision) : Choisir l'élève selon la règle écrite avant le criblage (meilleur macro-F1 sous contrainte de VRAM et de latence)
  - Preuve de fin : ADR-élève ; règle datée avant P1-11
  - Skills : experiment-preregistration ; dépendances : P1-11
- [ ] RM-16 (GPU) : Mesure pilote de débit : un pli, une configuration LoRA, 100 pas ; recaler budgets et calendrier (hypothèse, mesure, marge)
  - Preuve de fin : Tableau hypothèse, mesure, marge ; `PROTOCOLE.md` complété ; aucune durée annoncée avant cette mesure
  - Skills : vram-preflight, run-registry ; dépendances : P1-12
- [ ] P1-13 (GPU) : Balayage du taux d'apprentissage LoRA (1e-5, 2e-5, 5e-5, 1e-4), trois graines
  - Preuve de fin : 12 runs ; courbe taux contre macro-F1
  - Skills : lora-classifier-recipe, vram-preflight ; dépendances : P1-12
- [ ] P1-19 (GPU) : Variance entre graines : cinq graines de la configuration réglée
  - Preuve de fin : Écart-type publié ; règle de décision de RM-11 appliquée
  - Skills : paired-comparison, vram-preflight ; dépendances : P1-13
- [ ] P1-20 (doc) : Geler la configuration de référence (LoRA réglée) : fichier de config et run_id
  - Preuve de fin : `configs/reference.yaml` citant le run_id
  - Skills : run-registry ; dépendances : P1-19
- [ ] P1-26 (GPU) : Rejouer le run de référence avec la même graine ; mesurer le déterminisme
  - Preuve de fin : Prédictions identiques ou écart borné, consigné
  - Skills : run-registry, vram-preflight ; dépendances : P1-20
- [ ] P1-23 (mesure) : Analyse d'erreurs initiale : matrice de confusion hiérarchique, par spécialité, longueur, type de document
  - Preuve de fin : Tableaux et 20 erreurs relues
  - Skills : paired-comparison ; dépendances : P1-20
- [ ] P1-25 (doc) : Page d'analyse V0 dans le wiki et premier `RESULTATS.md` (positifs et négatifs)
  - Preuve de fin : Chaque chiffre cite un run_id ; `wiki-lint` vert
  - Skills : wiki-ingest, claim-gate ; dépendances : P1-23, RM-14
- [ ] RM-17 (décision) : Porte go/no-go après la LoRA de référence : la distillation se poursuit comme question scientifique, ou comme expérience d'apprentissage limitée si la LoRA est dominée par l'encodeur
  - Preuve de fin : Décision datée
  - Skills : doubt-driven-development ; dépendances : P1-20, P1-26
- [ ] G-P1 (doc) : Scorecard G-P1
  - Preuve de fin : `scorecards/G-P1.md`
  - Skills : claim-gate ; dépendances : *

## Étape R8 : spike de distillation miniature

- [ ] RM-18 (doc) : Ingérer au wiki les papiers A1, A2, A3 et A7 du Lot A avant leur première utilisation
  - Preuve de fin : Quatre pages sources à citations par lignes ; `wiki-lint` vert
  - Skills : wiki-ingest ; dépendances : P0-47
- [ ] P2-01 (GPU) : Professeur 1 : réglage minimal du taux sur un pli (QLoRA)
  - Preuve de fin : Run au registre
  - Skills : lora-classifier-recipe, vram-preflight ; dépendances : P0-08, P1-20
- [ ] P3-01 (code) : Perte de distillation `alpha·CE + (1 - alpha)·T²·KL` avec tests de gradient et cas limites
  - Preuve de fin : alpha=1 retrouve la CE ; KL nulle si les distributions sont égales
  - Skills : distillation-pipeline, test-driven-development ; dépendances : P1-20
- [ ] RM-19 (GPU) : Spike de distillation miniature : un pli ou un sous-échantillon, une paire professeur élève, perte CE et KL ; écart avec la recette LMSYS exacte documenté (CE, deux KL, deux pertes cosinus) ; coût du run complet estimé ; règle go/no-go préenregistrée
  - Preuve de fin : Run au registre ; coût mesuré ; décision écrite
  - Skills : distillation-pipeline, vram-preflight ; dépendances : P2-01, P3-01, P1-20, RM-18

## Étape R9 : expérience confirmatoire de distillation

- [ ] P2-02 (GPU) : Professeur 1 en cinq plis ; probabilités hors pli en Parquet avec manifeste
  - Preuve de fin : Fichiers et manifeste, un fichier par pli
  - Skills : distillation-pipeline, vram-preflight ; dépendances : P2-01
- [ ] P2-03 (code) : Contrôle hors pli : chaque exemple n'est prédit que par le professeur qui ne l'a pas vu
  - Preuve de fin : Test vert sur les logits stockés
  - Skills : leakage-guard ; dépendances : P2-02, P0-40
- [ ] P2-06 (mesure) : Audit des étiquettes : cleanlab sur les probabilités hors pli, file de relecture, relecture de 100 cas pour cohérence avec les définitions
  - Preuve de fin : `relabel_queue.csv` et rapport ; aucune étiquette de test modifiée
  - Skills : distillation-pipeline ; dépendances : P2-02
- [ ] P2-07 (GPU) : Pré-entraînement sur tâche voisine (`parhaf_specialty`, MorFITT en option), fusion de la LoRA, tête neuve
  - Preuve de fin : Runs et point de contrôle fusionné
  - Skills : lora-classifier-recipe, vram-preflight ; dépendances : P1-20, P0-37
- [ ] P2-08 (mesure) : Gain de la tâche voisine contre la référence, test apparié, trois graines
  - Preuve de fin : Verdict en trois valeurs
  - Skills : paired-comparison ; dépendances : P2-07, P1-19
- [ ] G-P2 (doc) : Scorecard G-P2
  - Preuve de fin : `scorecards/G-P2.md`
  - Skills : claim-gate ; dépendances : *
- [ ] P3-02 (GPU) : Élève distillé d'un professeur, alpha et T par défaut
  - Preuve de fin : Run au registre
  - Skills : distillation-pipeline, vram-preflight ; dépendances : P3-01, P2-03
- [ ] P3-07 (mesure) : Verdict apparié V1 : distillation, tâche voisine, les deux, contre la référence
  - Preuve de fin : Table de verdicts avec intervalles
  - Skills : paired-comparison ; dépendances : P3-02, P2-08
- [ ] RM-20 (mesure) : Ouverture unique du test scellé pour la comparaison confirmatoire, via le seul script autorisé
  - Preuve de fin : Un seul accès journalisé ; verdict confirmatoire en trois valeurs
  - Skills : leakage-guard ; dépendances : P3-07, P0-34
- [ ] RM-21 (décision) : Porte go/no-go après le verdict de distillation : le meilleur candidat mérite-t-il calibration et robustesse, ou le budget manque-t-il pour lever l'incertitude
  - Preuve de fin : Décision datée
  - Skills : doubt-driven-development ; dépendances : RM-20
- [ ] G-P3 (doc) : Scorecard G-P3
  - Preuve de fin : `scorecards/G-P3.md`
  - Skills : claim-gate ; dépendances : *

## Étape R10 : fiabilité du meilleur candidat

- [x] RM-23 (doc) : Ingérer au wiki TRIPOD-LLM (A8) avant la carte de modèle
  - Preuve de fin : Page source à citations ; `wiki-lint` vert
  - Skills : wiki-ingest ; dépendances : P0-47
- [ ] P4-04 (code) : Calibration par température et ECE avant et après
  - Preuve de fin : Diagramme de fiabilité
  - Skills : model-card-calibration ; dépendances : P3-07
- [ ] P4-05 (code) : Prédiction conforme avec MAPIE (LAC, APS, RAPS) ; couverture empirique contre niveau visé
  - Preuve de fin : Couverture mesurée sur le test (hypothèse d'échangeabilité énoncée) ; validation de RM-22
  - Skills : model-card-calibration ; dépendances : P4-04
- [ ] RM-22 (code) : Valider la prédiction conforme au-delà de la proximité des trois outils : cas jouets analytiques, invariants, couverture conditionnelle (par classe, par spécialité), test sous rupture d'échangeabilité
  - Preuve de fin : Tests verts ; couverture conditionnelle rapportée avec ses limites
  - Skills : test-driven-development ; dépendances : P4-05
- [ ] P4-08 (code) : Politique d'abstention et courbe automatisation contre exactitude ; recalibration si un modèle quantifié est retenu
  - Preuve de fin : Courbe et point de fonctionnement
  - Skills : model-card-calibration ; dépendances : P4-05
- [ ] P4-10 (doc) : Carte de modèle et checklist TRIPOD-LLM remplie
  - Preuve de fin : `model_cards/<modèle>.md` et checklist des 19 items
  - Skills : model-card-calibration ; dépendances : P4-08
- [ ] G-P4 (doc) : Scorecard G-P4
  - Preuve de fin : `scorecards/G-P4.md`
  - Skills : claim-gate ; dépendances : *

## Étape R11 : livraison ciblée (jalon B)

- [ ] P5-09 (mesure) : Reconstruction à froid : clone neuf puis `make reproduce-small`
  - Preuve de fin : Chiffre clé reproduit dans la tolérance
  - Skills : ci-cd-and-automation ; dépendances : P0-11, P0-42, P1-20
- [ ] P5-12 (doc) : Rapport final et textes sortants (CV, LinkedIn, lettre) passés par `claim-gate`
  - Preuve de fin : Tableau de preuve joint
  - Skills : claim-gate ; dépendances : P4-10, P5-09
- [ ] G-P5 (doc) : Scorecard G-P5
  - Preuve de fin : `scorecards/G-P5.md`
  - Skills : claim-gate ; dépendances : *

## Étape R12 : compléments de références et de réglage (chemin complet)

- [ ] P1-05 (mesure) : TF-IDF et régression logistique sur `parhaf_specialty`
  - Preuve de fin : Run au registre
  - Skills : experiment-preregistration ; dépendances : P1-04
- [ ] P1-08 (GPU) : doctomodernbert-fr (contexte long) sur la même tâche
  - Preuve de fin : Run au registre
  - Skills : experiment-preregistration, vram-preflight ; dépendances : P1-07
- [ ] P1-09 (GPU) : LLM candidat en zéro-shot, invite avec noms et définitions des classes
  - Preuve de fin : Run et invite figée
  - Skills : experiment-preregistration, vram-preflight ; dépendances : P0-38, P0-06
- [ ] P1-10 (GPU) : Même modèle en few-shot (3 puis 8 exemples tirés de l'entraînement seulement)
  - Preuve de fin : Run ; contrôle : exemples hors test
  - Skills : leakage-guard, vram-preflight ; dépendances : P1-09
- [ ] P1-14 (GPU) : Balayage du rang et d'alpha autour du meilleur taux
  - Preuve de fin : Runs au registre
  - Skills : lora-classifier-recipe, vram-preflight ; dépendances : P1-13
- [ ] P1-15 (GPU) : Balayage de la longueur de contexte et de la troncature (milieu, tête et fin)
  - Preuve de fin : Runs au registre
  - Skills : lora-classifier-recipe, vram-preflight ; dépendances : P1-13
- [ ] P1-16 (GPU) : Nombre d'époques et ordonnanceur
  - Preuve de fin : Runs au registre
  - Skills : lora-classifier-recipe, vram-preflight ; dépendances : P1-13
- [ ] P1-17 (GPU) : Tête de classification contre verbaliseur
  - Preuve de fin : Verdict en trois valeurs
  - Skills : paired-comparison, vram-preflight ; dépendances : P1-14
- [ ] P1-18 (GPU) : Pooling (dernier, moyenne, max) avec et sans masque bidirectionnel
  - Preuve de fin : Verdicts en trois valeurs
  - Skills : paired-comparison, vram-preflight ; dépendances : P1-14
- [ ] P1-21 (doc) : Documenter le budget de réglage par méthode (essais, heures) pour garantir un budget égal
  - Preuve de fin : Tableau méthode, essais, heures
  - Skills : run-registry ; dépendances : P1-20
- [ ] P1-22 (GPU) : Courbe d'apprentissage de la référence à 10, 25, 50, 100 % de l'entraînement
  - Preuve de fin : Courbe et runs
  - Skills : run-registry, vram-preflight ; dépendances : P1-20
- [ ] P1-24 (mesure) : Raccourcis : même modèle avec plis par patient contre plis par auteur ; comparaison au modèle témoin de P0-30
  - Preuve de fin : Verdict apparié ; ADR si l'écart est significatif
  - Skills : leakage-guard ; dépendances : P1-20, P0-29, P0-30
- [ ] P0-07 (spike) : Mesurer débit et mémoire de SDPA contre FlashAttention 2 (et Liger-Kernel si installable) sur SM120
  - Preuve de fin : Courbes débit et mémoire pour 3 longueurs ; décision écrite
  - Skills : performance-optimization, vram-preflight ; dépendances : P0-05

## Étape R13 : leviers de données et de distillation

- [ ] P0-18 (doc) : Entrée des sous-ensembles annotés PARHAF (conclusion, pseudo, biomarqueurs, infectiologie, réponse au traitement) : licences et fiches, sans les utiliser avant P6
  - Preuve de fin : Cinq fiches courtes
  - Skills : dataset-intake ; dépendances : P0-15
- [ ] P0-19 (doc) : Entrée de PARCOMED : choisir la version (commerciale CC BY ou research only), fiche, taille de l'échantillon utilisable
  - Preuve de fin : Fiche et décision écrite sur la version
  - Skills : dataset-intake ; dépendances : P0-12
- [ ] P0-24 (doc) : Entrée de MorFITT : licence à la source, fiche, contrat `morfitt_specialites` (multilabel)
  - Preuve de fin : Fiche et YAML valide au schéma
  - Skills : dataset-intake ; dépendances : P0-12, P0-35
- [ ] P0-25 (doc) : Entrée de CLISTER : licence à la source, fiche, niveaux de similarité nommés et définis, contrat `clister_similarite` (pair_ordinal)
  - Preuve de fin : Fiche et YAML valide ; si la licence interdit l'usage, tâche retirée par ADR
  - Skills : dataset-intake ; dépendances : P0-12, P0-35
- [ ] P0-26 (doc) : Entrée de DiaMED (repli) : licence et fiche seulement
  - Preuve de fin : Fiche courte
  - Skills : dataset-intake ; dépendances : P0-12
- [ ] P2-04 (GPU) : Professeur 2 d'une autre famille en cinq plis
  - Preuve de fin : Fichiers et manifeste
  - Skills : distillation-pipeline, vram-preflight ; dépendances : P2-03
- [ ] P2-05 (mesure) : Score hors pli de chaque professeur et de leur moyenne ; accord entre professeurs
  - Preuve de fin : Tableau et kappa
  - Skills : paired-comparison ; dépendances : P2-04
- [ ] P2-09 (GPU) : Pré-entraînement continu léger sur un échantillon de PARCOMED, puis mesure
  - Preuve de fin : Verdict
  - Skills : paired-comparison, vram-preflight ; dépendances : P0-19, P1-20
- [ ] P2-10 (GPU) : Données synthétiques par les professeurs, amorcées sur des exemples d'entraînement seulement, avec identifiant de source ; contrôle de fuite
  - Preuve de fin : Fichier avec lignée ; test vert
  - Skills : leakage-guard, vram-preflight ; dépendances : P2-02
- [ ] P2-11 (GPU) : Tâches multi-étiquettes (MorFITT) et sur paires (CLISTER) de bout en bout avec le même code
  - Preuve de fin : Deux runs au registre sans branche propre à une tâche
  - Skills : test-driven-development, vram-preflight ; dépendances : P0-24, P0-25, P1-20
- [ ] P2-12 (doc) : Pages wiki des professeurs, de la qualité des étiquettes et de la tâche voisine
  - Preuve de fin : Pages et `wiki-lint` vert
  - Skills : wiki-update ; dépendances : P2-08
- [ ] P3-03 (GPU) : Balayage d'alpha et de T
  - Preuve de fin : Runs au registre
  - Skills : distillation-pipeline, vram-preflight ; dépendances : P3-02
- [ ] P3-04 (GPU) : Plusieurs professeurs : moyenne des probabilités contre pondération par score hors pli
  - Preuve de fin : Verdict
  - Skills : paired-comparison, vram-preflight ; dépendances : P2-05, P3-02
- [ ] P3-05 (GPU) : Direction de la KL (directe, inverse, asymétrique)
  - Preuve de fin : Verdict
  - Skills : paired-comparison, vram-preflight ; dépendances : P3-02
- [ ] P3-06 (GPU) : Distillation des justifications : tâche auxiliaire de génération
  - Preuve de fin : Verdict ; l'explication n'est jamais une preuve de qualité
  - Skills : distillation-pipeline, vram-preflight ; dépendances : P3-02
- [ ] P3-08 (GPU) : Variantes LoRA (DoRA, rsLoRA, PiSSA, LoRA+), chacune avec son propre balayage de taux
  - Preuve de fin : Verdicts ; protocole conforme à arXiv 2602.04998
  - Skills : lora-classifier-recipe, vram-preflight ; dépendances : P1-20
- [ ] P3-09 (GPU) : Pondération de classes, perte focale, lissage d'étiquettes
  - Preuve de fin : Verdicts
  - Skills : paired-comparison, vram-preflight ; dépendances : P1-20
- [ ] P3-10 (GPU) : Courbes d'apprentissage de l'élève distillé à 10, 25, 50, 100 %
  - Preuve de fin : Courbe
  - Skills : run-registry, vram-preflight ; dépendances : P3-07
- [ ] P3-11 (GPU) : Étiquettes nettoyées contre brutes : impact du nettoyage
  - Preuve de fin : Verdict
  - Skills : paired-comparison, vram-preflight ; dépendances : P2-06
- [ ] P3-12 (GPU) : Niveaux bloc et trois caractères avec la meilleure recette
  - Preuve de fin : Tableau par niveau
  - Skills : run-registry, vram-preflight ; dépendances : P3-07
- [ ] P3-13 (mesure) : Analyse d'erreurs approfondie : spécialité, auteur, longueur, classes rares
  - Preuve de fin : Rapport avec 50 erreurs relues
  - Skills : paired-comparison ; dépendances : P3-07
- [ ] P3-14 (doc) : Consolider verdicts, `RESULTATS.md`, pages wiki (méthodes, résultats négatifs), tableau coût contre qualité ; contre-lecture adversariale des verdicts
  - Preuve de fin : Cohérence vérifiée ; constats de la contre-lecture classés
  - Skills : wiki-update, claim-gate, doubt-driven-development ; dépendances : P3-13
- [ ] P3-15 (mesure) : Revérifier l'ouverture du test embargoé de PARHAF ; si ouvert, préparer la soumission unique
  - Preuve de fin : Note datée ; soumission préenregistrée si possible
  - Skills : dataset-intake ; dépendances : P0-31

## Étape R14 : compression et robustesse

- [ ] P0-10 (spike) : Quantifier un petit modèle dense en INT8 (bitsandbytes), FP8 et NVFP4 (llm-compressor) ; vérifier chargement et prédiction sur SM120
  - Preuve de fin : Tableau format, charge, prédit, VRAM, latence ; NVFP4 marqué utilisable ou non
  - Skills : performance-optimization, vram-preflight ; dépendances : P0-05
- [ ] P4-01 (GPU) : Fusion des LoRA des cinq plis contre ensemble des cinq
  - Preuve de fin : Verdict
  - Skills : paired-comparison, vram-preflight ; dépendances : P3-07
- [ ] P4-02 (GPU) : Quantification : INT8 bitsandbytes, GPTQ, FP8, NVFP4 ; qualité, latence, VRAM sur la tâche
  - Preuve de fin : Tableau format contre métriques, runs au registre
  - Skills : performance-optimization, vram-preflight ; dépendances : P4-01, P0-10
- [ ] P4-03 (GPU) : Augmentation au test (troncature, ordre des documents)
  - Preuve de fin : Verdict
  - Skills : paired-comparison, vram-preflight ; dépendances : P4-01
- [ ] P4-06 (code) : Vérification croisée des implémentations (MAPIE, TorchCP, maison) : contrôle d'implémentation, pas validation des hypothèses
  - Preuve de fin : Trois couvertures dans la même tolérance
  - Skills : doubt-driven-development ; dépendances : P4-05
- [ ] P4-07 (mesure) : Robustesse : perturbations (fautes, abréviations, coupures, ordre des sections) et spécialité exclue de l'entraînement
  - Preuve de fin : Courbes de dégradation
  - Skills : paired-comparison ; dépendances : P4-01
- [ ] P4-09 (mesure) : Front de Pareto qualité contre coût (VRAM, latence, énergie)
  - Preuve de fin : Graphique et tableau
  - Skills : performance-optimization ; dépendances : P4-02

## Étape R15 : industrialisation

- [ ] P0-09 (spike) : Servir un classifieur avec vLLM (ou documenter l'échec) et comparer à Transformers et FastAPI sur 100 requêtes
  - Preuve de fin : Décision écrite : vLLM utilisable pour la classification, oui ou non, version incluse
  - Skills : performance-optimization, vram-preflight ; dépendances : P0-05
- [ ] P5-01 (code) : Service FastAPI qui lit le contrat : prédiction, ensemble conforme, abstention
  - Preuve de fin : Tests d'API verts
  - Skills : api-and-interface-design ; dépendances : P4-08
- [ ] P5-02 (mesure) : Charge et latence p50 et p95 du service sur la 5090
  - Preuve de fin : Rapport
  - Skills : performance-optimization ; dépendances : P5-01
- [ ] P5-03 (mesure) : Backend vLLM (si validé en P0-09) contre Transformers : débit
  - Preuve de fin : Tableau
  - Skills : performance-optimization ; dépendances : P5-01, P0-09
- [ ] P5-04 (code) : Indexation ElasticSearch (texte et prédictions) en conteneur local
  - Preuve de fin : Requête de test
  - Skills : api-and-interface-design ; dépendances : P5-01
- [ ] P5-05 (code) : Composant EDS-NLP exposant le classifieur ; test d'interopérabilité
  - Preuve de fin : Pipeline EDS-NLP de test vert
  - Skills : source-driven-development ; dépendances : P5-01
- [ ] P5-06 (code) : CI GitLab : tests, types, lint, secrets, test de transposabilité
  - Preuve de fin : Pipeline vert
  - Skills : ci-cd-and-automation ; dépendances : P0-42
- [ ] P5-07 (doc) : `docs/TRANSPOSER_AU_CHU.md` exécuté à blanc sur une tâche factice
  - Preuve de fin : La tâche factice tourne en suivant le guide seul
  - Skills : documentation-and-adrs ; dépendances : P5-06
- [ ] P5-08 (doc) : Surveillance de dérive, règles de maintenance, seuils de réentraînement, retour arrière
  - Preuve de fin : Document et simulation de dérive
  - Skills : observability-and-instrumentation, shipping-and-launch ; dépendances : P5-01
- [ ] P5-10 (doc) : Revue indépendante : code-reviewer, security-auditor, test-engineer ; doubt-driven sur les décisions clés
  - Preuve de fin : Rapports ; aucun envoi externe sans accord de Cyril
  - Skills : code-review-and-quality ; dépendances : P5-09
- [ ] P5-11 (code) : Démo locale avec bannière « données fictives, pas d'usage clinique »
  - Preuve de fin : Script de démo
  - Skills : shipping-and-launch ; dépendances : P5-01, P0-20

## Étape R16 : options (sur décision de Cyril)

- [ ] P6-01 (doc) : Contrat génératif de la tâche « conclusion » (entrée : corps du compte rendu ; sortie : texte ; champs fermés pour l'évaluation)
  - Preuve de fin : `task_specs/parhaf_conclusion.yaml` valide
  - Skills : dataset-intake ; dépendances : P0-18, P0-35
- [ ] P6-02 (GPU) : Baseline : LLM zéro-shot et few-shot
  - Preuve de fin : Run au registre
  - Skills : experiment-preregistration, vram-preflight ; dépendances : P6-01
- [ ] P6-03 (GPU) : SFT LoRA de l'élève
  - Preuve de fin : Run au registre
  - Skills : lora-classifier-recipe, vram-preflight ; dépendances : P6-02
- [ ] P6-04 (code) : Métrique de faits atomiques bidirectionnelle (extraction, appariement) validée sur 50 paires relues
  - Preuve de fin : Accord avec la relecture mesuré
  - Skills : test-driven-development ; dépendances : P6-01
- [ ] P6-05 (mesure) : LLM-juge distinct du générateur, validé sur un échantillon annoté à la main, stabilité mesurée
  - Preuve de fin : Accord juge et humain, stabilité consignés
  - Skills : doubt-driven-development ; dépendances : P6-04
- [ ] P6-06 (GPU) : Distillation sur politique avec `DistillationTrainer` (vocabulaire commun vérifié)
  - Preuve de fin : Run au registre
  - Skills : distillation-pipeline, vram-preflight ; dépendances : P6-03
- [ ] P6-07 (GPU) : GRPO à récompense vérifiable (F1 d'extraction, validité du JSON) sur la tâche d'extraction dérivée des spans
  - Preuve de fin : Run et récompense testée
  - Skills : experiment-preregistration, vram-preflight ; dépendances : P6-03
- [ ] P6-08 (GPU) : Décodage contraint (xgrammar, llguidance) : validité et latence
  - Preuve de fin : Tableau
  - Skills : performance-optimization, vram-preflight ; dépendances : P6-03
- [ ] R-01 (décision) : Fiche préenregistrée de location : question scientifique, déclencheur (section 5.2 du plan), durée, plafond
  - Preuve de fin : Fiche figée et accord de Cyril sur le plafond
  - Skills : experiment-preregistration ; dépendances : aucune
- [ ] R-02 (doc) : Choisir le fournisseur ; vérifier que les licences des données permettent l'hébergement tiers ; aucun secret dans l'image
  - Preuve de fin : Note et liste des fichiers autorisés
  - Skills : dataset-intake, security-and-hardening ; dépendances : R-01
- [ ] R-03 (spike) : Profil `hardware/<carte>.yaml` et pré-vol sur la machine louée
  - Preuve de fin : Pré-vol vert
  - Skills : vram-preflight ; dépendances : R-02
- [ ] R-04 (GPU) : Exécuter, rapatrier les artefacts, enregistrer le coût réel
  - Preuve de fin : Runs « loué » au registre avec le coût
  - Skills : run-registry, vram-preflight ; dépendances : R-03
- [ ] R-05 (mesure) : Comparer à protocole égal et présenter à côté des résultats 5090
  - Preuve de fin : Verdict ; matériel signalé
  - Skills : paired-comparison, claim-gate ; dépendances : R-04
