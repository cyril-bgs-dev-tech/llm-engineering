# Fiche préenregistrée : diagnostic de sous-entraînement de CamemBERT-bio (audit GLM, C1-A6/A7, EXPLORE)

- **question** : le déficit de CamemBERT-bio contre le TF-IDF (24,9 points au pli 0) vient-il du sous-entraînement à 2 époques (perte encore en baisse : 1,154 à 1e-4 après 180 pas, monotone avec le taux : 1e-5 0,067, 2e-5 0,279, 5e-5 0,427, 1e-4 0,448) ?
- **référence** : run `p1-07-camembert-bio-lr1e-4` (macro-F1 0,4484, 2 époques, 42,9 s).
- **variante** : seul changement : 4 puis 6 époques (taux 1e-4, graine 1000, pli 0, 508 tokens, lot effectif 32, micro-lot 16, plein). **Écart assumé et borné** : l'ADR-010 fixe 2 époques pour les recettes confirmatoires ; ces runs sont un diagnostic de la référence encodeur, enregistrés EXPLORE, sans rôle dans une famille confirmatoire, et la grille de taux reste celle de quatre valeurs.
- **jeux et découpage** : développement, pli 0 ; test scellé jamais lu.
- **métrique principale** : macro-F1 pli 0 ; **secondaires** : exactitude, log loss, ECE, perte finale.
- **critère de décision** : « sous-entraînement confirmé » si la macro-F1 à 4 ou 6 époques dépasse celle de 2 époques de plus de 2,0 points (δ) ; sinon « pas de gain d'époques ». Aucun verdict de gain contre le TF-IDF, un pli, une graine.
- **budget** : deux runs d'environ 90 s et 130 s de GPU, hors lot de nuit, après la fin de P1-11 (ne pas perturber un run en cours).
- **prédiction** : macro-F1 à 4 époques entre 0,50 et 0,62 (probabilité 0,6) ; l'écart avec le TF-IDF reste supérieur à 8 points à 6 époques (probabilité 0,7).
