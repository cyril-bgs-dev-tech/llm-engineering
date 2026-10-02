# Audit qualité du brainstorm initial et du déroulé d'exécution

Date de l'audit : 01/10/2026  
Document principal audité : `PLAN_PROJET.md` (V1, le brainstorm initial)  
Référence de comparaison : `PLAN_PROJET_V6.md`  
Documents de contrôle : `MICROTACHES.md`, `BOITE_A_OUTILS.md`, `docs/CATALOGUE_LEVIERS.md`, `AGENTS.md`  
Nature du document : audit de spécification, de stratégie d'exécution et de traçabilité des affirmations. Ce document ne remplace ni le plan maître, ni `PROTOCOLE.md`, ni une décision de Cyril.

## 1. Verdict exécutif

Le brainstorm V1 est meilleur qu'un simple inventaire d'idées : il contient déjà une intention honnête, des données non réelles, un protocole préalablement écrit, des probabilités de professeur hors pli, des résultats négatifs conservés et des portes de phase fondées sur des preuves. Son défaut central est toutefois structurel : il choisit très tôt une histoire technique et professionnelle à démontrer, puis organise l'exécution autour de cette histoire. Autrement dit, la distillation, le LLM classifieur et la reproduction d'une recette Kaggle apparaissent comme la destination avant que la question scientifique, le jeu principal, la référence forte, le budget et les critères d'arrêt soient complètement définis.

La V6 corrige une grande partie de ces défauts. Elle ajoute PARHAF, le découpage par patient, le contrôle par auteur, les contrats de tâche, le registre immuable, les scorecards, les règles de preuve, la calibration, la prédiction conforme et un backlog contrôlé automatiquement. Elle reste néanmoins trop large pour être un plan d'exécution optimal : 68 micro-tâches dans le chemin court, dont 47 en P0, retardent fortement le premier résultat scientifique. Le plan reste majoritairement découpé horizontalement par infrastructure, données, modèles et documentation, alors qu'un projet incertain gagnerait à produire très tôt une tranche verticale minimale de bout en bout.

La conclusion de l'audit est donc la suivante :

1. Ne pas réécrire la V1 comme si elle redevenait la référence. La conserver comme historique et appliquer les corrections au plan maître V6.
2. Rendre l'objectif neutre quant au vainqueur. La réussite du projet est de produire une conclusion fiable sous contraintes, même si TF-IDF ou un encodeur bat le LLM distillé.
3. Réduire le chemin court à un premier fil scientifique complet avant les raffinements d'ingénierie.
4. Distinguer explicitement reproduction, adaptation et exploration. La recette LMSYS ne doit pas être qualifiée de reproduite si sa perte, ses données, ses modèles, son budget et sa tâche diffèrent.
5. Transformer chaque affirmation en entrée traçable : source, révision, périmètre, statut, date de vérification et règle de reformulation.
6. Ne démarrer aucun run comparatif tant que les décisions humaines ouvertes, le protocole et les critères d'arrêt ne sont pas figés.

## 2. Périmètre, hypothèses et méthode de l'audit

### 2.1 Interprétation retenue

L'expression « brainstorm de planification initiale » est interprétée comme visant `PLAN_PROJET.md`, car ce fichier se désigne lui-même comme « Plan v1 » et `PLAN_PROJET_V6.md` indique que V1 à V5 sont historiques. La V6 est néanmoins auditée elle aussi, car elle constitue la source de vérité actuelle et porte le déroulé d'exécution réellement envisagé.

### 2.2 Ce qui a été contrôlé

- La qualité de la formulation des objectifs.
- La séparation entre objectifs, hypothèses, moyens, livrables et affirmations futures.
- La couverture des éléments attendus d'une spécification exploitable.
- La logique des dépendances, des portes et des critères d'arrêt.
- Le temps nécessaire pour obtenir une première preuve utile.
- La cohérence interne entre plan, backlog et boîte à outils.
- La traçabilité d'un échantillon d'affirmations externes prioritaires.
- Les risques de biais de confirmation, de fuite, de surévaluation et de sur-ingénierie.

### 2.3 Ce qui n'a pas été fait

- Aucune décision de la section 10 de la V6 n'a été prise à la place de Cyril.
- Aucun jeu de données n'a été téléchargé.
- Aucun modèle n'a été entraîné ou évalué.
- Aucune licence n'a été interprétée comme un avis juridique.
- La totalité des articles de `BOITE_A_OUTILS.md` n'a pas été réauditée ligne par ligne.
- Aucune revue croisée externe par Codex ou Gemini n'a été lancée.

### 2.4 Vérifications mécaniques exécutées

- `scripts/check_microtasks.py` a été exécuté avec le Python fourni par l'environnement Codex et l'option UTF-8.
- Résultat : 135 micro-tâches, 68 tâches marquées ★, 6 scorecards, dépendances et fermeture formelle du chemin court valides.
- Limite importante : le script vérifie surtout la cohérence syntaxique et compte les tâches associées aux catégories Q. Il ne démontre pas que les preuves existent, que les seuils sont bien calibrés, ni que le découpage est stratégiquement optimal.
- Dans l'environnement observé, `python scripts/check_microtasks.py` ne fonctionne pas tel quel, car `python` n'est pas dans le `PATH`. Avec un Python Windows en encodage CP1252, l'impression du symbole ★ provoque aussi une erreur. La commande reproductible doit donc passer par `uv run`, un exécutable Python explicitement documenté ou une configuration UTF-8.
- Le dossier observé n'est pas reconnu comme dépôt Git et ne contient pas de `.git`. C'est cohérent avec un projet encore avant P0, mais incompatible avec toute affirmation actuelle de versionnement, de CI ou de reconstruction depuis un clone.
- `PROTOCOLE.md`, `CONSTRAINTS.md`, `tasks/plan.md` et `tasks/todo.md` n'existent pas encore. Leur absence est normale avant leur micro-tâche de création, mais elle signifie que le projet n'est pas autorisé à entrer en phase d'implémentation ou de comparaison.

