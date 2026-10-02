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
