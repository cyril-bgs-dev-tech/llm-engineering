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

## État de la file au 04/10/2026 à 17h10Z (remplace les listes ci-dessus quand elles divergent)
**Chaîne GPU détachée, dans l'ordre** (chaque lot attend le TERMINE du précédent ; journaux dans `scratchpad/p1_11`) :
1. `run_llm_plis_2_3_4.sh` (RM-28, LoRA mûr plis 2 à 4, environ 10,5 h, début 16h01Z) ; fin du pli 2 vers 17h35Z, pli 3 vers 21h05Z, pli 4 vers 00h35Z ; TERMINE20.
2. `run_ancrage_et_service.sh` (RM-34 service du LoRA fusionné, RM-30 zéro-shot 4B et 9B) ; TERMINE22.
3. `run_encoder_gpu.sh` (RM-34 service de l'encodeur fp32 et bf16) ; TERMINE23.
4. `run_distillation_encodeur.sh` (RM-32, 30 runs, 2,5 h) ; TERMINE24.

**À consigner quand chaque lot finit** : pli du LoRA terminé (q5_uncertainty, compare_probs contre TF-IDF et encodeur, RESULTATS) ; zéro-shot (compare_probs contre le LoRA du pli 0) ; services (tableau de coût par 1 000 patients, carte de modèle) ; distillation (pooled_interval contre l'encodeur non distillé, verdict en trois valeurs).

**Sans GPU, faisable à tout moment** : cascade à seuil choisi sur un pli et rapportée sur les autres, dès que le LoRA a cinq plis (RM-40) ; conforme par famille et abstention du LoRA aux cinq plis ; ensemble LoRA + encodeur + TF-IDF aux cinq plis ; mise à jour de la carte de modèle, du rapport, du protocole v2, de la présentation, de la mémoire ; relectures (`code-reviewer`, `test-engineer`) du code ajouté ce jour (distill, zeroshot, servicecost, lot.sh, scripts de banc).

**Après la chaîne, sur décision de l'assistante** : 9B mûr (RM-31, 5 h), seconde graine du LoRA aux plis 1 à 4 si la variance l'exige, adoption propre de fla dans pyproject (GPU libre), quantification statique de l'encodeur (RM-38).

**Réservé à Cyril** : acceptation du protocole v2 (RM-37) ; ouverture du test scellé (RM-20) ; push ; envoi du brief GLM v5 ; location de GPU et API payante.