## 3. Diagnostic de maturité par dimension

Les appréciations ci-dessous ne sont pas des scorecards Q1 à Q12. Elles décrivent uniquement la maturité de la planification actuelle.

| Dimension | V1 | V6 | Diagnostic |
|---|---|---|---|
| Intention et honnêteté | Forte | Forte | Le manque d'expérience est dit, les résultats négatifs sont acceptés et les affirmations publiques sont différées. |
| Problème à résoudre | Partiel | Partiel | Le projet mélange objectif scientifique, démonstration de compétence, alignement avec une offre et construction d'un service. |
| Critères de succès | Faibles | Moyens | Les preuves de phase sont nombreuses, mais le succès global reste formulé comme « meilleur niveau mesurable » ou comme obtention d'un LLM distillé. |
| Neutralité expérimentale | Faible | Moyenne | Les références sont plus fortes en V6, mais le livrable cible présuppose encore un LLM distillé, calibré et abstentionniste. |
| Données et fuite | Faible à moyen | Fort sur le papier | La V6 traite patient, auteur, gabarit, test scellé et probabilités hors pli. Les seuils et le statut du split principal restent à figer. |
| Statistique | Moyen | Fort sur le papier | Appariement, bootstrap, graines et Holm sont prévus. L'unité de rééchantillonnage, la famille de tests et la puissance ne sont pas encore opérationnelles. |
| Exécution | Moyen | Trop large | Les dépendances formelles sont bonnes, mais le premier résultat arrive trop tard et P0 est surchargée. |
| Interfaces et contrats | Faible | Moyen à fort | Le contrat de tâche est une excellente direction. Les versions de schéma, CLI, manifestes et règles de compatibilité ne sont pas encore spécifiées. |
| Reproductibilité | Faible | Forte sur le papier | Verrouillage, Docker, empreintes et reconstruction à froid sont prévus, sans commandes canoniques encore disponibles. |
| Traçabilité des déclarations | Faible | Moyenne | La boîte à outils indique un statut de lecture, mais plusieurs phrases transforment encore une source ou une hypothèse en conclusion. |
| Maîtrise du périmètre | Faible | Moyenne | La piste générative est optionnelle, mais service, ElasticSearch, EDS-NLP, nombreuses variantes, triple conformité et documentation exhaustive s'accumulent. |
| Valeur pour la candidature | Forte si prouvée | Forte si focalisée | Le projet peut produire un récit crédible, à condition de ne pas sacrifier le premier résultat au désir de tout couvrir. |

## 4. Ce que la V1 fait déjà bien

Ces éléments doivent être conservés dans toute révision :

1. Le plan reconnaît explicitement le manque d'expérience initial au lieu de le masquer.
2. Il interdit toute publication de résultats non mesurés.
3. Il limite les données à des sources publiques, fictives ou générées.
4. Il prévoit un test scellé et des probabilités de professeurs hors pli.
5. Il sépare plusieurs phases et exige une preuve à chaque sortie.
6. Il conserve les résultats négatifs.
7. Il mesure qualité et coût, pas seulement une métrique de prédiction.
8. Il maintient la piste générative comme option et non comme prérequis initial.
9. Il reconnaît la compatibilité Blackwell comme un risque à vérifier.
10. Il prévoit des références encodeurs, ce qui évite une comparaison uniquement entre LLM.

La V6 améliore encore cette base avec les contrats de tâche, le registre immuable, les scorecards, les fiches de données, la séparation patient-auteur, la calibration, la conformité et la règle « aucun chiffre sans run_id ».

## 5. Défauts structurants du brainstorm V1

### 5.1 L'objectif est formulé comme un récit à rendre vrai

Le passage « ce projet existe pour que la réponse [...] devienne oui » est honnête, mais il introduit un biais de confirmation. Le projet risque de privilégier une configuration permettant de dire « j'ai fine-tuné et distillé un LLM » plutôt que la conclusion la plus utile sous contrainte.

Correction recommandée :

> Déterminer, sous une enveloppe de calcul fixée et sur une tâche clinique française fictive précisément définie, quelle famille de méthodes offre le meilleur compromis entre qualité, calibration, coût et reproductibilité. Le verdict peut être favorable à une méthode non LLM, à un encodeur, à une LoRA simple ou à la distillation.

Le fine-tuning reste une expérience obligatoire pour combler le manque de compétence, mais il ne devient pas artificiellement le meilleur produit final.

### 5.2 Le plan confond quatre objectifs

La V1 mélange :

- un objectif d'apprentissage personnel ;
- une question scientifique sur la distillation ;
- une preuve d'ingénierie transposable au CHU ;
- un artefact de candidature.

Ces objectifs peuvent coexister, mais leurs critères de succès ne sont pas identiques. Ils doivent être séparés dans le plan maître.

Proposition de hiérarchie :

| Niveau | Objectif | Preuve de succès |
|---|---|---|
| O1 Compétence | Réaliser au moins un fine-tuning LoRA ou QLoRA de bout en bout | Run reproductible, tests, configuration et analyse d'erreurs |
| O2 Science | Estimer l'effet causal pratique de la distillation face à une référence réglée | Comparaison préenregistrée, appariée, avec intervalle et verdict en trois valeurs |
| O3 Ingénierie | Montrer qu'une même chaîne accepte au moins deux contrats de tâche | Test de transposabilité, coût d'adaptation mesuré |
| O4 Candidature | Produire uniquement des affirmations défendables | Tableau claim-gate relié aux run_id et aux sources |

### 5.3 La solution est choisie avant la question

« Distiller des LLM » est à la fois le titre, la méthode de référence et la conclusion attendue. Une meilleure spécification devrait définir d'abord : population de données, tâche, unité d'analyse, métrique primaire, budget, comparateurs et seuil de décision. La distillation devient ensuite une hypothèse parmi d'autres.

