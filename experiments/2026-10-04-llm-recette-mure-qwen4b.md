# Fiche préenregistrée : le Qwen3.5-4B à recette mûre (10 époques), remplace le test de taille du 31B à 2 époques

Cite `experiments/2026-10-04-test-de-taille-gemma-4-31b.md` (non exécutée jusqu'au bout : arrêt anticipé à 19 pas, durée projetée 21 702 s au-delà de 1,5 fois l'estimation, puis annulée) et `2026-10-04-encodeur-recette-mure.md`. Raison du changement : à 10 époques, CamemBERT-bio passe de 0,553 à 0,771 de macro-F1, au-dessus du TF-IDF (0,6971 au pli 0) ; tester la taille avec 2 époques ne répondrait pas à la question.

- **question** : le Qwen3.5-4B, avec la même durée d'entraînement que l'encodeur mûr (10 époques), rattrape-t-il ou dépasse-t-il CamemBERT-bio à 10 époques (0,7714) et le TF-IDF (0,6971) au pli 0 ?
- **référence** : `20261003-194530-p1-11-qwen3-5-4b-lr1e-4` (2 époques, 0,5867) ; `camembert-recette-lr1e-4-ep10` (0,7714) ; TF-IDF pli 0 (0,6971).
- **variante** : seul le nombre d'époques change (10 au lieu de 2), taux 1e-4, LoRA r = 16 alpha 32, 4 096 tokens, lot effectif 32, micro-lot 1, graine 1000, pli 0 (cosinus recalculé sur la durée totale). Probabilités et adaptateur conservés.
- **jeux et découpage** : développement, pli 0 ; test scellé jamais lu.
- **métrique principale** : macro-F1 du pli 0 ; secondaires : exactitude, F1 par chapitre, log loss, ECE, durée, pic de mémoire.
- **critère de décision** : différences appariées (`scripts/pair_preds.py`, IC 95 %) contre CamemBERT à 10 époques et contre le TF-IDF : « rattrape » si l'IC contient 0 ; « dépasse » si borne basse > 0 ; « reste sous » si borne haute < 0 ; EXPLORE.
- **règle d'arrêt, écrite d'avance** : si le 4B à 10 époques reste résolument sous CamemBERT à 10 époques, on n'explore plus de LLM plus gros à durée mûre dans ce cycle (31B inclus) ; s'il rattrape ou dépasse, un test de taille à recette mûre devient justifié (décision de Cyril, coût estimé environ 20 h pour le 31B).
- **budget** : environ 15 100 s (5 fois les 3 024 s du run à 2 époques), `--limit-seconds 22700` (1,5 fois), soit 4,2 h, chargement et inférence compris en plus.
- **prédiction** : macro-F1 du 4B entre 0,65 et 0,80 (probabilité 0,6) ; au moins égale à CamemBERT à 10 époques, IC contenant 0 ou positif (probabilité 0,35) ; supérieure au TF-IDF du pli 0 avec IC entièrement positif (probabilité 0,45) ; au moins un des chapitres XII, XXI, XXII sort de zéro (probabilité 0,85).
