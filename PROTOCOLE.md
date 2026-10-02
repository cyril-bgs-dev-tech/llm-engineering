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

Section ajoutée après les empreintes des sections 1 à 4 ; elle ne modifie aucune règle figée. **Ce sont des hypothèses, pas des durées annoncées** : la règle 6 de la feuille de route interdit d'annoncer une durée avant la mesure pilote RM-16 (une LoRA réelle, 100 pas). Le budget **B** (heures de GPU du premier cycle) et le nombre d'essais **N** restent à fixer par Cyril (question Q5, ADR-004, ADR-007).

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
