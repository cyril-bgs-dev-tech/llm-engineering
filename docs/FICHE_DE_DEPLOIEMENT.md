# Fiche de déploiement par contrainte (RM-48, version du 05/10/2026)

Statut : **descriptif**, mesures de développement (EXPLORE) sur un jeu fictif, matériel : RTX 5090 et processeur de la machine du projet. Les qualités sont des macro-F1 sur 17 chapitres CIM-10, prédictions regroupées des cinq plis de développement (RESULTATS.md, sections « LoRA mûr aux cinq plis », « Distillation vers l'encodeur », « Service de l'encodeur sur GPU » et « Reprises des mesures de service »). **Aucun chiffre de ce tableau ne se transpose à des textes cliniques réels.** Le système final et son verdict confirmatoire dépendent du gel RM-50 et du test scellé : cette fiche sera relue après ces deux étapes.

## 1. Les cinq systèmes servables et leur coût mesuré

| Système | Macro-F1 (développement) | Latence d'un patient | Débit | Mémoire | Énergie pour 1 000 patients | Incertitude disponible |
|---|---|---|---|---|---|---|
| A. TF-IDF caractères équilibré | 0,720 | **1,9 ms (processeur)** | environ 570 patients par seconde | 20 Mo | négligeable (processeur) | conforme marginale et par famille ; couverture minimale par famille 0,897, 2,69 classes |
| D. Encodeur moyenné, 5 graines | 0,753 | 5 × 191 ms sur processeur ; 4,3 ms (un encodeur, GPU bf16) | 1 406 patients par seconde par encodeur (GPU bf16) | 0,35 Gio par encodeur (GPU) | 0,31 Wh par encodeur en lot de 1 | à recalculer |
| E. Ensemble encodeur et TF-IDF 50/50 | 0,772 | environ 960 ms sur processeur ; environ 25 ms sur GPU (5 × 4,3 ms plus TF-IDF) | selon le GPU | 5 encodeurs plus 20 Mo | environ 5 fois celle d'un encodeur | conforme par famille : couverture minimale 0,892, 1,89 classes |
| C2. Élève distillé de l'ensemble (un encodeur) | 0,795, **sous réserve de RM-56** | un encodeur : 191 ms (processeur), 4,3 ms (GPU bf16) | 1 406 patients par seconde (GPU bf16) | 0,35 Gio (GPU) | 0,31 Wh en lot de 1, 0,097 Wh en lot | à calculer après gel |
| F. LoRA 4B fusionné bf16 | 0,767 | 61 ms (p95 114 ms) | 6,4 patients par seconde en lot de 8 (le lot n'aide pas) | 14,1 Gio | **8,6 Wh** | conforme par famille : couverture minimale 0,894, 2,17 classes |

Mesures de service : runs `bench-lora-serving-llm-mur2-qwen3-5-4b-ep10-lr1e-4` et `bench-encoder-gpu-camembert-deploy-ep10-lr1e-4-energie15s` (énergie sur au moins 14 secondes de charge, prix du kWh pris comme paramètre à 0,25 euro, non mesuré). La quantification INT8 dynamique naïve de l'encodeur est écartée (latence réduite à 118 ms sur processeur mais macro-F1 effondrée à 0,336, run `quantization-camembert-deploy-ep10-lr1e-4` ; la quantification statique reste à tester, RM-44). L'élève C2 n'est pas mesuré en service séparément : il a l'architecture d'un seul encodeur, donc le coût d'un seul encodeur ; à confirmer par un banc après gel.

## 2. Arbre de décision par contrainte

1. **Pas de GPU (processeur seul)** : servir **A** (1,9 ms, 20 Mo, incertitude conforme prête) ; si 191 ms par patient sont acceptables, servir **C2** (un encodeur) à la place, **à condition que RM-56 préserve le gain de la distillation** ; l'ensemble E sur processeur coûte environ 1 seconde par patient, ce qui n'est défendable que hors ligne.
2. **GPU modeste (quelques Gio)** : servir **C2** en bf16 (0,35 Gio, 4,3 ms, 1 406 patients par seconde), ou **E** si l'ensemble reste préféré ; le LoRA ne tient pas dans cette contrainte (14,1 Gio, 61 ms).
3. **GPU de 32 Gio, qualité maximale** : **F** reste le modèle de qualité de référence ; il n'est pas distinct de l'encodeur moyenné (+1,45 [−1,10 ; +4,09] contre l'encodeur) ni de l'ensemble (−0,49) en développement. La **cascade encodeur puis LoRA** évite le LoRA pour 93,4 % des patients sans perte (+0,12 [−1,74 ; +1,90], non-infériorité à 2 points) et coûte environ 26 à 34 ms par patient contre 61 ms pour le LoRA seul (1,8 à 2,3 fois moins) ; elle n'a de sens que si le LoRA apporte une qualité que C2 n'a pas, ce que le développement ne montre pas.
4. **Énergie ou coût imposé** : **C2 en lot** (0,097 Wh pour 1 000 patients) ; le LoRA coûte environ 90 fois plus d'énergie par patient en lot, environ 28 fois plus en lot de 1.
5. **Exigence d'explicabilité de l'incertitude** : tous les systèmes disposent d'un ensemble de prédiction conforme par famille (Mondrian) et d'une abstention ; l'abstention à 70 % de couverture donne une exactitude de 0,948 (ensemble) et 0,953 (LoRA) ; la garantie dépend du système appelé : en cascade, elle se mesure par région, jamais par héritage.

## 3. Ce qui devient inutile, et ce qui ne l'est pas

- Le **LoRA** devient un modèle de qualité et un professeur potentiel, non un système de service, **si** C2 est maintenu après RM-56 : son bras de distillation a dégradé l'élève (−2,55 [−4,78 ; +0,02]), donc la distillation du LoRA vers l'encodeur est abandonnée.
- La **cascade** n'est utile que dans l'arbre 3 (GPU de 32 Gio et LoRA conservé) ; avec C2 en production elle perd son intérêt.
- L'**ensemble de cinq encodeurs** n'est justifié en service que si C2 est écarté ; il reste le professeur de C2.
- Aucune des améliorations de recette testées (lissage d'étiquettes, EMA, curriculum) n'est à déployer : résultats nuls ou négatifs (RESULTATS.md, recette d'encodeur v2). Le **bf16** est à adopter : équivalent en qualité à l'entraînement, 2,25 fois plus rapide.

## 4. Limites et conditions de relecture

1. Corpus fictif, étiquette issue d'un scénario ; aucune évaluation sur des textes réels (interdite par les règles du projet) : un déploiement hospitalier exigerait une validation locale.
2. Qualités : développement, cinq plis, bootstrap par blocs d'auteurs ; la confirmation vient du test scellé, une fois, après le gel (PROTOCOLE_V2.md).
3. Mesures de service : un jeu de 200 patients du pli 0, un seul GPU ; énergie lue par le capteur de la carte (hors processeur et refroidissement) ; coûts en euros indicatifs.
4. C2 dépend du verdict RM-56 (contrôle de la fuite de second ordre) ; cette fiche sera révisée à ce moment.
5. Pas de mesure de latence en charge concurrente, ni de service multi-utilisateurs, ni d'intégration à un système d'information hospitalier.
