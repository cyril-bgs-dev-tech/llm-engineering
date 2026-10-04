# Fiche préenregistrée : encodeur CamemBERT-bio par fenêtres sur tout le dossier (EXPLORE)

Écrite avant tout résultat. L'encodeur ne voit aujourd'hui que 508 tokens (254 de tête, 254 de fin) alors que la médiane d'un patient est de 1 143 tokens, le 95e centile de 2 826 et 60 % dépassent 1 024 (`results/measures/token_lengths.json`, tokenizer Qwen ; l'ordre de grandeur vaut pour le tokenizer de CamemBERT).

- **question** : lire tout le dossier (fenêtres de 510 tokens, logits moyennés, jusqu'à 8 fenêtres) améliore-t-il la macro-F1 de l'encodeur à recette égale ?
- **référence** : `camembert-epoques-lr1e-4-ep6` (0,5527, pli 0, graine 1000) et, pour la variante (b), le run de la recette mûre retenu ci-dessous.
- **variantes** : (a) 6 époques, taux 1e-4, fenêtres (seul changement : la lecture de tout le dossier) ; (b) fenêtres avec la recette (taux, époques) qui a la plus haute macro-F1 parmi les trois runs de `2026-10-04-encodeur-recette-mure` (égalité : le moins d'époques). Micro-lot de 2 patients, lot effectif 32.
- **jeux et découpage** : développement, pli 0, graine 1000 ; test scellé jamais lu.
- **métrique principale** : macro-F1 du pli 0 ; secondaires : exactitude, log loss, ECE, durée, pic de mémoire.
- **critère de décision** : différence appariée (`scripts/pair_preds.py`) avec la référence : « amélioration suggérée » si Δ ≥ +2,0 points et borne basse > 0 ; sinon « non résolu » ou « dégradation » ; EXPLORE, aucun verdict contre le TF-IDF.
- **budget** : (a) environ 7 minutes de GPU, (b) environ 12 minutes, au plus 30 minutes avec arrêt à 1,5 fois.
- **prédiction** : (a) gain entre +1 et +8 points (probabilité 0,55) ; (a) dépasse la référence (probabilité 0,75) ; (b) dépasse 0,62 (probabilité 0,4) ; (b) atteint ou dépasse le TF-IDF du pli 0, 0,6971 (probabilité 0,15).
