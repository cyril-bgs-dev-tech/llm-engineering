# PROTOCOLE : règles communes du projet LLM_finetuning

Statut : **gelé le 03/10/2026** (instantané `experiments/frozen/PROTOCOLE-2026-10-03.md`, empreinte dans `experiments/INDEX.md` et dans la page wiki `protocole-gele-2026-10-03`). Les sections 1 à 3 (P0-32, P0-33, RM-07) ont été figées par empreinte dans `experiments/INDEX.md` **avant** la mesure du raccourci d'auteur (P0-30), la section 4 après la mesure des quasi-doublons ; aucun instantané du fichier n'a été conservé à ces dates (voir 6.10, règle de gel n° 2). Les sections 5 et 6 (budget, métriques, tests, seuils, graines, gel) sont écrites en P0-46. Une section figée ne se modifie plus : un changement devient une nouvelle version qui cite l'ancienne et dit pourquoi.

Les valeurs des sections 1 à 4 ont été posées par Claude le 02/10/2026 en l'absence de réponse de Cyril ; Cyril les a confirmées sans modification le 03/10/2026 (C4, point 6.10).

## 1. Unité d'entrée (P0-32)

- **Unité : le patient.** L'entrée d'un exemple est la concaténation de ses documents, dans l'ordre de l'enregistrement, chacun précédé de sa balise de type (`[CRH]`, `[CRC]`, etc.) et séparés par une ligne vide. Raison : 962 patients ont 3 documents, l'étiquette est portée par le patient et non par le document, et un découpage par document ferait fuir un même patient entre partitions.
- **Longueur maximale : 4 096 tokens** (tokenizer du modèle utilisé). Mesure P0-21 : 99,8 % des patients tiennent sous cette limite pour Qwen3.5 et Qwen3.8, 99,9 % pour Gemma 4 et Mistral Small 3.2 ; aucun patient ne dépasse 8 192.
- **Troncature** au-delà : on garde les 2 048 premiers et les 2 048 derniers tokens, avec le marqueur `[...]` entre les deux. Raison : conclusion et diagnostic se trouvent le plus souvent en fin de document.
- **Aucune modification du texte** au premier cycle : noms fictifs, dates et en-têtes restent. Un retrait de ces éléments est une expérience (ablation), pas un prétraitement implicite.

## 2. Classes et classes rares (P0-33)

- **Étiquette de la tâche principale `parhaf_cim10_chapter`** : chapitre CIM-10 du diagnostic principal du scénario suggéré, dérivé des trois premiers caractères du code par la hiérarchie du ClaML 2019 (`llmft.cim10`). La lettre seule ne suffit pas (D, H).
- **Jeu de travail** : 4 220 patients identiques dans les deux formats de PARHAF (ADR-005), moins les patients dont le code est absent de la nomenclature (un cas mesuré : `N571`, GYNECOLOGIE-00116).
- **Seuil minimal : 20 patients par classe** sur l'ensemble du jeu de travail. Raison : une classe plus petite ne laisse pas 3 exemples dans le test scellé ni 4 par pli.
- **Regroupement** : toute classe sous le seuil est fusionnée dans une classe **`AUTRE`**, nommée et définie « chapitres CIM-10 trop rares dans ce corpus pour être appris ou évalués séparément ». Mesure P0-23 sur le parquet : 4 chapitres concernés (VII œil 2, VIII oreille 2, XVI période périnatale 4, XVII malformations 10), soit 18 patients ; le chapitre XX est absent du corpus.
- Le script de split écrit la liste finale des classes et leurs effectifs ; une classe `AUTRE` ne compte pas dans le calcul de la macro-F1 principale et est rapportée à part (elle n'est pas apprenable : hétérogène).
- Niveaux plus fins (bloc, trois caractères) : **exploratoires seulement** ; 105 blocs sur 165 et 506 catégories sur 554 ont moins de 20 exemples (P0-23).

## 3. Règles de split (RM-07)

- **Unité de split et de bootstrap : le patient.**
- **Test scellé interne : 15 % des patients**, tiré une fois, stratifié par classe, graine 20261002, jamais utilisé pour choisir quoi que ce soit ; ouvert une seule fois (RM-20). Son statut est **confirmatoire** ; ce n'est **pas** le test officiel de PARHAF, qui reste embargoé.
- **Plis de développement : 5 plis stratifiés par classe** sur les 85 % restants, même graine. Statut **exploratoire** (sélection de modèle, réglage).
- **Plis de contrôle groupés par auteur** : 5 plis `StratifiedGroupKFold` avec l'auteur comme groupe, même graine. Statut **exploratoire, contrôle de sensibilité** (devient la métrique principale si le raccourci d'auteur est signalé, voir ci-dessous).
- **Règle si stratification et groupement sont incompatibles** : le groupement par auteur prévaut pour les plis de contrôle ; le test scellé n'est jamais groupé, seulement stratifié, parce qu'il doit estimer la performance sur de nouveaux patients du même corpus.
- **Tolérance de déséquilibre** : pour toute classe d'au moins 50 patients, la part de la classe dans chaque pli stratifié ne s'écarte pas de plus de 30 % (relatif) de sa part globale ; pour les classes plus petites, au moins 2 patients par pli de développement et au moins 3 dans le test.
- **Auteurs présents dans une seule classe** : leur nombre et leur part des patients sont rapportés avant toute modélisation.
- **Seuil du raccourci d'auteur, fixé avant sa mesure.** Un modèle TF-IDF et régression logistique prédisant le chapitre à partir du seul trigramme d'auteur est comparé au même modèle qui n'utilise que la spécialité (information légitimement visible dans le texte). Le raccourci est **signalé** si la macro-F1 au niveau chapitre du modèle « auteur seul » dépasse celle du modèle « spécialité seule » d'au moins **3 points**, avec une borne inférieure d'intervalle de confiance à 95 % (bootstrap par patient, 1 000 tirages) strictement positive, sur les plis stratifiés. Si le raccourci est signalé, les plis groupés par auteur deviennent la métrique principale (ADR).
- Toutes les partitions sont écrites en fichiers d'identifiants dont la **SHA-256** est consignée ; un test échoue si un patient apparaît dans deux partitions ou un auteur dans deux plis de contrôle.

