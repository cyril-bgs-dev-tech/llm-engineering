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
1. `run_llm_plis_2_3_4.sh` (RM-28, LoRA mûr plis 2 à 4, environ 10,5 h, début 16h01Z) ; pli 2 fini à 19h47Z (consigné), pli 3 fini à 23h24Z, pli 4 fini à 02h58Z (tous consignés) ; domino 0 terminé (un pli dure environ 3 h 45 avec le chargement et l'évaluation) ; TERMINE20.
2. `run_ancrage_et_service.sh` (RM-34 service du LoRA fusionné, RM-30 zéro-shot 4B et 9B) ; TERMINE22.
3. `run_encoder_gpu.sh` (RM-34 service de l'encodeur fp32 et bf16) ; TERMINE23.
4. `run_distillation_encodeur.sh` (RM-32, 30 runs, 2,5 h) ; TERMINE24.

**Post-traitement automatique** : `post_plis_3_et_4.sh` (fait) ; `post_lora_plis.sh` (détaché, journal `post_lora.log`, TERMINE25) : à chaque pli du LoRA, q5_uncertainty et comparaisons contre TF-IDF et encodeur ; à la fin, fichier regroupé `cinq-plis-llm-mur`, `pooled_compare.py` contre TF-IDF, encodeur et ensemble, q5, conforme par famille et abstention à cinq plis. Il ne reste qu'à lire les sorties et consigner dans RESULTATS.

**Cascade (RM-40)** : fiche hachée `2026-10-04-cascade-cinq-plis` ; quand `post_lora_plis.sh` a écrit TERMINE25 : `cascade_cv.py cinq-plis-ensemble-encodeur5.probs.npz cinq-plis-llm-mur.probs.npz cascade-cinq-plis-encodeur-lora --register`, puis la variante TF-IDF (`tfidf-variant-char-balanced.probs.npz`, slug `cascade-cinq-plis-tfidf-lora`) ; refaire le modèle de latence avec la mesure de l'encodeur sur GPU.

**À consigner quand chaque lot finit** : pli du LoRA terminé (q5_uncertainty, compare_probs contre TF-IDF et encodeur, RESULTATS) ; zéro-shot (compare_probs contre le LoRA du pli 0) ; services (tableau de coût par 1 000 patients, carte de modèle) ; distillation (pooled_interval contre l'encodeur non distillé, verdict en trois valeurs).

**Sans GPU, faisable à tout moment** : cascade à seuil choisi sur un pli et rapportée sur les autres, dès que le LoRA a cinq plis (RM-40) ; conforme par famille et abstention du LoRA aux cinq plis ; ensemble LoRA + encodeur + TF-IDF aux cinq plis ; mise à jour de la carte de modèle, du rapport, du protocole v2, de la présentation, de la mémoire ; relectures (`code-reviewer`, `test-engineer`) du code ajouté ce jour (distill, zeroshot, servicecost, lot.sh, scripts de banc).

**Après la chaîne, sur décision de l'assistante** : 9B mûr (RM-31, 5 h), seconde graine du LoRA aux plis 1 à 4 si la variance l'exige, adoption propre de fla dans pyproject (GPU libre), quantification statique de l'encodeur (RM-38).

**Efficience et déploiement, tâches ajoutées le 04/10 au soir (voir roadmap §7)** : RM-46 (TF-IDF souple, CPU, fiche hachée, en cours avec le professeur ensemble, puis bras LoRA quand `cinq-plis-llm-mur` existe) ; RM-42 (module d'énergie et de coût au registre : écrire dans de nouveaux fichiers, brancher aux scripts après la fin du lot LoRA) ; après TERMINE24, GPU libre : RM-41 (débit d'entraînement : fiche d'équivalence d'abord, sur le pli 0, encodeur bf16 contre fp32 puis LoRA sans checkpointing en 100 pas), RM-45 (encodeur élagué), RM-47 (contexte et regroupement par longueur) ; sans GPU après `cascade_cv` : RM-43 (routage conforme), RM-44 (ONNX et INT8 statique, vérifier d'abord que `onnxruntime` s'installe sans casser le verrou) ; en dernier RM-48 (fiche de déploiement) quand les services sont mesurés.

**Cahiers GLM** : `docs/BRIEF_GLM_v6_audit_30_leviers.md` (30 leviers de performance, prêt, non envoyé) et `docs/BRIEF_GLM_v5_audit_second_cycle.md` (second cycle, non envoyé) ; les mettre à jour avec les plis 3 et 4 du LoRA et la distillation avant tout envoi.

**Chaîne de dominos (roadmap §4.1)** : ordre de travail après la chaîne GPU de nuit : (1) lire les sorties de `post_lora_plis.sh` et consigner ; (2) RM-41 (équivalence d'entraînement) puis les décisions de bifurcation (a) et (b) de la section 6 ; (3) fenêtre de décision synthétique et audit d'étiquettes (P2-10, P2-06) avant RM-50 ; (4) préparer, sans l'exécuter, la fiche de gel RM-50 et la prédiction chiffrée du test scellé (hachée seulement après acceptation du protocole v2 par Cyril) ; (5) rien d'autre n'est lancé entre RM-50 et RM-20. Chaque réveil du surveilleur note le domino en cours.

**Audit GLM v6 (triage fait)** : suite immédiate sans GPU : audit des erreurs confiantes (P2-06, gabarit à trois verdicts : étiquette contestable, rivale défendable, correcte ; agrégats seulement dans les sorties ; jamais d'étiquette de test modifiée) ; fiche de la recette d'encodeur v2 (RM-55) et des encodeurs alternatifs (RM-53, licence d'abord) à écrire pour la fenêtre GPU libre ; RM-54 (représentations gelées) idem.

**Post-traitement des dominos (CPU, détaché)** : `post_dominos.sh` (attend TERMINE25 ; sorties `post_dominos.out`, TERMINE27) : aperçu de la règle de sélection du système final (`final_selection_preview.py`, module `llmft.selection`), cascade validée hors pli encodeur puis LoRA et TF-IDF puis LoRA (`cascade_cv.py`, fiche `cascade-cinq-plis`) ; à lire et consigner, puis appliquer les règles de bifurcation (b) de la section 6 de la feuille de route.

**Chaîne GPU étendue (05/10)** : après TERMINE24 : `run_encodeur_v2.sh` (fiche `2026-10-05-encodeur-recette-v2`, RM-41 encodeur et RM-55, 60 runs, environ 4 h ; TERMINE26 ; journal `encodeur_v2.log`). Code : `llmft.train_v2`, `scripts/p1_encoder_v2.py`. À consigner à la fin : un tableau par facteur (macro-F1 regroupée de la moyenne des trois graines, différence avec la référence par blocs d'auteurs, vitesse et énergie pour bf16).

**Reprises de mesures de service (05/10)** : `run_service_lora_reprise.sh` (attend TERMINE26 ; banc du LoRA fusionné après correction du jeton de remplissage ; TERMINE28) puis `run_encodeur_gpu_reprise.sh` (attend TERMINE28 ; énergie de l'encodeur sur 15 secondes de charge, `llmft.energy.measure_repeated` ; TERMINE29). Les latences de l'encodeur sur GPU (6,0 ms fp32, 4,5 ms bf16) sont consignées ; l'énergie du premier banc est non fiable.

**Distillation imbriquée (RM-56, 05/10)** : `run_distillation_imbriquee.sh` (attend TERMINE29 ; fiche `2026-10-05-distillation-imbriquee` ; 40 encodeurs, 20 TF-IDF, 15 élèves, environ 3,5 h ; TERMINE31 ; analyse automatique `post_distillation_imbriquee.out`). À consigner : les deux différences par blocs d'auteurs et le verdict en quatre valeurs ; si le gain est préservé, l'élève distillé de l'ensemble devient candidat C2 du gel (RM-50).

**Réservé à Cyril** : acceptation du protocole v2 (RM-37) ; ouverture du test scellé (RM-20) ; push ; envoi du brief GLM v5 ; location de GPU et API payante.
