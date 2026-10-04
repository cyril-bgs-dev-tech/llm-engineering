# Tableau de preuve de la présentation (claim-gate)

Présentation : `docs/presentation/projet_llm_finetuning.html` (fichier unique, sans dépendance obligatoire ; polices Google en option avec repli système). Ouverture : double-clic, ou `D:\Projet Assistante IA\LLM_finetuning\docs\presentation\projet_llm_finetuning.html`. Navigation : flèches, espace, F pour le plein écran ; impression du navigateur = PDF, une diapositive par page.

Statuts : **prouvé** (renvoie à un run, un fichier ou une commande), **estimation** (jugement non mesuré, dit comme tel sur la diapositive).

| Diapositive | Affirmation | Preuve | Statut |
|---|---|---|---|
| 3 | 4 219 patients de travail, 633 de test, plis de 717 à 718, 17 chapitres, plus petit chapitre 31 (dév.) et 4 (test) | `results/measures/splits_summary.json`, ADR-005, ADR-006, `experiments/ERRATA-PROTOCOLE.md` | prouvé |
| 3 | 4 254 comptes rendus fictifs | parquet PARHAF, 4 254 lignes lues par `p1_04_06_tfidf.load` (avant filtre des chapitres) | prouvé |
| 4 | Protocole gelé : 9 instantanés SHA-256, δ = 2,0, K = 5, B = 90 h, N = 4, trois relectures | `experiments/INDEX.md`, `scripts/check_frozen.py`, `PROTOCOLE.md`, ADR-004, ADR-007 | prouvé |
| 5 | 1,7 % / 11,6 % / 50 % / 88 % de verdict résolu ou de gain confirmé à largeur 4 | `audit_GLM_5_3_v2.md` G6 (calcul analytique), run `power-curves-audit`, erratum section 6.3 | prouvé (approximation normale) |
| 6 | Bornes 0,025 et 0,058 ; TF-IDF 0,6844 [0,6573 ; 0,7089] ; CamemBERT-bio 0,4484 pli 0 ; écart −24,9 points | runs `p1-03-bounds`, `20261003-121942-p1-06-tfidf-chapter`, `p1-07-camembert-bio-lr1e-4`, `p1-07-camembert-minus-tfidf-fold0` | prouvé |
| 7 | Plis par auteur 0,6457 ; écart +3,87 [+1,27 ; +6,31] ; v2 +3,42 [+1,17 ; +5,78] ; trois lectures non tranchées | runs `rm-14-author-shortcut-tfidf` et `-v2`, ADR-011 | prouvé ; lectures = hypothèses, dites non tranchées |
| 8 | 245 tests, 58 runs, 12 ADR, 7/7 mutations tuées, wiki de 15 pages | `pytest --collect-only`, `ls results/runs`, `ls docs/decisions`, journal de nuit 12:30Z, `make check_wiki` | prouvé (comptes au 03/10/2026) |
| 9 | 11,5 / 19,8 / 19,7 / 26,4 Gio ; 0,54 / 0,65 / 0,87 s par exemple ; 6,6 h projetées | runs `debit-qwen3-5-4b-lora-4096`, `debit-gemma-4-e4b-lora-4096`, `debit-qwen3-5-9b-lora-4096`, `p0-08` (page wiki compatibilité) ; fiche P1-11 | prouvé ; 6,6 h = hypothèse non annoncée comme durée |
| 10 | 23 règles de nuit, journal, erreurs corrigées | `tasks/CONTRAT_NUIT.md`, `tasks/JOURNAL_NUIT_2026-10-02.md` | prouvé |
| 12 | **Notes de 0 à 10 : projet 5,0 ; SOTA open source 7,6 ; SOTA absolu 9,4** | Colonne projet : scorecard `scorecards/G-P0.md` (notes 0 à 3) et mesures du 03/10 ; colonnes SOTA : **aucune mesure** | **estimation** |

## Grille d'estimation de la diapositive 12 (jugement, à contre-expertiser, plus ou moins 1 point)

Échelle : 0 absent, 3 premiers éléments en place, 5 bonne pratique d'un dépôt de recherche, 7 niveau des meilleurs projets ouverts de même nature, 9 à 10 niveau industriel ou clinique réglementé. Le « SOTA » est le meilleur niveau connu **par composante**, pas un système unique.

