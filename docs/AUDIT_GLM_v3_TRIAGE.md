# Audit GLM 5.3 v3 : triage et exécution

Source : `audit_GLM_5_3_v3.md` (80 actions, 10 par composante, déposé le 03/10/2026). Statuts : **fait** (preuve citée), **en file** (GPU, ordre fixé dans `scripts/run_after_p1_11.sh` ou à suivre), **planifié** (dépend d'un résultat à venir), **bloqué** (dépend d'un acte de Cyril), **écarté** (avec raison). Rien ici ne change le protocole gelé. Les décisions en attente de Cyril ont été tranchées par délégation (`tasks/QUESTIONS_POUR_CYRIL.md`).

## Retours transversaux adoptés

| Retour GLM | Décision |
|---|---|
| Ne pas écrire « les LLM perdent contre TF-IDF » sur un criblage inachevé | Adopté : « criblage inachevé, un pli, une graine, aucun LLM ne bat encore le TF-IDF » partout |
| Le meilleur taux au bord de grille est un maximum de tirages bruités | Adopté : règle P1-12 écrite d'avance ; second pli pour les deux meilleurs taux avant P1-20 (planifié) |
| Ne pas hériter au LLM les chiffres d'incertitude du TF-IDF | Adopté : carte de modèle et gabarit séparent les périmètres ; `q5_uncertainty.py` accepte un seul pli et sera lancé sur le candidat |
| Q15 / Q18 / Q19 | Concordance avec les décisions déléguées (macro-F1 seule en confirmatoire ; gel maintenu ; exploration pondérée à un run) |
| Époques gelées à 2 | Non touché pour les recettes ; diagnostic CamemBERT à 4 et 6 époques en EXPLORE (fiche hachée) |
| Constat de GLM erroné ou imprécis | Les secondes de Gemma et du 9B sont permutées dans son tableau (registre : 4 226 s et 3 623 s) ; la grille de taux de CamemBERT était complète (4 taux), pas incomplète |

## C1 Performance
- A1 criblage : **en cours** (4B 1e-4, dernier des six).
- A2, A3 taux 2e-5 et 5e-5 : **planifié** (élève retenu par P1-12 ; coût 2,2 h pour le 9B).
- A4 analyse par chapitre : **fait** (P1-23 ; `RESULTATS.md`, `glm_v3_cpu.json`).
- A5 perte pondérée : **en file**, sur le 9B à 1e-4 (code testé, fiche hachée).
- A6 diagnostic CamemBERT : **fait** (perte encore en baisse, performance monotone avec le taux, runs de 43 s).
- A7 CamemBERT 4 et 6 époques : **fait** (0,5255 puis 0,5527 contre 0,4484 ; sous-entraînement confirmé ; non distinct du 4B à 6 époques).
- A8 ablation de troncature : **écarté** (9 patients tronqués sur 3 586, aucun dans les chapitres rares).
- A9 rang LoRA : **planifié** après RM-17.
- A10 ensemble TF-IDF × LLM : **planifié** (probabilités du candidat issues du rejeu P1-26).

