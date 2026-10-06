# Feuille de route unifiée

Version 1, 01/10/2026. Guide d'exécution du projet LLM_finetuning, issu du plan V6, du backlog, des audits de GLM 5.3 et de ChatGPT 5.6, et de mes propres vérifications du jour.

**Hiérarchie des documents.** `PLAN_PROJET_V6.md` dit quoi faire et pourquoi. `MICROTACHES.md` donne le détail de chaque micro-tâche et sa preuve de fin. **Ce fichier donne l'ordre d'exécution et les portes d'arrêt.** En cas de conflit d'ordre, ce fichier prévaut ; en cas de conflit sur le contenu ou la preuve d'une tâche, `MICROTACHES.md` prévaut. `python3 scripts/check_roadmap.py` vérifie que cette séquence place chaque micro-tâche une fois et respecte ses dépendances.

---

## 1. Le point sur les deux audits

### 1.1 Ce que chacun a regardé

- **GLM 5.3** : le déroulé d'exécution de P0 et au-delà. Question posée : où gagner du temps sans perdre en qualité ni en sécurité. Il a exécuté le vérificateur, lu les fichiers, relevé des mesures de machine. Il propose 14 actions, toutes des réorganisations ou des garde-fous, aucune ne touche un protocole ou une métrique.
- **ChatGPT 5.6** : la stratégie et la traçabilité des affirmations. Il audite le plan V1 puis la V6 comme spécification exécutable, contrôle 21 affirmations contre des sources primaires, et propose un autre déroulé en tranches verticales avec des critères d'arrêt.

