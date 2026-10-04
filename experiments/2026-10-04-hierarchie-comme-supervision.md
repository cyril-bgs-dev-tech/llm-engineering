# Fiche préenregistrée : hiérarchie CIM-10 comme supervision pour le TF-IDF (EXPLORE)

Écrite avant la lecture du moindre résultat de cette piste (les deux runs viennent d'être lancés).

- **question** : entraîner le TF-IDF sur les blocs CIM-10 (cibles plus fines, plus nombreuses) puis agréger les probabilités par chapitre améliore-t-il la macro-F1 du chapitre ?
- **référence** : TF-IDF chapitre, 5 plis, 0,6844 [0,6573 ; 0,7089] (`20261003-121942-p1-06-tfidf-chapter`), et la meilleure variante de recette si elle est connue.
- **variante** : seule la cible d'entraînement change (bloc le plus fin du ClaML au lieu du chapitre) ; configuration fixe C = 100, n-grammes (1, 2), avec ou sans poids de classe équilibrés ; agrégation = somme des probabilités des blocs d'un chapitre.
- **jeux et découpage** : développement, cinq plis par patient ; test scellé jamais lu.
- **métrique principale** : macro-F1 regroupée (17 chapitres) ; secondaires : exactitude, log loss.
- **critère de décision** : différence appariée (`scripts/compare_probs.py`, bootstrap stratifié, IC 95 %) avec la référence ; « amélioration » si borne basse > 0 et gain ≥ 2,0 points ; EXPLORE, aucune modification de la référence confirmatoire.
- **budget** : CPU, environ 15 minutes par run.
- **prédiction** : gain entre 0 et 3 points (probabilité 0,45) ; perte (probabilité 0,35) ; gain d'au moins 2 points avec borne basse positive (probabilité 0,15).
