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
| 12 | **Notes de 0 à 10 : projet 4,6 ; SOTA open source 7,6 ; SOTA absolu 9,4** | Colonne projet : scorecard `scorecards/G-P0.md` (notes 0 à 3) et mesures du 03/10 ; colonnes SOTA : **aucune mesure** | **estimation** |

## Grille d'estimation de la diapositive 12 (jugement, à contre-expertiser, plus ou moins 1 point)

Échelle : 0 absent, 3 premiers éléments en place, 5 bonne pratique d'un dépôt de recherche, 7 niveau des meilleurs projets ouverts de même nature, 9 à 10 niveau industriel ou clinique réglementé. Le « SOTA » est le meilleur niveau connu **par composante**, pas un système unique.

| Composante | Projet | Open source | Absolu | Raison de la note du projet |
|---|---|---|---|---|
| Performance du modèle | 3 | 8 | 9 | TF-IDF 0,68 ; encodeur 0,45 sous-entraîné ; aucun LLM concluant à ce jour (P1-11 en cours) |
| Rigueur statistique et protocole | 7 | 8 | 9 | protocole gelé et haché, test scellé, bootstrap apparié, puissance simulée ; mais une graine au développement, premier cycle non confirmatoire |
| Données et anti-fuite | 6 | 8 | 10 | contrôles de fuite et raccourci d'auteur mesuré ; mais corpus fictif, pas de données réelles |
| Fiabilité de l'incertitude | 1 | 7 | 9 | calibration et prédiction conforme non encore faites (Q5 de G-P0 = 0) |
| Analyse d'erreurs et robustesse | 3 | 7 | 9 | analyse par classe, spécialité et longueur du TF-IDF seulement ; pas de perturbation (Q4 de G-P0 = 0 puis partiel) |
| Reproductibilité et ingénierie | 7 | 8 | 9 | environnement verrouillé, typage strict, 245 tests, registre ; reconstruction à froid non testée |
| Efficience et déploiement | 3 | 8 | 10 | mesures de VRAM et de débit ; pas de latence p95, pas de service testé en charge (Q8, Q9 de G-P0 = 1) |
| Sûreté, conformité, honnêteté | 7 | 7 | 9 | aucune donnée réelle, résultats négatifs publiés, claim-gate ; pas de revue indépendante ni de carte de modèle |

Moyennes : projet 37 / 8 = 4,6 ; open source 61 / 8 = 7,6 ; absolu 75 / 8 = 9,4. Ces trois colonnes sont des jugements ; seule la colonne « projet » s'appuie sur des preuves du dépôt, et même elle reste une note d'auto-évaluation sans confirmation indépendante (aucune note 3 à G-P0).
