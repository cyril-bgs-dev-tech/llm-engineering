# Fiche préenregistrée : cascade par seuil de confiance validée hors pli, cinq plis (RM-40, EXPLORE)

Écrite avant que les prédictions du LoRA des plis 2 à 4 existent. Suite de l'aperçu `cascade-eval` (plis 0 et 1, seuil non validé).

- **question** : une cascade encodeur moyenné (cinq graines) puis LoRA mûr, à seuil de confiance choisi **sans voir le pli évalué**, garde-t-elle la macro-F1 du LoRA seul à 1 point près tout en évitant une part importante des appels au LoRA ?
- **références** : LoRA mûr seul (une graine par pli) ; encodeur moyenné seul ; meilleur TF-IDF.
- **variante** : pour chaque pli k, le seuil τ est choisi sur les quatre autres plis (prédictions regroupées) : plus petit τ de la grille {0,5 ; 0,6 ; 0,7 ; 0,8 ; 0,9 ; 0,95 ; 0,99} dont la macro-F1 de la cascade est à au plus 1,0 point de celle du LoRA seul (`llmft.cascade.choose_threshold`) ; la cascade est appliquée au pli k avec ce τ (`scripts/cascade_cv.py`). Variante secondaire : TF-IDF puis LoRA.
- **jeux et découpage** : développement, cinq plis ; test scellé jamais lu.
- **métrique principale** : macro-F1 sur 17 chapitres, prédictions regroupées de la cascade appliquée pli par pli avec son τ de validation croisée, moins celle du LoRA seul (`power_rule.pooled_interval`, IC 95 %) ; secondaires : part des cas traités par le premier modèle, latence moyenne modélisée (encodeur 5 × 191 ms sur processeur, LoRA 117 ms sur GPU, TF-IDF 1,9 ms).
- **critère de décision** : « non-infériorité » si la borne basse de l'IC de (cascade moins LoRA) est > −2,0 points (δ) ; « économie » si en plus la part des cas évités est ≥ 50 % ; sinon « non résolu » ou « échec ».
- **budget** : calcul sur processeur seul, quelques minutes.
- **prédiction** : non-infériorité atteinte (probabilité 0,7) ; part évitée entre 50 et 85 % (probabilité 0,65) ; la cascade dépasse le LoRA seul avec IC entièrement positif (probabilité 0,15).
