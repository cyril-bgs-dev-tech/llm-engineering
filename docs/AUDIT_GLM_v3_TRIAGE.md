# Audit GLM 5.3 v3 : triage et plan d'exécution

Source : `audit_GLM_5_3_v3.md` (80 actions, 10 par composante, déposé le 03/10/2026). Statut : fait, en cours, planifié, écarté. Rien ici ne change le protocole gelé ; les points de décision restent à Cyril.

## Retours transversaux adoptés

| Retour GLM | Décision |
|---|---|
| Ne pas écrire « les LLM perdent contre TF-IDF » sur un criblage à moitié rempli | Adopté : formulation « criblage inachevé, un pli, une graine, aucun LLM ne bat encore le TF-IDF » partout (présentation, RESULTATS) |
| Le meilleur taux au bord de grille est un maximum de tirages bruités | Adopté : P1-12 reste une règle écrite d'avance ; rejouer les deux meilleurs taux sur un second pli avant P1-20 (planifié) |
| Ne pas hériter au LLM les chiffres d'incertitude du TF-IDF | Adopté : mesure LLM d'abord (`q5_uncertainty.py` sur les `.probs.npz`), carte de modèle séparant les périmètres |
| Q15 : log loss équilibrée en secondaire | Concordant avec le défaut de Q16 |
| Q18 : protocole maintenu, deux chiffres, ADR préparée | Concordant avec la recommandation déposée |
| Q19 : perte pondérée = exploration à un run, EXPLORE | Concordant ; reste soumis à Cyril |
| Époques gelées à 2 (levier « durée ») | Non touché ; ADR/écart à trancher par Cyril avant P1-20 |

## Par composante (rang d'exécution)

### C1 Performance
- A1 finir le criblage : **en cours** (Qwen 9B 1e-5, puis Qwen 4B 1e-4).
- A2, A3 taux 2e-5 et 5e-5 : **planifié** après le choix de l'élève (P1-12) ; coût 5,6 à 7,6 h.
- A4 analyse par chapitre : **fait** (P1-23), matrice hiérarchique à compléter.
- A5 perte pondérée : **planifié**, sous réserve de Q19.
- A6 diagnostic de la courbe CamemBERT : **à faire** (CPU, lecture du registre).
- A7 CamemBERT à 4 époques : **écarté tant que Cyril ne tranche pas** (époques gelées).
- A8 ablation de troncature, A9 rang LoRA, A10 ensemble TF-IDF × LLM : **planifié**, après RM-17 ; A10 est faisable sans entraînement dès que les `.probs.npz` du 9B existent (les `.probs.npz` n'existent encore que pour Gemma 1e-5 ; le 9B 1e-5 et le 4B 1e-4 les écriront).

### C2 Rigueur
- A1 P1-19 cinq graines : **planifié** (partie code faite).
- A2 RM-17 règle de puissance, A7 réplique indépendante : **planifié** après A1.
- A3 effectifs par pli et par classe : **fait** dans cette session (`results/measures/glm_v3_cpu.json`).
- A4 classement des échecs : **fait** (`failures.py`).
- A5 macro-F1 pondérée et micro-F1 : **fait** dans cette session.
- A6 gabarit « non résolu », A8 bayésien EXPLORE, A9 scorecard G-P0, A10 alerte 80 % de B : **planifié** (CPU).

### C3 Données
- A8 composition des plis : **fait** (RESULTATS.md). A1 RM-14 sans identifiants d'auteur et A4 spécialité contre auteur : **planifié** (CPU, développement seulement).
- A2, A6 agrégats auteurs × chapitres, patients tronqués : **planifié** (agrégats sans identifiant).
- A3, A5, A7, A9, A10 : **planifié** (A10 : étiqueter les trois lectures de RM-14 comme non tranchées, à faire dans RESULTATS et wiki).

### C4 Incertitude
- A1 à A5, A9 sur le 9B : **bloqué** par les `.probs.npz` du 9B 1e-5 (en cours) ; `q5_uncertainty.py` est prêt.
- A7 conservation des probabilités par test : **fait** (`tests/test_scripts_save_probs.py`, N24).
- A6 Wilson : **fait** dans `conformal.wilson`, à brancher aux sorties par classe.
- A8 simulation couverture par classe aux effectifs du test : **planifié** (aucune étiquette de test).

### C5 Erreurs et robustesse
- A1 sauvegarde d'adaptateurs : **fait**, à vérifier au premier run concerné.
- A3 destination des erreurs des chapitres à F1 nulle : **fait** (`scripts/glm_v3_cpu_measures.py`) ; A2 matrice en blocs CIM-10 : **planifié** (la table des blocs n'est pas dans le dépôt de données).
- A4, A8 perturbations et leave-one-specialty-out sur TF-IDF : **planifié** (CPU).
- A5 perturbations sur le 9B : **bloqué** par l'adaptateur sauvegardé.
- A6, A7, A9, A10 : **planifié**.

### C6 Reproductibilité
- A1 reconstruction à froid, A2 déterminisme GPU (P1-26), A9 `make test-gpu` : **planifié** (A1 et A9 dès que le GPU est libre pour A9).
- A3 cache mypy rapide : **mesuré, neutre (33 s contre 40 s), non adopté**.
- A4 empreinte d'adaptateur au registre : **planifié** (suite de la sauvegarde).
- A5, A6, A7, A8, A10 : **planifié** (wiki, release de test, incident tokenizer, pip-audit).

### C7 Efficience
- A1 vLLM, A2 débit à 4 096 tokens, A4 quantification, A8 latence : **planifié** après libération du GPU (≈ 19 h 50 UTC).
- A3 front de Pareto : **à faire** dès la fin du criblage ; chaque point marqué de son périmètre (pli 0 contre 5 plis).
- A5 bucketing, A10 chargement des professeurs : **écarté pour l'instant** (modifierait la comparaison de budgets ; test sur lots jouets d'abord).
- A6, A7, A9 : **planifié**.

### C8 Sûreté et honnêteté
- A1 carte de modèle provisoire : **planifié**, périmètres séparés, statut EXPLORE.
- A4 consigner les audits v2 et v3 : **en cours** (ce fichier).
- A2, A3, A5 à A10 : **planifié**.

## Ordre d'exécution retenu (sans GPU d'abord)
1. Effectifs, macro pondérée contre micro, matrice hiérarchique, destination des erreurs (fait ici).
2. RM-14 : lectures 1, 2 et A8 (CPU), étiquetage « non tranché ».
3. Dès libération du GPU : `q5_uncertainty.py` sur le 9B ; P1-12 ; second pli pour les deux meilleurs taux ; grille complète de l'élève retenu ; P1-19 ; RM-17 ; mesures de service.
