# File de travail de nuit (inépuisable, par ordre de priorité)

Mise à jour le 04/10/2026 (audit GLM v4 intégré ; règle de sélection : information attendue par heure, bon marché d'abord).

## Lots GPU en cours ou en file (état de 03h40Z)
1. Qwen3.5-4B à 10 époques sur GPU libre (fiche v2, journal `llm_mur2.log`, fin vers 07h45Z). **Aucun calcul CPU ou GPU lourd pendant ce run.**
2. Ensuite (dans l'ordre, un lot à la fois) : (a) si le 4B mûr rattrape l'encodeur, ajouter ses probabilités à l'ensemble et mesurer ; (b) synthétique ciblé (fiche écrite, code de lignée prêt, génération à mesurer au pré-vol) ; (c) robustesse de l'encodeur et du 4B par inférence (perturbations) ; (d) cinq encodeurs au pli 2 pour une troisième confirmation.
Terminés cette nuit : criblage, grille du 4B, encodeur (recette, fenêtres, saturation, graines, pli 1), leave-one-author-out, partitions répétées, RM-17 sur l'encodeur, service TF-IDF, INT8 (échec), rapport préliminaire.

## À consigner à la fin de chaque lot
- Résultats dans `RESULTATS.md` (avec `run_id`), comparaisons appariées (`pair_preds.py`, `compare_probs.py`), probabilités conservées, incertitude (`q5_uncertainty.py`), robustesse sur adaptateur ou poids sauvegardés.
- Règle de puissance : lancer `rm17_power_rule.py` sur les graines de l'encodeur (EXPLORE, largeur d'IC mesurée sur l'encodeur, dire que ce n'est pas la LoRA du protocole).

## Faisable sans GPU (prendre dans l'ordre)
1. Lire `loao.out` (leave-one-author-out TF-IDF) et consigner : départage de RM-14.
2. Table d'abstention par modèle (couverture, exactitude conditionnelle) et intervalle de Wilson de « la classe jamais couverte » (audit v4, E-c2, E-c3).
3. Brier des prédictions préenregistrées de l'assistant (audit v4, B-c5) : `docs/CALIBRATION_PREDICTIONS_ASSISTANT.md`.
4. ADR du second cycle (recettes mûres, budget égal par famille, 5 graines sur l'encodeur) après saturation et graines.
5. Présentation et mémoire à jour après chaque lot.
6. Étalonnage par plis d'auteurs pour l'encodeur dans le service (`serving.py` accepte un modèle de transformers ?), carte de modèle v2.
7. Rapports : gabarit rempli pour l'encodeur mûr ; claim-gate sur chaque sortie.
8. Réserves : tests de couverture par bloc CIM-10 (audit E-c1), simulation de couverture par classe sur les plis réels (E-c5).

## Idées de Cyril à instruire (04/10)
- Lire `split-check.out` (écart patient contre auteur sur partitions répétées, variance par classe) et consigner : part de l'écart due à la discrétisation des petites classes.
- Sur-échantillonnage ciblé des chapitres rares : fiche écrite et hachée (`2026-10-04-synthetique-cible-chapitres-rares`) ; code de génération et contrôle de lignée à écrire après le 4B à 10 époques (tests d'abord).

## Après libération du GPU (sans décision humaine)
- Robustesse du 4B et de l'encodeur par inférence (perturbations) ; latence de l'encodeur (p50, p95) ; export INT8 mesuré.
- Confirmer l'ensemble encodeur + TF-IDF sur un second pli (pli 1, cinq graines d'encodeur, ~25 minutes GPU, fiche à écrire d'abord) ; puis ajouter le 4B mûr à l'ensemble s'il rattrape.
- Si le 4B à 10 époques rattrape l'encodeur : une fiche de test de taille à recette mûre (coût estimé environ 20 h pour le 31B : décision de Cyril, jamais lancée seule).