Les deux ont lu le dépôt entier. Les deux confirment que le vérificateur est vert (135 micro-tâches, 68 ★ à l'époque) et que rien n'avait été lancé (ni donnée, ni modèle, ni dépôt Git).

### 1.2 Où ils convergent (retenu)

| # | Point | GLM | ChatGPT | Décision |
|---|---|---|---|---|
| 1 | Aucun résultat de spike ne peut être inscrit « au registre » tant que le registre n'existe pas | 1.1 | 6.15 (commandes) | RM-05 : mini-registre avant tout spike |
| 2 | Le dossier n'est pas un dépôt Git ; rien n'impose `.gitignore` avant de télécharger des données sous conditions d'usage | 1.3 | 2.4 | RM-03 avant P0-14 |
| 3 | P0 est trop chargée et trop horizontale ; vLLM et la quantification fine n'ont pas leur place dans le chemin critique | 2.4 | 6.6, 6.7 | P0-09 et P0-10 repoussés en R14 et R15, juste avant leur premier usage |
| 4 | Il manque des commandes canoniques reproductibles | 3.1, 3.2, 4 n°5 | 2.4, 6.15 | RM-04, RM-10 |
| 5 | Le vérificateur compte des tâches, il ne prouve pas les notes de qualité | 3.1 | 6.12 | RM-10 (contrôles en plus), RM-12 (schéma de preuve) |
| 6 | L'ingestion de huit papiers ne doit pas bloquer la porte de P0 | 2.6 | 6.7 | P0-47 réduit à trois papiers ; RM-18 et RM-23 avant usage |
| 7 | La stratification des plis suppose la politique des classes rares, et la règle auteur contre classe doit être écrite d'avance | 1.2 | 6.8 | P0-28 dépend de P0-33 et de RM-07 |
| 8 | Le test de transposabilité doit tourner sans GPU et mesurer le coût d'ajout d'une tâche | 3.3 | 6.4 | P0-44 en deux variantes (`cpu`, `gpu`) |
| 9 | Ne pas sacrifier le socle de preuve pour aller plus vite | 5 | 4, 15 | Les invariants du § 1.6 restent intacts |

### 1.3 Où ils divergent, et mon arbitrage

| Sujet | GLM | ChatGPT | Arbitrage |
|---|---|---|---|
| Taille du chemin court | Le garde tel quel : « fermé et vérifié par un script » est une vraie défense MVP | « Fermé » n'est pas « minimal » ; 68 tâches retardent trop le premier résultat | Les deux ont raison sur des plans différents. Je garde l'ensemble mais le **découpe en deux jalons** (A à l'étape R7, B à R11) avec cinq portes d'arrêt, et j'allège le premier cycle (criblage de 2 à 3 modèles au lieu de 4 à 6 ; zéro-shot et raccourcis du LLM déplacés au chemin complet). Le compte de ★ **monte** de 68 à 92 : j'ajoute 24 tâches de cadrage et de portes (surtout petites : décision, document, test), je promeus 2 tâches existantes (P0-03, P0-31) et j'en retire 2 (P1-09, P1-24). C'est l'inverse d'une soustraction, et je le dis : la valeur obtenue vient de l'ordre et des portes, pas du compte. Le jalon A permet de s'arrêter après un premier résultat honnête |
| Valeur de P4-06 (trois outils de prédiction conforme) | Le range parmi les points forts | Trois nombres proches ne valident pas l'hypothèse d'échangeabilité | ChatGPT a raison sur les hypothèses ; GLM a raison sur la détection de bugs. P4-06 est reformulé en contrôle d'implémentation ; RM-22 ajoute les cas analytiques, la couverture conditionnelle et la rupture d'échangeabilité |
| Premier risque à lever | Mini-registre, puis spikes matériels | Viabilité des données (CPU) avant tout gros modèle | Un spike léger PyTorch et SM120 (environ 30 minutes, impact bloquant) d'abord ; puis les données ; les gros téléchargements (P0-06, P0-08) seulement après la porte RM-08 |
| Quand ingérer au wiki | Au plus tôt, en tâche de fond | Pas avant la porte de P0 | Trois papiers à G-P0 ; le reste avant son premier usage |
| Nature de l'objectif | Non discuté | Doit être neutre quant au vainqueur | Adopté. Cyril ayant demandé de tester les stratégies de LMSYS, distillation et tâche voisine restent des expériences obligatoires ; le livrable, lui, ne présume aucun gagnant |

### 1.4 Ce que j'ai vérifié moi-même

| Affirmation | Source | Ma vérification (01/10/2026) | Statut |
|---|---|---|---|
| Le registre n'existe pas quand P0-08 écrit « au registre » | GLM 1.1 | Lecture de `MICROTACHES.md` : P0-08 l'exige, P0-41 dépend de P0-11 et vient après | Prouvé |
| P0-28 ne dépend pas de P0-33 | GLM 1.2 | Lecture : P0-28 ne dépend que de P0-22 | Prouvé |
| Le dossier n'est pas un dépôt Git | GLM 1.3, ChatGPT 2.4 | Le listage du dossier ne montre aucun `.git` | Prouvé |
| Qwen3.8-27B et Gemma 4 31B se chargent par `AutoModelForMultimodalLM`, sans mention de classification | ChatGPT § 7 | Cartes officielles lues : classe recommandée `AutoModelForMultimodalLM`, vision-langage natif, Apache 2.0, aucune mention de `AutoModelForSequenceClassification` | Prouvé au niveau des cartes. La compatibilité réelle reste à tester en P0-06, et c'est bloquant pour les professeurs |
| Gemma 4 est à accès conditionné | Mon plan V6 | La carte affiche Apache 2.0 et aucun gating. Seul MedGemma relève de conditions particulières (Health AI Developer Foundations) | Mon plan se trompait ; corrigé, à reconfirmer à l'ouverture de la page avec le compte de Cyril |
| PARHAF : 4 254 patients | Mon plan V6 contre ChatGPT (4 259 patients, 6 190 documents) | L'API du dépôt HF donne `train` = 4 254 exemples, révision `60426ccdbbbb335e0281f2e5c236b89100ffbd42`, modifiée le 09/06/2026, non conditionné. L'article donne 4 254 patients et 6 185 documents publiés ; la fiche en prose cite d'autres totaux | Les sources divergent réellement. P0-21 tranche par comptage, avec la révision épinglée |
| La perte de la 1re place de LMSYS est plus riche que CE + KL | ChatGPT § 7 | Dépôt lu plus tôt : `loss = (loss_ce + loss_grad1 + cos_loss1 + loss_grad2 + cos_loss2) / 5`. La perte du plan est donc une baseline adaptée, pas la recette exacte | Prouvé ; RM-19 documente l'écart |
| « sayoulala » contre « shyoulala » est une faute de frappe | GLM § 4 n°1 | Le write-up Kaggle est signé `sayoulala` et lie `github.com/shyoulala/LMSYS_BlackPearl` : deux identifiants réels, un par plateforme | Réfuté |
| Annotés « conclusion » : 7 554 lignes contre 3 664 + 108 documents | GLM § 4 n°2 | Probablement des lignes de spans contre des documents, non tranché | À revérifier en P0-18 |
| `AGENTS.md` référence `.Codex/` | Nouveau | Lu : deux chemins en `.Codex`, alors que les dossiers sont `.codex` et `.claude` ; le fichier duplique CLAUDE.md, donc risque de dérive | Prouvé ; corrigé par RM-04 |
| `python scripts/check_microtasks.py` n'est pas reproductible tel quel | ChatGPT 2.4 | De mon côté j'ai toujours lancé `python3`. L'affichage de ★ peut échouer en CP1252 : sortie UTF-8 forcée dans le script | Corrigé |
| RAM visible sous WSL : 68 Go, pilote 610.47, 198 Go libres sur D: | GLM 1.4, 1.5 | Non revérifié par moi : relevé de GLM | **Non vérifié** ; mesuré en RM-06 |
| ext4 est plus rapide que `/mnt/d` pour les poids | GLM 1.4 | Hypothèse plausible, non mesurée ici | À mesurer en RM-06 |

### 1.5 Non retenu ou différé

- **Carte de capacités** (ChatGPT 6.5) : utile quand la base de code grandira ; l'ordre ci-dessous couvre les mêmes dépendances. À réévaluer au début de P5.
- **`.wslconfig`** pour relever le plafond de RAM (GLM 1.5) : décision de Cyril, non prise.
- **Sous-agents pendant les temps d'attente** (GLM 2.7) : retenu comme règle de conduite (§ 8), limité aux documents.
- **Deux ans de calendrier chiffré** : aucun calendrier n'est annoncé avant la mesure pilote RM-16 (ChatGPT 5.9).

### 1.6 Ce qui reste intact, parce que les deux audits le protègent

Test scellé à accès unique (P0-34) ; test de transposabilité ; chemin court fermé et vérifié par script ; verdict en trois valeurs ; résultats négatifs publiés au même rang ; `claim-gate` ; fiches préenregistrées immuables avec plafond de location ; règle « ne jamais toucher un processus GPU qu'on n'a pas lancé » ; aucune donnée de patient réel.

---

## 2. Principes de la séquence

1. **Tranche verticale d'abord.** Un fil complet (donnée, contrat, split, modèle, métrique, registre, rapport) sur un modèle trivial avant tout gros modèle.
2. **Le risque d'abord, classé** : priorité = impact × probabilité ÷ coût de levée. D'où : spike PyTorch léger, viabilité des données, puis seulement les gros modèles.
3. **CPU avant GPU.** Toute question qui se tranche sans GPU se tranche avant d'en réserver un.
4. **Chaque phase se clôt sur une porte d'arrêt** (§ 6) qui peut dire « simplifier » ou « arrêter », pas seulement « continuer ».
5. **Développement sur plis, confirmation une seule fois.** Toute comparaison de développement utilise les prédictions hors pli. Le test scellé n'est ouvert qu'une fois par expérience confirmatoire (RM-20).
6. **Aucune durée annoncée avant une mesure.** Les estimations portent trois valeurs : hypothèse, mesure pilote, marge (RM-16).
7. **Objectif neutre.** Le projet réussit s'il produit une conclusion fiable sous contraintes, même si TF-IDF ou un encodeur bat le LLM distillé.

---

## 3. Cap, question, succès et limites (reformulations proposées, à valider)

**Cap.** Construire une chaîne reproductible qui compare, sur des comptes rendus cliniques français fictifs et sous budget RTX 5090, une référence non neuronale, un encodeur, une LoRA de LLM et une distillation. Mesurer leur qualité, leur calibration, leur robustesse et leur coût. Retenir le meilleur compromis admissible sans présumer qu'un LLM ou la distillation gagne. Toute conclusion reste limitée au corpus, à la tâche, au split et au matériel effectivement testés.

**Question principale.** À budget de réglage égal et sur la tâche `parhaf_cim10_chapter` définie par contrat, la distillation au niveau des classes améliore-t-elle la LoRA de référence d'une ampleur pratiquement utile, au-delà de la variance entre graines, sans dégrader excessivement le coût, la calibration et la robustesse ? Les termes « budget égal », « pratiquement utile » et « excessivement » reçoivent leurs valeurs dans RM-02 et RM-11, avant tout run comparatif.

**Quatre objectifs, quatre preuves.**

| Objectif | Ce qu'il demande | Preuve de succès |
|---|---|---|
| O1 Compétence | Au moins un fine-tuning LoRA ou QLoRA de bout en bout | Run reproductible, tests, configuration, analyse d'erreurs |
| O2 Science | Mesurer l'effet pratique de la distillation et de la tâche voisine face à une référence réglée | Comparaison préenregistrée, appariée, avec intervalle et verdict en trois valeurs |
| O3 Ingénierie | Une même chaîne accepte au moins deux contrats de tâche de la même famille | Test de transposabilité ; coût d'ajout mesuré |
| O4 Candidature | Ne produire que des affirmations défendables | Tableau `claim-gate` relié aux run_id et aux sources |

**Succès global.** (1) Au moins un fine-tuning LLM complet est reproductible et enregistré. (2) La comparaison principale produit un verdict honnête, négatif ou non résolu compris. (3) Les fuites patient, auteur et quasi-doublon sont testées. (4) Le meilleur candidat est comparé sur la qualité, la calibration et le coût. (5) Une seconde tâche compatible traverse le noyau sans le modifier. (6) Chaque affirmation externe est reliée à une source ou à un run_id. (7) Le rapport distingue données fictives, scénario suggéré et vérité clinique. Le succès ne dépend pas du fait que la distillation gagne.

**Non-objectifs.** Validation clinique. Généralisation à des comptes rendus réels. Décision diagnostique ou thérapeutique. Reproduction exacte de toute la solution Kaggle. Prétention à l'état de l'art. Déploiement hospitalier réel. Couverture de tous les outils de l'offre. Entraînement 70B ou location sans déclencheur accepté.

**Vocabulaire.** « Reproduction » est réservé à la vérification d'un mécanisme exact de la recette source (étiquette `REP`). Le transfert au clinique français est une adaptation (`ADAPT`) ; le reste est exploratoire (`EXPLORE`). Chaque expérience porte l'une de ces trois étiquettes (P0-46).

**« Local »** se précise par RM-02 : local-données (aucun texte ni artefact dérivé ne quitte la machine), local-calcul (entraînement et inférence sur la seule RTX 5090), local-démonstration (service accessible sur la machine ou le réseau privé). Une location de GPU rompt local-calcul mais peut rester compatible avec local-données.

**Deux jalons de communication.**
- **Jalon A (fin de R7)** : premier résultat honnête. Références, une LoRA de référence, `RESULTATS.md`. C'est le premier moment où l'on peut dire vrai « j'ai affiné un LLM, voici le protocole et les chiffres ».
- **Jalon B (fin de R11)** : MVP complet. Distillation et tâche voisine comparées, calibration, prédiction conforme, carte de modèle, reconstruction à froid, textes sortants passés par `claim-gate`.

---

## 4. Carte des étapes

| Étape | Objectif | Porte de sortie | Arrêt ou repli si | Jalon |
|---|---|---|---|---|
| R0 | Cadrer, archiver l'offre, décider, créer le dépôt local | Décisions datées ; dépôt local ; SPEC-P0 validée | Une décision bloquante reste ouverte : poser la question, ne rien supposer | |
| R1 | Socle machine minimal | Spikes PyTorch et bibliothèques verts ; environnement figé ; licences auditées | PyTorch sans SM120 : plan B du plan V6, § 9 | |
| R2 | Viabilité des données (CPU) | Révision PARHAF épinglée ; comptages ; splits ; raccourci d'auteur mesuré ; **RM-08** | Étiquettes ou groupes inexploitables : simplifier la cible ou changer de tâche | |
| R3 | Fil synthétique de bout en bout | `make smoke` vert sur environnement propre ; tests anti-fuite ; transposabilité | Le fil ne tient pas sur la tâche jouet : corriger avant tout modèle | |
| R4 | Compatibilité des modèles et budget | Tableau de compatibilité ; élève présélectionné ; budget par vague | Aucun modèle ne tient ou ne classe : repli verbaliseur, ou modèle plus petit | |
| R5 | Geler le protocole | `PROTOCOLE.md` figé, empreinte consignée ; **G-P0** | Une valeur de cap manque (B, N, seuil utile) : ne pas figer | |
| R6 | Références sur la tâche principale | Tableau de références avec intervalles ; raccourcis mesurés ; **RM-15** | Résultat dominé par les raccourcis ou puissance insuffisante | |
| R7 | Une LoRA de référence | Variance de graines ; configuration gelée ; premier `RESULTATS.md` ; **RM-17** ; **G-P1** | LoRA dominée par l'encodeur : poursuivre en expérience d'apprentissage limitée | **A** |
| R8 | Spike de distillation miniature | Perte testée ; coût du run complet mesuré ; décision go/no-go | OOM, coût hors budget, aucune tendance | |
| R9 | Expérience confirmatoire | Probabilités hors pli ; verdict apparié ; test scellé ouvert une fois ; **RM-21** ; **G-P2** ; **G-P3** | Verdict non résolu et aucun budget pour lever l'incertitude | |
| R10 | Fiabilité du meilleur candidat | Calibration, couverture conforme validée, abstention, carte de modèle ; **G-P4** | Couverture hors cible sans cause identifiée | |
| R11 | Livraison ciblée | Reconstruction à froid ; rapport ; `claim-gate` ; **G-P5** | | **B** |
| R12 à R16 | Chemin complet et options (références et réglage, leviers, compression, industrialisation, pistes optionnelles) | Selon la décision de périmètre de Cyril | | |

### 4.1 Chaîne critique : des petits dominos au domino géant (05/10/2026)

Principe : un objectif n'en fait tomber un autre que si la **cause physique est écrite** : chacun produit une pièce de preuve (un run au registre, une fiche hachée, un intervalle) dont le suivant a besoin. On commence par le plus petit domino qui touche le suivant ; le domino géant est connu d'avance : **RM-20 (ouverture unique du test scellé) sur un système figé (RM-50)**, puis **RM-49 (ancrage sur benchmark public à résultats publiés)**. Détail, critères de 10/10 et plafonds : `docs/CHAINE_DE_DOMINOS.md`.

| Domino | Tâches | Étape | Pièce de preuve produite | Composantes |
|---|---|---|---|---|
| 0 | RM-28 | R7 | probabilités hors pli du LoRA sur cinq plis | performance, rigueur |
| 1 | RM-34, RM-42, RM-30 | R7, R11 | latence, débit, énergie par profil ; repère zéro-shot | efficience, honnêteté |
| 2 | RM-32 | R8 | élève distillé et écart au professeur | efficience, performance par coût |
| 3 | RM-41 | R7 | débit d'entraînement à résultat équivalent | efficience |
| 4 | P2-06, P2-10 | R9, R13 | audit d'étiquettes ; synthétique ciblé | performance, données, erreurs |
| 5 | RM-50 | R9 | ADR de gel, prédiction hachée du test scellé | rigueur |
| 6 | RM-37 | R9 | acceptation de Cyril | rigueur |
| 7 | RM-20, RM-51 | R9, R10 | verdict confirmatoire ; incertitude confirmée | rigueur, performance, incertitude |
| 8 | RM-33, RM-39 | R10, R14 | couverture par famille ; nouveaux auteurs | incertitude, erreurs |
| 9 | RM-49 | R13 | tableau chiffres publiés contre les nôtres | performance, données ; **fait le 06/10/2026** : mélange 50/50 à 71,74 [69,60 ; 73,71] de F1 pondéré contre 71,95 publié au mieux (« dans la bande du publié », pas au-dessus : performance 8 et non 9), encodeur seul 65,53 (non reproduit au sens strict de la fiche), TF-IDF 69,85 ; références publiées vérifiées à la source (tableau 3 de arXiv 2402.16689) ; run `20261006-223731-morfitt-final-resume` |
| 10 | P5-09, P5-12, RM-48 | R11 | reconstruction à froid, rapport, fiche de déploiement | reproductibilité, honnêteté, efficience |
| 11 | P5-10 | R15 | revue indépendante | rigueur, honnêteté |

**Correspondance avec la notation** : les huit composantes de la présentation se rattachent aux douze catégories Q : *performance* = résultat mesuré sous Q2 et Q3 ; *rigueur* = Q2 et Q3 ; *données* = Q1 ; *incertitude* = Q5 ; *erreurs et robustesse* = Q4 ; *reproductibilité et ingénierie* = Q6 et Q7 ; *efficience et déploiement* = Q8 et Q9 ; *sûreté, conformité, honnêteté* = Q10, Q11 et Q12. À chaque scorecard, on note l'écart entre la note estimée de la présentation et la note 0 à 3 prouvée (RM-52).

**Règles d'ordonnancement** : (1) un seul lot GPU à la fois, enchaîné par marqueurs ; le calcul CPU léger se fait en parallèle, à priorité basse ; (2) aucune tâche ne modifie un fichier qu'un lot en cours importe (RM-41 attend la fin du lot RM-28) ; (3) aucune nouvelle recette ne s'insère entre RM-50 et RM-20 ; (4) le synthétique ciblé et l'audit d'étiquettes (P2-06, P2-10) se tranchent **avant** RM-50 si le budget le permet (fenêtre de décision, sans dépendance de fermeture entre tâches ★ et non ★) ; (5) l'ancrage RM-49 se lit **après** RM-20 pour ne pas influencer le choix du candidat.

---

## 5. La séquence

Chaque étape liste ses micro-tâches **dans l'ordre d'exécution**. Les identifiants renvoient à `MICROTACHES.md`, qui garde la définition complète et la preuve de fin. Au début de chaque étape, charger les skills indiqués.

### Étape R0 : cadrage et fondations légères

**Objectif** : poser le cadre avant toute installation lourde.
**Skills à charger** : interview-me, documentation-and-adrs, git-workflow-and-versioning, spec-driven-development, planning-and-task-breakdown.
**Porte de sortie** : décisions de cadrage datées ; dépôt local initialisé ; SPEC-P0 validée par Cyril.
**Arrêt ou repli si** : une décision bloquante reste ouverte, on pose la question et on n'avance pas sur une supposition.

| ID | Rôle dans l'étape | Point d'attention |
|---|---|---|
| RM-24 | Générer `tasks/plan.md` et `tasks/todo.md` depuis cette feuille de route | `python3 scripts/check_roadmap.py --export` |
| RM-01 | Archiver l'offre CHUGA | Le texte intégral n'existe que dans une autre session ; Cyril le fournit |
| P0-02 | Décisions 1 à 5 : emplacement, dépôt, périmètre, date limite, démo | Réponses « provisoires » datées acceptées |
| RM-02 | Cap du premier cycle : B, N, métrique primaire, seuil utile, « local » | B et N obligatoires avant P0-46 |
| RM-03 | `git init` local, `.gitignore`, commit d'amorçage montré à Cyril | Aucun commit sans accord ; aucun dépôt distant |
| RM-04 | SPEC-P0 courte, commandes canoniques, une seule source de règles | AGENTS.md aligné sur CLAUDE.md |

### Étape R1 : socle machine minimal

**Objectif** : lever le risque matériel le plus bloquant avec le moins de téléchargement.
**Skills à charger** : vram-preflight, debugging-and-error-recovery, ci-cd-and-automation, security-and-hardening, run-registry.
**Porte de sortie** : PyTorch voit `sm_120` ; bibliothèques de fine-tuning vérifiées ; machine mesurée ; environnement figé ; licences des dépendances auditées.
**Arrêt ou repli si** : PyTorch ne s'exécute pas sur SM120, plan B du plan V6 section 9 présenté à Cyril avant de continuer.

| ID | Rôle dans l'étape | Point d'attention |
|---|---|---|
| RM-05 | Mini-registre JSON en ajout seul | Avant tout spike |
| P0-04 | Spike PyTorch cu128 puis cu130, `sm_120` | Environnement partagé avec P0-05 (un seul cycle de téléchargement) |
| P0-05 | Spike transformers v5, peft, trl, accelerate, bitsandbytes | Même environnement jetable |
| RM-06 | Machine vue par WSL : RAM, disque, ext4 contre `/mnt/d`, `HF_HOME` | Seule étape où la RAM réelle est mesurée |
| P0-11 | Verrouillage `uv.lock`, Dockerfile, `hardware/rtx5090.yaml` | Fixe aussi l'emplacement des poids et des points de sauvegarde |
| P0-12 | Audit des licences des dépendances | |

### Étape R2 : viabilité des données (CPU seulement)

**Objectif** : savoir si la question principale peut réellement être posée, avant d'installer un gros modèle.
**Skills à charger** : dataset-intake, leakage-guard, experiment-preregistration, source-driven-development.
**Porte de sortie** : révision PARHAF épinglée ; comptages sourcés ; présence et distribution du diagnostic principal ; splits par patient et par auteur ; raccourci d'auteur mesuré ; décision RM-08.
**Arrêt ou repli si** : classes trop rares, groupes auteur insolubles ou étiquette inadéquate : simplifier la cible (niveau chapitre, regroupements) ou changer de tâche. Ne pas installer de gros modèle.

| ID | Rôle dans l'étape | Point d'attention |
|---|---|---|
| P0-14 | Téléchargement scripté, révision épinglée, empreintes | Après RM-03 (`.gitignore` en place) |
| P0-15 | Licence et usages interdits lus à la source | Licence, conditions et usages exclus consignés séparément |
| P0-21 | Comptages : patients, documents, spécialités, types, longueurs | Chaque chiffre cite source, révision et périmètre |
| P0-22 | Présence du diagnostic principal CIM-10 | |
| P0-17 | Recherche de données personnelles sur 200 documents | |
| P0-27 | Nomenclature CIM-10 officielle, hiérarchie | Conditions de réutilisation lues |
| P0-23 | Distribution des classes aux trois niveaux | |
| P0-20 | Règles de formulation déduites des conditions d'usage | Consultées par `claim-gate` |
| P0-31 | État de l'ouverture du test embargoé (CodaBench) | Promu ★ : il conditionne le plan de confirmation |
| P0-16 | Fiche du jeu PARHAF | |
| P0-32 | Unité d'entrée : document ou patient | |
| P0-33 | Politique des classes rares | Avant la stratification |
| RM-07 | Règles de split préenregistrées, seuil du raccourci d'auteur chiffré avant observation | |
| P0-28 | Découpage par patient, test scellé interne, 5 plis | Dépend de P0-33 et de RM-07 |
| P0-29 | Plis groupés par auteur | |
| P0-30 | Modèle témoin du raccourci d'auteur | Seuil fixé par RM-07 |
| P0-34 | Accès au test scellé réservé à un seul script | |
| RM-08 | **Porte go/no-go sur la viabilité des données** | Décision datée avec les chiffres |

### Étape R3 : fil synthétique de bout en bout

**Objectif** : valider l'architecture minimale sans coût GPU significatif.
**Skills à charger** : spec-driven-development, test-driven-development, constraint-driven-development, api-and-interface-design, incremental-implementation, run-registry.
**Porte de sortie** : `make smoke` enchaîne contrat, chargeur, split, modèle trivial CPU, métriques, registre, reprise, rapport, et se rejoue sur environnement propre ; un cas de fuite piégé est détecté ; un contrat invalide est rejeté.
**Arrêt ou repli si** : le fil ne tient pas sur la tâche jouet, on corrige avant de toucher un modèle réel.

| ID | Rôle dans l'étape | Point d'attention |
|---|---|---|
| P0-35 | Schéma Pydantic du contrat de tâche | Tests d'abord |
| P0-36 | Contrat `parhaf_doctype` | |
| P0-37 | Contrat `parhaf_specialty` | |
| P0-39 | Tâche jouet synthétique | Données déterministes |
| P0-38 | Contrat `parhaf_cim10_chapter`, noms officiels, définitions | Relu en contexte neuf |
| P0-41 | Registre de runs complet | Remplace le mini-registre, format compatible |
| P0-43 | Chargeur générique | Empreinte des partitions comparée à une référence |
| P0-40 | Tests `leakage-guard` | Un cas piégé doit échouer |
| P0-42 | `CONSTRAINTS.md` et `make check` | gitleaks dès le premier commit |
| P0-13 | `accelerate launch` avec reprise vérifiée | Nécessaire aux runs de nuit |
| P0-44 | Test de transposabilité, variantes `cpu` et `gpu` | Coût d'ajout mesuré |
| RM-09 | `make smoke` rejoué sur environnement propre | Première reconstruction à froid, tôt |
| RM-10 | Contrôles renforcés ; `make check` inclut les trois vérificateurs | |

### Étape R4 : compatibilité des modèles et budget

**Objectif** : savoir quels modèles se chargent, classent et tiennent en mémoire, puis préciser le budget.
**Skills à charger** : vram-preflight, lora-classifier-recipe, doubt-driven-development, experiment-preregistration.
**Porte de sortie** : tableau de compatibilité par modèle ; élève du premier cycle présélectionné par règle écrite ; pic de mémoire du plus gros professeur mesuré ; budget par vague.
**Arrêt ou repli si** : aucun professeur de 24 à 31 milliards ne tient ou n'accepte une tête de classification, repli verbaliseur, ou professeur plus petit, ou déclencheur de location (plan V6, section 5.2).

| ID | Rôle dans l'étape | Point d'attention |
|---|---|---|
| P0-01 | Modèles à accès conditionné | Réduit à MedGemma si Gemma 4 est confirmé non conditionné |
| P0-03 | Décisions 7 à 9 : location, revue croisée, relecture d'étiquettes | « Non décidé » accepté si daté |
| P0-06 | Compatibilité de classification | Élèves d'abord ; gros professeur chargé une seule fois ; cartes multimodales : P0-06 est bloquant |
| RM-13 | Présélection de l'élève, règle écrite avant les résultats | |
| P0-08 | Banc de 10 pas du gros professeur en QLoRA | Même chargement que P0-06 |
| P0-45 | Budget de calcul par vague | |

### Étape R5 : geler le protocole

**Objectif** : écrire et figer tout ce qui doit l'être avant le premier run comparatif.
**Skills à charger** : experiment-preregistration, doubt-driven-development, paired-comparison, claim-gate, wiki-ingest.
**Porte de sortie** : `PROTOCOLE.md` figé, empreinte aussi consignée dans une page wiki ; scorecard G-P0 au plancher, une preuve par note.
**Arrêt ou repli si** : B, N, la métrique primaire ou le seuil utile manquent, on ne fige pas.

| ID | Rôle dans l'étape | Point d'attention |
|---|---|---|
| RM-11 | Estimand, rééchantillonnage hiérarchique, famille de Holm, effet minimal utile | Remplace la règle des deux écarts-types |
| RM-12 | Schéma de preuve des scorecards, degrés d'indépendance | Une indépendance se déclare avec son degré |
| P0-47 | Ingestion de trois papiers (PARHAF, Learning Rate Matters, têtes de classification) | Les autres avant usage |
| P0-46 | `PROTOCOLE.md` : métriques, tests, seuils, graines, étiquettes REP, ADAPT, EXPLORE | Relecture adversariale en contexte neuf ; SHA-256 |
| G-P0 | Scorecard G-P0 | Preuve citée pour chaque note |

### Étape R6 : références sur la tâche principale

**Objectif** : obtenir le premier résultat scientifique utile et décider s'il justifie un LLM.
**Skills à charger** : paired-comparison, run-registry, leakage-guard, experiment-preregistration, vram-preflight.
**Porte de sortie** : références avec intervalles de confiance et coût ; harnais et tests statistiques validés ; raccourci d'auteur mesuré sur les références ; décision RM-15.
**Arrêt ou repli si** : les références rendent la comparaison non informative (variance, puissance, raccourcis) : simplifier avant d'engager un LLM.

| ID | Rôle dans l'étape | Point d'attention |
|---|---|---|
| P1-01 | Harnais d'évaluation | Tests sur cas à réponse connue |
| P1-02 | Bootstrap apparié, McNemar, permutation, Holm | Vérifiés contre SciPy et statsmodels |
| P1-03 | Bornes : majorité et aléatoire | |
| P1-04 | TF-IDF et régression logistique sur `parhaf_doctype` | |
| P1-06 | TF-IDF et régression logistique sur `parhaf_cim10_chapter` | |
| P1-07 | Encodeur français affiné (DrBERT ou CamemBERT-bio) | Réglage consigné |
| RM-14 | Raccourcis sur les références : plis patient contre plis auteur | |
| RM-25 | Références bon marché à recette mûre et même effort de réglage (TF-IDF caractères et poids, encodeur 10 époques, cinq graines) | Fait le 04/10/2026 : la recette gelée à 2 époques sous-estimait les modèles appris |
| RM-26 | Discrétisation et auteur : variance par classe, partitions répétées, leave-one-author-out, débiaisage | Fait le 04/10/2026 : cinq classes portent 85 % de la variance |
| RM-15 | **Porte go/no-go après les références** | |

### Étape R7 : une LoRA de référence (jalon A)

**Objectif** : prouver le fine-tuning LLM avec le plus petit espace de recherche défendable.
**Skills à charger** : lora-classifier-recipe, vram-preflight, run-registry, paired-comparison, claim-gate, wiki-ingest.
**Porte de sortie** : élève choisi par la règle écrite ; taux d'apprentissage réglé ; variance de graines mesurée ; configuration gelée ; premier `RESULTATS.md` ; G-P1.
**Arrêt ou repli si** : la LoRA est dominée par l'encodeur en qualité et en coût, la distillation se poursuit comme expérience d'apprentissage limitée, et non comme candidat présumé (RM-17).

| ID | Rôle dans l'étape | Point d'attention |
|---|---|---|
| P1-11 | Criblage de 2 à 3 candidats fixés par RM-13 | Un pli, réglages identiques |
| P1-12 | Choix de l'élève par la règle écrite avant | |
| RM-27 | LoRA de l'élève retenu à recette mûre (10 époques), pli 0 en deux graines, pli 1 en une graine | Fait le 04/10/2026 : 0,7795 et 0,7893 (pli 0), 0,7415 (pli 1) |
| RM-30 | Ancrage externe : LLM ouvert local en zéro-shot et quelques exemples sur le pli 0, sous-ensembles d'usage à part | Zéro-shot fait le 05/10/2026 (4B 0,493, 9B 0,473) ; quelques exemples (P1-10) restent au chemin complet |
| RM-16 | Mesure pilote du débit : recaler budgets et calendrier | Première durée annoncée, sur mesure |
| RM-42 | Énergie et coût par run au registre, Pareto généré | Rend l'efficience mesurable à chaque run, pas seulement au service |
| P1-13 | Balayage du taux d'apprentissage, une graine par taux (ADR-010) | |
| P1-19 | Variance entre graines, cinq graines | |
| P1-20 | Geler la configuration de référence | |
| P1-26 | Rejeu à la même graine, déterminisme | |
| P1-23 | Analyse d'erreurs initiale | |
| P1-25 | Page d'analyse et premier `RESULTATS.md` | Résultats négatifs au même rang |
| RM-28 | LoRA mûr aux plis 2, 3 et 4 : évaluation à cinq plis et professeur strictement hors pli (environ 10,5 h de GPU) | **Fait le 05/10/2026** : LoRA regroupé 0,7673, +4,71 contre le TF-IDF (résolu), +1,45 contre l'encodeur (non résolu), −0,49 contre l'ensemble ; bifurcation (b) non remplie |
| RM-29 | Règle de puissance v2 : largeur de la différence entre deux systèmes sur cinq plis, seuil 4,0 | Fait en partie : 3,09 par patients, **3,39 par blocs d'auteurs à 95 %** (question primaire unique), 4,24 à 98,33 % ; reste à refaire avec le LoRA |
| RM-52 | Rubrique de notation vérifiable par composante, correspondance Q1 à Q12, chaîne de dominos | Fait le 05/10/2026 (section 4.1) ; écart note estimée contre scorecard à chaque porte |
| RM-41 | Débit d'entraînement à résultat équivalent (checkpointing, noyaux linéaires, bf16 de l'encodeur) | Jamais pendant un lot en cours ; équivalence statistique d'abord ; **bf16 de l'encodeur fait le 05/10/2026 : équivalent (−0,07 [−1,67 ; +1,69]), ×2,25 plus rapide** ; reste le LoRA (checkpointing, noyaux) |
| RM-17 | **Porte go/no-go après la LoRA de référence** | |
| G-P1 | Scorecard G-P1 | **Jalon A** |

### Étape R8 : spike de distillation miniature

**Objectif** : vérifier le mécanisme, la mémoire et le signal avant cinq plis coûteux.
**Skills à charger** : distillation-pipeline, test-driven-development, vram-preflight, wiki-ingest.
**Porte de sortie** : perte testée sur cas analytiques ; un pli, une paire professeur élève ; écart avec la recette LMSYS exacte documenté ; coût du run complet mesuré ; règle go/no-go préenregistrée.
**Arrêt ou repli si** : OOM, temps complet hors budget, aucune tendance utile : ne pas lancer les cinq plis.

| ID | Rôle dans l'étape | Point d'attention |
|---|---|---|
| RM-18 | Ingérer les papiers A1, A2, A3 et A7 | Avant leur premier usage |
| P2-01 | Professeur 1 : réglage minimal du taux (QLoRA) | |
| P3-01 | Perte de distillation et ses tests | Ne dépend plus des logits hors pli |
| RM-19 | **Spike de distillation et décision go/no-go** | Règle préenregistrée |
| RM-32 | Élève distillé de la LoRA mûr vers l'encodeur, professeur strictement hors pli | Thèse du projet : qualité du LoRA à coût d'encodeur ; fiche hachée et lot en attente (04/10/2026), 30 runs ; bras ensemble : gain confirmé (+3,47 [+2,25 ; +5,08], au-dessus du professeur) ; bras LoRA : non (−2,55) |
| RM-56 | **Distillation à professeur imbriqué (contrôle de la fuite de second ordre)** | À lever avant de s'appuyer sur le gain de l'élève ; sinon le test scellé tranche ; **fait le 05/10/2026 : gain non préservé (−0,77 [−2,46 ; +0,96]), fuite significative (−4,24 [−6,00 ; −2,90]) ; C1 et C2 sortent ; la règle retient G (ensemble des trois familles)** |

### Étape R9 : expérience confirmatoire de distillation

**Objectif** : répondre à la question scientifique centrale.
**Skills à charger** : distillation-pipeline, leakage-guard, paired-comparison, lora-classifier-recipe, claim-gate.
**Porte de sortie** : probabilités hors pli complètes avec manifeste ; configuration gelée ; **système final figé et prédiction du test scellé hachée (RM-50) avant l'ouverture** ; référence, tâche voisine, distillation et combinaison comparées ; verdict en trois valeurs ; test scellé ouvert une seule fois ; G-P2 et G-P3.
**Arrêt ou repli si** : verdict non résolu et aucun budget pour lever l'incertitude.

| ID | Rôle dans l'étape | Point d'attention |
|---|---|---|
| P2-02 | Professeur 1 en cinq plis, logits hors pli | Manifeste |
| P2-03 | Contrôle strictement hors pli | |
| P2-06 | Audit des étiquettes (cleanlab, relecture de 100 cas) | Aucune étiquette de test modifiée ; pilote fait le 05/10/2026 sur 30 erreurs confiantes (ambiguïté de codage établie, contre-expertise par un codeur à prévoir) |
| P2-07 | Pré-entraînement sur tâche voisine | Tête jetée et réapprise |
| P2-08 | Gain de la tâche voisine, test apparié | |
| G-P2 | Scorecard G-P2 | |
| P3-02 | Élève distillé | |
| P3-07 | Entraîner les 20 modèles gelés ; l'évaluation est celle de RM-20 (ADR-010) | Pas de verdict avant RM-20 |
| RM-37 | **Acceptation du protocole v2 par Cyril** | **Acceptée le 05/10/2026** : `PROTOCOLE_V2.md` (instantané gelé) ; la règle de puissance v2 ne passe pas au format du test scellé (largeur 7,7 à 10,2 contre 4,0), déclaré d'avance |
| RM-50 | **Gel du système final et prédiction chiffrée du test scellé** | Règle de sélection écrite avant lecture ; rien ne change après ; brouillon : `docs/BROUILLON_GEL_SYSTEME_FINAL.md` ; **prérequis faits le 06/10/2026** : LoRA final (run `20261006-022716-final-lora-s1000`) et son temps A (`20261006-023402-temps-a-lora-s1000`), empreintes des sept composants de G au registre (section 8 du brouillon), RM-37 acceptée ; **gel exécuté le 06/10/2026 (Q22 validée)** : `docs/decisions/ADR-016-gel-du-systeme-final.md`, `results/frozen_final.json` (sha256 `8cb2382c…`), prédiction chiffrée hachée dans `experiments/INDEX.md`, répétition générale du temps B avec G (run `20261006-182842-repetition-generale-temps-b`), `sealed_evaluation.py check` : préconditions toutes remplies, **test scellé non ouvert** ; l'ouverture (RM-20) reste une décision séparée de Cyril |
| RM-20 | Ouverture unique du test scellé | Un seul accès journalisé ; **fait le 06/10/2026 à 20h59Z** (autorisée par Cyril) : G 0,8131 contre 0,7402 pour le TF-IDF, **+7,28 [+1,55 ; +12,62] par blocs d'auteurs : non résolu à δ = 2,0** ; prédiction préenregistrée notée (quatre réussites sur six) ; run `20261006-210015-ouverture-test-scelle-g`, `results/sealed_result.json` |
| RM-21 | **Porte go/no-go après le verdict de distillation** | |
| G-P3 | Scorecard G-P3 | Contre-lecture adversariale des verdicts exigée par le tableau « qui prouve quoi » |

### Étape R10 : fiabilité du meilleur candidat

**Objectif** : calibrer, conformiser et documenter le meilleur point retenu, quelle que soit sa famille.
**Skills à charger** : model-card-calibration, test-driven-development, doubt-driven-development, wiki-ingest.
**Porte de sortie** : température et ECE ; couverture conforme avec hypothèses explicites et validations de RM-22 ; politique d'abstention ; carte de modèle ; TRIPOD-LLM remplie ; G-P4.
**Arrêt ou repli si** : couverture hors cible sans cause identifiée.

| ID | Rôle dans l'étape | Point d'attention |
|---|---|---|
| RM-23 | Ingérer TRIPOD-LLM | |
| P4-04 | Calibration par température, ECE avant et après | S'applique au meilleur candidat, pas seulement à l'élève distillé |
| P4-05 | Prédiction conforme MAPIE, couverture empirique | Hypothèse d'échangeabilité énoncée |
| RM-22 | Validation conforme : cas analytiques, invariants, couverture conditionnelle, rupture d'échangeabilité | |
| RM-33 | Conforme conditionnel par famille (Mondrian) et couverture par famille avec Wilson | La couverture marginale cache des familles à 0,56 |
| RM-51 | Lecture confirmatoire de l'incertitude et de la robustesse sur le test scellé | Second temps de RM-20 ; seuils figés avant l'ouverture ; **incertitude lue le 06/10/2026** (couverture marginale 0,924, par famille 0,916, minimum 0,821 sur une famille de 56 patients ; exactitude 0,962 à 70 % de couverture) ; **reste** la robustesse aux nouveaux auteurs sur le test et l'ablation de contenu (aucune seconde lecture) |
| P4-08 | Politique d'abstention, courbe automatisation contre exactitude | |
| P4-10 | Carte de modèle et checklist TRIPOD-LLM | **Carte v4 du candidat G écrite le 06/10/2026** (`docs/CARTE_DE_MODELE_V4.md` : composition, performance, incertitude, abstention, coûts par composante, résultats négatifs, limites ; chaque chiffre cite un run) ; **non close** : checklist des 19 items et chiffres confirmatoires à rejouer après le gel et RM-51 |
| G-P4 | Scorecard G-P4 | |

### Étape R11 : livraison ciblée (jalon B)

**Objectif** : ne livrer que ce qui sert la candidature et la démonstration de rigueur.
**Skills à charger** : claim-gate, ci-cd-and-automation, documentation-and-adrs.
**Porte de sortie** : reconstruction à froid d'un chiffre clé dans la tolérance ; rapport final ; tous les textes sortants (CV, LinkedIn, lettre) passés par `claim-gate` ; G-P5.
**Arrêt ou repli si** : aucune affirmation ne peut être reliée à un run, on la retire.

| ID | Rôle dans l'étape | Point d'attention |
|---|---|---|
| RM-34 | Mesures de service par profil : latence, débit, mémoire, énergie ; LoRA fusionné ; encodeur sur GPU | **Fait le 05/10/2026** : LoRA fusionné 61 ms et 8,6 Wh pour 1 000 patients ; encodeur bf16 4,3 ms et 0,31 Wh ; TF-IDF 1,9 ms ; INT8 naïf écarté |
| RM-35 | Service multi-modèles avec ensembles conformes, abstention et conteneur vérifié | Tests et banc de latence |
| RM-36 | Rapport préliminaire, carte v3, fiche de données, protocole v2, tableaux regénérés, contrôle des références | Fait le 04/10/2026 ; à tenir à jour |
| RM-48 | **Fiche de déploiement par contrainte et règle de décision** | Dit quels systèmes deviennent inutiles à servir |
| P5-09 | Reconstruction à froid : clone neuf puis `make reproduce-small` | |
| P5-12 | Rapport final et textes sortants passés par `claim-gate` | Aucune formulation au-delà de la preuve ; **rapport final écrit et passé par `claim-gate` le 07/10/2026** (`docs/RAPPORT_FINAL_2026-10-07.md`, tableau de preuve de onze lignes dont trois reformulations ou retraits) ; **reste** les textes de candidature (CV, LinkedIn, lettre), qui exigent un accord de Cyril et le même passage |
| G-P5 | Scorecard G-P5 | **Jalon B : fin du MVP** |

### Étape R12 : compléments de références et de réglage (chemin complet)

**Objectif** : étoffer les références et le réglage de la LoRA.
**Skills à charger** : lora-classifier-recipe, paired-comparison, leakage-guard, performance-optimization.
**Porte de sortie** : références complémentaires et réglage complet consignés avec verdicts.
**Arrêt ou repli si** : le budget B est atteint.

| ID | Rôle dans l'étape | Point d'attention |
|---|---|---|
| P1-05 | TF-IDF sur `parhaf_specialty` | |
| P1-08 | doctomodernbert-fr (contexte long) | |
| P1-09 | LLM en zéro-shot | Sorti du premier cycle |
| P1-10 | Few-shot, exemples hors test | |
| P1-14 | Balayage du rang et d'alpha | |
| P1-15 | Longueur de contexte et troncature | |
| RM-47 | Débit contre macro-F1 par longueur de contexte, regroupement par longueur | Après RM-41 |
| P1-16 | Époques et ordonnanceur | |
| P1-17 | Tête contre verbaliseur | |
| P1-18 | Pooling, avec et sans masque bidirectionnel | |
| P1-21 | Budget de réglage par méthode | |
| P1-22 | Courbe d'apprentissage de la référence | |
| P1-24 | Raccourcis du LLM : plis patient contre plis auteur | Sorti du premier cycle |
| P0-07 | SDPA contre FlashAttention 2 sur SM120 | |
| RM-31 | Capacité à recette mûre : 9B LoRA 10 époques au pli 0 | Arrêt de l'exploration de taille si le gain est sous δ |
| RM-53 | Encodeurs français alternatifs (DrBERT, ModernBERT-fr) à recette mûre | Licence d'abord ; deux fois moins cher qu'un pli de LoRA |
| RM-54 | Représentations gelées d'un LLM et régression logistique | Embeddings de 0,5 h contre 3,7 h d'affinage |
| RM-55 | Recette d'encodeur v2 : lissage, EMA, curriculum, un facteur à la fois | Environ 1,2 h par facteur (trois graines, cinq plis) ; **fait le 05/10/2026 : aucun des trois ne gagne** (−0,70, −1,20, −0,13), résultats négatifs publiés |

### Étape R13 : leviers de données et de distillation

**Objectif** : explorer les leviers du catalogue au-delà de la distillation simple.
**Skills à charger** : dataset-intake, distillation-pipeline, lora-classifier-recipe, paired-comparison, wiki-update.
**Porte de sortie** : verdict en trois valeurs pour chaque levier testé ; résultats négatifs publiés.
**Arrêt ou repli si** : un levier sans gain sort du programme, publié comme résultat négatif.

| ID | Rôle dans l'étape | Point d'attention |
|---|---|---|
| P0-18 | Fiches des sous-ensembles annotés PARHAF | À clore avant leur premier usage |
| P0-19 | Fiche PARCOMED | |
| P0-24 | MorFITT : fiche et contrat | |
| P0-25 | CLISTER : fiche et contrat | |
| P0-26 | DiaMED : fiche courte | |
| P2-04 | Professeur 2 d'une autre famille | |
| P2-05 | Score hors pli et accord entre professeurs | |
| P2-09 | Pré-entraînement continu léger sur PARCOMED | |
| P2-10 | Données synthétiques avec lignée | Contrôle de fuite |
| P2-11 | Multi-étiquettes et paires de bout en bout | |
| RM-49 | Ancrage sur un benchmark public à résultats publiés (MorFITT) avec le même code | Seul moyen vérifiable de se situer face à l'état de l'art ; chiffres publiés cités avec source ; **préparé le 05/10/2026** : jeu téléchargé (CC BY-SA 4.0), fiche hachée, code et lot en attente du marqueur d'ouverture du test scellé |
| P2-12 | Pages wiki des professeurs et de la qualité des étiquettes | |
| RM-45 | Encodeur élagué (six couches), avec et sans distillation | Latence divisée par deux visée ; fiche hachée (05/10/2026) ; **fait le 06/10/2026** (30 runs, après correction du quoting de `$LOGDIR` qui le faisait sortir en code 2) : **dégradé** dans les trois comparaisons de la fiche (élagué contre complet −13,08 [−15,88 ; −10,14] ; distillé contre complet distillé −12,37 [−14,80 ; −9,74] ; distillé contre complet −8,89 [−10,78 ; −6,42]), latence ×1,99 sur processeur, ×1,28 (fp32) et ×1,63 (bf16) sur GPU ; **non retenu pour le service** ; run `20261006-121213-encodeur-elague-analyse-cinq-plis` |
| RM-46 | Élève TF-IDF à étiquettes souples | Latence de 2 ms conservée ; bras ensemble fait le 04/10/2026 : +0,69 [−1,03 ; +2,29], non résolu, 15 % de l'écart au professeur ; bras LoRA à faire |
| P3-03 | Balayage d'alpha et de T | |
| P3-04 | Plusieurs professeurs : moyenne ou pondération | |
| P3-05 | Direction de la KL | |
| P3-06 | Distillation des justifications | |
| P3-08 | Variantes LoRA, chacune avec son balayage de taux | |
| P3-09 | Pondération de classes, perte focale | |
| P3-10 | Courbes d'apprentissage de l'élève distillé | |
| P3-11 | Étiquettes nettoyées contre brutes | |
| P3-12 | Niveaux bloc et trois caractères | |
| P3-13 | Analyse d'erreurs approfondie | |
| P3-14 | Consolidation et contre-lecture des verdicts | |
| P3-15 | Nouvelle vérification de l'ouverture du test embargoé | |

### Étape R14 : compression et robustesse

**Objectif** : mesurer ce que coûtent la fusion, la quantification et les perturbations.
**Skills à charger** : performance-optimization, paired-comparison, model-card-calibration.
**Porte de sortie** : front de Pareto qualité contre coût ; robustesse mesurée.
**Arrêt ou repli si** : NVFP4 instable sur SM120, repli FP8 ou INT8.

| ID | Rôle dans l'étape | Point d'attention |
|---|---|---|
| P0-10 | Spike de quantification (INT8, FP8, NVFP4) | Juste avant son premier usage |
| P4-01 | Fusion des LoRA des cinq plis contre ensemble | |
| P4-02 | Quantification sur la tâche : qualité, latence, VRAM | |
| P4-03 | Augmentation au test | |
| P4-06 | Vérification croisée des implémentations conformes | Contrôle d'implémentation, pas validation des hypothèses |
| P4-07 | Robustesse : perturbations et spécialité exclue | |
| P4-09 | Front de Pareto | |
| RM-38 | Encodeur quantifié correctement (statique, sélectif, ONNX) | Fait en partie le 04/10/2026 : INT8 dynamique sélectif, l'effondrement vient du feed-forward ; attention seule −1,3 point, +11 % de vitesse, non retenue ; reste la quantification statique |
| RM-44 | Export ONNX Runtime et quantification statique étalonnée de l'encodeur | Dépendance au verrou seulement si retenue ; **partiel et négatif le 06/10/2026** : ONNX 32 bits identique (0,7362, latence p50 +8 %), INT8 statique min-max effondré à 0,0227 et plus lent (+39 %) ; variantes par centiles non mesurées (calibration de 128 textes à plus de 40 Go de RAM, coupée par `scripts/mem_guard.sh`) ; run `20261006-091535-onnx-int8-statique-partiel-camembert-deploy-ep10-lr1e-4` (statut `aborted`) ; **clos sur le résultat partiel le 06/10/2026 (Q25 validée)** : INT8 statique non retenu |
| RM-39 | Robustesse des modèles appris : perturbations, ablations de contenu, leave-one-author-out | Le TF-IDF à caractères est déjà insensible ; **partie inférence faite le 06/10/2026** (encodeur et LoRA, pli 0, cinq variantes, runs `20261006-171647-robustesse-modeles-appris-encoder` et `20261006-173250-robustesse-modeles-appris-lora`) : aucune perturbation de forme dégradée de façon résolue ; encodeur dégradé sans le début (−7,46), **LoRA effondré sans la fin (−64,0, cause non établie)** ; **diagnostic fait le 06/10/2026** (runs `20261006-181026-robustesse-lora-diagnostic-fin-retiree`, `20261006-182233-robustesse-lora-saut-de-ligne`) : palier dès 10 % de fin retirée, pas de collapse, le LoRA classe sur la fin de séquence ; le saut de ligne final explique une grande part sans tout expliquer ; **nouveaux auteurs de l'encodeur faits le 06/10/2026** (15 runs en plis d'auteurs, run `20261006-213214-encodeur-plis-auteurs-analyse`) : 0,7075 contre 0,6742 pour le TF-IDF, +3,32 [+0,53 ; +6,29] non résolu, perte de 5,2 points comparable à celle du TF-IDF ; **reste** un entraînement avec fin aléatoire (correction du LoRA) et le LoRA en plis d'auteurs (5 × 3,6 h, non fait) |
| RM-40 | Cascade par seuil de confiance (TF-IDF, encodeur, LoRA) (cascade_cv à cinq plis fait : encodeur puis LoRA non-inférieur, 93 % sans LoRA ; TF-IDF puis LoRA non) : calcul alloué selon la difficulté du cas | Aperçu hors ligne : 50 à 80 % des cas sans le LoRA, sans perte de macro-F1 ; seuil à valider sur plis distincts |
| RM-43 | Routage de la cascade par taille de l'ensemble conforme | Compare au seuil de probabilité ; **fait le 05/10/2026** : non-infériorité, 45,5 % sans LoRA, couverture par région mesurée (0,95 et 0,91) ; la cascade à seuil, plus économe, n'a pas sa couverture par région mesurée |

