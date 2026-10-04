# Fiche préenregistrée : confirmation de l'ensemble encodeur + TF-IDF sur un second pli (EXPLORE)

Écrite avant tout run de ce pli. Suite de l'ensemble encodeur (5 graines) + TF-IDF caractères et poids équilibrés observé au pli 0 (+4,54 points [+1,43 ; +8,00], poids 0,5 essayé en deuxième parmi trois).

- **question** : l'avantage de l'ensemble sur la meilleure référence bon marché se reproduit-il sur un pli différent (pli 1, 718 patients) ?
- **référence** : TF-IDF caractères 3 à 5 et poids équilibrés (`tfidf-variant-char-balanced`, prédictions hors pli du pli 1).
- **variante** : ensemble 0,5 / 0,5 de la moyenne des probabilités de 5 encodeurs CamemBERT-bio (10 époques, 1e-4, 508 tokens tête et fin, graines 1000 à 1004, entraînés sur les plis 0, 2, 3, 4) et des probabilités hors pli du TF-IDF. **Le poids 0,5 est fixé ici, avant le run** ; aucun réglage n'est fait sur le pli 1.
- **jeux et découpage** : développement, pli 1 comme validation ; test scellé jamais lu.
- **métrique principale** : macro-F1 du pli 1 ; secondaires : exactitude, F1 des cinq petits chapitres.
- **critère de décision** : différence appariée (`scripts/compare_probs.py`, IC 95 %) : « confirmé » si borne basse > 0 ; « non reproduit » si l'IC contient 0 ou est négatif ; avec les deux plis, une moyenne des deux écarts est rapportée ; EXPLORE.
- **budget** : cinq runs d'encodeur d'environ 4 minutes (20 minutes de GPU, en parallèle du Qwen3.5-4B à 10 époques) ; aucune dépense de CPU notable.
- **prédiction** : l'ensemble dépasse le TF-IDF au pli 1 (probabilité 0,8) ; IC entièrement positif (probabilité 0,5) ; écart au pli 1 inférieur à celui du pli 0 (probabilité 0,65, régression vers la moyenne) ; l'ensemble dépasse l'encodeur seul au pli 1 (probabilité 0,75).