| Composante | Projet | Open source | Absolu | Raison de la note du projet |
|---|---|---|---|---|
| Performance du modèle | 5 | 8 | 9 | TF-IDF 0,68 ; encodeur 0,45 sous-entraîné ; Qwen3.5-4B 0,587 et Qwen3.5-9B 0,565 sur le pli 0, sous le TF-IDF ; aucun LLM ne le bat à ce jour (P1-11 terminé, élève Qwen3.5-4B) |
| Rigueur statistique et protocole | 7 | 8 | 9 | protocole gelé et haché, test scellé, bootstrap apparié, puissance simulée ; mais une graine au développement, premier cycle non confirmatoire |
| Données et anti-fuite | 7 | 8 | 10 | contrôles de fuite et raccourci d'auteur mesuré ; mais corpus fictif, pas de données réelles |
| Fiabilité de l'incertitude | 6 | 7 | 9 | **révisée de 1 à 4 le 03/10** : calibration, conforme (LAC, APS, par classe, Wilson) et sélectif implémentés, validés sur données synthétiques (14 tests) et mesurés sur le TF-IDF avec test de décalage (run `q5-uncertainty-tfidf-chapter`) ; reste : LLM, politique d'abstention chiffrée, hors distribution, test scellé (Q5 de G-P0 = 0 avant) |
| Analyse d'erreurs et robustesse | 6 | 7 | 9 | **révisée de 3 à 4 le 03/10** : confusions, composition expliquant le creux de longueur, perturbations (−5,6 points sans accents), hors spécialité (0,52) et sous-groupes, tous sur TF-IDF ; la robustesse des LLM n'est pas mesurée |
| Reproductibilité et ingénierie | 8 | 8 | 9 | environnement verrouillé, typage strict, 245 tests, registre ; reconstruction à froid non testée |
| Efficience et déploiement | 5 | 8 | 10 | mesures de VRAM et de débit ; pas de latence p95, pas de service testé en charge (Q8, Q9 de G-P0 = 1) |
| Sûreté, conformité, honnêteté | 8 | 7 | 9 | **révisée de 7 à 8 le 03/10** : carte de modèle provisoire, gabarit de rapport, deux audits indépendants consignés (GLM v2, v3), journal des accès au test scellé ; pas encore de revue humaine externe |

Moyennes : projet 52 / 8 = 6,5 ; open source 61 / 8 = 7,6 ; absolu 75 / 8 = 9,4. Ces trois colonnes sont des jugements ; seule la colonne « projet » s'appuie sur des preuves du dépôt, et même elle reste une note d'auto-évaluation sans confirmation indépendante (aucune note 3 à G-P0).

| 14 | Qwen3.5-9B 0,565 ; Gemma-4-E4B 0,456 (1e-4) et 0,142 (1e-5) ; écarts −13,2 et +10,9 points | runs `20261003-163427-p1-11-qwen3-5-9b-lr1e-4`, `20261003-152759-p1-11-gemma-4-e4b-lr1e-4`, `20261003-174127-p1-11-gemma-4-e4b-lr1e-5` et comparaisons appariées du pli 0 | prouvé (pli 0 seulement, criblage inachevé) |

| 15 | Qwen3.5-4B 0,5867 (1e-4), 11,1 points sous le TF-IDF ; écart avec le 9B non résolu ; élève retenu | runs `20261003-194530-p1-11-qwen3-5-4b-lr1e-4`, `…-qwen4b-1e-4-minus-tfidf-fold0`, `…-qwen4b-minus-qwen9b-1e-4-fold0` ; ADR-014 | prouvé (pli 0, une graine) |
| 16 | CamemBERT-bio 6 époques 0,553, non distinct du 4B (−3,4 [−8,2 ; +2,1]) ; 128 s | runs `camembert-epoques-lr1e-4-ep6`, `camembert-ep6-minus-qwen4b-fold0`, fiche `2026-10-03-camembert-epoques-diagnostic` | prouvé (pli 0, EXPLORE) |
| 17 | Perte pondérée sur le 4B : −2,3 points [−5,3 ; +1,5], non résolu ; rejeu de même graine : 40 prédictions sur 717 différentes | runs `q19-qwen3-5-4b-lr1e-4-perte-ponderee`, `q19-weighted-minus-unweighted-4b-fold0`, `p1-26-rejeu-qwen3-5-4b-lr1e-4` | prouvé (pli 0, une graine) |
| 18 | Ensembles par moyenne de probabilités sous le TF-IDF ; test de taille Gemma-4-31B en cours | `results/measures/ensemble_fold0.json` ; fiche `2026-10-04-test-de-taille-gemma-4-31b` | prouvé pour les ensembles ; test de taille : en cours, aucun résultat |
| 19 | 290 tests, 89 runs, 14 ADR, wiki de 18 pages | `pytest --collect-only`, `ls results/runs`, `docs/decisions`, index du wiki | prouvé (compté le 04/10) |

**Révision du 04/10 à 02h30Z (estimations, ±1)** : Performance 3 → 4 (meilleure recette TF-IDF 0,72, encodeur mûr 0,73 ± 0,026 sur cinq graines, mais aucun verdict confirmatoire et le LoRA mûr n'est pas encore mesuré) ; Fiabilité de l'incertitude 4 → 5 (mesurée sur trois familles de modèles, étalonnage par plis d'auteurs, table d'abstention) ; Analyse d'erreurs et robustesse 4 → 5 (plafond d'erreur par accord de modèles, composition des petits chapitres, leave-one-author-out en cours) ; Efficience et déploiement 3 → 5 (service TF-IDF mesuré : 20 Mo, p50 1,9 ms, 568 patients par seconde ; encodeur 190 ms ; quantification INT8 naïve testée et rejetée ; coût par recette connu). Aucune de ces notes n'est une scorecard : les preuves sont celles de RESULTATS.md.

