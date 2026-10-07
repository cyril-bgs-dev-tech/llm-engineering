# Commandes du dépôt (générées le 04/10/2026 à partir des en-têtes de `scripts/`)

Toutes les mesures d'analyse portent sur le **développement** ; aucun script ne lit le test scellé en dehors de `src/llmft/sealed.py`. Lancer avec `.venv/bin/python scripts/<nom>` depuis la racine ; les lots GPU se lancent détachés (`setsid nohup`) avec `LOGDIR` défini (`scripts/run_*.sh`).

| Script | Rôle | Usage |
|---|---|---|
| `abstention_table.py` | Audit GLM v4, E-c2 : table d'abstention par modèle (pli 0) : exactitude conditionnelle à la couverture choisie, avec intervalle de Wilson 95 %, et taux de renvoi à l'huma |  |
| `bench_serving.py` | Mesure de service du bundle d'inférence sur des textes du développement (jamais le test scellé) : latence par patient (p50, p95), débit par lot, taille, mémoire. | Usage : bench_serving.py [dossier du bundle] [--register] |
| `budget_alert.py` | Heures de GPU consommées d'après le registre contre B = 90 h ; code de sortie 1 à 80 % de B (alerte du protocole). |  |
| `build_bundle.py` | Construit le service d'inférence (TF-IDF caractères et poids équilibrés) sur tout le développement ; température, quantile conforme et seuil d'abstention | Usage : build_bundle.py [dossier de sortie]   (défaut : artifacts/models/tfidf_chapter_charbal_v1) |
| `check_changed_coverage.py` | Couverture des lignes modifiées de src/ : lit le rapport JSON de pytest-cov et le diff Git, sans relancer la suite. |  |
| `check_deck_layout.py` | Contrôle de mise en page de la présentation (débordements, chevauchements, pied de page, titre orphelin) ; `make check-deck`. | Usage : check_deck_layout.py [fichier.html] [--shots DOSSIER] ; exige playwright et un navigateur (python3 système). |
| `check_frozen.py` | Vérifie que chaque instantané gelé cité par `experiments/INDEX.md` a bien l'empreinte consignée. |  |
| `check_microtasks.py` | Vérifie la cohérence de MICROTACHES.md et son accord avec PLAN_PROJET_V6.md. |  |
| `check_roadmap.py` | Vérifie roadmap_unifié.md contre MICROTACHES.md, et exporte tasks/plan.md et tasks/todo.md. |  |
| `check_rules_sync.py` | AGENTS.md (Codex) doit rester la copie de CLAUDE.md, aux chemins de dossiers d'agents près : une seule source de règles (RM-04). |  |
| `check_scorecards.py` | Vérifie chaque `scorecards/G-P<n>.md` : schéma de preuve (RM-12) et plancher de la porte lu dans PLAN_PROJET_V6.md. |  |
| `check_wiki.py` | Branche le lint mécanique du wiki sur `make check` : échec sur lien cassé, frontmatter manquant ou collision de slug. |  |
| `check_wiki_quotes.py` | Vérifie que chaque citation littérale d'une page du wiki figure mot pour mot dans les lignes citées du fichier brut. |  |
| `cold_rebuild.sh` | Reconstruction à froid (audit GLM C6-A1) : clone neuf du dépôt, environnement verrouillé, contrôles et fil synthétique. Usage : scripts/cold_rebuild.sh [dossier]   ; écri |  |
| `compare_determinism.py` | P1-26 : compare un run et son rejeu (même graine) : historiques de perte et prédictions. Usage : compare_determinism.py RUN_ID_A RUN_ID_B SLUG_PRED_A SLUG_PRED_B |  |
| `compare_probs.py` | Différence appariée de macro-F1 de plusieurs fichiers de probabilités (.probs.npz) contre une référence, sur les patients communs. | Usage : compare_probs.py REF.npz VARIANTE.npz [VARIANTE.npz ...] SLUG [--register] |
| `coverage_by_family.py` | Audit GLM v4, E-c1 (version par familles de chapitres) : couverture conforme LAC à 90 % par famille avec Wilson, TF-IDF, étalonnage croisé par plis par patient, développe | Usage : coverage_by_family.py [--register] |
| `floor_guard.py` | Garde-fou du plancher de CONSTRAINTS.md : détecte, dans le diff, les mouvements qui abaissent la barre. |  |
| `gen_task_contracts.py` | Génère `task_specs/*.yaml` (P0-36 à P0-39). Les noms de chapitres viennent du ClaML de l'ATIH, jamais d'une saisie à la main. |  |
| `glm_v3_authors.py` | Audit GLM v3, C3-A1, A2, A4 : traces d'auteur dans le texte, table auteurs par chapitre, stylométrie. Développement seulement, agrégats seulement. | Usage : glm_v3_authors.py |
| `glm_v3_coverage_sim.py` | Audit GLM v3, C4-A8 : couverture par classe attendue aux effectifs du test (aucune étiquette de test lue). |  |
| `glm_v3_cpu_measures.py` | Mesures sans GPU de l'audit GLM v3 (C2-A3, C2-A5, C5-A3) : effectifs par pli et classe, macro/pondérée/micro, destination des erreurs. |  |
| `glm_v3_families.py` | Audit GLM v3, C5-A2 : erreurs lues au niveau de familles de chapitres CIM-10 (regroupement du projet, non normatif), pli 0, développement seulement. |  |
| `glm_v3_loso_tfidf.py` | Audit GLM v3, C5-A8 : hors distribution par spécialité exclue (leave-one-specialty-out) sur le TF-IDF du chapitre, développement seulement, EXPLORE. |  |
| `glm_v3_neardup_sensitivity.py` | Audit GLM v3, C3-A3 : sensibilité du contrôle de quasi-doublons au seuil (0,6 à 0,8), sans toucher au seuil figé 0,8. Agrégats seulement. |  |
| `glm_v3_perturb_tfidf.py` | Audit GLM v3, C5-A4 : robustesse du TF-IDF aux perturbations de texte, pli 0 (entraînement sur les plis 1 à 4, configuration choisie au pli 0 par P1-06). |  |
| `glm_v3_subgroups_bayes.py` | Audit GLM v3, C8-A3 et C2-A8 : performance par sous-groupe (spécialité, longueur, volume de l'auteur) et lecture bayésienne EXPLORE de l'écart 9B contre TF-IDF. |  |
| `glm_v3_truncated.py` | Audit GLM v3, C3-A6 : patients dont le texte dépasse 4 096 tokens (troncature tête+fin des LLM), par chapitre. Agrégats seulement. |  |
| `hier_supervision_tfidf.py` | Piste « hiérarchie comme supervision » (EXPLORE) : TF-IDF entraîné sur les blocs CIM-10 (plus fins que le chapitre), probabilités agrégées par chapitre. | Usage : hier_supervision_tfidf.py {plain/balanced} [--register] |
| `loao_tfidf.py` | Audit GLM v4, F-c1 : leave-one-author-out sur le TF-IDF du chapitre (estimation « nouveaux auteurs »), développement seulement, EXPLORE. | Usage : loao_tfidf.py [--register] |
| `make_splits.py` | P0-28, P0-29, P0-33 : jeu de travail PARHAF, classes et découpages (PROTOCOLE.md sections 2 et 3). |  |
| `measure_author_shortcut.py` | P0-30 : raccourci d'auteur. Règle et seuil figés dans PROTOCOLE.md section 3 (empreinte dans experiments/INDEX.md). |  |
| `measure_token_lengths.py` | P0-21 : longueurs en tokens des documents et des patients (documents concaténés) pour chaque tokenizer candidat. |  |
| `p1_03_bounds.py` | P1-03 : bornes sans modèle (classe majoritaire, tirage uniforme, tirage selon la prévalence, prior) sur les trois tâches, par pli de développement. | Usage : p1_03_bounds.py [--register] |
| `p1_04_06_tfidf.py` | P1-04 (doctype) et P1-06 (chapitre) : TF-IDF + régression logistique hors pli, selon la fiche `experiments/2026-10-03-p1-04-06-tfidf.md`. |  |
| `p1_23_errors.py` | P1-23 : analyse d'erreurs d'un fichier de prédictions hors pli sur le chapitre (développement seulement). | Usage : p1_23_errors.py PRED.json SLUG [--register] |
| `p1_finetune.py` | Affinage d'un classifieur de chapitre CIM-10 sur le pli de développement k (P1-07 encodeur, P1-11 / P1-13 LoRA), selon une fiche préenregistrée. | Usage : p1_finetune.py MODELE --mode {lora/full} --lr LR [--fold 0] [--epochs 2] [--max-len 4096] [--rank 16] [--alpha 32] [--effective-batch 32] |
| `pair_preds.py` | Différence appariée de macro-F1 (A moins B) entre deux fichiers de prédictions hors pli sur le chapitre, sur les patients communs. | Usage : pair_preds.py A.json B.json SLUG [--register]   (fichiers de `results/predictions/`, clés `ids` et `pred`) |
| `prior_correction.py` | Audit GLM v4, A-c1 : correction de priorité à l'inférence, p' ∝ p / q^tau (q = prévalence d'entraînement des plis ≠ 0), pli 0, développement seulement. | Usage : prior_correction.py PROBS.npz [PROBS.npz ...] [--register] |
| `q5_uncertainty.py` | Q5 : fiabilité de l'incertitude d'un modèle sur le chapitre, à partir de probabilités hors pli (développement seulement ; test scellé jamais lu). | Usage : q5_uncertainty.py PROBS.npz SLUG [--shift PROBS_AUTEUR.npz] [--register] |
| `quantize_eval_encoder.py` | Efficience de l'encodeur déployable : macro-F1 du pli 0 et latence par patient en CPU, flottant 32 bits contre quantification dynamique INT8 (PyTorch, sans dépendance de  | Usage : quantize_eval_encoder.py SLUG_DU_MODELE_SAUVEGARDE [--threads 8] [--n 200] [--register]   (modèle sous artifacts/models/<slug>, développement  |
| `rm14_pair.py` | RM-14 : verdict apparié entre les plis par patient (P1-06) et les plis par auteur, selon `experiments/2026-10-03-rm-14-raccourci-tfidf.md`. |  |
| `rm17_power_rule.py` | RM-17 : règle de puissance (PROTOCOLE.md 6.3), à lancer une seule fois après P1-19 et P1-20, jamais avec une autre graine de bootstrap. | Usage : rm17_power_rule.py [--register] / --rehearsal FICHIER.json FICHIER.json FICHIER.json / --files ... |
| `run_after_p1_11.sh` | Après P1-11 (seconde passe terminée) : diagnostic d'époques de CamemBERT-bio, rejeu du 9B à 1e-4 (déterminisme P1-26 et conservation des probabilités et de l'adaptateur), |  |
| `run_after_p1_12.sh` | Après P1-12 (élève : Qwen3.5-4B, ADR-014) : attend la fin des runs en cours, puis diagnostic d'époques CamemBERT (si absent), rejeu de déterminisme du 4B, grille complète |  |
| `run_after_p1_12b.sh` | Reprise après P1-12 : relance les runs absents du registre (panique ou segfault du tokenizer Rust, codes 1, 134, 139), jusqu'à 4 essais ; ordre : rejeu P1-26 d'abord. gri |  |
| `run_deploy_encoder.sh` | Candidat de déploiement : CamemBERT-bio 10 époques 1e-4 (recette de la fiche 2026-10-04-encodeur-recette-mure, graine 1000) avec sauvegarde des poids, puis mesure INT8 en |  |
| `run_encodeur_fenetres.sh` | Encodeur par fenêtres (fiche 2026-10-04-encodeur-par-fenetres) : (a) 6 époques 1e-4 ; (b) meilleure recette de la recette mûre. Attend TERMINE9. |  |
| `run_encodeur_graines.sh` | Saturation et graines de l'encodeur (fiche 2026-10-04-encodeur-saturation-et-graines). Attend TERMINE10 (encodeur par fenêtres). |  |
| `run_encodeur_recette.sh` | Recette mûre de l'encodeur (fiche 2026-10-04-encodeur-recette-mure) : trois runs courts, essais multiples sur panne du tokenizer. |  |
| `run_ensemble_pli1.sh` | Confirmation de l'ensemble au pli 1 (fiche 2026-10-04-confirmation-ensemble-pli1) : cinq encodeurs, graines 1000 à 1004, en parallèle du LoRA (mémoire GPU suffisante). |  |
| `run_llm_mur.sh` | Qwen3.5-4B à 10 époques (fiche 2026-10-04-llm-recette-mure-qwen4b). Attend TERMINE11 (graines de l'encodeur). |  |
| `run_llm_mur2.sh` | Qwen3.5-4B à 10 époques, relance en exclusivité (fiche 2026-10-04-llm-recette-mure-qwen4b-v2). Attend TERMINE14 (runs d'encodeur du pli 1). Un seul essai : un arrêt antic |  |
| `run_p1_11.sh` | P1-11 : six runs séquentiels (fiche experiments/2026-10-03-p1-11-criblage-eleves.md). Journal par run dans $LOGDIR. Limites d'arrêt anticipé = 1,5 fois la projection de l |  |
| `run_p1_11_missing.sh` | P1-11, seconde passe : relance les runs absents du registre (segfault du tokenizer le 03/10/2026), avec le vrai code de sortie et jusqu'à 3 essais par run en cas de plant |  |
| `run_p1_19.sh` | P1-19 : quatre graines supplémentaires (1001 à 1004) du Qwen3.5-4B à 1e-4 ; la graine 1000 est le run P1-11 existant (s_0). Attend TERMINE5 de la reprise. Essais multiple |  |
| `run_preflight_31b.sh` | Pré-vol du Gemma-4-31B en QLoRA NF4 (3 pas, exemples les plus longs d'abord), après la fin de la reprise P1-12b. Essais multiples sur panne du tokenizer. |  |
| `run_test_taille_31b.sh` | Test de taille : Gemma-4-31B en QLoRA NF4, pli 0, 1e-4, 2 époques (fiche 2026-10-04-test-de-taille-gemma-4-31b). Jusqu'à 3 essais sur panne du tokenizer. |  |
| `silence_watch.sh` | Témoin d'activité (tasks/SURVEILLEUR_SILENCE.md) : écrit dans results/logs/silence.log chaque minute où le silence dépasse 300 s. Activité = dernière modification du jour |  |
| `smoke.py` | RM-09 : fil synthétique de bout en bout, sur CPU, sans donnée réelle. |  |
| `split_discretization_check.py` | Hypothèse de Cyril (04/10) : l'écart patient contre auteur vient en partie de la discrétisation des petites classes et de plis de validation inégaux. | Usage : split_discretization_check.py [--register] |
| `stress_tfidf_ab.py` | Test de charge du TF-IDF (fiches 2026-10-07-stress-tfidf-par-coeur et 2026-10-07-stress-tfidf-libre-contre-epingle) : un processus fils par essai, panne brute, empreinte du résultat. | Usage : stress_tfidf_ab.py [--tours 3 \| --libre-contre-epingle N] [--register] ; à lancer sous run_guarded.sh. |
| `tfidf_variants.py` | Variantes de recette du TF-IDF sur le chapitre (fiche 2026-10-04-tfidf-variantes-recette) : cinq plis par patient, EXPLORE. | Usage : tfidf_variants.py {balanced/char/char-balanced} [--folds author] [--register] |