### 5.4 L'analogie LMSYS vers le clinique est suraffirmée

Les phrases « le parallèle [...] est direct » et « c'est exactement la contrainte de la compétition » sont trop fortes. LMSYS prédit une préférence entre deux réponses de chat avec une métrique et une distribution propres à la compétition. Le projet clinique prédit des catégories à partir de documents ou de patients, avec des risques de fuite, une hiérarchie d'étiquettes et une finalité différentes.

Le fait que deux tâches acceptent deux textes ne suffit pas à établir une équivalence. CLISTER et LMSYS diffèrent aussi par leur cible : score ordinal de similarité d'un côté, préférence probabiliste à trois classes de l'autre.

Reformulation :

> La recette LMSYS constitue une source d'hypothèses techniques transférables à tester. Sa validité sur les tâches PARHAF n'est pas présumée.

### 5.5 « Reproduction » est le mauvais mot pour le programme réel

Une reproduction fidèle demanderait au minimum la même tâche, les mêmes données, la même fonction de perte, les mêmes modèles ou des équivalents justifiés, le même protocole et un critère explicite de concordance avec le résultat publié. Le projet change presque tous ces éléments.

Il faut distinguer trois pistes :

- `REP` : vérification ciblée d'un mécanisme exact de la recette source ;
- `ADAPT` : transfert du mécanisme à la classification clinique française ;
- `EXPLORE` : variantes nouvelles propres au projet.

Le résultat attendu est une adaptation contrôlée, pas une reproduction globale de la première place LMSYS.

### 5.6 Le jeu principal initial est trop faible pour soutenir l'ambition

DiaMED avec 739 cas et environ vingt chapitres risque de produire de faibles effectifs par classe, une grande variance et peu de puissance pour départager des recettes coûteuses. La phrase « c'est précisément là que la distillation doit prouver son intérêt » transforme une intuition en obligation de résultat.

La V6 corrige utilement ce point en choisissant PARHAF, mais elle doit encore faire de la viabilité de la cible une première porte CPU : disponibilité des étiquettes, distribution, classes rares, textes qui divulguent directement le scénario et faisabilité du split groupé.

### 5.7 Le protocole V1 expose le test à l'itération

Le plan annonce des ablations S1 à S7 et des comparaisons sur le test. Si le test est consulté après chaque variante, il devient de fait une validation adaptative. Le test scellé doit être ouvert une seule fois pour la sélection finale, après développement sur plis ou validation imbriquée.

Il faut distinguer :

- développement : validation croisée ou validation interne ;
- sélection : règle préenregistrée sur métrique primaire ;
- confirmation : test scellé, une fois ;
- exploration postérieure : clairement étiquetée exploratoire, sans recycler le verdict confirmatoire.

### 5.8 Les stratégies S1 à S7 ne sont pas indépendantes

« Chaque stratégie ajoutée seule à la référence » n'est pas toujours définissable. La fusion de LoRA suppose plusieurs plis, la distillation suppose un professeur, et la quantification porte sur un modèle déjà choisi. Une simple ablation unitaire ne mesure pas correctement les interactions.

Il faut un graphe de traitements et une matrice de comparaison préenregistrée : référence, ajout admissible, coût incrémental, interaction étudiée, famille statistique et règle d'arrêt.

### 5.9 Les estimations de délai et de mémoire ne sont pas des engagements prouvés

Les budgets VRAM, « environ 2 à 3 semaines » et « P1 + P3 suffisent » sont insuffisamment étayés. P3 dépend de P2, et les temps GPU ne sont pas dérivés d'un débit mesuré. Toute estimation doit porter trois valeurs : hypothèse, mesure pilote, intervalle avec marge.

### 5.10 L'industrialisation risque d'être une imitation de l'offre

FastAPI, ElasticSearch, GitLab, Wiki et maintenance sont ajoutés parce qu'ils figurent dans l'offre. Ils peuvent être pertinents, mais ils ne doivent pas précéder le résultat scientifique. Le projet doit démontrer une capacité d'intégration minimale, puis n'ajouter une intégration que si elle soutient un critère de candidature ou une preuve de transposabilité.

## 6. Audit de la V6 comme spécification exécutable

### 6.1 Couverture des éléments attendus d'une spécification

| Élément | État | Observation |
|---|---|---|
| Objectif | Partiel | Le cap est clair, mais le livrable présuppose qu'un LLM distillé est la bonne sortie. |
| Commandes | Absent | Aucune liste canonique de commandes d'installation, test, lint, mini-run, reprise et reproduction. |
| Structure du projet | Partiel | La V1 donne une arborescence, mais la V6 ajoute de nouveaux artefacts sans arborescence consolidée. |
| Style de code | Absent | Identifiants en anglais et documentation en français sont définis, mais aucun exemple canonique ni règle de module. |
| Stratégie de test | Forte mais dispersée | De nombreux tests sont prévus dans les micro-tâches ; niveaux, commandes et seuils restent à centraliser dans `CONSTRAINTS.md`. |
| Limites Always / Ask first / Never | Forte mais dispersée | `AGENTS.md` contient des règles solides, mais elles ne sont pas résumées dans la spécification pour le lecteur humain. |
| Critères de succès globaux | Partiels | Les portes sont précises, le succès scientifique global et les critères d'arrêt ne le sont pas assez. |
| Questions ouvertes | Forte | La section 10 les expose correctement et réserve les décisions à Cyril. |
| Carte de capacités | Absente | Le plan regroupe plusieurs capacités indépendamment vérifiables dans un seul flux P0 à P6. |

### 6.2 Le « meilleur niveau mesurable » n'est pas testable

La promesse « le meilleur niveau mesurable sur une RTX 5090 » ne définit ni espace de recherche, ni temps maximal, ni nombre d'essais, ni métrique primaire, ni seuil de coût. Elle est ouverte et encourage l'optimisation sans fin.