| 20 | Encodeur 10 époques, cinq graines : 0,7293 ± 0,0256 ; règle de puissance 12,2 points contre 4,0 ; TF-IDF caractères et poids équilibrés 0,7202 | runs `camembert-recette-lr1e-4-ep10`, `camembert-graine-ep10-s1` à `s4`, `rm-17-power-rule-encodeur-ep10`, `tfidf-variant-char-balanced` | prouvé (pli 0 pour l'encodeur, EXPLORE) |
| 21 | Service TF-IDF : 20,4 Mo, p50 1,9 ms, p95 4,0 ms, 568 patients/s | run `bench-serving-tfidf-charbal-v1` | prouvé (CPU, 200 patients du développement) |
| 22 | Qwen3.5-4B LoRA à 10 époques : 0,7795 (+19,3 sur 2 époques) ; +6,4 [+2,0 ; +11,4] contre le meilleur TF-IDF ; +4,9 [−0,35 ; +10,5] contre l'encodeur moyenné | runs `llm-mur2-qwen3-5-4b-ep10-lr1e-4`, `llm-mur2-minus-4b-2ep-fold0`, `llm10-et-ensembles-minus-tfidf-variant-char-balanced` | prouvé (pli 0, une graine, EXPLORE) |
| 23 | LoRA mûr au pli 1 : 0,7415 ; +5,3 [+0,75 ; +9,95] contre le TF-IDF ; −1,1 [−6,0 ; +4,0] contre l'encodeur moyenné | runs `llm-mur-pli1-qwen3-5-4b-ep10-lr1e-4`, `pli1-llm10-et-ensembles-minus-pli1-tfidf-charbal` | prouvé (pli 1, une graine, EXPLORE) |

**Révision du 04/10 à 11h30Z (estimations, ±1)** : Performance 4 → 5 (LoRA mûr 0,7795 et 0,7415 sur deux plis, encodeur moyenné 0,73 et 0,75, tous deux au-dessus du meilleur TF-IDF de 4 à 6 points ; toujours EXPLORE, une graine pour le LoRA, aucun verdict confirmatoire, pas de comparaison à un état de l'art externe) ; Fiabilité de l'incertitude 5 → 6 (LoRA mûr : ECE 0,028 et 0,034 après température, 1,15 classe par ensemble, 0,96 d'exactitude à 70 % de couverture, sur deux plis ; réserves : couverture par famille hétérogène, un modèle à une graine) ; Analyse d'erreurs et robustesse 5 → 6 (LoRA mûr insensible aux trois perturbations testées, plafond d'erreur, leave-one-author-out, discrétisation). Rigueur, données, reproductibilité, efficience et honnêteté inchangées.

| 24 | Robustesse du LoRA mûr : accents −0,5, fautes +1,6, casse −1,3 (bruit de mesure) ; TF-IDF à mots −5,6 sans accents ; TF-IDF à caractères insensible (+1,0 ; ablations −0,1 à −0,6) | run `robustness-llm-mur2-qwen3-5-4b-ep10-lr1e-4`, `results/measures/glm_v3_perturb_tfidf.json` | prouvé (pli 0, une graine) |
| 25 | Pli 2 : encodeur moyenné +1,2 (non résolu), ensemble encodeur + TF-IDF +4,3 [+1,2 ; +7,5] ; sur trois plis l'ensemble +4,5, +6,2, +4,3 | runs `camembert-pli2-ep10-s0` à `s4`, `pli2-encodeur-minus-tfidf-charbal` | prouvé (EXPLORE, trois plis) |

**Révision du 04/10 à 12h30Z (estimations, ±1)** : Données et anti-fuite 6 → 7 (fiche de données `docs/FICHE_DE_DONNEES_PARHAF.md`, leave-one-author-out, partitions répétées, débiaisage par auteur testé et fermé, audit des erreurs confiantes) ; Reproductibilité et ingénierie 7 → 8 (tableaux regénérés depuis le registre, contrôle automatique des références de runs branché à `make check`, budget en contrôle, 300 tests). Rigueur inchangée à 7 : le protocole v2 est un brouillon non accepté et l'aperçu de puissance (4,29 points à 95 % sur trois plis) n'est pas une règle appliquée.
| 26 | Règle de puissance v2 (aperçu) : largeur 4,29 points à 95 % pour « ensemble encodeur + TF-IDF moins TF-IDF » sur trois plis (2 152 prédictions) ; 316 tests, 155 runs, 15 ADR, wiki de 19 pages | run `v2-power-preview-3-plis`, `pytest --collect-only`, `ls results/runs`, `docs/decisions`, index du wiki | prouvé (EXPLORE ; comptes du 04/10) |
| 27 | LoRA mûr, graine 1001 au pli 0 : 0,7893 ; écart avec la graine 1000 +1,0 [−3,1 ; +5,0] ; contre l'encodeur moyenné +5,75 [+1,1 ; +10,6] | runs `llm-mur-s1001-qwen3-5-4b-ep10-lr1e-4`, `llm-s1001-minus-s1000-fold0`, `llm-graine1001-et-moyenne-minus-encodeur` | prouvé (EXPLORE, un pli) |