### Étape R15 : industrialisation

**Objectif** : n'industrialiser que ce qui sert un cas de démonstration explicite.
**Skills à charger** : api-and-interface-design, ci-cd-and-automation, observability-and-instrumentation, shipping-and-launch, code-review-and-quality, security-and-hardening.
**Porte de sortie** : service testé ; guide de transposition exécuté à blanc ; revue indépendante.
**Arrêt ou repli si** : un composant ne sert qu'à cocher un mot de l'offre, on ne le construit pas.

| ID | Rôle dans l'étape | Point d'attention |
|---|---|---|
| P0-09 | Spike vLLM | Juste avant son premier usage |
| P5-01 | Service FastAPI lisant le contrat | |
| P5-02 | Charge et latence p50 et p95 | |
| P5-03 | vLLM contre Transformers | |
| P5-04 | Indexation ElasticSearch | Seulement avec un scénario de démonstration |
| P5-05 | Composant EDS-NLP | Idem |
| P5-06 | CI GitLab | Seulement après création autorisée du dépôt |
| P5-07 | Guide `TRANSPOSER_AU_CHU.md` exécuté à blanc | |
| P5-08 | Dérive, maintenance, retour arrière | |
| P5-10 | Revue indépendante | Aucun envoi externe sans accord de Cyril ; **faite le 06/10/2026 par trois sous-agents locaux** (0 bloquant ; 12 constats importants ; 72 mutations survivantes dans les tests, tuées par 88 tests ajoutés ; 12 défauts corrigés) : `docs/revue_independante/` ; indépendance de personne et de modèle absente : relecture humaine à prévoir |
| P5-11 | Démo locale avec bannière « données fictives » | |
| RM-57 | Contournement des plantages du tokenizer et garde-fous mémoire | **Fait le 06/10/2026** : sous-processus épinglé (`src/llmft/tokenizer_guard.py`, `tokenizer_child.py`, 5 tests), run `20261005-224632-tokenizers-course-threads-qwen35` (25 échecs sur 31 runs sans épinglage, 0 sur 78 épinglés), `scripts/mem_watch.sh`, `scripts/mem_guard.sh`, page du wiki `incidents-et-audits-externes` ; `make check` vert |
| RM-58 | Fiabilité des lots : cache des identifiants, guillemetage des `run_*.sh`, identité vérifiée | **Guillemetage fait le 06/10/2026** (cause du code 2 de RM-45 : chemin du dépôt avec espaces) : 20 redirections dans 13 scripts plus les 3 corrigés avant, contrôle statique `tests/test_lot_scripts_quoting.py` (rouge avant, vert après) ; **identité vérifiée le 06/10/2026** : identifiants du sous-processus épinglé identiques au calcul non épinglé sur les 3 586 textes (CamemBERT-bio à 508 : 1 796 069 identifiants ; Qwen3.5-4B à 4096 : 4 754 872), run `20261006-105551-tokenizer-identite-sous-processus-epingle` (exploratoire ; coût mesuré du sous-processus : 75 s et 132 s par appel, sous charge GPU) ; **cache disque des identifiants fait le 06/10/2026** (`src/llmft/tokenizer_guard.py`, `artifacts/token_cache`, clé : nom, longueur, versions de `tokenizers` et `transformers`, empreinte de chaque texte ; 5 tests dans `tests/test_token_cache.py`, rouge avant) : CamemBERT-bio, 44,7 s au premier appel puis 0,07 s, identifiants identiques ; limite : la clé ne contient pas l'empreinte des fichiers du tokenizer ; **RM-58 faite** (Q24 : décision de garder le sous-processus pour tous les modèles) |

