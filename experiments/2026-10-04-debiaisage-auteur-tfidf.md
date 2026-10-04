# Fiche préenregistrée : entraînement débiaisé par auteur du TF-IDF (EXPLORE)

Écrite avant tout résultat. Suite du leave-one-author-out (signature d'auteur d'environ 2 points) : un entraînement qui pèse moins les auteurs prolifiques réduit-il le raccourci d'auteur et améliore-t-il la généralisation à de nouveaux auteurs ?

- **question** : des poids d'exemples décroissant avec le volume de l'auteur dans l'entraînement améliorent-ils la macro-F1 sur des plis groupés par auteur, sans perdre sur les plis par patient ?
- **référence** : TF-IDF mots (1, 2), C = 100, sans poids, mêmes plis : par patient 0,636 à 0,643 ; par groupes d'auteurs 0,5894 (`split-discretization-check`).
- **variantes** : poids = (n̄ / n_auteur) normalisés à une moyenne de 1 sur l'entraînement (« inv ») ; poids = √(n̄ / n_auteur) normalisés (« invsqrt »), n_auteur calculé sur les patients de l'entraînement du pli.
- **jeux et découpage** : développement, cinq plis, `StratifiedKFold` par patient (graine 1) et `StratifiedGroupKFold` par auteur (graine 1) ; test scellé jamais lu.
- **métrique principale** : macro-F1 regroupée sur les prédictions hors pli par groupes d'auteurs ; secondaire : macro-F1 par patient, écart patient moins auteur.
- **critère de décision** : différence appariée (`scripts/compare_probs.py`) avec la référence sans poids sur les plis groupés : « amélioration » si borne basse > 0 et gain ≥ 1,0 point ; sinon « non résolu » ou « dégradation » ; EXPLORE.
- **budget** : 6 ajustements de cinq plis en CPU, un seul processus (environ 30 minutes), sans concurrence avec le run GPU en cours.
- **prédiction** : gain d'au moins 1,0 point sur plis groupés (probabilité 0,3) ; perte de plus de 1 point sur plis par patient (probabilité 0,45) ; réduction de l'écart patient moins auteur (probabilité 0,5).
