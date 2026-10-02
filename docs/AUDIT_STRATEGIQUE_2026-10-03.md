# Audit et recommandations stratégiques : efficience des actions, constats et méthodes

**Date** : 03/10/2026. **Auteur** : Claude (Sonnet 5.5), à la demande de Cyril. **Statut** : document de travail, non figé, **à ne pas diffuser avant `claim-gate`**. **Données** : aucune donnée de patient ; seuls des effectifs agrégés et des mesures du registre (`results/runs/`) sont cités. **Aucune sortie hors machine n'a eu lieu** : le cahier de livrables pour GLM (couche 5) est un texte que Cyril décide d'envoyer ou non (règle du projet : revue croisée externe seulement avec son accord à chaque fois).

**Méthode en couches.** Chaque couche enrichit la précédente sans la réécrire, pour que l'on voie ce que chaque passe apporte.
1. **Audit initial** : constats et recommandations tirés de ce qui s'est passé.
2. **Augmentation par les données** : chaque constat est rattaché à une mesure, un `run_id` ou une source de session ; ce qui reste sans chiffre est dit.
3. **Brainstorming** : idées nouvelles, évaluées par une matrice gain, coût, risque, réversibilité.
4. **Contextualisation statistique** : simulations enregistrées (`20261002-221006-power-sketch-ic-width-v2`, `20261002-225747-power-curves-audit`), lecture des intervalles, des probabilités de verdict et des tailles d'échantillon.
5. **Cahier de livrables pour GLM**, affiné par les couches 2 à 4.

---

## 0. Lecture rapide