### Étape R16 : options (sur décision de Cyril)

**Objectif** : piste générative et location de GPU, chacune avec sa spécification propre. **Règle de Cyril (05/10/2026)** : la location de GPU distant et le stockage payant restent prévus comme options possibles, mais **aucun test ne les utilise : tous les tests se font en local** (RTX 5090 et disque de la machine) ; aucune tâche des étapes R0 à R15 ne dépend d'un coût.
**Skills à charger** : experiment-preregistration, distillation-pipeline, doubt-driven-development, dataset-intake, security-and-hardening.
**Porte de sortie** : selon l'option ouverte.
**Arrêt ou repli si** : la décision de Cyril manque, l'option reste fermée.

| ID | Rôle dans l'étape | Point d'attention |
|---|---|---|
| P6-01 | Contrat génératif de la conclusion | Module indépendant |
| P6-02 | Baseline zéro-shot et few-shot | |
| P6-03 | SFT LoRA | |
| P6-04 | Métrique de faits atomiques validée | |
| P6-05 | LLM-juge validé sur échantillon relu | |
| P6-06 | Distillation sur politique (TRL) | |
| P6-07 | GRPO à récompense vérifiable | |
| P6-08 | Décodage contraint | |
| R-01 | Fiche de location | Plafond validé par Cyril |
| R-02 | Fournisseur et licences de données | |
| R-03 | Profil matériel et pré-vol sur la machine louée | |
| R-04 | Exécuter et rapatrier | |
| R-05 | Comparer à protocole égal | |

