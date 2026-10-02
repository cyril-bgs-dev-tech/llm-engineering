# PROTOCOLE : règles communes du projet LLM_finetuning

Statut : **brouillon daté du 02/10/2026**. Les sections 1 à 3 (P0-32, P0-33, RM-07) sont figées par empreinte dans `experiments/INDEX.md` **avant** la mesure du raccourci d'auteur (P0-30). Les sections suivantes (métriques, tests statistiques, seuils de décision, budget, gel) s'ajoutent en P0-46. Une section figée ne se modifie plus : un changement devient une nouvelle version qui cite l'ancienne et dit pourquoi.

Valeurs de départ proposées par Claude le 02/10/2026 en l'absence de réponse de Cyril : à confirmer ou corriger avant le gel final de P0-46.

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

## 5. Budget de calcul par vague (P0-45), brouillon ajouté le 02/10/2026

Section ajoutée après les empreintes des sections 1 à 4 ; elle ne modifie aucune règle figée. **Ce sont des hypothèses, pas des durées annoncées** : la règle 6 de la feuille de route interdit d'annoncer une durée avant la mesure pilote RM-16 (une LoRA réelle, 100 pas). Le budget **B** est fixé à **90 h** par Cyril le 02/10/2026 (section 6.3) ; le nombre d'essais **N** reste à fixer (question Q11, ADR-004).

**Entrées mesurées.** Débits du banc P0-08 et de P0-06 (runs `p0-06-*` et `p0-08-*` du registre, page [compatibilite-modeles-p0-06](knowledge/wiki/pages/compatibilite-modeles-p0-06.md)) ; longueurs réelles de P0-21 : environ 1 309 tokens par patient avec le tokenizer Qwen et 1 272 avec celui de Gemma ; 2 868 patients d'entraînement par pli de développement (4 plis sur 5, plis de 717 à 718) et 3 586 pour le développement entier. Calcul enregistré au run `p0-45-budget-hypotheses`.

| Modèle | Débit à 1 024 tokens | Débit à 4 096 tokens | Heures par pli et par époque (optimiste) | Idem (pessimiste) |
|---|---|---|---|---|
| Gemma-4-31B QLoRA (professeur) | 641 tokens/s | 423 tokens/s | 1,58 | 2,40 |
| Qwen3.8-27B QLoRA (professeur) | 585 tokens/s | 360 tokens/s | 1,78 | 2,90 |
| Qwen3.5-9B bf16 (élève) | 1 660 tokens/s | non mesuré | 0,63 | non mesuré |
| Qwen3.5-4B bf16 (élève) | 2 284 tokens/s | non mesuré | 0,46 | non mesuré |
| Gemma-4-E4B bf16 (élève) | 2 922 tokens/s | non mesuré | 0,35 | non mesuré |

**Hypothèses du calcul** : le débit à 1 024 tokens vaut pour les patients réels (borne optimiste) ; le débit à 4 096 tokens, plus bas, donne la borne pessimiste (professeurs seulement) ; aucun surcoût de remplissage ni de chargement des données ; **deux époques** (le nombre réel se règle en P1-16) ; cinq graines (K = 5, ADR-007).

| Poste | Heures de GPU (optimiste) | Remarque |
|---|---|---|
| Vague V0 : criblage de trois élèves sur un pli (P1-11) | 2,9 | un pli, réglages identiques |
| V0 : balayage du taux d'apprentissage, 12 runs d'un pli (P1-13) | 8,3 à 15,1 | élève E4B à 9B |
| V0 : variance entre graines, 5 runs d'un pli (P1-19) | 3,5 à 6,3 | idem |
| **Sous-total V0** | **14,7 à 24,2** | selon l'élève |
| V1 : professeur en cinq plis, deux époques (P2-02) | 15,8 à 17,8, pessimiste 24,0 à 29,0 | le plus gros poste unique |
| V1 : comparaison confirmatoire, 4 recettes × 5 graines sur le développement entier (P3-07) | 17,3 à 31,4 | référence, tâche voisine, distillation, les deux |
| **Premier cycle V0 + V1** | **environ 48 à 73, jusqu'à 85 en pessimiste** | hors postes ci-dessous |

**Non compté** : le pré-entraînement sur tâche voisine (P2-07), l'inférence hors pli, la calibration et la prédiction conforme, les relances après échec, les chargements de modèle (de 5 à 7 minutes pour un professeur), les vagues V2 à V5. **Lecture** : le poste dominant est le professeur en cinq plis, puis la comparaison confirmatoire, dont le coût est proportionnel à K ; réduire K ou le nombre de recettes est un choix de protocole à faire **avant** le gel (P0-46), pas après un résultat.

