# ADR-015 : second cycle, recettes mûres et budget de réglage égal par famille (PROPOSÉE, non appliquée)

Statut : **proposée** le 04/10/2026 (audit GLM v4, décision déléguée Q20 et Q21). **Le protocole gelé n'est pas modifié** : cette ADR décrit la version suivante, à accepter par Cyril avant tout run du second cycle.

## Contexte (mesures du 04/10/2026, pli 0 sauf mention, EXPLORE)
- La recette gelée (4 taux, 2 époques) sous-estime fortement les modèles appris : CamemBERT-bio passe de 0,448 (2 époques) à 0,553 (6) puis à 0,73 environ (10 à 20 époques, cinq graines 0,7293 ± 0,0256) ; le meilleur taux de chaque famille est toujours au bord supérieur de la grille ; le 4B LoRA croît strictement avec le taux.
- Le TF-IDF bien réglé (caractères 3 à 5, poids équilibrés) atteint 0,7202 sur cinq plis (+3,65 points résolu contre la référence v1) et 0,7184 au pli 0 : **équivalent à l'encodeur mûr** à 20 Mo et 2 ms (encodeur : 443 Mo, 190 ms en CPU).
- À graine égale deux runs GPU diffèrent (rejeu : 0,7714 → 0,7362) ; écart-type entre graines 2,6 points ; **la règle de puissance échoue** (largeur 12,2 points contre 4,0 sur les cinq graines de l'encodeur).

## Décision proposée
1. **Recettes mûres pour toutes les familles**, avec la même clause d'égalité de budget : même nombre de runs de réglage, mêmes heures de calcul, même critère et même pli de sélection ; les dimensions de la grille diffèrent par famille et sont préenregistrées avant les runs de la famille (TF-IDF : C, n-grammes, poids, analyseur ; encodeur : époques de 4 à 20, taux 5e-5 à 1e-4 ; LoRA : époques de 4 à 10, taux jusqu'à 2e-4).
2. **Plateforme d'expérience bon marché** : les comparaisons sur la contribution des techniques (distillation, pré-entraînement voisin) se font d'abord sur l'encodeur (3,5 à 5 minutes par run) avec **cinq graines et cinq plis** ; le LLM LoRA est un bras de comparaison, pas la plateforme.
3. **Évaluation par plis (largeur simulée 3,8 à 6,7) et non par un seul pli de 717 patients** pour toute comparaison présentée comme résolue ; rapport systématique des plis par patient **et** des plis par auteur (écart de 3,9 points du TF-IDF) ; leave-one-author-out comme mesure « nouveaux auteurs ».
4. **Conserver** : test scellé à ouverture unique en deux temps, métrique primaire macro-F1 sur 17 chapitres, δ = 2,0 (à réviser seulement si la largeur à cinq plis reste au-dessus de 4 points), verdict en trois valeurs, fiches hachées avant les runs.
5. **Professeur de distillation** : conditionné à un pilote sur l'encodeur (le professeur est le LLM mûr, l'élève l'encodeur ou le TF-IDF) et à la règle de puissance du second cycle ; aucun run de professeur avant.

## Conséquences
Le coût estimé du second cycle tombe à quelques heures de GPU pour les familles bon marché (cinq plis × cinq graines × 4 minutes ≈ 1,7 h par recette d'encodeur) ; le LLM mûr ajoute environ 4,2 h par run de 10 époques (4B). Le premier cycle reste classé EXPLORE et ses résultats sont publiés tels quels (recette gelée à 2 époques sous-estimée, mesure faite).

## Ce qui reste à décider par Cyril
Accepter la version suivante du protocole (sections 1, 3 et 4 du protocole gelé touchées : époques, grille, plis d'évaluation) et dire si δ reste à 2,0.
