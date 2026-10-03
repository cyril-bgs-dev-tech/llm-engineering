# Fiche préenregistrée : variance entre graines du Qwen3.5-4B réglé (P1-19)

Suite d'ADR-014 et de la fiche P1-13. Entrée de la règle de puissance RM-17 (PROTOCOLE.md 6.3).

- **question** : quelle est la variance de la macro-F1 du pli 0 entre cinq graines de la configuration réglée du Qwen3.5-4B ? Quelle largeur moyenne d'IC à 98,33 % donne la règle de puissance sur les paires de graines ?
- **référence** : run `20261003-194530-p1-11-qwen3-5-4b-lr1e-4` (graine 1000, taux 1e-4, plus haute macro-F1 de la grille mesurée, au bord supérieur signalé) ; il sert de graine `s_0` : configuration exactement identique à celle des quatre runs ci-dessous.
- **variante** : seule la graine change : 1001, 1002, 1003, 1004 (`1000 + k`, protocole 6.4), taux 1e-4, 2 époques, pli 0.
- **jeux et découpage** : développement, pli 0 ; prédictions par patient enregistrées avec empreinte (`predictions_sha256`) ; test scellé jamais lu.
- **métrique principale** : macro-F1 du pli 0 par graine et écart-type entre graines. **Secondaires** : exactitude, log loss, durée.
- **critère de décision** : règle RM-17 écrite dans PROTOCOLE.md 6.3, appliquée sans reformulation par `scripts/rm17_power_rule.py` (R = 10 000, graine de bootstrap 20261002, seuil 4,0 points) ; une graine divergente n'est pas remplacée (6.4) et la présentation devient « non combiné » pour elle.
- **budget** : quatre runs d'environ 3 000 s (≈ 3,4 h), `--limit-seconds 4650`.
- **prédiction** : écart-type de la macro-F1 entre graines compris entre 0,8 et 3,0 points (probabilité 0,7) ; largeur moyenne de la règle de puissance supérieure à 4,0 points, donc règle échouée (probabilité 0,85) ; aucune graine ne diverge (probabilité 0,95).
