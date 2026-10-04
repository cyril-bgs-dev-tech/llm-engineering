# Fiche préenregistrée : recette mûre de l'encodeur CamemBERT-bio (EXPLORE ; fait suite à `2026-10-03-camembert-epoques-diagnostic`)

Écrite avant tout résultat de ces runs. Raison : à 6 époques la macro-F1 monte encore (0,448, 0,526, 0,553) et le meilleur taux est au bord de la grille ; la référence encodeur n'a pas eu l'effort de réglage donné au TF-IDF (variante à 0,7202).

- **question** : où la macro-F1 de CamemBERT-bio sature-t-elle quand on étend la durée et le taux au-delà de la grille gelée ?
- **référence** : runs `camembert-epoques-lr1e-4-ep6` (0,5527) et `p1-07-camembert-bio-lr1e-4` (0,4484, recette gelée).
- **variantes** (trois runs, pli 0, graine 1000, 508 tokens tête et fin, lot effectif 32) : (a) 1e-4, 10 époques ; (b) 2e-4, 6 époques ; (c) 2e-4, 10 époques. Aucun autre changement.
- **jeux et découpage** : développement, pli 0 ; test scellé jamais lu.
- **métrique principale** : macro-F1 du pli 0 ; secondaires : exactitude, log loss, ECE, perte finale.
- **critère de décision** : meilleure macro-F1 des trois contre le run à 6 époques (différence appariée, `scripts/pair_preds.py`) ; EXPLORE, aucun verdict contre le TF-IDF ; le taux 2e-4 sort de la grille gelée du protocole (écart assumé, aucun statut confirmatoire).
- **budget** : environ 3 à 5 minutes de GPU par run, 13 minutes au total.
- **prédiction** : au moins un des trois dépasse 0,60 (probabilité 0,5) ; aucun ne dépasse le TF-IDF du pli 0 (0,6971) (probabilité 0,75) ; (a) meilleure que 6 époques à 1e-4 (probabilité 0,65).