---

## 6. Portes d'arrêt

| Porte | Après | Continuer si | Arrêter ou réduire si |
|---|---|---|---|
| RM-08 | R2 | Tâche, étiquettes et splits exploitables | Classes trop rares, groupes auteur insolubles, étiquette inadéquate |
| RM-15 | R6 | Références et variance permettent une comparaison informative | Résultat dominé par des raccourcis ou puissance insuffisante |
| RM-17 | R7 | La LoRA apporte une information ou une compétence utile dans le budget | Coût disproportionné sans signal : distillation réduite à une expérience d'apprentissage |
| RM-19 | R8 | Faisabilité, coût et tendance acceptables | OOM, temps complet hors budget, aucune tendance |
| RM-21 | R9 | Un candidat mérite calibration et robustesse | Verdict non résolu et aucun budget pour lever l'incertitude |
| Avant R15 | R11 | Un consommateur et un scénario de démonstration existent | Le service ne sert qu'à cocher un mot de l'offre |
| Avant R16 location | | Déclencheur scientifique précis et plafond accepté | La location sert seulement à agrandir le modèle |


**Règles de bifurcation écrites d'avance (05/10/2026)** : (a) *distillation (RM-32)* : élève à moins de 2 points du professeur, le LoRA sort du service et l'élève devient le système bon marché de référence ; élève à plus de 4 points sous l'encodeur non distillé, la distillation est publiée comme résultat négatif et l'ensemble encodeur + TF-IDF reste le système bon marché ; entre les deux, non résolu, une seconde graine par pli au plus. (b) *LoRA à cinq plis* : au moins 2 points au-dessus de l'ensemble avec borne basse positive, il entre dans le système final ; sinon il reste un professeur. (c) *synthétique et audit (P2-10, P2-06)* : gain résolu sur les cinq petits chapitres, entrée dans le système final ; sinon retrait et résultat négatif publié. (d) *benchmark public (RM-49)* : un chiffre publié dépassé avec intervalle, la performance se note 9 sur ce repère ; sinon 8, avec le repère cité honnêtement. (e) *débit d'entraînement (RM-41)* : équivalence statistique non démontrée, la modification n'entre pas dans les fiches.

