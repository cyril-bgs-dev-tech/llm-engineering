# Fiche préenregistrée : variantes de recette du TF-IDF (même effort de recherche que les LLM, EXPLORE)

Cite `experiments/2026-10-03-p1-04-06-tfidf.md` et `…-tfidf-v2-grille-etendue.md` sans les modifier. Raison : le TF-IDF de référence n'a eu qu'une seule recette ; les LLM ont eu une grille de taux, un diagnostic d'époques et une perte pondérée. Un budget de réglage inégal fausse la comparaison.

- **question** : le poids de classe équilibré et/ou des n-grammes de caractères améliorent-ils la macro-F1 du TF-IDF sur les cinq plis ?
- **référence** : run `20261003-121942-p1-06-tfidf-chapter` (0,6844 ; IC 95 % [0,6573 ; 0,7089]) ; probabilités `results/predictions/p1-06-tfidf-chapter.probs.npz`.
- **variantes** (trois, chacune un seul ou deux changements) : (a) `class_weight="balanced"` ; (b) analyseur `char_wb`, n-grammes (3, 5) ; (c) les deux. Grille de C réduite à {10, 100, 1 000}, sélection sur le pli suivant comme la référence (égalité : C le plus bas).
- **jeux et découpage** : développement, cinq plis par patient, prédictions hors pli regroupées ; test scellé jamais lu.
- **métrique principale** : macro-F1 regroupée (17 chapitres) et IC 95 % ; **secondaires** : exactitude, log loss, ECE, log loss équilibrée.
- **critère de décision** : différence appariée (bootstrap stratifié, mêmes patients) avec la référence : « amélioration » si borne basse > 0 et gain ≥ δ = 2,0 points ; « absence d'amélioration » si borne haute < δ ; sinon « non résolu ». **EXPLORE** : la référence confirmatoire (v1) ne change pas ; une variante retenue ne le devient que par une nouvelle version du protocole et une ADR. Comparaisons multiples (trois variantes) : correction de Holm annoncée, intervalles à 95 % non ajustés rapportés comme tels.
- **budget** : CPU seulement, au plus 3 h ; aucun GPU.
- **prédiction** : (a) gain de macro-F1 entre 0 et 3 points (probabilité 0,5) ; (b) gain inférieur à 1 point ou perte (probabilité 0,6) ; au moins une variante améliore la référence de plus de δ avec borne basse positive (probabilité 0,2).
