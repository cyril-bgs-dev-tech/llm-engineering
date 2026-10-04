---
title: Conclusions corrigées du 04/10/2026 : recette gelée, tirage unique, discrétisation des petites classes
category: Analyses
summary: Trois erreurs de lecture du premier cycle (recette à 2 époques, conclusion sur un seul tirage, métrique dominée par cinq classes) et ce que les mesures disent maintenant, avec renvoi aux runs
tags: [analyse, recette, variance, macro-f1, correction]
sources: [resultats, audit-glm-v4]
created: 2026-10-04
updated: 2026-10-04
---

# Conclusions corrigées du 04/10/2026

## 1. La recette gelée à 2 époques sous-estime les modèles appris
CamemBERT-bio passe de 0,448 à 2 époques à 0,553 à 6 puis à environ 0,73 entre 10 et 20 époques ; la durée sature au-delà de 10.[^1] Le Qwen3.5-4B à 2 époques (0,587) croît strictement avec le taux et son meilleur taux est au bord de la grille ; le TF-IDF gagne 3,65 points avec des n-grammes de caractères et des poids équilibrés (0,7202).[^2] La phrase « aucun modèle appris ne bat le TF-IDF » est un artefact de la recette gelée et ne doit plus être écrite.

## 2. Un seul tirage ne se conclut pas
Le premier run de l'encodeur à 10 époques (0,7714) était un tirage favorable : à graine égale le rejeu donne 0,7362 ; les cinq graines donnent 0,7293 ± 0,0256 (étendue 6,4 points).[^3] À recette mûre, l'encodeur moyenné bat le meilleur TF-IDF de +1,5 point au pli 0 (non résolu) et de +6,4 points au pli 1 ; l'ensemble avec le TF-IDF n'apporte rien sur l'encodeur moyenné.[^4] La règle de puissance sur ces graines donne une largeur d'IC de 12,2 points contre 4,0 admis : échec, donc EXPLORE.[^3]

## 3. La macro-F1 est une mesure de cinq classes
Les cinq plus petits chapitres (IV, V, XII, XXI, XXII ; 27 à 63 patients au développement) portent 85 % de la variance bootstrap de la macro-F1 (écart-type 1,3 point sur 3 586 prédictions) ; un patient de ces classes déplace la macro-F1 de 0,2 à 0,5 point.[^5] L'écart patient contre auteur (5,06 points sur partitions répétées) n'est pas un artefact de composition ; la signature d'auteur pure vaut environ 2 points (leave-one-author-out 0,6185), le reste est un rétrécissement de l'entraînement.[^5] La correction de priorité à l'inférence récupère 13,8 points pour un encodeur à 6 époques mais seulement 1,0 à 10 : le déficit des petits chapitres est un sous-apprentissage de la queue de distribution.[^6]

## Conséquences pour la méthode
Graines avant conclusion ; recettes mûres et budget de réglage égal par famille (ADR-015) ; plis plutôt qu'un pli unique pour toute comparaison présentée comme résolue ; rapporter les écarts avec leur périmètre.

[^1]: RESULTATS.md [synthesis] — sections « Diagnostic d'époques », « Recette mûre de l'encodeur », « Saturation de la durée »
[^2]: RESULTATS.md [synthesis] — grille de taux du Qwen3.5-4B ; variantes de recette du TF-IDF
[^3]: RESULTATS.md [synthesis] — « Cinq graines de l'encodeur à 10 époques et règle de puissance »
[^4]: RESULTATS.md [synthesis] — « Confirmation de l'ensemble au pli 1 »
[^5]: RESULTATS.md [synthesis] — « Discrétisation des petites classes », « Leave-one-author-out », partitions répétées
[^6]: RESULTATS.md [synthesis] — « Correction de priorité à l'inférence »