## 4. Contrôles anti-fuite (P0-40), ajoutés le 02/10/2026

Section ajoutée **après** la mesure des quasi-doublons du jeu de travail (sections 1 à 3 inchangées) ; la nouvelle empreinte de ce fichier est consignée dans `experiments/INDEX.md`.

- **Quasi-doublon** : deux patients dont les textes concaténés et normalisés (minuscules, ponctuation retirée, espaces réduits) ont une similarité de Jaccard d'au moins **0,8** sur les 5-grammes de caractères. Seuil choisi **après** avoir vu les effectifs (9 paires à 0,8 sur 4 219 patients, 44 à 0,7, 164 à 0,6, 531 à 0,5) : à 0,8 les textes sont quasiment des copies ; en dessous, la ressemblance vient surtout du gabarit d'un même auteur (95 % des paires à 0,5 ont le même auteur). Le seuil ne se relève jamais pour faire passer un test.
- **Règle de split corrigée** (écart constaté : sur le premier découpage, 8 des 9 paires à 0,8 étaient réparties entre partitions) : les patients quasi-doublons forment un groupe qui reste **dans une seule partition** ; test et plis de développement sont tirés par `StratifiedGroupKFold` sur ces groupes (test = 3 plis de 20, soit environ 15 %). Les plis de contrôle restent groupés par auteur.
- **Contrôles rejoués à chaque changement de données ou de découpage** (`tests/test_leakage.py`, `tests/test_leakage_lib.py`, `tests/test_sealed_access.py`, `tests/test_splits_real.py`) : aucun patient dans deux partitions ; aucune paire à 0,8 entre partitions différentes ; empreinte du fichier de partitions égale à la référence ; porte unique d'accès au test scellé ; contrôle hors pli et sources de synthétique (bibliothèque testée sur cas piégés, branchée aux pipelines de distillation en P2 et P3).

## 5. Budget de calcul par vague (P0-45), ajouté le 02/10/2026, corrigé le 03/10/2026 après relecture

Section ajoutée après les empreintes des sections 1 à 4 ; elle ne modifie aucune règle figée. **Ce sont des hypothèses, pas des durées annoncées** : la règle 6 de la feuille de route interdit d'annoncer une durée avant la mesure pilote RM-16 (une LoRA réelle, 100 pas). Le budget **B** est fixé à **90 h** par Cyril le 02/10/2026 (section 6.3) ; le nombre d'essais **N** est fixé à **4** (section 6.3, ADR-004).

**Entrées mesurées.** Débits du banc P0-08 et de P0-06 (runs `p0-06-*` et `p0-08-*` du registre, page [compatibilite-modeles-p0-06](knowledge/wiki/pages/compatibilite-modeles-p0-06.md)) ; longueurs réelles de P0-21 : environ 1 309 tokens par patient avec le tokenizer Qwen et 1 272 avec celui de Gemma ; 2 868 patients d'entraînement par pli de développement (4 plis sur 5, plis de 717 à 718) et 3 586 pour le développement entier. Calcul enregistré au run `p0-45-budget-hypotheses`.

| Modèle | Débit à 1 024 tokens | Débit à 4 096 tokens | Heures par pli et par époque (optimiste) | Idem (pessimiste) |
|---|---|---|---|---|
| Gemma-4-31B QLoRA (professeur) | 641 tokens/s | 423 tokens/s | 1,58 | 2,40 |
| Qwen3.8-27B QLoRA (professeur) | 585 tokens/s | 360 tokens/s | 1,78 | 2,90 |
| Qwen3.5-9B bf16 (élève) | 1 660 tokens/s | non mesuré | 0,63 | non mesuré |
| Qwen3.5-4B bf16 (élève) | 2 284 tokens/s | non mesuré | 0,46 | non mesuré |
| Gemma-4-E4B bf16 (élève) | 2 922 tokens/s | non mesuré | 0,35 | non mesuré |