Remplacement recommandé :

> Sous un budget de [B] heures GPU sur RTX 5090 et [N] essais de réglage par famille, sélectionner le point Pareto admissible selon macro-F1, log loss, calibration, VRAM et latence. Les valeurs B et N sont décidées par Cyril avant V0.

Les crochets restent ouverts tant que la décision de budget n'est pas prise.

### 6.3 Le livrable cible est biaisé vers une technique

« Un classifieur LLM distillé, calibré, capable de s'abstenir » définit déjà le gagnant. Le livrable devrait être :

> Une chaîne expérimentale générique et un candidat final choisi après comparaison préenregistrée. Le candidat peut être TF-IDF, encodeur, LoRA simple ou élève distillé. Si aucun candidat n'atteint les critères minimaux, le livrable est un verdict négatif documenté et reproductible.

### 6.4 « Tout se transpose en changeant un contrat » est trop absolu

Le contrat ne peut pas absorber automatiquement les différences de tokenisation, de multi-label, d'ordinalité, de pooling, de métriques, de calibration et de génération. Le code peut avoir un noyau générique, mais il aura nécessairement des adaptateurs explicites.

Critère plus précis :

> Ajouter une tâche de même famille ne modifie pas le noyau d'entraînement et d'évaluation ; seules une spécification YAML et un adaptateur de données situé dans un répertoire autorisé changent. Le coût d'ajout est mesuré en fichiers, lignes et durée.

La recherche des identifiants de tâche dans `src/` est utile mais insuffisante : du code peut rester couplé par forme, colonnes ou métriques sans contenir le nom du task_id.

### 6.5 Une carte de capacités manque avant le plan de phases

Proposition de carte, à faire valider avant de réordonner le backlog :

| Module stable | Responsabilité | Dépend de |
|---|---|---|
| `governance` | Décisions, budgets, licences, règles de publication | rien |
| `data-contracts` | Intake, version, labels, splits, contrats de tâche | `governance` |
| `experiment-core` | Configurations, registre, reprise, exécution reproductible | `governance` |
| `evaluation-core` | Métriques, appariement, calibration, fuites | `data-contracts`, `experiment-core` |
| `baseline-models` | TF-IDF, encodeur, LoRA de référence | `data-contracts`, `evaluation-core` |
| `distillation` | Professeurs hors pli, pertes, élève | `baseline-models` |
| `candidate-safety` | Calibration, conformité, abstention, robustesse | `distillation` ou meilleur modèle de `baseline-models` |
| `delivery` | Reconstruction, service et intégrations retenues | `candidate-safety` |
| `generative-track` | Résumé ou extraction générative optionnelle | décision explicite de Cyril, composants génériques utiles |

Cette carte montre que la calibration et l'abstention doivent pouvoir s'appliquer au meilleur modèle, pas uniquement au modèle distillé.

### 6.6 P0 est trop grosse et trop horizontale

La P0 comporte 47 micro-tâches. Le chemin court attend notamment des décisions, des spikes sur plusieurs modèles, un Dockerfile, un audit de dépendances, une fiche de données, plusieurs contrats, un registre, un chargeur générique, des tests de fuite, un protocole et huit pages wiki avant G-P0.

Le risque est de passer plusieurs jours ou semaines à construire une infrastructure sans savoir si la tâche principale est viable et si un signal de base existe.

Le principe « le risque d'abord » doit utiliser un classement explicite :

`priorité = impact × probabilité ÷ coût de levée`

Avec cette règle, la présence, la qualité et la distribution de la cible PARHAF sont probablement à vérifier avant le support exhaustif de six modèles ou la quantification NVFP4.

### 6.7 Le chemin court n'est pas un MVP au sens stratégique

Le chemin ★ est formellement fermé, ce que le script confirme. Il n'est cependant pas minimal :

- P1-11 crible quatre à six modèles.
- P1-13 prévoit douze runs.
- P1-19 ajoute cinq graines.
- P2-02 entraîne cinq plis d'un professeur.
- P0-47 exige l'ingestion de huit papiers avant la porte P0.
- La reconstruction à froid n'arrive qu'en P5, longtemps après le premier run.

Le MVP scientifique devrait répondre à une question plus petite : « la chaîne peut-elle produire un résultat honnête, reproductible et comparable sur une tâche principale ? »

### 6.8 Le split principal n'est pas fixé assez tôt

La V6 prévoit un split par patient, puis un split groupé par auteur en contrôle, et rend le split auteur principal si un modèle témoin prédit au-delà du hasard. La direction est bonne, mais « au-delà du hasard » doit devenir un seuil préenregistré avant l'observation. Il faut aussi définir ce qui se passe si groupement par auteur et stratification par classe sont incompatibles.

À préciser dans `PROTOCOLE.md` :

- unité de split ;
- unité de bootstrap ;
- règle de groupement ;
- tolérance de déséquilibre ;
- seuil faisant du contrôle auteur le résultat principal ;
- traitement des auteurs n'apparaissant que dans une classe ;
- statut confirmatoire ou exploratoire de chaque split.

### 6.9 La règle « gain supérieur à deux écarts-types » est ad hoc

L'écart-type entre graines et l'incertitude appariée entre exemples mesurent des sources de variance différentes. Une règle fixe combinant les deux n'est pas automatiquement un test valide. Il faut définir un estimand, par exemple la différence moyenne de macro-F1 entre recettes sous variation de graine, puis un modèle ou un bootstrap hiérarchique approprié. À défaut, présenter séparément : intervalle sur exemples, variance entre graines, taille d'effet pratique et décision préenregistrée.

### 6.10 La famille de comparaisons de Holm n'est pas définie

« Correction de Holm » ne suffit pas. Le plan doit dire quels tests appartiennent à la même famille : tous les leviers d'une vague, toutes les métriques, tous les niveaux CIM-10 ou uniquement la métrique primaire. Sans cela, la correction peut être appliquée après coup de manière favorable.