**Arrêt anticipé (proposition, à valider avec B).** Un run est interrompu et enregistré `aborted` avec sa raison si : une perte devient non finie ; ou, après 10 % des pas, son temps projeté dépasse de 50 % la durée préenregistrée ; ou le plafond d'heures de sa vague est atteint. Un run interrompu n'est jamais compté comme un résultat.

**Règle de repli (proposition, ordre à respecter).** Si B ne couvre pas le professeur en cinq plis : (1) réduire le nombre d'époques à la valeur retenue en P1-16 ; (2) choisir un professeur plus petit (Qwen3.5-9B contre un élève de 4B) en le disant dans le rapport ; (3) seulement ensuite, déclencheur de location de la section 5.2 du plan, avec fiche préenregistrée et plafond validé par Cyril. Aucun repli ne change la métrique, les plis ni le test scellé.

## 6. Métriques, tests, seuils, graines, étiquettes et gel (P0-46), brouillon ajouté le 02/10/2026

**Brouillon, non gelé.** Il reprend ADR-004 et ADR-007 (proposées) et n'invente aucune valeur qui appartient à Cyril : chaque valeur encore ouverte porte la marque `[À FIXER Q…]` et le gel (point 6.9) est **interdit tant qu'une marque subsiste**. Les sections 1 à 4 restent figées par leurs empreintes.

### 6.1 Métriques

- **Primaire : macro-F1 au niveau chapitre CIM-10** sur les 17 classes évaluées. La classe `AUTRE` reste dans l'espace de prédiction (un patient d'un chapitre évalué prédit `AUTRE` compte comme faux négatif de son chapitre) mais **n'entre pas dans la moyenne** : l'appelant passe à `llmft.metrics.macro_f1` la liste `labels` des 17 classes seulement. `AUTRE` est rapportée à part (précision, rappel, effectif).
- **Secondaires** : exactitude ; log loss ; ECE à 10 tranches de confiance égales ; coût (heures de GPU, pic de VRAM, latence par patient). Le coefficient de Spearman (P1-01) ne s'applique pas aux tâches fermées sans ordre : il n'est pas calculé ici.
- **Par classe** : F1, précision et rappel de chaque chapitre sont toujours publiés avec leur effectif de test ; les chapitres de moins de 10 patients de test sont marqués « effectif très faible » dans tout tableau.
- Les fonctions sont celles de `src/llmft/metrics.py`, vérifiées sur cas construits à la main (P1-01) ; aucune autre implémentation n'est utilisée pour un chiffre publié.

### 6.2 Tests statistiques et verdict

- **Estimand, rééchantillonnage hiérarchique (patients stratifiés par classe, puis graines), famille confirmatoire de trois comparaisons, intervalle au niveau de Bonferroni de 98,33 %, verdict en trois valeurs** : tels que décrits dans ADR-007 (points 1 à 4), qui fait foi. Ce protocole ne les redéfinit pas ; il les rend contraignants au gel.
- **Contrôles complémentaires, non décisionnels** : McNemar sur l'exactitude, permutation appariée sur la macro-F1, Wilcoxon sur les scores par pli. Un désaccord entre un contrôle et le verdict est signalé dans le rapport, il ne change pas le verdict.
- **Nombre de rééchantillonnages** : 10 000, graine de rééchantillonnage fixée à 20261002 (valeur de graine déjà utilisée pour le découpage, conservée pour ne pas multiplier les conventions).
- **Rien d'autre n'est confirmatoire.** Toute comparaison hors de la famille de trois est étiquetée EXPLORE, avec intervalle non ajusté et sans verdict.

### 6.3 Seuils de décision