**Hypothèses du calcul** : le débit à 1 024 tokens vaut pour les patients réels (borne optimiste) ; le débit à 4 096 tokens, plus bas, donne la borne pessimiste (professeurs seulement) ; aucun surcoût de remplissage ni de chargement des données ; **deux époques pour toutes les recettes** (valeur du protocole au premier cycle, non réglée : P1-16 n'est pas dans le chemin court, C6) ; cinq graines confirmatoires (K = 5, ADR-007).

**Budget du premier cycle, version du 03/10/2026** (run `20261002-230546-budget-v3-premier-cycle`, calculé par `scripts/spikes/budget_v2.py` à partir des débits ci-dessus ; **hypothèses**, deux époques pour toutes les recettes, réglage sur une seule graine pour toutes les familles, référence comprise, élève entre Gemma-4-E4B et Qwen3.5-9B) :

| Poste | Heures de GPU (optimiste, élève E4B à 9B) | Remarque |
|---|---|---|
| Criblage de trois élèves sur un pli, deux taux chacun (P1-11) | 5,8 | ADR-009 |
| Réglage de la référence, 4 taux × 1 graine (P1-13) | 2,8 à 5,0 | P1-13 prévoit trois graines : exécutée à une graine (C2, ADR-010) |
| Variance entre graines, 5 runs de la référence (P1-19) | 3,5 à 6,3 | |
| Rejeu de la référence (P1-26) | 0,7 à 1,3 | |
| Réglage de chaque variante, 3 × 4 taux × 1 graine | 8,4 à 15,1 | règle d'égalité de budget (ADR-004) |
| Réglage du taux du professeur, 1 taux sur un pli (P2-01) | 3,2 à 3,6 | |
| Professeur en cinq plis, deux époques (P2-02) | 15,8 à 17,8 ; pessimiste 24,0 à 29,0 | le plus gros poste unique |
| Comparaison confirmatoire, 4 recettes × 5 graines sur le développement entier (P3-07) | 17,5 à 31,5 | entraînement seulement : **l'évaluation est celle de RM-20** |
| **Total optimiste** | **57,6 à 86,3** | |
| **Total avec professeur pessimiste** (réglage P2-01 compris) | **67,5 à 99,8** | le débit pessimiste n'existe que pour les professeurs : le haut de la plage est encore optimiste côté élève |

**Lecture par combinaison** (optimiste ; pessimiste), heures de GPU :

| Élève | Professeur Gemma-4-31B | Professeur Qwen3.8-27B |
|---|---|---|
| Gemma-4-E4B | 57,6 ; 67,5 | 60,0 ; 73,5 |
| Qwen3.5-4B | 68,0 ; 77,8 | 70,4 ; 83,8 |
| Qwen3.5-9B | 83,9 ; 93,8 | 86,3 ; 99,8 |

B = 90 h tient **avec marge** seulement avec l'E4B ; avec le 4B et le professeur Qwen, il reste environ 6 h pour tous les postes non comptés, ce qui n'est pas « tenir » en pratique ; **avec le Qwen3.5-9B, B est dépassé dans l'hypothèse pessimiste même avec le professeur le moins cher** (93,8 h). L'élève n'est choisi qu'en P1-12 : le budget se lit comme **une plage**, et l'alerte à 80 % de B (72 h) se déclenche déjà avec l'E4B et le professeur Qwen en pessimiste. La décision de Cyril (C7, 6.10) est le repli ci-dessous.

**Non compté, donc sans aucune marge** : le pré-entraînement sur tâche voisine (P2-07, nécessaire à H2 et H3), le spike de distillation (RM-19), l'encodeur à 4 taux (P1-07), les relances après panne (6.4), l'inférence hors pli, la calibration et la prédiction conforme, les chargements de modèle (5 à 7 minutes par professeur), les vagues V2 à V5. Le plus gros poste est le professeur en cinq plis, puis la comparaison confirmatoire, proportionnelle à K ; réduire K ou le nombre de recettes est un choix à faire **avant** le gel, pas après un résultat.

**Arrêt anticipé (règle adoptée avec B = 90 h).** Pour les runs de **criblage, de réglage et de professeur** : un run est interrompu et enregistré `aborted` avec sa raison si, après 10 % des pas, sa durée projetée dépasse de 50 % celle de sa fiche préenregistrée (cette durée ne peut venir que des hypothèses de cette section : RM-16 vient après P1-12). Pour **tous** les runs, une perte non finie interrompt le run et l'enregistre `failed` (6.4). Il n'y a **pas de plafond par vague** : le plafond est B ; à 80 % de B consommé (somme des runs du registre), Cyril est prévenu avant toute nouvelle dépense. Les runs confirmatoires ne sont jamais interrompus pour leur durée.

**Règle de repli (ordre à respecter ; les époques sont fixées à 2 pour toutes les recettes au premier cycle, C6, donc il n'y a plus de repli sur les époques).** Si B ne couvre pas le professeur en cinq plis : (1) choisir le candidat suivant de P1-12 dont le coût estimé tient dans B, en le disant dans le rapport ; (2) choisir un professeur plus petit (Qwen3.5-9B contre un élève de 4B) en le disant ; (3) seulement ensuite, déclencheur de location de la section 5.2 du plan, avec fiche préenregistrée et plafond validé par Cyril, **sous réserve de la définition de « local »** (ADR-004, encore provisoire). Aucun repli ne change la métrique, les plis ni le test scellé.

## 6. Métriques, tests, seuils, graines, étiquettes et gel (P0-46), version du 03/10/2026

**Gelée le 03/10/2026.** Écrite après trois relectures adversariales en contexte neuf du 03/10/2026 (54 constats, classés dans `tasks/JOURNAL.md`). Elle reprend ADR-004 et ADR-007 (acceptée le 03/10/2026) et les valeurs de Cyril : δ = 2,0, K = 5, B = 90 h (02/10), N = 4 et niveau conforme 90 % (03/10). **Huit confirmations de Cyril (C1 à C8, point 6.10) ont été données le 03/10/2026.** 

### 6.1 Métriques

- **Primaire : macro-F1 au niveau chapitre CIM-10** sur les 17 chapitres évalués. Le modèle a **18 sorties** (17 chapitres plus `AUTRE`). Un patient d'un chapitre évalué prédit `AUTRE` est un faux négatif de son chapitre ; `AUTRE` **n'entre pas dans la moyenne** : l'appelant passe à `llmft.metrics.macro_f1` la liste `labels` des 17 chapitres. Une classe sans exemple ni prédiction compte 0 (convention de `metrics.py`).
- **Secondaires** : exactitude, log loss et ECE à 10 tranches de confiance égales, calculés sur les 18 sorties (`AUTRE` comptée comme une classe ordinaire, comme le contrat `task_specs/parhaf_cim10_chapter.yaml`) ; coût (heures de GPU, pic de VRAM, latence par patient). `AUTRE` est de plus rapportée à part (précision, rappel, effectif). Spearman (P1-01) ne s'applique pas à des classes sans ordre : non calculé.
- **Unité** : les écarts de macro-F1 s'expriment en **points** (écart sur l'échelle 0 à 1, multiplié par 100). δ = 2,0 points = 0,020 dans le code.
- **Effectifs réels du test scellé** (`results/measures/splits_summary.json`, champ `test_class_counts`, calculé par `scripts/make_splits.py`) : 633 patients, dont 4 `AUTRE` ; les chapitres les plus petits comptent XXII 4, XII 6, XXI 7, IV 9 et V 9 patients. **Cinq des 17 chapitres sont sous le seuil « effectif très faible » (moins de 10)** et pèsent chacun autant que le chapitre II (174 patients) dans la macro-F1 ; tout tableau les marque.
- Par classe : F1, précision et rappel de chaque chapitre sont toujours publiés avec leur effectif de test. Aucune autre implémentation que `src/llmft/metrics.py` ne produit un chiffre publié.

### 6.2 Tests statistiques et verdict

- **Estimand, rééchantillonnage hiérarchique, famille confirmatoire de trois comparaisons, verdict en trois valeurs** : ADR-007 (points 1 à 4) fait foi. Ce protocole en précise les paramètres :
  - intervalle **percentile** ; R = 10 000 répliques ; générateur `numpy.random.default_rng` (PCG64), graine 20261002 (même valeur que le découpage, sans conséquence statistique) ;
  - **niveau 98,33 %** (Bonferroni, m = 3) pour la famille ; **95 % non ajusté** pour tout intervalle EXPLORE ; les queues de 0,83 % reposent sur environ 83 répliques, ce qui est dit dans le rapport ;
  - dans le tirage stratifié par classe, `AUTRE` est une **strate à part** (4 patients) : elle est tirée mais n'entre pas dans la macro-F1 ;
  - la correction de **Holm** est **rapportée à titre informatif**, jamais décisionnelle : le verdict utilise l'intervalle de Bonferroni ;
  - la variabilité du **professeur** et du **pré-entraînement** n'est **pas** dans l'intervalle (seules les graines de l'élève y sont) : l'estimand est « la recette avec **ce** professeur et **ce** pré-entraînement ».
- **Contrôles complémentaires, non décisionnels** : McNemar sur l'exactitude, permutation appariée sur la macro-F1, Wilcoxon sur les scores par pli. Un désaccord avec le verdict est signalé, il ne le change pas.
- **« Famille de méthodes »** : référence, distillation, pré-entraînement sur tâche voisine, les deux. La famille confirmatoire est H1 (distillation), H2 (tâche voisine), H3 (les deux), chacune contre la référence.
- **Tout le reste est EXPLORE**, y compris les comparaisons avec TF-IDF et les encodeurs (C5, 03/10/2026) : intervalle à 95 % non ajusté, aucun verdict. **Seule l'ouverture du test scellé (RM-20) peut rendre un verdict, uniquement pour H1 à H3 et uniquement si la règle de puissance de 6.3 a réussi** ; P2-08 et P3-07 entraînent sans évaluer (6.8).

### 6.3 Seuils de décision

| Paramètre | Valeur | Statut |
|---|---|---|
| δ, seuil « pratiquement utile » | **2,0 points** de macro-F1 (0,020) | fixé par Cyril le 02/10/2026 |
| K, graines d'entraînement par recette confirmatoire | **5** | fixé par Cyril le 02/10/2026 |
| B, heures de GPU du premier cycle | **90 h** | fixé par Cyril le 02/10/2026 ; la section 5 montre qu'il ne tient pas avec l'élève le plus gros dans l'hypothèse pessimiste, repli de la section 5 (C7) |
| N, essais de réglage par famille | **4** taux d'apprentissage (1e-5, 2e-5, 5e-5, 1e-4), une graine, **grille jamais étendue** | fixé par Cyril le 03/10/2026 |
| Époques | **2** pour toutes les recettes | fixé par Cyril le 03/10/2026 (C6) |
| Niveau de couverture conforme | **90 %** (α = 0,10) | fixé par Cyril le 03/10/2026 |
| Quasi-doublon, taille minimale de classe, raccourci d'auteur | 0,8 ; 20 patients ; 3 points | figés (sections 3 et 4), confirmés le 03/10/2026 |

**Règle de puissance et repli (confirmée par Cyril le 03/10/2026, C1 ; mise en œuvre précisée après la seconde relecture).**
1. **Quand** : à la porte **RM-17**, après P1-19 (cinq graines de la référence sur le pli 0) et P1-20 (référence gelée), **avant P2-01** : la règle conditionne plus de 40 h de calcul. **Aucun run supplémentaire** : elle utilise les prédictions hors pli des cinq runs de P1-19.
2. **Calcul, entièrement spécifié** : on dispose des prédictions par patient des runs `ok` de P1-19 (jusqu'à cinq graines `s_0 … s_4`, le run `s_0` pouvant être celui du réglage du taux retenu s'il a exactement la même configuration). Pour **chaque paire de graines (i, j)**, dans l'ordre lexicographique : bootstrap **sur patients seulement**, **R = 10 000 répliques** (comme 6.2), tiré dans le pool du pli 0 **stratifié par classe avec pour tailles de strate les effectifs du test scellé** (`test_class_counts`, 633 patients dont 4 `AUTRE`), **le même tirage de patients servant aux deux graines de la paire**, intervalle **percentile à 98,33 %** de la différence de macro-F1 (17 chapitres), **largeur = borne haute moins borne basse, en points, non arrondie**. Générateur `numpy.random.default_rng` (PCG64), **graine 20261002**, un seul flux consommé dans l'ordre des paires ; **le calcul ne se relance jamais avec une autre graine**. **La statistique est la moyenne des largeurs de toutes les paires.** Si P1-19 a moins de cinq runs `ok`, on utilise les k(k−1)/2 paires disponibles ; **avec moins de 3 graines `ok`, la règle échoue** (pas assez de paires pour la mesurer). Aucune prédiction du test scellé n'est utilisée. Le calcul est un **ordre de grandeur** de la largeur des vraies comparaisons (graines d'une même recette, patients seuls, pool de 717 patients dont certaines classes n'ont que 2 à 6 patients) : le rapport le dit, sans prétendre à un sens du biais.
3. **Seuil strict** : si la moyenne des largeurs dépasse **4,0 points** (2 × δ), comparée sur la valeur non arrondie, la règle échoue, sans tolérance et **sans sortie anticipée** : les dix paires coûtent quelques secondes de calcul, aucune décision ne se prend sur une seule paire.
4. **Si la règle échoue** : δ, K et la famille **ne changent pas** ; les fiches de H1 à H3 passent au statut **EXPLORE** (95 % non ajusté, aucun verdict), ce basculement n'étant **pas** un changement de famille (6.10, règle 5) ; il est consigné par une ligne datée dans `experiments/INDEX.md` (colonnes habituelles ; objet « règle de puissance : échec » ou « réussite », `run_id` du calcul dans la colonne Fichier), **avant tout run de H1 à H3** (les runs de réglage ne comptent pas) ; la branche « réussite » est consignée de la même façon, pour que l'absence de ligne ne soit pas la seule preuve. Le test scellé n'est alors ouvert **qu'une fois** (6.8) : le temps A couvre **toutes les recettes gelées et le candidat final** ; le temps B rend, pour H1 à H3, des **intervalles EXPLORE à 95 % non ajustés sans verdict**, et les métriques du candidat final. La porte RM-17 reçoit ce résultat : poursuivre H1 à H3 comme expériences exploratoires, ou s'arrêter, est une décision de Cyril.
5. **Si la règle réussit** (largeur ≤ 4,0) : H1 à H3 restent confirmatoires, **mais cela ne garantit pas un verdict résolu**. Avec une largeur de 4 points, « gain confirmé » exige un écart observé supérieur à δ + 2 = 4 points, et « absence de gain utile » un écart inférieur à 0 ; **un vrai gain de 3 points n'est confirmé que dans environ 12 % des cas** (approximation normale, z = 2,394), un vrai gain égal à δ n'est confirmé que dans moins de 1 % des cas, et la largeur de la vraie comparaison est plus grande que celle de la règle. **« Non résolu » est le résultat attendu, pas un échec du protocole** ; le rapport le dit avant l'ouverture.
6. **Alerte déjà connue** : une simulation (run `20261002-221006-power-sketch-ic-width-v2` ; prédictions inventées ; bootstrap sur patients seuls) donne 7,8 à 13,7 points en moyenne selon le scénario (minimum 5,7 sur les tirages) sur les effectifs réels du test. Ce n'est pas la mesure ci-dessus, mais l'échec est probable. Sa largeur de 7,8 à 13,7 est une **moyenne de scénario** ; aucune simulation ne passe sous 4.
7. **Alternative écartée** : relever δ après avoir vu la largeur reviendrait à fixer le critère d'après les données (ADR-007, « δ dérivé des données »). Cyril a choisi le repli ci-dessus plutôt qu'un δ′ fixé avant le gel.

### 6.4 Graines et pannes

- **Graine de découpage** : 20261002, jamais modifiée pendant un cycle. **Graines d'entraînement** : `s_k = 1000 + k`, k = 0 … K−1, la même liste pour toutes les recettes (les **entraînements** partagent les graines ; le **bootstrap** tire ses graines indépendamment par recette, voir ci-dessous) ; le réglage (une graine) utilise `s_0 = 1000`.
- **Appariement** : il vient du **même tirage de patients** appliqué aux deux recettes ; les graines sont tirées **indépendamment par recette** (ADR-007, étape 2).
- **Classement d'un échec, une seule définition** : un run qui ne finit pas est enregistré **`failed`** et la graine reste au registre ; l'historique de perte est consigné. **Divergence** = au moins une perte non finie dans cet historique ; **panne d'infrastructure** = tout autre échec (mémoire, coupure, entrée-sortie). Le classement est fait **par le code du registre à partir de l'historique, pas par jugement après coup** ; **ce code n'existe pas encore** : il est ajouté à la tâche P1-19 (extension du registre, test sur cas piégés : perte non finie puis mémoire, mémoire seule, relance de la même graine).
- **Panne d'infrastructure** : relance autorisée avec la même graine et la même configuration, avec, si c'est une panne mémoire, un micro-lot plus petit à **lot effectif égal** ; la relance est consignée au registre et comptée au budget ; elle ne s'applique pas à une divergence.
- **Divergence** : c'est un résultat de cette graine, **non remplacée**, **non relancée**. **Risque accepté, dit à Cyril** : la référence étant commune à H1, H2 et H3, une seule graine divergente de la référence ou d'une variante fait K < 5 et rend la comparaison concernée « non résolue » (règle « K < 5 » d'ADR-007, point 2 : présentation séparée « non combiné », aucun verdict confirmatoire). Le taux d'apprentissage est choisi à une graine : **un taux qui a divergé en réglage est exclu du choix** ; **si les quatre taux d'une famille divergent, la famille est déclarée non entraînable à cette configuration** (comparaison correspondante « non résolue », consignée) ; **un run `aborted` en réglage (durée projetée) est relancé une fois avec la même configuration**, et, s'il est de nouveau interrompu, exclu du choix. La règle d'arrêt de la section 5 vise les runs de criblage, de réglage et de professeur ; **P1-19, P1-26 et P2-07 ne sont jamais interrompus pour leur durée**.
- Les runs **confirmatoires** ne sont jamais interrompus pour leur durée projetée (section 5).

### 6.5 Recettes, réglage et gel de leur configuration

- **Référence** : LoRA réglée, configuration gelée en P1-20 (`configs/reference.yaml` citant le `run_id`).
- **Ce qui est fixé avant tout run de réglage de H1 à H3** et consigné dans la fiche préenregistrée de chaque recette, dont l'**empreinte SHA-256 datée est ajoutée à `experiments/INDEX.md`** : le **professeur** (ou la moyenne de professeurs), α et T de la perte, la **tâche de pré-entraînement** et sa durée, les époques (2). Ces choix **ne dépendent d'aucun résultat de l'élève**. Rien de cela n'est réglé au premier cycle ; seul le taux d'apprentissage l'est.
- **Choix du taux, identique pour toutes les familles** : pli 0, une graine (`s_0`), 4 taux, critère = macro-F1 (17 chapitres) la plus élevée, une égalité exacte allant au taux le plus bas. Avec une seule graine sur un pli, le choix est de fait **le maximum de 4 tirages bruités** ; le biais est le même pour toutes les familles et le rapport le dit. **La grille n'est jamais étendue** (aucune cinquième valeur : l'ordre du backlog fige la référence en P1-20 avant le réglage des variantes, et N reste 4). Si le meilleur taux d'une famille est à un bord de la grille (1e-5 ou 1e-4), le rapport le signale comme **risque de sous-réglage**, sans rouvrir la grille.
- Un réglage de la référence seule ne suffit pas : la règle d'égalité de budget (ADR-004) s'applique à chaque variante.
- **Candidat final** : désigné **par Cyril avant l'ouverture du test scellé**, sur les estimations de développement (réglage du pli 0, variance de P1-19) et les coûts, sa désignation étant consignée avec sa date et sa raison dans `experiments/INDEX.md`. Il peut être une recette de la famille, TF-IDF ou un encodeur ; **son ré-entraînement sur le développement entier avant le temps A** est à budgéter s'il s'agit d'un encodeur (non compté en section 5).

### 6.6 Niveau conforme (P4-05)

- **Couverture visée : 90 %** (α = 0,10), consigné ici (aucune ADR séparée). D'autres niveaux (80 %, 95 %) sont rapportés en sensibilité.
- La **fonction de score** (LAC, APS ou RAPS) et ses hyperparamètres sont choisis **sur la calibration**, jamais sur le test. La calibration utilise des prédictions **hors pli** de modèles entraînés sur 80 % du développement ; le test est prédit par un modèle entraîné sur 100 % du développement : cet écart à l'échangeabilité est dit.
- **Fuite propre aux candidats distillés** : pour H1 ou H3, la cible d'un patient du pli j vient d'un professeur qui a vu les étiquettes du pli j évalué ; les scores de calibration sont alors **optimistes** et la couverture sur le test peut tomber sous 90 %. La couverture est rapportée **avec cette réserve** ; des professeurs imbriqués ne sont pas budgétés au premier cycle.
- **Condition** : la couverture n'est mesurée sur le test que si la fonction de score, la température et les prédictions hors pli du candidat sont **prêtes avant le temps A** (P4-04 et P4-05, parties calibration et choix du score). **RM-20 ne dépend pas d'elles** : si elles ne sont pas prêtes, **la couverture sur le test est abandonnée**, le rapport le dit et la mesure se fait sur le développement (exploratoire). Les entraînements hors pli du candidat ne sont pas budgétés (section 5).
- La couverture est mesurée sur le test scellé **dans l'ouverture unique de 6.8**, **marginale et par classe**, avec un **intervalle de Wilson à 95 %** ; un écart au niveau visé est un résultat. Une analyse « par spécialité » ou de rupture d'échangeabilité (RM-22) se fait sur le **développement ou des données synthétiques**, jamais sur le test.

### 6.7 Étiquettes REP, ADAPT, EXPLORE et statut statistique

- Chaque fiche porte **une étiquette de provenance** : **REP** (tous les critères de la recette source sont repris à l'identique : hyperparamètres, objectif, données ; sur un autre jeu, ce n'est plus REP), **ADAPT** (transfert d'une méthode au clinique français ou à ce jeu), **EXPLORE** (le reste).
- **Précédence** : REP seulement si tous les critères exacts sont vérifiés, sinon ADAPT, sinon EXPLORE ; en cas de doute, la plus faible l'emporte. Appliquer la recette du 1er LMSYS à PARHAF est ADAPT.
- **Statut statistique, champ séparé** : `confirmatoire` ou `exploratoire`. Les fiches H1 à H3 sont **ADAPT** et **confirmatoires**, **sauf basculement** vers `exploratoire` (a) par la règle de puissance (6.3, point 4) pour les trois, ou (b) pour **la comparaison concernée** quand ses 5 graines ne sont pas toutes `ok` avant l'ouverture (6.8) ; chaque basculement est consigné par une ligne datée de `experiments/INDEX.md` ; tout le reste est `exploratoire`.
- Une étiquette erronée ne se modifie pas : la fiche est **annulée et recréée sous un nouvel identifiant**, l'annulation étant consignée.

### 6.8 Développement et confirmation

- **Développement** : plis stratifiés, statut exploratoire (réglage, choix de l'élève, ADR-009), appariement sur les prédictions hors pli. **Aucun verdict n'en sort**, et **aucune estimation de développement de H1 à H3 n'existe au premier cycle** hors le réglage (pli 0, une graine) : P2-08 et P3-07 **entraînent** mais **n'évaluent pas** ; leur évaluation est celle de RM-20. La porte RM-17 décide sur ce réglage exploratoire et sur P1-19, et le dit ; RM-21 vient après RM-20.
- Les plis groupés par auteur sont un contrôle : le raccourci d'auteur est mesuré et **n'est pas signalé** (run `20261001-222107-p0-30-author-shortcut-v2`, écart −0,86 point, intervalle à 95 % [−2,16 ; +0,38], seuil de 3 points ; ADR-006) ; la clause de la section 3 qui en ferait la métrique principale ne s'applique donc pas.
- **Fuite connue et bornée** : en distillation hors pli, la cible d'un patient du pli j vient d'un professeur entraîné sans le pli j mais avec les étiquettes du pli k évalué : biais léger possible sur le choix du taux de H1. Il **n'atteint pas le test scellé** (aucun professeur ni élève n'y est entraîné).
- **Confirmation : une seule ouverture du test scellé, en deux temps** (RM-20, garde `tests/test_sealed_access.py`).
  - **Code requis avant RM-20** (pas encore écrit) : dans `src/llmft/sealed.py`, **deux fonctions distinctes** : l'une renvoie **identifiants et textes seulement, sans colonne d'étiquette**, sans écrire de marqueur (temps A) ; l'autre écrit le marqueur puis renvoie les étiquettes (temps B). **Le chemin du marqueur est fixé** (`data/splits/sealed_opened.marker`) et son empreinte est consignée dans `experiments/INDEX.md` dès sa création. **La liste `ALLOWED` du garde et le nom du script d'évaluation sont arrêtés avant l'écriture du script**, sans affaiblir le garde (`CONSTRAINTS.md`).
  - **Condition par comparaison, vérifiée par le script** : H_i est évaluable si les **5 graines** de la référence et de H_i sont `ok` au registre. Sinon, H_i bascule en `exploratoire` (6.7), son résultat est la présentation « non combiné » d'ADR-007 (point 2) sur les graines disponibles, et le test s'ouvre quand même pour les autres comparaisons et pour le candidat final. La désignation du candidat final est consignée avant (contrôle au gel et à l'ouverture, à la main).
  - **Temps A** : prédictions sur le **texte** du test de **toutes les recettes gelées** (toutes les graines disponibles), du candidat final et des scores conformes éventuels (6.6) ; **aucune étiquette n'est lue** ; **écriture unique par recette** avec empreinte ; relançable en cas de panne ; une relance ne remplace pas une série déjà écrite.
  - **Répétition générale obligatoire** : la fonction du temps B est exécutée avec succès, avant l'ouverture, sur les prédictions hors pli du développement ou des données synthétiques ; elle calcule tout en mémoire **avant** d'écrire un fichier.
  - **Temps B** : ouverture du marqueur, lecture des étiquettes, calcul de **toutes** les métriques, des intervalles, des verdicts et de la couverture à partir des prédictions du temps A, avec une écriture atomique des résultats.
  - **« Consommé sans résultat »** : si le temps B échoue après l'écriture du marqueur, le marqueur est conservé (aucune seconde ouverture) et **le test est perdu** pour les comparaisons concernées, qui restent **sans évaluation** ; la répétition générale rend ce cas improbable. Un résultat partiel n'a **aucun statut de verdict** et est publié comme partiel.
- **Test officiel de PARHAF** : embargoé, hors périmètre, jamais mélangé au test interne.

### 6.9 Preuves et relecture adversariale

- Une note de scorecard suit le schéma de RM-12 (`scorecards/TEMPLATE.md`).
- Trois relectures adversariales en contexte neuf ont eu lieu le 03/10/2026 (sous-agent local en lecture seule, sans historique) ; leurs constats et leur classement sont dans `tasks/JOURNAL.md`. Une revue par Codex ou Gemini n'a lieu qu'avec l'accord de Cyril à chaque fois (envoi hors machine). **Les corrections faites après la troisième relecture n'ont été relues que par leur auteur** (aucun relecteur extérieur) ; cette limite est consignée au journal et un défaut trouvé plus tard suit la règle 4 de 6.10 (nouvelle version, jamais une modification en place).

### 6.10 Règles de gel et confirmations

**Confirmations de Cyril données le 03/10/2026** :
- **C1** règle de puissance et repli (6.3) ; **C2** B = 90 h maintenu, **toutes les familles réglées sur une seule graine** ; **C3** ADR-009 ratifiée ; **C4** valeurs des sections 1 à 4 confirmées sans modification ; **C5** TF-IDF et encodeurs en EXPLORE, P2-08 et P3-07 sans verdict.

**Confirmations de Cyril données le 03/10/2026, après la seconde relecture** :
- **C6** : **2 époques pour toutes les recettes** au premier cycle, non réglées (P1-16 n'est pas dans le chemin court).
- **C7** : **B = 90 h maintenu** ; si l'élève retenu est le Qwen3.5-9B et que B ne suffit pas, le repli de la section 5 s'applique (élève plus petit, puis professeur plus petit, puis location sur décision de Cyril) ; alerte à 80 % de B consommé.
- **C8** : les deux risques dits sont acceptés : (a) une seule graine divergente de la référence ou d'une variante rend la comparaison « non résolue » (6.4) ; (b) un verdict résolu est improbable même si la règle de puissance réussit (6.3, point 5).

**Repli (3) de la section 5** (location de GPU) : **admis comme ouvert** tant que Cyril n'a pas fixé la définition de « local » (ADR-004) ; sa clôture par ADR ne modifie pas ce protocole.

**Règles de gel.**
1. Le gel exige : C1 à C8 datées (fait le 03/10/2026) ; plus aucune mention d'ouverture **portant sur une valeur ou une règle du protocole** dans `PROTOCOLE.md` et dans les ADR 004, 007, 009 et 010, relevée par `grep -inE "propos|défaut|à confirmer|provisoire|brouillon|à ratifier|à fixer|à recaler|non gelé|reste à faire|reste ouvert|hypothèse"` puis **triée à la main** ; **la liste triée avec la raison de chaque occurrence admise est consignée dans `tasks/JOURNAL.md`, pas dans le fichier haché** ; une dernière passe de relecture sur les lignes modifiées après la seconde relecture ; `make check` vert.
2. **Périmètre de l'instantané** : sont copiés ensemble dans `experiments/frozen/` à la date du gel, chacun avec son SHA-256 dans `experiments/INDEX.md` : `PROTOCOLE.md`, ADR-004, ADR-007, ADR-009, ADR-010, `task_specs/parhaf_cim10_chapter.yaml`, `src/llmft/metrics.py`, `results/measures/splits_summary.json` et `data/splits/parhaf_cim10_chapter.sha256` (empreinte complète des partitions). Les neuf entrées sont obligatoires : `scripts/check_frozen.py` échoue si une manque dès qu'une ligne d'instantané existe, ou si une ligne citant `experiments/frozen/` n'est pas lisible. **L'instantané est la version qui fait foi** ; le fichier vivant peut recevoir des errata (`experiments/ERRATA-PROTOCOLE.md`), **jamais** une modification de règle, de valeur du tableau 6.3, de seuil, de graine ni d'effectif de strate. Le script `scripts/check_frozen.py`, lancé par `make check`, échoue si l'empreinte d'un instantané ne correspond pas à son entrée de l'index.
3. L'empreinte est consignée **avant P1-02** (premier run de P1 écrivant au registre), dans `experiments/INDEX.md` **et** dans une page wiki datée. Les empreintes des sections 4 et antérieures portent sur des états du fichier dont aucun instantané n'existe : elles ne prouvent rien sur ces sections, d'où C4.
4. Une section gelée ne se modifie plus. Un changement devient une nouvelle version qui cite l'ancienne, dit pourquoi, **ne dépend d'aucun résultat vu**, et reçoit sa propre empreinte. **Exception de la section 5** : un recalage de B après la mesure pilote RM-16 est une nouvelle version de la section 5 **seule**, déclarée « dépend d'une mesure pilote », décidée par Cyril, qui ne change ni la métrique, ni δ, ni K, ni N, ni la famille confirmatoire.
5. Un changement de métrique primaire, de δ, de K, de N ou de **famille confirmatoire** exige une nouvelle ADR motivée **à partir de P1-02** ; la même règle couvre **le seuil et le niveau de la règle de puissance, R, la grille de taux, les époques, le niveau conforme et la liste des graines** ; **après RM-17 aucune modification de 6.3 n'est admise** ; après un recalage de la section 5, **B fait foi dans la section 5 seule** ; les verdicts déjà rendus restent publiés avec l'ancienne règle. Le basculement de statut de 6.3 (point 4) n'est **pas** un changement de famille.