1. **Le matériel n'est pas le goulot, la statistique l'est.** Sur 633 patients de test, l'intervalle d'une différence de macro-F1 entre deux modèles de même niveau mesure de 7,4 à 14,3 points de large dans la simulation, pour 4 points admis par la règle de puissance. Il faudrait de 2 200 à 8 000 patients pour atteindre 4 points ; le jeu de travail en compte 4 219.
2. **Environ 78 % des heures de GPU du budget dépendent de cette règle** (professeur en cinq plis, réglage des variantes, comparaison confirmatoire, réglage du professeur : 44,9 à 68,0 h sur 57,6 à 86,3 h). Si la règle échoue, ces heures produisent des estimations exploratoires, pas des verdicts.
3. **Une évaluation par validation croisée sur 2 871 à 3 572 patients ramène la largeur à 3,3 à 6,7 points** (5 scénarios sur 8 passent sous 4, 6 sur 8 en comptant 4,0). C'est la piste stratégique la plus rentable : elle exige une nouvelle version du protocole et une décision de Cyril.
4. **L'effort de relecture ne converge pas aussi vite qu'il coûte.** Trois relectures adversariales (16, 18 et 20 constats ; 9 bloquants au total) ont consommé 438 746 jetons et 22,5 minutes de sous-agent. Quatre bloquants sur neuf sont des contradictions internes, quatre des règles inexécutables, un une erreur d'arithmétique (classement de l'auteur, subjectif). Cela pointe un défaut de méthode (texte dupliqué, règles sans propriétaire), pas un manque de relecteurs.
5. **Les actions les plus rentables de la période** ont été celles qui ont produit un fait vérifiable à bas coût : les spikes sur vrais poids (bug du gradient checkpointing), la CI (20 erreurs d'exécutable), les simulations de puissance (avant de dépenser 90 h).
6. **Recommandation en une phrase** : cesser d'écrire des règles avant d'avoir une première macro-F1, geler un noyau minimal, mesurer la largeur réelle à RM-17, et décider du design confirmatoire sur ce chiffre.

---

## Couche 1. Audit initial

### 1.1 Ce qui a été fait (période du 02 au 03/10/2026)

- **R4 close** : compatibilité de classification de cinq modèles, banc des deux plus gros professeurs en QLoRA 4 bits, budget de calcul, présélection de l'élève (ADR-009).
- **Infrastructure** : dépôt GitHub privé, CI (GitHub Actions), audit hebdomadaire des dépendances, release sur tag (ADR-008).
- **Wiki** : sources A1, A4, A5, A6, A7, A8 ingérées (A2 et A3 bloquées : pages Kaggle illisibles hors navigateur).
- **Protocole (P0-46)** : sections 5 et 6 écrites, ADR-007 acceptée, ADR-009 ratifiée, ADR-010 (écarts au plan), contrôle des instantanés gelés (`check_frozen`). **Non gelé** : la troisième relecture a rendu 2 bloquants non encore traités.
- **Décisions de Cyril obtenues** : δ = 2,0, K = 5, B = 90 h, N = 4, couverture 90 %, 2 époques, risques acceptés.

### 1.2 Constats

**A. Ce qui fonctionne (à conserver)**
- Mesurer avant d'affirmer : les spikes sur vrais poids ont donné des chiffres de mémoire et de débit, et ont révélé un défaut de code (gradient checkpointing sauté en silence en voie B).
- Le registre en ajout seul et la règle « un chiffre sans `run_id` n'existe pas » : ils ont permis de retrouver et corriger mon erreur sur les effectifs de test (esquisse v1 à effectifs proportionnels, remplacée par la v2).
- La CI reproduisant un clone neuf : elle a trouvé en un run ce que la machine locale ne voyait pas.
- Les relectures adversariales en contexte neuf : elles ont trouvé de vrais défauts (poste de budget de 25 à 45 h oublié, règle de puissance inapplicable).

**B. Ce qui coûte du temps sans produire de fait**
- Le crochet pré-commit : environ une minute par commit sur `/mnt/d` (horodatages gitleaks de quatre commits consécutifs : 6:46, 6:47, 6:48, 6:49 PM). Cause non mesurée : à isoler avant toute optimisation.
- Les boucles de relecture sur un texte en cours d'écriture (voir 1.3).
- Les attentes sur des sources non récupérables (A2, A3) : question à Cyril restée sans réponse.

**C. Défauts de méthode relevés**
1. **Duplication des nombres entre documents** : δ, K, B, N, époques, niveaux, effectifs apparaissent dans le protocole, trois ADR, le backlog, la feuille de route, le plan. Chaque modification crée une dérive à rattraper.
2. **Règles sans propriétaire exécutable** : une règle écrite sans micro-tâche, sans code et sans test n'est pas exécutée (réglage du taux des variantes, classement des échecs « par le code du registre » qui n'existe pas, temps A de l'ouverture du test non réalisable avec `sealed.py`).
3. **Latitude après coup** : plusieurs paramètres (seuil 4,0, R, niveau, grille, époques) pouvaient encore changer après un résultat sans déclencher d'ADR.
4. **Estimation de budget incomplète** : le réglage égal des variantes (règle d'égalité de ADR-004) n'était pas compté.
5. **Lecture de la scène statistique tardive** : le problème de puissance est apparu après l'écriture de la règle de verdict, non avant.
6. **Une lecture de partition scellée hors porte** : un relecteur a compté les étiquettes du test (agrégats, sans usage pour un choix). Aucune conséquence, mais le cas montre que la porte d'accès ne protège que le code, pas les agents.

### 1.3 Recommandations v1

| # | Recommandation | Raison |
|---|---|---|
| R1 | **Source unique des valeurs** : `configs/protocol.yaml` (δ, K, N, B, époques, graines, niveaux, R, seuil de puissance), documents qui y renvoient, test de cohérence | Défaut C1 |
| R2 | **Gel en deux niveaux** : noyau minimal gelé (métrique, δ, K, N, estimand, règle de verdict, ouverture unique, partitions) ; détails opérationnels dans des fiches de recette préenregistrées, chacune hachée | Défauts C2 et C3 : la surface relue diminue |
| R3 | **Une règle = une tâche + un test** avant le gel | Défaut C2 |
| R4 | **Limiter les relectures** : au plus deux tours, ensuite gel avec résiduel listé ; relecture du seul diff | Cadence des 3 tours |
| R5 | **Mesurer la largeur réelle d'intervalle à RM-17** avant de fixer le design confirmatoire | Défaut C5, couche 4 |
| R6 | **Étudier un design confirmatoire sur prédictions hors pli** (couche 4) | Gain de puissance |
| R7 | **Mesurer le crochet pré-commit** (`time` par étape) avant de l'alléger | Constat B |
| R8 | **Interdire aux sous-agents toute lecture d'étiquette de test** dans leur consigne (déjà fait pour les relectures 2 et 3) et le consigner comme règle | Constat C6 |

---

## Couche 2. Augmentation par les données mesurées

### 2.1 Consommation et budget

| Mesure | Valeur | Source |
|---|---|---|
| GPU consommé par les runs finaux de spike | environ 0,9 h (somme des chargements et des pas des cinq spikes P0-06 et P0-08) | `knowledge/raw/spike-p0-06-*.json` |
| GPU perdu au run non terminé de Gemma-4-E4B | environ 0,43 h (26 minutes de saturation 32 Go) | journal du 02/10, incident de méthode |
| Part de B = 90 h déjà consommée | environ 1,5 % | calcul ci-dessus |
| Budget v2 optimiste | 57,6 à 86,3 h | `20261002-230546-budget-v3-premier-cycle` |
| Budget v3 avec professeur pessimiste (réglage P2-01 compris, corrigé après la troisième relecture) | 67,5 à 99,8 h ; par combinaison élève et professeur : 57,6 à 99,8 h (E4B + Gemma optimiste, 9B + Qwen pessimiste) ; seul l'E4B tient avec marge sous 90 h | `20261002-230546-budget-v3-premier-cycle` |
| Heures dépendant de la règle de puissance (professeur 5 plis 15,8 à 17,8, réglage professeur 3,2 à 3,6, réglage variantes 8,4 à 15,1, confirmatoire 17,5 à 31,5) | 44,9 à 68,0 h, soit environ 78 % du total optimiste | budget v2 |
| Postes non comptés | P2-07, RM-19, P1-07, relances, calibration, chargements | `PROTOCOLE.md` section 5 |

### 2.2 Coût des relectures et croissance du texte

| Relecture | Constats | Bloquants | Jetons du sous-agent | Durée |
|---|---|---|---|---|
| 1 (03/10) | 16 | 4 | 130 850 | 354 s |
| 2 | 18 | 3 | 144 688 | 472 s |
| 3 | 20 | 2 | 163 208 | 525 s |
| **Total** | **54** | **9** | **438 746** | **1 351 s (22,5 min)** |

- Taille du protocole : 73 lignes en début de période, 190 lignes et 5 492 mots aujourd'hui.
- **Nature des 9 bloquants (mon classement, subjectif)** : 4 contradictions internes (arrêt anticipé contre pannes ; sortie anticipée contre moyenne ; 6.4 contre 6.8 ; mentions de brouillon dans le fichier à hacher), 4 règles inexécutables (règle de puissance deux fois, extension de grille, mécanique du gel), 1 arithmétique (budget).
- **Lecture** : le nombre de constats par tour ne baisse pas (16, 18, 20), parce que chaque correction ajoute du texte nouveau ; les bloquants, eux, baissent (4, 3, 2). Ce n'est pas un indicateur de convergence tant que le texte grossit.

### 2.3 Dépôt et CI

- 27 commits au dépôt, 50 tâches cochées sur 165 (115 ouvertes).
- CI : premier run vert en 169 s (deux jobs). Les deux jobs étaient verts sur les derniers pushs.
- Aucune valeur de macro-F1 de modèle n'existe : toutes les décisions de design reposent sur des mesures de mémoire, de débit et sur des simulations.

### 2.4 Effectifs (agrégés, `results/measures/splits_summary.json`)

- Jeu de travail : 4 219 patients. Test scellé : 633 (629 évalués plus 4 `AUTRE`). Développement : 3 586 (plis de 717 à 718).
- Chapitres les plus petits du test : XXII 4, XII 6, XXI 7, IV 9, V 9. **Cinq chapitres sur 17 sont sous 10 patients de test et pèsent chacun autant que le chapitre II (174 patients) dans la macro-F1.**

### 2.5 Ce qui reste sans chiffre
- Le temps réel passé en crochet par étape ; la cause de la minute par commit.
- La corrélation réelle des erreurs entre deux graines d'une même LoRA (elle décide du résultat de la règle de puissance).
- Le débit à 4 096 tokens des élèves ; le surcoût de remplissage.

---

## Couche 3. Brainstorming

Matrice d'évaluation (gain d'efficience ou de puissance ; coût de mise en œuvre ; risque ; réversibilité). Notation : élevé / moyen / faible.

| # | Idée | Gain | Coût | Risque | Réversible | Verdict |
|---|---|---|---|---|---|---|
| I1 | **Fichier unique de valeurs** `configs/protocol.yaml` plus test de cohérence avec les documents | élevé (supprime la dérive) | faible | faible | oui | **faire** |
| I2 | **Gel en deux niveaux** : noyau minimal haché, fiches de recette hachées une à une | élevé | moyen | faible | oui | **faire** |
| I3 | **Design confirmatoire sur prédictions hors pli des plis 1 à 4** (2 871 patients) avec réglage seulement sur le pli 0, test scellé réservé au candidat final | **très élevé** (largeur divisée par environ 2) | moyen (nouvelle version du protocole, nouvelle ADR) | moyen : biais de sélection, fuite du professeur en distillation | partiel | **décider à RM-17 sur la largeur mesurée** |
| I4 | **Métrique de verdict moins sensible aux petits chapitres** : exactitude, log loss ou macro-F1 restreinte aux chapitres d'au moins 16 patients de test | moyen (macro-F1 restreinte : 6,3 à 11,8 contre 7,4 à 14,3 à 629) | faible | élevé : change la métrique primaire (ADR requise) | non après le premier run | à **rapporter en secondaire**, pas à substituer |
| I5 | **Fusionner les chapitres rares** dans `AUTRE` | élevé | élevé : touche les classes et les partitions figées | élevé | non | écarté au premier cycle |
| I6 | **Re-tirer un test plus gros** (le test n'a jamais été ouvert) | faible (extrapolée à 1 200 patients, la largeur reste de 5,4 à 10,4 dans les quatre scénarios du test) | élevé | moyen | non | écarté |
| I7 | **Analyse bayésienne complémentaire** (probabilité postérieure que Δ dépasse δ), exploratoire | moyen (lisibilité pour un lecteur non statisticien) | faible | faible | oui | **faire, en EXPLORE** |
| I8 | **Redistribuer les heures de graines vers l'évaluation de plus de patients** : la variance vient surtout des patients, pas des graines | moyen | faible | faible | oui | à vérifier en RM-17 |
| I9 | **Alléger le crochet pré-commit** (gitleaks sur les fichiers indexés seulement, cache mypy, contrôles sur fichiers modifiés) après mesure | moyen | faible | faible | oui | **faire après mesure** |
| I10 | **Relectures limitées** : deux tours, diff seul, gabarit de classes de défauts (contradiction, règle sans tâche, latitude, arithmétique) | élevé | faible | faible | oui | **faire** |
| I11 | **Tranche verticale** : arrêter d'écrire des règles, produire la première macro-F1 de référence (P1-03, P1-04, P1-06) puis décider | **très élevé** | faible | faible | oui | **priorité** |
| I12 | **Réserver les sous-agents aux portes** (protocole, gel, scorecards) | moyen | faible | faible | oui | faire |
| I13 | **Scorecard G-P0 avec preuves immuables** (runs, instantané) | moyen | moyen | faible | oui | après le gel |

---

## Couche 4. Contextualisation statistique avancée

**Source** : run `20261002-225747-power-curves-audit` (simulation, `scripts/spikes/power_curves.py`, graine 3, 10 jeux par scénario, 200 répliques). **Hypothèses** : deux modèles de même niveau (écart réel nul), difficulté latente partagée (corrélation 0,5 ou 0,8), erreurs vers une classe tirée selon la prévalence, bootstrap stratifié par classe **sur les patients seuls** (la variance entre graines s'y ajoute). **Limites** : corrélations inventées ; effectifs des plis 1 à 4 proportionnels à ceux du développement (non mesurés pli par pli) ; ce sont des **ordres de grandeur**, pas des mesures de modèles.

### 4.1 Largeur de l'intervalle à 98,33 % de la différence (points)

| Évaluation | n | Exactitude visée, corrélation | Macro-F1, 17 chapitres | Exactitude | Macro-F1, 12 grands chapitres |
|---|---|---|---|---|---|
| Test scellé | 629 | 0,6 ; 0,5 | 14,3 | 9,9 | 11,8 |
| | | 0,6 ; 0,8 | 8,2 | 5,2 | 6,9 |
| | | 0,8 ; 0,5 | 8,4 | 6,2 | 7,4 |
| | | 0,8 ; 0,8 | 7,4 | 5,3 | 6,3 |
| Plis 1 à 4 | 2 871 | 0,6 ; 0,5 | 6,7 | 4,7 | 5,3 |
| | | 0,6 ; 0,8 | 3,8 | 2,3 | 3,2 |
| | | 0,8 ; 0,5 | 4,0 | 3,0 | 3,4 |
| | | 0,8 ; 0,8 | 3,9 | 2,7 | 3,0 |
| Développement entier | 3 572 | 0,6 ; 0,5 | 6,1 | 4,3 | 5,2 |
| | | 0,6 ; 0,8 | 3,8 | 2,2 | 3,0 |
| | | 0,8 ; 0,5 | 3,7 | 2,7 | 3,1 |
| | | 0,8 ; 0,8 | 3,3 | 2,2 | 2,7 |

**Lectures**
1. **La largeur varie à peu près en 1 sur racine de n** : de 629 à 2 871 patients, elle est divisée par 1,9 à 2,2 selon le scénario (théorie : 2,1).
2. **Le seuil de 4 points n'est atteint sur le test que si les erreurs sont presque identiques** et jamais dans les quatre scénarios simulés. Il faudrait **2 150 à 8 040 patients** (extrapolation en 1 sur racine de n depuis 7,4 à 14,3 points à 629) ; le jeu entier en compte 4 219.
3. **La corrélation des erreurs pèse autant que la taille** : à 629 patients, passer de 0,5 à 0,8 de corrélation réduit la largeur de 14,3 à 8,2. Hypothèse non vérifiée : deux graines d'une même recette seraient plus corrélées que deux recettes différentes ; **la règle de puissance de `PROTOCOLE.md` 6.3 mesure donc le cas le plus favorable** (borne vraisemblablement basse de la largeur d'une vraie comparaison, sans que le sens du biais soit démontré).
4. **La macro-F1 est la métrique la plus bruitée** : à 629 patients, l'exactitude est 1,4 à 1,6 fois plus étroite ; restreindre la macro-F1 aux 12 chapitres d'au moins 16 patients gagne 1,0 à 2,5 points. Cela confirme que **les cinq chapitres de 4 à 9 patients dominent l'incertitude**.
5. **Un design par prédictions hors pli sur 2 871 à 3 572 patients atteint 3,3 à 4,0 points dans six scénarios sur huit** (cinq strictement sous 4 ; ceux de forte corrélation ou d'exactitude élevée), mais pas dans le scénario le plus défavorable (6,1 à 6,7).

### 4.2 Probabilité de verdict avec la règle d'ADR-007 (δ = 2,0)

Gain confirmé si le bas de l'intervalle dépasse δ, absence de gain utile si le haut est sous δ, non résolu sinon. Approximation normale (z = 2,394), sigma = largeur sur 2z.

| Largeur (points) | Vrai gain 0 : absence de gain utile | Vrai gain 3 : confirmé | Vrai gain 5 : confirmé | Vrai gain 5 : non résolu |
|---|---|---|---|---|
| 4 | 50 % | 11,6 % | 88,4 % | 11,6 % |
| 6 | 21,2 % | 5,5 % | 50,0 % | 50,0 % |
| 8 | 11,6 % | 3,6 % | 27,5 % | 72,5 % |
| 10 | 7,5 % | 2,8 % | 16,9 % | 83,1 % |

**Lectures**
1. **Même à largeur 4, un vrai gain de 3 points (utile, car supérieur à δ) n'est confirmé que dans 11,6 % des cas.** Un vrai gain égal à δ n'est confirmé que dans moins de 1 % des cas (correction relevée par la troisième relecture : le texte du protocole dit « jamais », ce qui est inexact).
2. **Pour un vrai gain de 5 points, la probabilité de confirmation est de 88 % à largeur 4 mais de 17 % à largeur 10.** La largeur réelle est donc le paramètre qui décide du projet.
3. **La règle d'absence de gain est un test de non-infériorité déguisé** : à largeur 4 et vrai gain nul, elle ne répond « absence de gain utile » que 50 % du temps. Un verdict négatif confirmé est plus difficile à obtenir qu'il n'y paraît, ce qui pèse sur l'objectif de neutralité du projet (« réussir même si TF-IDF bat le LLM ») : c'est une interprétation de l'auteur, pas un résultat de simulation.
4. **Conséquence sur le texte du livrable** : avec le design actuel, le rapport attendu est « non résolu » dans la grande majorité des cas ; le dire est honnête, mais il ne faut pas laisser croire à un verdict confirmatoire probable.

### 4.3 Ce que la mesure de RM-17 doit trancher

Arbre de décision proposé (à pré-enregistrer comme texte d'ADR, pas à geler dans le protocole tant que Cyril n'a pas choisi) :

| Largeur mesurée sur P1-19 ramenée à la taille d'évaluation | Évaluation sur le test scellé (633) | Évaluation hors pli (2 871) | Décision |
|---|---|---|---|
| Au plus 4 sur 633 | **réussie** | (réussie a fortiori) | H1 à H3 restent confirmatoires sur le test |
| Plus de 4 sur 633, au plus 4 sur 2 871 | échoue | **réussit** | proposer à Cyril le design I3 (nouvelle version du protocole), sinon EXPLORE |
| Plus de 4 sur 2 871 | échoue | échoue | H1 à H3 en EXPLORE, test réservé au candidat final |

### 4.4 Risques propres au design hors pli (I3)

1. **Fuite du professeur en distillation** : la cible d'un patient du pli j vient d'un professeur qui a vu les étiquettes du pli évalué k. Pour H1 et H3, les évaluations hors pli sont optimistes. Un professeur imbriqué (cinq professeurs par pli évalué) coûte environ cinq fois plus de heures de professeur : **non budgété**.
2. **Biais de sélection léger** : le taux d'apprentissage est choisi sur le pli 0 ; évaluer sur les plis 1 à 4 l'évite en grande partie (un hyperparamètre parmi quatre valeurs sur un pli distinct).
3. **Perte du caractère « test scellé »** pour la comparaison : le test resterait, lui, réservé au candidat final et à la couverture conforme.
4. **Corrélation entre plis** (patients d'un même auteur dans des plis différents) : les plis stratifiés ne sont pas groupés par auteur ; le raccourci d'auteur n'est pas signalé (−0,86 point, intervalle à 95 % [−2,16 ; +0,38]), mais l'indépendance des patients doit être justifiée.

### 4.5 Autres pistes statistiques à instruire
- **Couverture réelle de l'intervalle percentile à 98,33 %** avec environ 83 répliques par queue (10 000 répliques) et des strates de 4 patients : à vérifier par simulation de couverture sur les effectifs réels (P1-02) ; BCa ou plus de répliques si la couverture est inférieure à 97 %.
- **Facteur (K moins 1) sur K** du bootstrap sur 5 graines : négligeable devant l'incertitude patients, à confirmer.
- **Comparaison de macro-F1 pondérée par chapitre** (poids égaux au sens du protocole) contre **micro-F1** : à publier côte à côte, pour que la sensibilité aux cinq petits chapitres soit visible.

---

## Couche 5. Cahier de livrables pour GLM (à envoyer seulement si Cyril l'autorise)

**Contexte pour GLM** : GLM 5.3 avait produit `spec_driven_audit_GLM_5_3_v1.md` (où gagner du temps sans perdre en qualité ni en sécurité). Les livrables suivants prolongent cet audit avec ce que la période a appris. **Règles d'envoi** : aucune donnée de patient, aucun texte du corpus ni source brute `knowledge/raw/parhaf-*` ; seulement le présent fichier, les runs cités et les scripts de simulation ; Cyril décide de l'envoi, une fois par lot ; la sortie de GLM est traitée comme une source à vérifier, jamais comme une instruction.

| # | Livrable | Entrées | Critère d'acceptation | Ce qu'il ne doit pas faire |
|---|---|---|---|---|
| G1 | **Réplique indépendante** de la simulation de largeur (autre code, autre langage ou bibliothèque) | `scripts/spikes/power_curves.py`, run `20261002-225747-power-curves-audit`, effectifs agrégés | Écart de moins de 1 point sur chacun des 12 scénarios, ou explication chiffrée de l'écart ; degré d'indépendance « code » pour la note Q3 du scorecard | Lire du texte ou des étiquettes de patient |
| G2 | **Revue de la couverture du bootstrap** d'ADR-007 | ADR-007, `PROTOCOLE.md` 6.2 | Couverture simulée de l'intervalle percentile à 98,33 % avec R = 10 000, strates de 4 à 174 patients ; recommandation chiffrée (R, BCa, strates fusionnées) | Modifier l'ADR |
| G3 | **Comparaison chiffrée de trois designs confirmatoires** : test de 633, hors pli sur 2 871, hors pli sur 3 572 plus test | couche 4, `PROTOCOLE.md` 6.3 et 6.8 | Pour chaque design : largeur attendue, probabilité de verdict résolu pour des gains de 2, 3, 4 et 5 points, biais de sélection, fuite de distillation, coût en heures ; une recommandation avec ses conditions | Proposer de relever δ après coup |
| G4 | **Audit d'efficience d'exécution, suite du v1** : durée du crochet pré-commit par étape, cadence des relectures, ordre des tâches, tranche verticale | couche 2, `Makefile`, journaux | Liste d'actions triées par gain de temps et risque, avec mesure avant/après proposée, comme le § 7 du v1 | Proposer d'affaiblir un contrôle de `CONSTRAINTS.md` |
| G5 | **Modèle de coût avec incertitude** : intervalles sur les débits et les heures, Monte-Carlo sur les hypothèses (époques, surcoût de remplissage, élève choisi) | `scripts/spikes/budget_v2.py`, run `20261002-230546-budget-v3-premier-cycle` | Distribution de la durée totale et probabilité de dépasser B = 90 h par choix d'élève et de professeur | Annoncer une durée en jours ou en semaines avant RM-16 |
| G6 | **Contre-lecture des probabilités de verdict** et du choix de δ | couche 4.2 | Table pour δ de 1,5, 2,0, 3,0 et 4,0, et pour des largeurs de 3 à 10 ; avis motivé sur la règle d'absence de gain | Fixer δ à la place de Cyril |

**Correction du 03/10/2026 (après retour de Cyril).** Les missions G1 à G6 ci-dessous étaient en partie **redondantes** : G1 (réplique de la simulation) refait un calcul déjà fait, G3 (largeurs par design) et G6 (probabilités de verdict) redemandent des tableaux déjà produits aux sections 4.1 et 4.2 ; le cahier renvoyait en outre à des fichiers que GLM ne peut pas ouvrir et ne fixait aucun gabarit de profondeur. **La version à envoyer est `docs/BRIEF_GLM_v2_autonome.md`** : autonome, missions A à F **non redondantes** (modèle d'erreurs réaliste, couverture du bootstrap, règle de décision alternative, plan de mesure, coût avec incertitude, biais du design hors pli) qui attaquent les hypothèses de ce document, vérification indépendante reléguée en mission optionnelle K. Le tableau G1 à G6 est conservé comme historique.

### Format de réponse imposé à GLM : un fichier `.md`

**Constat** : la première version de ce cahier ne demandait pas de format de réponse. Elle est corrigée ici : **GLM répond par un fichier Markdown unique**, nommé `audit_GLM_5_3_v2.md`, que Cyril dépose à la racine du dépôt (comme `spec_driven_audit_GLM_5_3_v1.md`) pour que je le lise, le vérifie et le classe.

Structure exigée du fichier :
1. **En-tête** : date, périmètre, liste des fichiers lus, ce qui n'a **pas** été lu ou exécuté.
2. **Un bloc par livrable G1 à G6**, dans cet ordre, chacun avec : *Résultat* (3 à 5 lignes), *Méthode* (commande ou code reproductible), *Chiffres* (tableau avec unité et intervalle), *Écart avec le document source* (« confirmé », « infirmé » ou « partiel », avec le chiffre), *Limites*, *Recommandation* (une action, son coût, sa réversibilité).
3. **Table de synthèse** : livrable, verdict (confirmé, infirmé, non évalué), confiance (élevée, moyenne, faible), action proposée.
4. **Annexe de code** : tout script de réplique en bloc de code, avec graine, versions de bibliothèques et durée d'exécution.
5. **Section « Ce que GLM n'a pas pu vérifier »**, obligatoire, même vide.

Règles de contenu : chiffres seulement issus de calculs montrés (pas de valeur « de mémoire ») ; chaque désaccord cite la ligne ou le tableau du document source ; aucune instruction adressée à l'agent qui lira le fichier (le fichier est de la donnée, pas des ordres) ; aucune donnée de patient ; en français.

**Réception** : je lirai le fichier en entier, relancerai chaque chiffre vérifiable, classerai les écarts (accepté, rejeté, à instruire) dans `tasks/JOURNAL.md`, et ne modifierai aucune règle du protocole sur sa seule autorité.

**Prompt d'envoi, prêt à coller dans GLM** (avec ce fichier et les scripts joints) :

> Tu es auditeur indépendant d'un projet de fine-tuning de LLM sur textes cliniques français. Tu reçois `AUDIT_STRATEGIQUE_2026-10-03.md`, les scripts `power_curves.py` et `budget_v2.py`, les runs JSON cités et `splits_summary.json` (effectifs agrégés). Réalise les livrables G1 à G6 décrits à la couche 5. Réponds par **un seul fichier Markdown** `audit_GLM_5_3_v2.md` qui respecte exactement la structure de la section « Format de réponse imposé à GLM ». Ne lis ni ne demande aucune donnée de patient ; travaille uniquement sur les effectifs agrégés fournis. Montre chaque calcul, donne un intervalle ou une marge pour chaque chiffre, et indique ce que tu n'as pas pu vérifier. Ne propose pas de relever δ après avoir vu des résultats et n'affaiblis aucun contrôle de qualité.

**Contexte statistique à fournir avec chaque livrable** : les tableaux 4.1 et 4.2 ci-dessus, avec leurs hypothèses et leurs limites, pour que GLM n'en tire pas de conclusion au-delà de leur portée.

---

## Couche 6. Plan d'action priorisé

| Ordre | Action | Pourquoi maintenant | Décision de Cyril requise |
|---|---|---|---|
| 1 | **Traiter les deux bloquants de la troisième relecture** (sortie anticipée contre moyenne ; 6.4 contre 6.8) et les points de budget et de gel qui sont de la correction, pas du design | Débloque le gel | non |
| 2 | **Appliquer I1 et I10** : fichier de valeurs unique, deux tours de relecture au plus | Stoppe la dérive documentaire | non |
| 3 | **Geler un noyau minimal** (I2), renvoyer les détails opérationnels à des fiches préenregistrées | Réduit la surface de relecture et le risque de geler une erreur | oui (périmètre du gel) |
| 4 | **Commencer P1-03, P1-04, P1-06** : premières références chiffrées | Aucune décision n'est fondée sur une macro-F1 aujourd'hui | non |
| 5 | **Enregistrer, dans P1-19, les prédictions par patient avec empreinte** et ajouter une micro-tâche de classement des échecs | Condition de la règle de puissance | non |
| 6 | **RM-17 : mesurer la largeur réelle** et choisir le design confirmatoire (arbre 4.3) | Conditionne 78 % des heures de GPU | oui |
| 7 | **Mesurer le crochet pré-commit** puis l'alléger (I9) | Gain de temps récurrent | non |
| 8 | **Si Cyril l'autorise, envoyer le cahier G1 à G6 à GLM** | Fournit l'indépendance « code » et « méthode » | oui (envoi hors machine) |

### Ce qu'il ne faut pas faire
- Relever δ après avoir vu la largeur (fixe le critère d'après les données).
- Changer la métrique primaire après le premier run (ADR requise).
- Étendre la grille de taux après avoir gelé la référence.
- Lancer 90 h de GPU avant la mesure de RM-17.
- Annoncer qu'un gain est confirmé sans la largeur et le `run_id`.

### Limites de cet audit
- Les simulations ne portent que sur des différences nulles entre deux modèles de même niveau, avec des corrélations inventées.
- Le classement des bloquants et des défauts est le mien, donc subjectif.
- Les durées et les jetons des sous-agents viennent des notifications de session, pas du registre.
- Aucune macro-F1 réelle n'existe encore : toute conclusion sur la distillation serait prématurée.

---

## Annexe : sources et traçabilité

| Élément | Source |
|---|---|
| Largeurs d'intervalle, probabilités, tailles nécessaires | `results/runs/20261002-225747-power-curves-audit.json` |
| Esquisse initiale corrigée | `results/runs/20261002-221006-power-sketch-ic-width-v2.json` (la v1 `…200851…` utilisait des effectifs proportionnels) |
| Budget | `results/runs/20261002-230546-budget-v3-premier-cycle.json`, `20261002-115918-p0-45-budget-hypotheses.json` |
| Effectifs | `results/measures/splits_summary.json` |
| Constats des relectures | `tasks/JOURNAL.md` (sections du 03/10/2026) |
| Règles et ADR | `PROTOCOLE.md`, ADR-004, 007, 009, 010 |
| Audit précédent | `spec_driven_audit_GLM_5_3_v1.md`, `roadmap_unifié.md` |

## Tableau de preuve (`claim-gate`, 03/10/2026)

Ce document est destiné à sortir du dépôt (envoi à GLM sur décision de Cyril). Chaque affirmation chiffrée a été tracée ; les interprétations sont étiquetées comme telles dans le texte. Aucun tiret cadratin (vérifié par `grep -P "\x{2014}"`).

| Affirmation | Preuve | Statut |
|---|---|---|
| Largeurs d'intervalle selon la taille et la métrique (couche 4.1) | run `20261002-225747-power-curves-audit` | prouvé, **simulation** à corrélations inventées, dit dans le texte |
| Probabilités de verdict (4.2) | même run, champ `verdict_probabilities` (calcul normal, pas de modèle de classifieur) | prouvé, approximation dite |
| 2 150 à 8 040 patients pour 4 points | même run, champ `patients_needed_for_width_4_from_629` (extrapolation en 1 sur racine de n) | prouvé, extrapolation dite |
| 78 % des heures de GPU dépendent de la règle de puissance (44,9 à 68,0 h sur 57,6 à 86,3 h) | run `20261002-230546-budget-v3-premier-cycle`, somme de quatre postes recalculée (77,9 % et 78,8 %) | prouvé, **hypothèses de budget** |
| Budget par combinaison élève et professeur (57,6 à 99,8 h) | même run, champ `total_optimistic_pessimistic_by_student_teacher` | prouvé, hypothèses |
| GPU consommé environ 1,5 % de B | somme des chargements et pas des runs `p0-06-*` et `p0-08-*` (environ 0,9 h) plus l'essai non terminé de 26 minutes (journal du 02/10) | prouvé, calcul simple |
| Trois relectures : 16, 18, 20 constats ; 9 bloquants ; 438 746 jetons ; 22,5 minutes | notifications de session et `tasks/JOURNAL.md` ; **absents du registre** | prouvé par la session, source dite |
| Classement 4 contradictions, 4 règles inexécutables, 1 arithmétique | jugement de l'auteur | **reformulé** (« classement de l'auteur, subjectif ») |
| Crochet pré-commit environ 1 minute par commit | horodatages gitleaks de quatre commits consécutifs ; cause non mesurée | prouvé, cause non établie |
| 27 commits, 50 tâches cochées sur 165 | `git log`, `tasks/todo.md` | prouvé |
| « Le design hors pli ramène la largeur à 3,3 à 6,7 points » | run `…225747…`, évaluations à 2 871 et 3 572 patients | prouvé en simulation, **pas en conditions réelles** |
| « Deux graines d'une même recette seraient plus corrélées que deux recettes » | aucune | **reformulé** en hypothèse non vérifiée |
| « La règle d'absence de gain dessert la neutralité du projet » | aucune simulation | **reformulé** en interprétation |
| Aucune macro-F1 de modèle n'existe | `results/runs/` ne contient aucun run de classification de qualité | prouvé |