| Paramètre | Valeur | Statut |
|---|---|---|
| δ, seuil « pratiquement utile » (points de macro-F1) | **2,0** | fixé par Cyril le 02/10/2026 (ADR-007, point 5) |
| K, graines d'entraînement par recette confirmatoire | **5** | fixé par Cyril le 02/10/2026 (minimum d'ADR-007) |
| B, heures de GPU du premier cycle | **90 h** | fixé par Cyril le 02/10/2026 ; à recaler après la mesure pilote RM-16, tout changement passant par Cyril |
| N, essais de réglage par famille de méthodes | `[À FIXER Q11]` ; proposition : 4 (les quatre taux d'apprentissage de P1-13), même budget de réglage pour la référence et chaque variante | égalité de budget entre méthodes (ADR-004) |
| Règle de puissance avant run confirmatoire | si la largeur de l'intervalle apparié à 98,33 % dépasse 2 × δ, on ne lance pas le test scellé : on réduit l'ambition, on augmente K ou on déclare la comparaison exploratoire | adoptée (ADR-007, point 5), vérifiée en RM-15 |
| Seuil de quasi-doublon, taille minimale de classe, seuil du raccourci d'auteur | 0,8 ; 20 patients ; 3 points | figés (sections 3 et 4) |

### 6.4 Graines

- **Graine de découpage** : 20261002 (figée, section 3). Elle ne change jamais pendant un cycle.
- **Graines d'entraînement** : `s_k = 1000 + k` pour `k = 0 … K-1`, la même liste pour toutes les recettes d'une comparaison (appariement). Une graine ne sert qu'à l'initialisation de la tête, de la LoRA (si non pré-entraînée), à l'ordre des lots et à l'abandon.
- **Une graine défaillante n'est pas remplacée** : un run qui diverge ou s'interrompt reste au registre (`aborted` ou `failed`) et le verdict est calculé sur les graines restantes, en le disant ; si moins de 3 graines restent pour une recette, le verdict est « non résolu » d'office.
- Les prédictions de chaque (recette, graine) sont conservées par identifiant de patient pour que l'appariement soit rejouable (`run-registry`).

### 6.5 Niveau conforme (prédiction conforme, P4-05)

- **Niveau de couverture visé : 90 %** (α = 0,10), `[À FIXER Q11]` pour confirmation. Les fonctions de score (LAC, APS, RAPS) sont comparées à ce niveau unique ; d'autres niveaux (80 %, 95 %) sont rapportés comme sensibilité.
- **Données de calibration** : des prédictions hors pli du développement, jamais le test scellé ; la couverture est **mesurée** sur le test scellé, une seule fois, avec l'hypothèse d'échangeabilité énoncée (corpus fictif, patients d'un même corpus : aucune garantie hors de lui).
- La couverture empirique est comparée au niveau visé avec un intervalle binomial ; un écart est un résultat, pas un défaut à corriger après coup.

### 6.6 Étiquettes REP, ADAPT et EXPLORE

Chaque fiche d'expérience (`experiments/<date>-<slug>.md`) porte **une** étiquette dans son en-tête, choisie avant le run :
- **REP** : vérification d'un mécanisme **exact** de la recette d'une source citée (mêmes hyperparamètres, même objectif), réservée à ce cas. Le mot « reproduction » n'est employé pour rien d'autre.
- **ADAPT** : transfert d'une méthode au clinique français ou à ce jeu (changement de données, de modèle, de langue).
- **EXPLORE** : tout le reste, y compris toute comparaison hors de la famille confirmatoire ; aucun verdict, intervalle non ajusté.
Une fiche sans étiquette n'est pas figée ; une étiquette ne se change pas après le run.

### 6.7 Développement et confirmation

- **Développement** : plis stratifiés, statut exploratoire (réglage, choix de l'élève, ADR-009). L'appariement se fait sur les prédictions hors pli. Aucun verdict n'en sort.
- **Confirmation** : test scellé interne, **ouvert une seule fois**, par le seul script autorisé (RM-20, garde `tests/test_sealed_access.py`), après gel de la configuration de chaque recette (P1-20 pour la référence) et vérification de la règle de puissance. Un second accès est une violation de protocole : il est consigné, et le verdict correspondant devient exploratoire.
- **Test officiel de PARHAF** : embargoé, hors périmètre ; il n'est jamais mélangé au test interne.

### 6.8 Preuves, scorecards et relecture adversariale

- Une note de scorecard suit le schéma de preuve de RM-12 (`scorecards/TEMPLATE.md`) : exigence, artefact et empreinte, commande de reproduction, attendu et observé, degré d'indépendance de la confirmation, date, défaut résiduel.
- **Relecture adversariale en contexte neuf avant le gel** : un relecteur sans l'historique de la conversation reçoit ce fichier, ADR-004, ADR-007, ADR-009 et le plan V6 (sections 0 à 6 et 8), et cherche : une valeur ouverte oubliée, une règle ambiguë (deux lectures possibles), une décision qui dépend d'un résultat, un verdict impossible à produire. Chaque constat est classé **bloquant** (corrigé avant gel), **accepté** (raison écrite) ou **rejeté** (raison écrite). Le relecteur est un sous-agent du dépôt (`code-reviewer` ou `general-purpose`) ; une revue par Codex ou Gemini n'a lieu qu'avec l'accord de Cyril à chaque fois, car elle envoie du contenu hors machine.

### 6.9 Règles de gel

1. Le gel exige : plus aucune marque `[À FIXER]` ; relecture du point 6.8 faite et classée ; `make check` vert.
2. Empreinte SHA-256 de l'état entier du fichier consignée **avant tout run de P1** dans `experiments/INDEX.md` **et** dans une page wiki datée.
3. Une section gelée ne se modifie plus. Un changement devient une nouvelle version, qui cite l'ancienne, dit pourquoi, **ne dépend d'aucun résultat vu** ou le déclare explicitement, et reçoit sa propre empreinte.
4. Un changement de métrique primaire, de δ, de K ou de famille confirmatoire après le premier run comparatif exige une nouvelle ADR motivée ; les verdicts déjà rendus restent publiés avec l'ancienne règle.
