# Fiche préenregistrée : troisième pli de l'encodeur et seconde graine du LoRA mûr (EXPLORE)

Écrite avant les runs. Suite des confirmations du pli 1 : l'avantage du modèle mûr sur le TF-IDF est positif aux deux plis ; la variance du LoRA entre graines n'est pas mesurée (une graine par pli).

- **question** : (a) l'encodeur moyenné sur cinq graines bat-il le meilleur TF-IDF au pli 2 ? (b) quelle est l'ampleur du changement de macro-F1 du LoRA mûr entre deux graines au pli 0 ?
- **références** : (a) TF-IDF caractères et poids équilibrés, prédictions hors pli du pli 2 ; (b) le run `llm-mur2-qwen3-5-4b-ep10-lr1e-4` (graine 1000, 0,7795).
- **variantes** : (a) cinq encodeurs CamemBERT-bio, 10 époques, 1e-4, graines 1000 à 1004, entraînés sur les plis 0, 1, 3, 4 ; (b) Qwen3.5-4B LoRA 10 époques, 1e-4, graine 1001, pli 0, mêmes paramètres.
- **jeux et découpage** : développement, plis 2 (a) et 0 (b) ; test scellé jamais lu.
- **métrique principale** : macro-F1 ; secondaires : exactitude, F1 par chapitre, incertitude.
- **critère de décision** : (a) différence appariée (`scripts/compare_probs.py`) : « confirmé » si borne basse > 0 ; (b) écart des deux graines, rapporté tel quel avec la différence appariée ; EXPLORE ; rapporter l'écart moyen sur trois plis pour (a).
- **budget** : (a) 5 runs de 4 à 5 minutes ; (b) environ 12 500 s, `--limit-seconds 18800` ; GPU libre, aucun calcul concurrent.
- **prédiction** : (a) l'encodeur moyenné dépasse le TF-IDF au pli 2 (probabilité 0,8), IC entièrement positif (probabilité 0,45) ; (b) l'écart entre les deux graines du LoRA est inférieur à 3 points de macro-F1 (probabilité 0,6) ; la graine 1001 donne moins de 0,7795 (probabilité 0,6, régression vers la moyenne).