### 6.11 La conformité ne se valide pas par trois nombres proches

MAPIE, TorchCP et une implémentation maison ne constituent pas trois expériences indépendantes. Des couvertures proches peuvent simplement partager la même mauvaise hypothèse ou le même split. La validation devrait inclure : cas jouets analytiques, invariants, comparaison à une référence, couverture conditionnelle pertinente et test sous rupture d'échangeabilité. La phrase « garantie valable sur PARHAF » doit être remplacée par « garantie conditionnelle aux hypothèses, évaluée sur le split PARHAF observé ».

### 6.12 La scorecard peut devenir un indicateur de volume plutôt que de preuve

Le script compte le nombre de micro-tâches associées à Q1-Q12. Ce comptage ne prouve pas la note. Une seule preuve forte peut être suffisante ; dix tâches faibles ne le sont pas. Chaque scorecard doit valider un schéma de preuve :

- identifiant de l'exigence ;
- artefact exact et empreinte ;
- commande de reproduction ;
- résultat attendu et observé ;
- auteur ou mécanisme de confirmation indépendante ;
- date ;
- défaut résiduel ;
- justification de la note.

### 6.13 La confirmation « indépendante » doit être définie

Une seconde implémentation écrite par le même agent avec le même contexte n'est pas nécessairement indépendante. Il faut définir les degrés :

- indépendance de code ;
- indépendance de données ;
- indépendance de méthode ;
- indépendance de personne ou de contexte ;
- reconstruction à froid.

La V6 ne doit pas attribuer automatiquement une note 3 simplement parce qu'un second outil produit une valeur proche.

### 6.14 L'environnement identique local-location est irréaliste au sens strict

Une image conteneur peut garder le même espace utilisateur, mais les pilotes, le noyau GPU et certaines bibliothèques compilées dépendent de l'hôte. La promesse doit devenir « image utilisateur identique avec matrice de compatibilité des pilotes et profil matériel distinct ».

### 6.15 Les commandes canoniques manquent

Le plan devrait publier dès P0 les commandes contractuelles, même si elles sont initialement des cibles à implémenter :

```text
uv sync --frozen
uv run pytest
uv run ruff check .
uv run mypy src
uv run python scripts/check_microtasks.py
uv run python -m <module> validate-task --spec <path>
uv run python -m <module> smoke-train --task <id> --hardware rtx5090
uv run python -m <module> evaluate --run-id <id> --sealed-test
make reproduce-small
```

Les noms exacts restent à approuver lors de la spécification de l'interface CLI.

## 7. Audit des déclarations prioritaires

Statuts utilisés :

- **Prouvé** : source primaire ou artefact local directement concordant.
- **Partiellement prouvé** : source présente, mais formulation plus large que la preuve.
- **À vérifier** : source secondaire, recherche seule, version ou périmètre absent.
- **À reformuler** : jugement ou hypothèse présenté comme un fait.
- **À retirer pour l'instant** : affirmation non soutenue ou prématurée.

| Affirmation | Localisation | Statut | Observation et correction |
|---|---|---|---|
| L'offre CHUGA contient les missions et la stack listées | V1 lignes 7 à 13 ; V6 ligne 16 | À vérifier | Le texte de l'offre n'est pas dans le dépôt. Archiver l'annonce, son URL ou PDF, la date et une empreinte avant de fonder le périmètre dessus. |
| Le parallèle LMSYS-CHU est direct et la contrainte est exactement la même | V1 lignes 34 à 36 | À reformuler | Analogie utile, mais tâches, données, risques et matériel diffèrent. Employer « hypothèse de transfert ». |
| CLISTER est le format exact de LMSYS et sert directement l'évaluation de textes générés | V1 lignes 57 à 64 | À reformuler | Deux entrées ne suffisent pas : cible ordinale de similarité contre préférence de réponse. Le lien avec la qualité générative doit être démontré, pas affirmé. |
| Le faible volume de DiaMED est précisément l'endroit où la distillation doit prouver son intérêt | V1 lignes 53 à 54 | À reformuler | C'est une hypothèse ; le faible volume peut aussi rendre l'effet non résolu. |
| QLoRA 24 à 27B tient dans 20 à 28 Go | V1 lignes 87 à 96 | À vérifier | Estimation sans run_id. Conserver uniquement comme hypothèse de pré-vol. |
| Un 7 à 9B est « déployable sur un GPU hospitalier » | V1 ligne 91 | À reformuler | Le matériel du CHU n'est pas documenté. Dire « cible de taille pour une carte unique comparable, à confirmer ». |
| P1 + P3 suffisent pour la candidature | V1 lignes 178 à 180 | À reformuler | P3 dépend de P2 ; le minimum dépend aussi de la date, de la qualité du résultat et de claim-gate. |
| Le projet prendra environ deux à trois semaines | V1 ligne 178 | À retirer pour l'instant | Aucun débit pilote ni calendrier de disponibilité n'étaye cette estimation. |
| PARHAF contient 4 254 patients publiés | V6 ligne 27 | À corriger et versionner | La fiche actuelle affiche 4 259 patients et 6 190 documents. Le papier décrit 5 009 cas et 7 394 rapports au total, embargo compris. Chaque chiffre doit citer source, révision et périmètre. |
| PARHAF a 18 ou 20 spécialités | V6 lignes 102 et 123 | Partiellement prouvé | Le papier parle de 18 spécialités d'auteurs ; la fiche actuelle expose 20 valeurs de spécialité. Les concepts ne sont pas nécessairement identiques. Les nommer séparément. |
| Les usages « décision clinique, validation, généralisation, déploiement » sont interdits | V6 ligne 122 | Partiellement prouvé | La fiche officielle les classe comme usages exclus ou non prévus. Ne pas les confondre automatiquement avec une clause de licence juridiquement opposable ; consigner séparément licence, conditions et intended/excluded uses. |
| PARTAGES prévoit sept modèles et huit cas d'usage | V6 lignes 29 et 126 | Prouvé | La page officielle du Health Data Hub indique sept modèles et huit cas d'usage. |
| Le cas résumé va d'octobre 2026 à juin 2027 et utilise les faits atomiques | V6 ligne 127 | Prouvé | La fiche officielle donne le calendrier du 01/10/2026 au 30/06/2027 et décrit la comparaison bidirectionnelle de faits atomiques. |
| Le découplage par contrat est exactement ce qu'un site évaluateur attend | V6 ligne 127 | À reformuler | C'est une inférence raisonnable, pas une exigence explicitement démontrée. Dire « compatible avec l'architecture fédérée décrite ». |
| `DistillationTrainer` exige un vocabulaire commun | V6 ligne 31 | Prouvé | La documentation officielle TRL le dit explicitement pour le modèle professeur. |
| La perte `alpha*CE + (1-alpha)*T²*KL` reproduit la première place LMSYS | V6 lignes 171 et 187 | À reformuler | Le dépôt de la solution publiée utilise CE, deux KL et deux pertes cosinus, moyennées. La perte V6 est une baseline adaptée de distillation au niveau des classes, pas la reproduction exacte. |
| Qwen3.8-27B et Gemma 4 31B sont des candidats directs à `AutoModelForSequenceClassification` | V6 lignes 147 à 149 et 167 | À vérifier | Les cartes officielles les présentent comme modèles multimodaux génératifs chargés via `AutoModelForMultimodalLM`. P0-06 est donc bloquant, pas une simple formalité. |
| Tout se transpose en changeant un YAML | V6 lignes 19 et 133 | À reformuler | Il faut autoriser des adaptateurs de famille et mesurer l'effort de transposition. |
| Une couverture conforme observée sur PARHAF constitue une garantie valable sur PARHAF | V6 ligne 174 | À reformuler | La garantie dépend de l'échangeabilité et du protocole de split ; l'observation empirique ne prouve pas l'hypothèse. |
| 68 tâches forment un chemin court fermé | V6 ligne 210 | Prouvé formellement | Le script local confirme 68 tâches ★ sur 135 et l'absence d'erreur structurelle. « Fermé » ne signifie pas « minimal » ni « faisable dans le délai ». |
| La recette LMSYS peut être copiée | `BOITE_A_OUTILS.md` ligne 61 | Correctement limité | Le dépôt ne présente pas de licence visible ; le plan exige lecture et réimplémentation. Conserver cette règle. |

