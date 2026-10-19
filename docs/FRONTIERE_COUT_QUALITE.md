# Frontière coût-qualité des systèmes servables (07/10/2026, mise à jour du 17/10/2026)

**Mise à jour du 17/10/2026** : ajout de G servi en cascade E puis G (RM-60), relu dans le registre par le même script (run `20261017-030538-frontiere-cout-qualite`, qui remplace `20261017-030144-frontiere-cout-qualite`, enregistré sans tampon de santé ; les valeurs des autres systèmes sont inchangées).

Statut : **mesure descriptive** (EXPLORE), développement, cinq plis, aucune étiquette du test scellé lue. Chaque valeur est lue dans le registre par `scripts/pareto_cout_qualite.py` (run `20261007-094900-frontiere-cout-qualite`, résultats dans `results/measures/pareto_cout_qualite.json`) ; rien n'est saisi à la main. **Dominé** veut dire : un autre système a une macro-F1 au moins égale, un coût d'entraînement au plus égal et une latence au plus égale, avec une inégalité stricte quelque part. Le calcul porte sur des **estimations ponctuelles** : un écart de macro-F1 non résolu (intervalle qui contient zéro) ne prouve pas qu'un système vaut mieux qu'un autre, il dit seulement qu'à coût plus élevé on n'a pas mesuré mieux.

## Tableau

| Système | macro-F1 (5 plis) | Entraînement | Latence p50 | Dominé par |
|---|---|---|---|---|
| A. TF-IDF caractères (processeur) | 0,7202 | 0,01 h (48 s) | 1,9 ms | aucun (frontière) |
| D. Cinq encodeurs (GPU, bf16) | 0,7528 | 0,64 h | 26,0 ms | aucun (frontière) |
| E. Cinq encodeurs + TF-IDF (GPU) | 0,7721 | 0,65 h | 28,8 ms | aucun (frontière) |
| E sur processeur seul | 0,7721 | 0,65 h | 801,5 ms | E sur GPU (autre matériel : voir règle par contrainte) |
| F. LoRA 4B seul (GPU) | 0,7673 | 4,45 h | 61,0 ms | E sur GPU |
| **G. LoRA + encodeurs + TF-IDF (GPU)** | **0,7799** | 5,11 h | 91,6 ms | aucun (frontière) |
| Cascade encodeurs puis LoRA, seuil 0,5 | 0,7685 | 5,09 h | 30,0 ms (modélisée) | E sur GPU |
| Cascade encodeurs puis LoRA, routage conforme | 0,7696 | 5,09 h | 59,2 ms (modélisée) | E sur GPU |
| **G servi en cascade E puis G, seuil 0,6 (GPU, HTTP)** | **0,7789** | 5,11 h | **38,4 ms (moyenne attendue)** | aucun (frontière) |
| C2. Élève distillé x3, professeurs imbriqués (écarté, RM-56) | 0,7530 | 0,93 h | 16,2 ms (modélisée) | aucun (frontière) |

Sources : macro-F1 de `selection-systeme-final-apres-rm56`, `cascade-cinq-plis-encodeur-lora`, `cascade-conforme-cinq-plis` ; entraînement : durées des runs `final-*` (le LoRA 16 035 s sur les 3 586 patients) ; latences de G, E et des étages : runs `20261007-094117-service-g-bout-en-bout-gpu` et `20261007-094745-service-g-bout-en-bout-cpu` (médiane du premier passage ; deux passages acceptés par le critère de la fiche) ; TF-IDF : `bench-serving-tfidf-charbal-v1`. Les cascades encodeurs puis LoRA et l'élève sont **modélisés** : latences d'étage mesurées, parts de routage mesurées hors pli. **G en cascade** : macro-F1 hors pli du run `20261017-012416-cascade-e-puis-g`, latence moyenne attendue du service HTTP (chemins mesurés pondérés par la part hors pli, run `20261017-015754-service-g-cascade`) ; la colonne donne une moyenne, pas une médiane.

## Ce que cela dit

1. **Le LoRA seul est dominé** : 4,45 h d'entraînement et 61 ms pour une macro-F1 (0,7673) qui n'est pas au-dessus de celle de E (0,7721, 0,65 h, 28,8 ms). Les deux cascades sont dominées pour la même raison : elles gardent le coût d'entraînement du LoRA et ne dépassent pas E.
2. **G coûte 7,9 fois le temps d'entraînement de E et 3,2 fois sa latence pour +0,78 point de macro-F1 non résolu** (développement ; sur le test scellé, G moins E vaut +0,99 [−3,71 ; +5,00], sans verdict). G reste sur la frontière parce qu'il est le plus haut en qualité, et il reste le système retenu par la règle de sélection écrite d'avance ; **E n'est pas démontré non inférieur à G** (borne basse −2,79 contre une marge de −2,0) : on ne peut donc pas écrire que E remplace G, seulement que le LoRA ne se justifie que si les 0,78 point comptent.
3. **L'élève distillé (C2) est sur la frontière à qualité égale à D** (0,7530 contre 0,7528) avec une latence modélisée plus basse : il a été écarté (RM-56) parce que son gain apparent contre un témoin non distillé n'est pas préservé avec des professeurs imbriqués, **pas** parce qu'il serait plus cher. Son avantage de coût sur D est de l'ordre de 10 ms : sans portée pratique.
4. **G servi en cascade E puis G est sur la frontière** (17/10/2026) : même entraînement que G, qualité à −0,10 point de G (intervalle [−0,23 ; +0,02], non inférieure à la marge de 2,0) et latence moyenne attendue de 38,4 ms contre 91,6 ms au p50 pour G d'un seul tenant ; énergie attendue 3,06 Wh pour 1 000 patients contre 10,67 Wh pour G complet dans la même mesure (run `20261017-025855-energie-service-g-cascade`). Il ne domine pas G (qualité un peu plus basse en point estimé) et n'est pas dominé par E (qualité plus haute en point estimé, écart non résolu : +0,68 [−0,72 ; +2,68]).
5. **Les options testées et écartées** n'entrent pas dans le tableau (une dimension manque ou elles sont hors comparaison). L'encodeur élagué à six couches (macro-F1 groupée 0,6297 contre 0,7605 pour l'encodeur complet, 59 ms sur processeur contre 117 ms), l'INT8 statique (0,0227, 236 ms contre 184 ms en 32 bits) et Qwen3.5-4B sans affinage (0,493, pli 0 seulement) sont au-dessous de A en qualité et au-dessus en coût. L'élève TF-IDF souple (0,7271) est 0,7 point au-dessus de A, mais son entraînement exige le professeur ensemble.

## Limites

Estimations ponctuelles sans intervalle de dominance ; qualité de développement (la confirmation unique est dans la carte de modèle) ; latences d'un seul GPU et d'un seul processeur, 200 patients, médianes ; coût d'entraînement = durée du run final tel qu'enregistré (les durées des encodeurs varient de 325 à 552 s selon la charge de la machine ce jour-là) ; énergie non incluse dans la dominance (G : 10,5 Wh pour 1 000 patients, `RESULTATS.md`) ; cascades modélisées, non servies.