## C2 Rigueur
- A1 P1-19 cinq graines : **planifié** (après P1-12 et la grille de l'élève).
- A2 RM-17 : **code fait et testé** (`power_rule.py`, `scripts/rm17_power_rule.py`) ; exécution après P1-19.
- A3 effectifs par pli et classe : **fait**.
- A4 classement des échecs : **fait** (`failures.py`).
- A5 macro pondérée et micro : **fait**.
- A6 gabarit « non résolu » : **fait** (`docs/GABARIT_RAPPORT.md`).
- A7 réplique de la règle de puissance : **fait** (test contre une réplique scikit-learn).
- A8 lecture complémentaire : **fait** (EXPLORE).
- A9 scorecard G-P0 : **fait** (existe, `scorecards/G-P0.md`).
- A10 alerte à 80 % de B : **fait** (`budget.py`, `scripts/budget_alert.py`, 4,1 h enregistrées).

## C3 Données
- A1 identifiants d'auteur dans le texte : **fait** (1 patient sur 4 254 ; stylométrie 0,917).
- A2 table auteurs par chapitre : **fait**.
- A3 sensibilité du seuil : **fait** (9, 45, 171 paires ; presque toutes du même auteur).
- A4 spécialité contre auteur : **fait** (RM-14 : 0,385 contre 0,377).
- A5 scénarios Q18 : **fait** (ADR-013 de repli, déclencheurs écrits).
- A6 patients tronqués : **fait**.
- A7 empreintes : **fait** (`check_frozen`, `make check`).
- A8 composition des plis : **fait**.
- A9 estimand du test scellé dans le gabarit : **fait**.
- A10 lectures « non tranchées » : **fait** (`RESULTATS.md`, ADR-011/013).

## C4 Incertitude
- A1, A2, A3, A4, A5, A9 sur un LLM : **en file** via le rejeu du 9B (probabilités) ; `q5_uncertainty.py` accepte un seul pli ; répétition faite sur le 9B 1e-5.
- A6 Wilson : **fait** (dans `conformal.evaluate`, sorties par classe).
- A7 conservation des probabilités : **fait** (test de conformité, N24).
- A8 simulation de couverture : **fait** (`glm_v3_coverage_sim.json`).
- A10 écart d'échangeabilité dans le gabarit : **fait**.

## C5 Erreurs et robustesse
- A1 sauvegarde d'adaptateurs : **fait et vérifié** (196 Mo, 9B 1e-5).
- A2 lecture hiérarchique : **fait** (familles du projet, `glm_v3_families.json` ; les blocs fins du ClaML n’ajoutent pas d’information sans prédiction au niveau du bloc).
- A3 destination des erreurs : **fait**.
- A4 perturbations TF-IDF : **fait** ; A5 sur le 9B : **planifié** (adaptateur du rejeu).
- A6, A7 lecture d'erreurs et creux de longueur : **fait** (agrégats, effet de composition).
- A8 hors spécialité : **fait** (0,522).
- A9 tableau croisé : **fait** dans `RESULTATS.md` et `glm_v3_subgroups_bayes.json`.
- A10 gabarit d'analyse : **fait** (`p1_23_errors.py` pour chaque futur run).

## C6 Reproductibilité
- A1 reconstruction à froid : **fait** (26 s, cache chaud).
- A2 déterminisme GPU (P1-26) : **en file** (rejeu du 9B ; comparaison scriptée et testée).
- A3 cache mypy : **écarté** (33 s contre 40 s, dans le bruit).
- A4 empreinte d'adaptateur au registre : **planifié** (le champ `adapter_dir` est écrit ; empreinte à ajouter).
- A5 pages wiki par composante : **fait** (`etat-par-composante`).
- A6 release sur tag : **bloqué** (exige un push, réservé à Cyril).
- A7 incident tokenizer : **fait** (page wiki).
- A8 audit hebdomadaire : **fait** (workflow `audit-hebdomadaire.yml`, pip-audit).
- A9 `make test-gpu` : **planifié** (après libération du GPU).
- A10 contrats des modules : **fait** (page wiki).

## C7 Efficience
- A1 vLLM, A2 débit à 4 096 tokens, A4 quantification, A8 latence : **planifié** (GPU libre après la file).
- A3 front de Pareto : **fait** (provisoire, dans la carte de modèle).
- A5 bucketing, A10 chargement des professeurs : **écartés** pour l'instant (modifient la comparaison de budgets ; test sur lots jouets d'abord).
- A6 puissance consommée : **en cours** (échantillonnage passif `gpu_power_p1-11_second_pass.csv`).
- A7 dérive : **fait** (`drift.py`, 3 tests).
- A9 politique mémoire : **fait** (plafond 28 Gio dans la fiche P1-12 et le protocole).

## C8 Honnêteté
- A1 carte de modèle : **fait** (provisoire).
- A2 TRIPOD : **fait** (dans la carte).
- A3 sous-groupes : **fait**.
- A4 audits consignés : **fait**.
- A5 claim-gate : **fait** (gabarit, tableau de preuve de la présentation).
- A6 lectures de RM-14 : **fait**.
- A7 journal des accès : **fait** (`sealed.log_access`, testé).
- A8 attente « non résolu » : **fait** (gabarit).
- A9 licences : **fait**.
- A10 « ce que nous ne savons pas » : **fait** (gabarit).

## Suite (GPU), dans l'ordre
1. Fin du criblage (4B 1e-4, fin vers 19 h 40 UTC).
2. File `run_after_p1_11.sh` : CamemBERT à 4 et 6 époques, rejeu du 9B (P1-26, probabilités, adaptateur), exploration Q19.
3. P1-12 (règle écrite d'avance), second pli pour les deux meilleurs taux, grille complète de l'élève retenu, P1-19, RM-17, mesures de service, `make test-gpu`.