## 8. Sources primaires utilisées pour le contrôle externe

1. [Fiche officielle PARHAF sur Hugging Face](https://huggingface.co/datasets/HealthDataHub/PARHAF) : statistiques publiées, structure, origine, usages prévus et exclus.
2. [Article PARHAF, arXiv:2603.20494](https://arxiv.org/abs/2603.20494) : périmètre total du corpus et méthode de constitution.
3. [Page officielle du projet PARTAGES](https://www.health-data-hub.fr/page/projet-partages) : sept modèles, huit cas d'usage et plateforme d'évaluation fédérée.
4. [Fiche officielle du cas d'usage résumé PARTAGES](https://www.health-data-hub.fr/projets/resume-automatique-multicentrique-des-comptes-rendus-medicaux-cas-dusage-3-projet-partages) : finalité, faits atomiques, évaluation distribuée et calendrier.
5. [Documentation officielle TRL DistillationTrainer](https://huggingface.co/docs/trl/en/distillation_trainer) : distillation autorégressive sur politique et vocabulaire commun du professeur et de l'élève.
6. [Dépôt publié LMSYS BlackPearl](https://github.com/shyoulala/LMSYS_BlackPearl) : matériel, modèles, cinq plis, pertes, fusion LoRA et GPTQ.
7. [Carte officielle Qwen3.8-27B](https://huggingface.co/Qwen/Qwen3.8-27B) : architecture multimodale générative, licence et chargement recommandé.
8. [Carte officielle Gemma 4 31B](https://huggingface.co/google/gemma-4-31B) : architecture multimodale générative, licence et chargement recommandé.

Toutes les autres références de `BOITE_A_OUTILS.md` conservent leur statut local tant qu'elles n'ont pas été relues à la source et ingérées avec citations précises.

## 9. Déroulé d'exécution recommandé

Ce déroulé ne doit pas remplacer le backlog sans validation de Cyril. Il propose une meilleure logique de réduction du risque et de temps vers la première preuve.

### G0. Gate humaine et archivage des sources

Objectif : rendre la suite autorisée et auditable.

Critères de sortie :

- décisions 1 à 6 de la section 10 datées, même si certaines réponses sont « non pour le MVP » ;
- date de candidature ou horizon de décision connu ;
- texte de l'offre archivé et empreinté ;
- périmètre « local » défini : données locales, calcul local, ou absence totale de service externe ;
- budget maximal du premier cycle fixé ;
- revue externe et location laissées fermées sans accord explicite.

### S0. Viabilité des données, CPU seulement

Objectif : savoir si la question principale peut réellement être posée.

Critères de sortie :

- révision PARHAF épinglée ;
- licence, conditions et usages exclus séparés ;
- nombres recomptés ;
- disponibilité et format du diagnostic principal mesurés ;
- distributions de classes et groupes auteur-patient établies ;
- faisabilité d'au moins un split groupé évaluée ;
- décision explicite : continuer, simplifier la cible ou changer de tâche.

Arrêt : si les classes, les groupes ou les étiquettes empêchent une estimation crédible, ne pas installer six gros modèles.

### S1. Fil synthétique de bout en bout

Objectif : valider l'architecture minimale sans coût GPU significatif.

Chaîne : contrat synthétique -> chargeur -> split -> modèle trivial -> métriques -> registre -> reprise -> rapport.

Critères de sortie :

- un seul contrat valide et un contrat invalide rejeté ;
- registre immuable ;
- cas de fuite piégé détecté ;
- commande unique documentée ;
- reproduction depuis un environnement propre ou jetable.

### S2. Baseline réelle sur une seule tâche principale

Objectif : obtenir le premier résultat scientifique utile.

Comparateurs minimaux : majorité, TF-IDF + régression logistique, un encodeur français.

Critères de sortie :

- métrique primaire et unités figées ;
- validation groupée ;
- intervalle et coût ;
- analyse de raccourci auteur-gabarit ;
- score suffisamment informatif pour justifier ou arrêter le LLM.

### S3. Une LoRA de référence

Objectif : prouver le fine-tuning LLM avec le plus petit espace de recherche défendable.

Contraintes :

- un seul élève présélectionné après le spike de compatibilité ;
- taux d'apprentissage prioritaire ;
- budget identique publié ;
- pas de criblage de six modèles dans le premier cycle ;
- cinq graines seulement sur la configuration retenue, si le budget le permet.

Gate : si la LoRA est dominée en qualité et coût par l'encodeur, la distillation n'est poursuivie que comme expérience d'apprentissage explicitement limitée, pas comme candidat final présumé.

### S4. Spike de distillation miniature

Objectif : vérifier mécanisme, mémoire et signal avant cinq plis coûteux.

Critères de sortie :

- perte testée sur cas analytiques ;
- un pli ou sous-échantillon ;
- une seule paire professeur-élève ;
- différence entre recette LMSYS exacte et baseline CE+KL documentée ;
- estimation mesurée du coût du run complet ;
- règle go/no-go préenregistrée.

### S5. Expérience confirmatoire de distillation

Objectif : répondre à la question scientifique centrale.

Critères de sortie :

- probabilités hors pli complètes avec manifeste ;
- configuration gelée ;
- famille de tests et correction multiples définies ;
- référence, tâche voisine, distillation et combinaison comparées ;
- verdict `gain`, `absence de gain` ou `non résolu` ;
- test scellé ouvert une seule fois selon le protocole.

### S6. Fiabilité du meilleur candidat, quelle que soit sa famille

Objectif : calibrer, conformiser et tester la robustesse du meilleur point Pareto, pas seulement l'élève distillé.

Critères de sortie :

- calibration et ECE ;
- couverture conforme avec hypothèses explicites ;
- politique d'abstention ;
- robustesse aux perturbations ;
- carte de modèle ;
- limites « données fictives » visibles.

### S7. Livraison ciblée

Objectif : ne construire que l'industrialisation utile à la candidature ou à la démonstration.

Ordre recommandé :

1. reconstruction à froid ;
2. rapport et claim-gate ;
3. démo locale minimale si Cyril la choisit ;
4. service FastAPI si nécessaire ;
5. EDS-NLP et ElasticSearch uniquement avec un cas de démonstration explicite ;
6. CI distante uniquement après création autorisée du dépôt.

### S8. Piste générative indépendante

La piste résumé doit devenir un module optionnel avec sa propre spécification. Elle ne doit pas être la phase suivante naturelle d'un pipeline de classification, car son contrat, ses métriques, ses modèles et ses risques sont différents.

## 10. Critères d'arrêt recommandés

Un plan intelligent dit aussi quand ne pas continuer.

| Point de décision | Continuer si | Arrêter ou réduire si |
|---|---|---|
| Après S0 | Tâche, labels et split sont exploitables | Classes trop rares, groupe auteur insoluble, label inadéquat |
| Après S2 | Baselines et variance permettent une comparaison informative | Résultat dominé par raccourcis ou puissance insuffisante |
| Après S3 | LoRA apporte une information ou une compétence utile dans le budget | Coût disproportionné sans signal et aucun objectif pédagogique restant |
| Après S4 | Le spike de distillation montre faisabilité et coût acceptable | OOM, temps complet hors budget, aucune tendance utile |
| Après S5 | Un candidat mérite calibration et robustesse | Verdict non résolu et aucun budget pour lever l'incertitude |
| Avant service | Un consommateur et un scénario de démonstration existent | Le service ne sert qu'à cocher un mot de l'offre |
| Avant location | Déclencheur scientifique précis et plafond accepté | La location sert seulement à agrandir le modèle sans question nouvelle |

## 11. Réécritures prioritaires proposées

### 11.1 Cap du projet

Formulation recommandée :

> Construire une chaîne reproductible permettant de comparer, sur des comptes rendus cliniques français fictifs et sous budget RTX 5090, une référence non neuronale, un encodeur, une LoRA de LLM et une distillation. Le projet mesure leur qualité, leur calibration, leur robustesse et leur coût. Il retient le meilleur compromis admissible sans présumer qu'un LLM ou la distillation gagne. Toute conclusion reste limitée au corpus, à la tâche, au split et au matériel effectivement testés.

### 11.2 Question principale

> À budget de réglage égal et sur la tâche `parhaf_cim10_chapter` définie par contrat, la distillation au niveau des classes améliore-t-elle la LoRA de référence d'une ampleur pratiquement utile, au-delà de la variance entre graines, sans dégrader excessivement coût, calibration et robustesse ?

Les termes « budget égal », « pratiquement utile » et « excessivement » doivent recevoir des valeurs décidées dans `PROTOCOLE.md` avant P1.

### 11.3 Succès global

Le projet est réussi si :

1. au moins un fine-tuning LLM complet est reproductible et enregistré ;
2. la comparaison principale produit un verdict honnête, y compris négatif ou non résolu ;
3. les fuites patient, auteur et quasi-doublon sont testées ;
4. le meilleur candidat est comparé sur qualité, calibration et coût ;
5. une seconde tâche compatible traverse le noyau sans modification de celui-ci ;
6. chaque affirmation externe est reliée à une source ou un run_id ;
7. le rapport distingue données fictives, scénario suggéré et vérité clinique.

Le succès ne dépend pas du fait que la distillation gagne.

### 11.4 Non-objectifs

- Validation clinique.
- Généralisation à des comptes rendus réels.
- Décision diagnostique ou thérapeutique.
- Reproduction exacte de toute la solution Kaggle.
- État de l'art.
- Déploiement hospitalier réel.
- Couverture exhaustive de tous les outils cités dans l'offre.
- Entraînement 70B ou location sans déclencheur accepté.

### 11.5 Définition opérationnelle de « local »

À choisir explicitement :

- **Local-données** : aucun texte ni artefact dérivé ne quitte la machine ; téléchargements de poids et documentation autorisés.
- **Local-calcul** : entraînement et inférence uniquement sur la RTX 5090.
- **Local-démonstration** : service et interface accessibles uniquement sur la machine ou le réseau privé.

Une location de GPU rompt `local-calcul` mais peut rester compatible avec `local-données` si les conditions du jeu et la fiche de location l'autorisent.

## 12. Optimisations stratégiques à plus fort rendement

### Priorité critique avant P0

1. Archiver l'offre CHUGA et ses passages exacts.
2. Faire décider par Cyril date, périmètre, dépôt, démo et modèles conditionnés.
3. Rendre l'objectif neutre vis-à-vis du gagnant.
4. Définir le budget de la première boucle et la métrique primaire.
5. Épingler la révision PARHAF et corriger les chiffres.
6. Séparer reproduction LMSYS et adaptation clinique.
7. Réordonner le MVP autour d'un fil vertical.

### Priorité haute avant le premier run comparatif

1. Définir le split confirmatoire et l'unité de bootstrap.
2. Définir la famille Holm et la taille d'effet minimale utile.
3. Écrire les commandes canoniques et les versions de schémas.
4. Définir les critères go/no-go après baseline, LoRA et spike de distillation.
5. Spécifier la preuve nécessaire pour chaque note de scorecard.

### Priorité moyenne avant P4-P5

1. Appliquer calibration et abstention au meilleur candidat, pas uniquement au LLM distillé.
2. Justifier chaque intégration par un consommateur et un scénario.
3. Définir la compatibilité conteneur-pilote pour local et location.
4. Mettre la piste générative dans une spécification distincte.
5. Définir ce qu'une revue indépendante signifie réellement.

## 13. Registre de preuves de cet audit

| Observation de l'audit | Preuve | Statut |
|---|---|---|
| `PLAN_PROJET.md` est le brainstorm V1 | En-tête du fichier, ligne 3 | Prouvé |
| La V6 est la référence actuelle | `PLAN_PROJET_V6.md`, ligne 3 ; `AGENTS.md` | Prouvé |
| Le backlog contient 135 tâches et 68 tâches ★ | Exécution locale de `scripts/check_microtasks.py` | Prouvé |
| La fermeture formelle du chemin court est valide | Sortie « OK : aucune erreur » du script | Prouvé |
| Le chemin court est stratégiquement trop large | Inspection des tâches ★ et nombre de runs requis | Jugement argumenté, à arbitrer |
| Le chiffre PARHAF 4 254 n'est pas le chiffre de la fiche actuelle | Fiche officielle actuelle : 4 259 patients, 6 190 documents | Prouvé pour la fiche consultée ; révision à épingler |
| PARTAGES annonce sept modèles et huit cas d'usage | Page officielle PARTAGES | Prouvé |
| Le calendrier résumé est octobre 2026 à juin 2027 | Fiche officielle du cas d'usage résumé | Prouvé |
| TRL impose un vocabulaire commun au professeur et à l'élève | Documentation officielle `DistillationTrainer` | Prouvé |
| La perte publiée de LMSYS n'est pas seulement CE + un KL | README du dépôt : CE + 2 KL + 2 cosinus, moyenne | Prouvé pour le code publié |
| Qwen3.8-27B et Gemma 4 31B sont documentés comme génératifs multimodaux | Cartes officielles et classes de chargement | Prouvé ; compatibilité classification non prouvée |
| Le dossier n'est pas actuellement un dépôt Git | `git status` et absence locale de `.git` | Prouvé dans l'environnement observé |
| La commande Python courte n'est pas reproductible telle quelle ici | `python` absent du PATH ; problème CP1252 avec ★ | Prouvé dans l'environnement observé |

## 14. Questions réservées à Cyril

L'audit ne les tranche pas :

1. Quelle date de candidature pilote le chemin critique ?
2. Le premier objectif est-il l'apprentissage, une preuve de candidature, ou une étude complète ?
3. Quel budget GPU maximal autoriser avant le premier verdict ?
4. Le MVP doit-il s'arrêter après une LoRA reproductible ou inclure obligatoirement une distillation complète ?
5. Le dépôt doit-il être créé maintenant, et sur quelle plateforme ?
6. La démo doit-elle rester locale ?
7. Les modèles conditionnés sont-ils autorisés ?
8. Quel seuil pratique justifie de poursuivre une méthode plus coûteuse ?
9. La revue clinique externe est-elle hors périmètre de façon définitive ?

## 15. Conclusion

Le plan possède une excellente culture de preuve, mais il gagnera davantage en intelligence stratégique par soustraction que par ajout. La priorité n'est plus de trouver de nouveaux outils ou de nouvelles catégories de qualité. Elle est de raccourcir la boucle entre une question précise, un run minimal, une preuve, un verdict et une décision d'arrêt.

La meilleure version du projet n'est pas celle qui entraîne le plus de modèles. C'est celle qui peut expliquer, avec des artefacts reproductibles, pourquoi une méthode a été essayée, quel effet elle a eu, combien elle a coûté, dans quelles limites le résultat tient et pourquoi l'étape suivante a été poursuivie ou abandonnée.
