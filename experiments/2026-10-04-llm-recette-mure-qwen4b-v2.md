# Fiche préenregistrée v2 : Qwen3.5-4B à 10 époques, relance en exclusivité du GPU et du processeur

Cite `experiments/2026-10-04-llm-recette-mure-qwen4b.md` sans la modifier. Le premier run (`20261004-030327-llm-mur-qwen3-5-4b-ep10-lr1e-4`) a été interrompu par la règle d'arrêt anticipé (durée projetée 23 383 s au-delà de la limite de 22 700 s) après 43 minutes ; il a partagé le GPU avec des runs d'encodeur et le processeur avec des calculs lourds (leave-one-author-out, partitions répétées), alors que l'estimation de 15 100 s suppose le GPU seul (le run à 2 époques, seul sur la carte, a pris 3 024 s : 1 512 s par époque).

- **question, référence, variante, jeux, métriques, critère de décision, règle d'arrêt de la lecture** : inchangés (voir la fiche citée).
- **changement** : exécution **sans autre processus GPU ni calcul CPU lourd pendant le run** (les runs d'encodeur du pli 1 sont terminés avant le lancement) ; mêmes paramètres, limite d'arrêt anticipé inchangée (22 700 s). Si la règle d'arrêt se déclenche encore, le run n'est pas relancé une troisième fois : son échec est la mesure (le LoRA à 10 époques ne tient pas dans 6 h de projection sur cette carte).
- **budget** : environ 15 100 s (4,2 h) sur GPU libre.
- **prédiction** : l'arrêt anticipé ne se déclenche pas sur GPU libre (probabilité 0,8) ; les autres prédictions de la fiche citée sont inchangées.
