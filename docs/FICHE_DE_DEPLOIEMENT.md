# Fiche de déploiement par contrainte (RM-48, version du 05/10/2026)

Statut : **descriptif, révisé le 05/10/2026 après RM-56 (l'élève distillé est écarté)**, mesures de développement (EXPLORE) sur un jeu fictif, matériel : RTX 5090 et processeur de la machine du projet. Les qualités sont des macro-F1 sur 17 chapitres CIM-10, prédictions regroupées des cinq plis de développement (RESULTATS.md, sections « LoRA mûr aux cinq plis », « Distillation vers l'encodeur », « Service de l'encodeur sur GPU » et « Reprises des mesures de service »). **Aucun chiffre de ce tableau ne se transpose à des textes cliniques réels.** Le système final retenu par la règle est G (ensemble LoRA + encodeur + TF-IDF, 0,780) ; son gel (RM-50) et le test scellé sont à venir : cette fiche sera relue après ces deux étapes.

## 1. Les cinq systèmes servables et leur coût mesuré

| Système | Macro-F1 (développement) | Latence d'un patient | Débit | Mémoire | Énergie pour 1 000 patients | Incertitude disponible |
|---|---|---|---|---|---|---|
| A. TF-IDF caractères équilibré | 0,720 | **1,9 ms (processeur)** | environ 570 patients par seconde | 20 Mo | négligeable (processeur) | conforme marginale et par famille ; couverture minimale par famille 0,897, 2,69 classes |
| D. Encodeur moyenné, 5 graines | 0,753 | 5 × 191 ms sur processeur ; 4,3 ms (un encodeur, GPU bf16) | 1 406 patients par seconde par encodeur (GPU bf16) | 0,35 Gio par encodeur (GPU) | 0,31 Wh par encodeur en lot de 1 | à recalculer |
| E. Ensemble encodeur et TF-IDF 50/50 | 0,772 | environ 960 ms sur processeur ; environ 25 ms sur GPU (5 × 4,3 ms plus TF-IDF) | selon le GPU | 5 encodeurs plus 20 Mo | environ 5 fois celle d'un encodeur | conforme par famille : couverture minimale 0,892, 1,89 classes |
| ~~C2. Élève distillé de l'ensemble (un encodeur)~~ **écarté après RM-56** | 0,795 non imbriqué (artefact) ; **0,753 avec professeurs imbriqués** | un encodeur : 191 ms (processeur), 4,3 ms (GPU bf16) | 1 406 patients par seconde (GPU bf16) | 0,35 Gio (GPU) | 0,31 Wh en lot de 1, 0,097 Wh en lot | à calculer après gel |
| F. LoRA 4B fusionné bf16 | 0,767 | 61 ms (p95 114 ms) | 6,4 patients par seconde en lot de 8 (le lot n'aide pas) | 14,1 Gio | **8,6 Wh** | conforme par famille : couverture minimale 0,894, 2,17 classes |

Mesures de service : runs `bench-lora-serving-llm-mur2-qwen3-5-4b-ep10-lr1e-4` et `bench-encoder-gpu-camembert-deploy-ep10-lr1e-4-energie15s` (énergie sur au moins 14 secondes de charge, prix du kWh pris comme paramètre à 0,25 euro, non mesuré). La quantification INT8 dynamique naïve de l'encodeur est écartée (latence réduite à 118 ms sur processeur mais macro-F1 effondrée à 0,336, run `quantization-camembert-deploy-ep10-lr1e-4` ; la quantification statique reste à tester, RM-44). L'élève C2 n'est pas mesuré en service séparément : il a l'architecture d'un seul encodeur, donc le coût d'un seul encodeur ; à confirmer par un banc après gel.

## 2. Arbre de décision par contrainte (révisé après RM-56)

1. **Pas de GPU (processeur seul)** : servir **A** (1,9 ms, 20 Mo, incertitude conforme prête). Un seul encodeur (191 ms, 0,753 en moyenne) n'apporte pas de gain résolu sur le TF-IDF seul à cette échelle de mesure sans l'ensemble ; l'ensemble E sur processeur coûte environ 1 seconde par patient, ce qui n'est défendable que hors ligne.
2. **GPU modeste (quelques Gio)** : servir **E** (cinq encodeurs en bf16 plus le TF-IDF, environ 25 ms, environ 2 Gio, 0,772) ; le LoRA ne tient pas dans cette contrainte (14,1 Gio, 61 ms).
3. **GPU de 32 Gio, qualité maximale** : **G** (ensemble LoRA, encodeur et TF-IDF à parts égales, 0,780) est le système retenu par la règle de sélection ; il coûte le LoRA (61 ms) plus l'ensemble E. Contre E (+0,78) et contre F (+1,27), G n'est pas distinct en développement ; il n'est retenu que parce qu'il est le seul admissible. La **cascade encodeur puis LoRA** évite le LoRA pour 93,4 % des patients sans perte (+0,12 [−1,74 ; +1,90], non-infériorité à 2 points) et coûte environ 26 à 34 ms par patient contre 61 ms pour le LoRA seul (1,8 à 2,3 fois moins) ; la cascade n'a pas été mesurée pour l'ensemble des trois familles G.
4. **Énergie ou coût imposé** : un encodeur seul en lot coûte 0,097 Wh pour 1 000 patients (0,31 Wh en lot de 1) et le LoRA environ 90 fois plus en lot, 28 fois plus en lot de 1 ; l'ensemble E coûte environ cinq fois un encodeur ; **la distillation vers un seul encodeur, qui aurait rapproché ces coûts, est écartée** (RM-56).
5. **Incertitude** : tous les systèmes disposent d'un ensemble de prédiction conforme par famille (Mondrian) et d'une abstention ; l'abstention à 70 % de couverture donne une exactitude de 0,948 (ensemble) et 0,953 (LoRA) ; la garantie dépend du système appelé : en cascade, elle se mesure par région, jamais par héritage ; G n'a pas encore sa couverture conditionnelle calculée (RM-51 après l'ouverture).

## 3. Ce qui devient inutile, et ce qui ne l'est pas

- **Inutile** : la distillation vers un seul encodeur (gain non préservé, fuite de second ordre significative) ; les trois facteurs de recette testés (lissage d'étiquettes, EMA, curriculum : résultats nuls ou négatifs) ; la quantification INT8 dynamique naïve.
- **À adopter** : le **bf16** pour l'encodeur (équivalent en qualité à l'entraînement, 2,25 fois plus rapide, 2,85 fois moins d'énergie ; à l'inférence, l'équivalence de qualité reste à vérifier) ; la fusion de l'adaptateur LoRA (latence divisée par deux environ).
- **Reste utile** : le LoRA (dans G, et seul modèle à plus haute capacité de contexte) ; l'ensemble de cinq encodeurs (dans E et G) ; le TF-IDF (référence, système sans GPU, composante de E et G).

## 4. Limites et conditions de relecture

1. Corpus fictif, étiquette issue d'un scénario ; aucune évaluation sur des textes réels (interdite par les règles du projet) : un déploiement hospitalier exigerait une validation locale.
2. Qualités : développement, cinq plis, bootstrap par blocs d'auteurs ; la confirmation vient du test scellé, une fois, après le gel (PROTOCOLE_V2.md) ; la probabilité d'un « gain confirmé » de G contre le TF-IDF est d'environ 47 % au format du test.
3. Mesures de service : un jeu de 200 patients du pli 0, un seul GPU ; énergie lue par le capteur de la carte (hors processeur et refroidissement) ; coûts en euros indicatifs ; G n'est pas mesuré en service d'un seul tenant (sommes de composantes).
4. Pas de mesure de latence en charge concurrente, ni de service multi-utilisateurs, ni d'intégration à un système d'information hospitalier.
