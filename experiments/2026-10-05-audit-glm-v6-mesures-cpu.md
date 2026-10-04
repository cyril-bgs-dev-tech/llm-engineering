# Fiche préenregistrée : quatre mesures sans GPU issues de l'audit GLM v6 (EXPLORE, cinq plis)

Écrite avant les runs. Source : `audit_GLM_v6.md` (leviers 1, 4, 11 et 15, et vérification du sous-groupe « pool » qui corrige une erreur de notre cahier : le champ `pool` désigne des **sous-ensembles d'usage annotés du corpus, déjà présents dans les plis de développement**, et non une piscine hors distribution). Calcul sur processeur, aucun GPU.

## A. Bootstrap par blocs d'auteurs (levier 1)
- **question** : les intervalles des différences regroupées (ensemble moins TF-IDF, encodeur moyenné moins TF-IDF) résistent-ils à la corrélation des erreurs au sein d'un auteur (104 auteurs) ?
- **variante** : `llmft.cluster_bootstrap.cluster_interval`, tirage des auteurs avec remise, 5 000 répliques, même tirage pour les deux systèmes ; comparé à l'intervalle par patients (`pooled_interval`).
- **critère de décision** : « résiste » si la borne basse de l'ensemble moins TF-IDF reste > 0 et la largeur ≤ 4,0 ; « affaibli » si la borne basse reste > 0 mais la largeur dépasse 4,0 ; « invalidé » si la borne basse est ≤ 0.
- **prédiction** : l'intervalle par blocs est plus large que l'intervalle par patients (probabilité 0,85) ; la borne basse de l'ensemble moins TF-IDF reste > 0 (0,8) ; la largeur reste ≤ 4,0 (0,45).

## B. Empilement appris et réglage de la décision (leviers 4 et 15)
- **question** : une combinaison apprise hors pli de l'encodeur moyenné et du TF-IDF dépasse-t-elle le mélange fixe 50/50 ?
- **variantes** (validation croisée par pli : poids ou règle appris sur les quatre autres plis, appliqués au pli évalué) : S0 mélange 50/50 (référence) ; S1 poids global du mélange choisi sur une grille de 0 à 1 par pas de 0,1 ; S2 régression logistique multinomiale sur les log-probabilités des deux systèmes (C = 0,1, poids de classe équilibrés) ; S4 S0 plus un biais par classe sur les log-probabilités (montée par coordonnées, trois passes, grille {−1 ; −0,5 ; −0,25 ; 0,25 ; 0,5 ; 1}) appris sur les quatre autres plis.
- **critère de décision** : différence regroupée avec S0 par bootstrap d'auteurs ; « gain confirmé » si la borne basse est > 0 et la différence ≥ δ = 2,0 ; « sans gain » si l'IC tient dans ±δ ; sinon « non résolu ».
- **prédiction** : S1 : +0,0 à +0,5 (probabilité 0,6 que la différence soit dans cet intervalle) ; S2 : −1,0 à +1,5 (0,6) ; S4 : −0,5 à +1,0 (0,6) ; aucun ne confirme un gain ≥ 2,0 (0,85).

## C. Décomposition de variance de l'encodeur (levier 11)
- **question** : quelle part de la variance de la macro-F1 vient du pli, de la graine et du reste (interaction et non-déterminisme du GPU) ?
- **variante** : macro-F1 par pli de chaque graine (5 plis × 5 graines, recette à 10 époques) ; analyse de variance à deux facteurs sans répétition ; le non-déterminisme du GPU n'est pas séparable de l'interaction sans rejeu (un seul rejeu à graine égale existe : 0,7714 contre 0,7362 au pli 0).
- **critère** : rapporter les trois composantes ; aucune décision.
- **prédiction** : la variance de pli domine l'écart-type de graine (écart-type de pli supérieur à 1,5 fois celui de graine, probabilité 0,6).

## D. Mesure par sous-ensemble d'usage (`pool`)
- **question** : la performance diffère-t-elle entre le sous-ensemble général (3 048 patients de développement) et les sous-ensembles d'usage (codage CIM-10 : 245 ; infectiologie : 110 ; oncologie, réponse au traitement : 92 ; oncologie, biomarqueurs : 91) ?
- **variante** : exactitude et macro-F1 (la macro-F1 des petits sous-ensembles est instable : exactitude avec intervalle de Wilson 95 % en principal) de l'ensemble, de l'encodeur moyenné et du TF-IDF, prédictions regroupées hors pli.
- **critère** : rapporter les écarts entre sous-ensembles avec intervalles ; un sous-ensemble dont la borne haute d'exactitude est sous la borne basse du général est « plus difficile ».
- **prédiction** : le sous-ensemble de codage CIM-10 a une exactitude supérieure au général (probabilité 0,5) ; au moins un sous-ensemble est « plus difficile » (0,55).

## Budget, jeux, périmètre
Quelques minutes de processeur, un thread, priorité basse ; développement seulement ; test scellé jamais lu ; les étiquettes ne sont pas modifiées.