---

## 7. Journal des amendements appliqués le 01/10/2026

Appliqués dans `MICROTACHES.md`, sans renuméroter :

- **Dépendances** : P0-04 et P0-08 dépendent de RM-05 ; P0-14 de RM-03 ; P0-28 de P0-33 et RM-07 ; P0-30 de RM-07 ; P1-11 de RM-13 ; P1-25 de P1-23 et RM-14 (plus de P1-24) ; P3-01 de P1-20 au lieu de P2-03, et P3-02 de P2-03 en plus ; P5-03 de P0-09 ; P0-46 de RM-02, RM-07, RM-11, RM-12.
- **Portée ★** : P0-31 devient ★ ; P0-03 devient ★ (décisions qui conditionnent R4) ; P1-09 et P1-24 sortent du chemin court.
- **Preuves** : P0-06 (classe de chargement réelle, repli verbaliseur), P0-21 (source, révision, périmètre), P0-30 (seuil fixé avant), P0-42 (gitleaks dès le premier commit), P0-43 (empreinte des partitions), P0-44 (deux variantes, coût d'ajout), P0-46 (REP, ADAPT, EXPLORE ; empreinte aussi dans le wiki), P0-47 (trois papiers), P4-05 et P4-06 (validation conforme et contrôle d'implémentation).
- **Nouvelle phase RM** : 24 tâches issues des audits.
- **Chemin court** : de 68 à 92 tâches ★ ; 159 tâches au total.

