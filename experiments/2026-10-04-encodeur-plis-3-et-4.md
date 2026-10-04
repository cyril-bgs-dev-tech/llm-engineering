# Fiche préenregistrée : plis 3 et 4 de l'encodeur (complément de l'évaluation à cinq plis, EXPLORE)

Écrite avant les runs. Complète les plis 0, 1 et 2 (cinq graines chacun) pour disposer des 3 586 prédictions hors pli de l'ensemble encodeur et mesurer la règle de puissance v2 sans extrapolation.

- **question** : (a) la largeur de l'IC de « ensemble encodeur + TF-IDF moins TF-IDF » sur cinq plis passe-t-elle sous 4,0 points (95 %) ? (b) l'avantage de l'ensemble se reproduit-il aux plis 3 et 4 ?
- **référence** : TF-IDF caractères et poids équilibrés, prédictions hors pli.
- **variante** : cinq encodeurs CamemBERT-bio, 10 époques, 1e-4, 508 tokens tête et fin, graines 1000 à 1004, aux plis 3 puis 4 (entraînés sur les quatre autres plis) ; ensemble 50/50 avec le TF-IDF, poids fixé avant.
- **jeux et découpage** : développement ; test scellé jamais lu.
- **métrique principale** : macro-F1 ; secondaire : largeur de l'IC (`scripts/v2_power_preview.py`).
- **critère de décision** : (a) largeur à 95 % ≤ 4,0 : la règle v2 passe ; (b) ensemble moins TF-IDF avec borne basse > 0 par pli ; EXPLORE, aucun statut confirmatoire.
- **budget** : dix runs d'environ 5 minutes (50 minutes de GPU) après la fin du LoRA graine 1001, GPU libre.
- **prédiction** : la largeur à 95 % sur cinq plis est inférieure à 4,0 (probabilité 0,7) ; l'ensemble dépasse le TF-IDF à chacun des plis 3 et 4 (probabilité 0,85) avec IC entièrement positif aux deux (probabilité 0,35).