À appliquer dans `PLAN_PROJET_V6.md` (formulations corrigées par ChatGPT et par ma vérification) : livrable cible rendu neutre ; « meilleur niveau mesurable » remplacé par un compromis sous budget B et N ; « tout se transpose en changeant un contrat » remplacé par « une tâche de même famille ne modifie pas le noyau » ; « exactement ce qu'un site évaluateur attend » remplacé par « compatible avec l'architecture fédérée décrite » ; couverture conforme « valable sur PARHAF » remplacée par « conditionnelle aux hypothèses, évaluée sur le split observé » ; « trois mesures indépendantes » remplacé par « trois implémentations qui se recoupent » ; chiffres PARHAF avec révision et divergence de sources ; Gemma 4 non conditionné ; « plusieurs semaines » remplacé par « durée à mesurer en RM-16 » ; compte du chemin court.

### Amendements du 04/10/2026 (mesures du premier cycle, audits GLM v3 et v4)

- **16 tâches ajoutées sans renuméroter** (RM-25 à RM-40) : 12 ★ (références à recette mûre, discrétisation et auteur, LoRA mûr sur deux puis cinq plis, règle de puissance v2, ancrage externe, distillation vers l'encodeur, conforme par famille, mesures et service, rapport, acceptation du protocole v2) et 4 non ★ (9B mûr, quantification correcte, robustesse des modèles appris, cascade par seuil de confiance). Chemin court : 104 ★ sur 175.
- **Motif** : la recette gelée à 2 époques sous-estimait fortement les modèles appris (encodeur 0,448 contre 0,73 ; LoRA 0,587 contre 0,78), la règle de puissance v1 échoue (12,2 points contre 4,0), le meilleur TF-IDF bat la référence v1 de 3,65 points, et l'évaluation sur un pli est trop bruitée (cinq classes portent 85 % de la variance).
- **Protocole** : le protocole v1 reste gelé ; `docs/PROTOCOLE_V2_BROUILLON.md` et l'ADR-015 décrivent la suite, à accepter par Cyril (RM-37) avant tout run du second cycle et avant RM-20.
- **Tâches déjà réalisées à l'ajout** : RM-25, RM-26, RM-27, RM-36.
- **Existant recoupé** : P1-09 et P1-10 sont réalisées pour le pli 0 par RM-30 (elles restent au chemin complet pour les autres modèles) ; P1-16 (époques) est couverte pour l'encodeur et le LoRA par RM-25 et RM-27 ; P4-02, P4-07 et P4-09 restent les tâches de compression, de robustesse et de Pareto du chemin complet.

### Amendements du 04/10/2026, soir (efficience et déploiement)

- **8 tâches ajoutées sans renuméroter** (RM-41 à RM-48) : 3 ★ (débit d'entraînement, énergie et coût par run, fiche de déploiement) et 5 non ★ (routage conforme de la cascade, ONNX et INT8 statique, encodeur élagué, élève TF-IDF souple, longueur de contexte). Chemin court : 107 ★ sur 183.
- **Motif** : les dix leviers d'efficience et de déploiement retenus (distillation vers un élève bon marché, débit d'entraînement, mesures de service, cascade, quantification correcte, élève plus léger, service empaqueté, énergie par run, contexte adaptatif, fiche de décision) sont couverts par RM-32, RM-34, RM-35, RM-40 et ces huit tâches ; le service FastAPI, la charge, vLLM contre Transformers et la dérive restent P5-01, P5-02, P5-03 et P5-08, sans doublon.
- **RM-49 ajoutée le 05/10/2026** (benchmark public à résultats publiés) : sans repère publié, aucun écart avec l'état de l'art n'est vérifiable ; chemin court : 107 ★ sur 184.
- **Chaîne de dominos (05/10/2026)** : section 4.1 ajoutée (chemin critique, correspondance Q1 à Q12 et huit composantes, règles d'ordonnancement) ; règles de bifurcation écrites d'avance en section 6 ; **RM-50, RM-51, RM-52 ajoutées** (gel du système final avant l'ouverture, lecture confirmatoire de l'incertitude, rubrique de notation) ; RM-20 dépend désormais de RM-50 ; chemin court : 110 ★ sur 187.
- **Audit GLM v6 (05/10/2026)** : triage dans `docs/AUDIT_GLM_v6_TRIAGE.md` ; RM-53 à RM-55 ajoutées (encodeurs alternatifs, représentations gelées d'un LLM, recette d'encodeur v2) ; RM-29 réécrite (bootstrap par blocs d'auteurs, question primaire unique à 95 %) ; RM-43 complétée (couverture par région de la cascade) ; chemin court inchangé : 110 ★ sur 190.
- **RM-56 ajoutée le 05/10/2026** (distillation à professeur imbriqué) après le verdict de RM-32 : l'élève distillé de l'ensemble bat son professeur de +2,3 ; une fuite de second ordre est possible et doit être contrôlée ; chemin court : 111 ★ sur 191.
- **Règle d'exécution** : aucune de ces tâches ne modifie un fichier qu'un lot en cours importe ; RM-41 attend la fin du lot RM-28 et se valide par équivalence statistique avant tout usage dans une fiche préenregistrée.

---

## 8. Règles de conduite d'exécution

1. **Charger les skills de l'étape avant d'agir**, puis les utiliser pour ce pour quoi ils existent : un skill de méthode ne se récite pas, il se suit.
2. **Une étape se clôt sur ses preuves, jamais sur une impression.** À chaque porte, résumé court à Cyril : ce qui est prouvé, ce qui ne l'est pas, ce que la porte décide.
3. **Décisions de Cyril** : on propose avec un défaut recommandé et on attend la réponse. Une décision ouverte ne se comble jamais par une supposition.
4. **Git** : `git init` local est autorisé après P0-02. Aucun commit, push, dépôt distant ou changement de visibilité sans demande explicite.
5. **Temps d'attente utile** : pendant qu'une réponse de Cyril est attendue, avancer sur ce qui est indépendant (documents, téléchargements légers). Un sous-agent peut rédiger un brouillon dans `docs/` ou `knowledge/`, jamais lancer de GPU ni envoyer de contenu hors de la machine.
6. **GPU** : un processus que l'agent n'a pas lancé se signale et reste en place.
7. **Si un spike bloquant échoue**, on s'arrête et on présente le plan B (plan V6, section 9) avant de poursuivre.
8. **Une tâche qui dépasse environ 2 heures** se découpe encore.
9. **Revue croisée par Codex ou Gemini** : jamais sans accord explicite, à chaque fois.
10. **Aucune durée, aucun gain, aucun classement annoncé sans run_id.**

---

## 9. Décisions réservées à Cyril

| # | Décision | Bloque à partir de | Défaut recommandé |
|---|---|---|---|
| 1 | Emplacement du dossier | RM-03 | Rester ici |
| 2 | Plateforme du dépôt distant | Création distante (sur demande) | GitLab privé, plus tard ; Git local d'abord |
| 3 | Périmètre : jalon A, jalon B ou chemin complet | R6 | Jalon B |
| 4 | Date limite de candidature au CHUGA | Choix du jalon | Aucune connue |
| 5 | Démo locale ou publique (conditions d'usage de PARHAF) | P5-11 | Locale |
| 6 | Modèles à accès conditionné (MedGemma) | P0-06 | MedGemma optionnelle ; Gemma 4 en Apache 2.0 |
| 7 | Cap : budget B, essais N, métrique primaire, seuil « pratiquement utile », « local » (RM-02) | P0-46 | Métrique primaire proposée : macro-F1 au niveau chapitre. B et N à fixer après RM-16 |
| 8 | Fournisseur et plafond de location | R16 | Aucune location |
| 9 | Revue croisée externe | P5-10 | Fermée |
| 10 | Relecture des étiquettes (tu n'es pas clinicien) | P2-06 | Cohérence avec les définitions seulement |
| 11 | Fournir le texte intégral de l'offre CHUGA | RM-01 | À coller par Cyril |
| 12 | Relever le plafond de RAM de WSL (`.wslconfig`) | Aucun | À décider après RM-06 |

---

## 10. Vérificateurs et mode d'emploi

```text
python3 scripts/check_microtasks.py           # backlog : identifiants, dépendances, chemin court, couverture Q
python3 scripts/check_roadmap.py              # séquence : chaque tâche une fois, dépendances respectées
python3 scripts/check_roadmap.py --export     # régénère tasks/plan.md et tasks/todo.md (les cases cochées sont conservées)
```

Les deux vérificateurs forcent la sortie en UTF-8 et ne dépendent d'aucune bibliothèque tierce. Une modification de cette feuille de route ou du backlog se termine par leur relance.
- **Mise à jour du 06/10/2026** : LoRA final et temps A faits (RM-50 n'attend plus que la décision de Cyril) ; RM-44 partiel et négatif ; RM-45 lancé ; **RM-57 et RM-58 ajoutées** sans renuméroter (contournement du tokenizer et garde-fous mémoire, fait ; fiabilité des lots, à faire) ; état croisé des notes et des leviers dans `docs/SUIVI_NOTES_ET_LEVIERS.md` ; chemin court inchangé : 111 ★ sur 193.
