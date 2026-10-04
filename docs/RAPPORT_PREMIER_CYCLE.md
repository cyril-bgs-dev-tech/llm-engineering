# Rapport préliminaire du premier cycle (04/10/2026) : classer le chapitre CIM-10 de comptes rendus cliniques fictifs français

Statut : **EXPLORE, développement seulement**. Le test scellé (633 patients) n'a jamais été ouvert ; aucun verdict confirmatoire n'existe. Chaque chiffre renvoie à un `run_id` de `RESULTATS.md`. Gabarit : `docs/GABARIT_RAPPORT.md`.

## 1. Ce que le lecteur doit comprendre d'abord
- La question : que gagne-t-on à adapter un modèle (affinage complet d'un encodeur, LoRA d'un LLM, plus tard distillation) par rapport à une référence lexicale peu coûteuse ?
- La règle de puissance échoue (largeur d'IC moyenne 12,2 points sur cinq graines d'encodeur, contre 4,0 admis) : **aucune comparaison de ce cycle ne peut être confirmatoire** ; « non résolu » est le résultat attendu.
- La recette gelée du protocole (4 taux, 2 époques) sous-estime fortement les modèles appris (le Qwen3.5-4B passe de 0,587 à 0,7795 avec 10 époques) ; les chiffres ci-dessous séparent la recette gelée de la recette mûre.

## 2. Données et estimand
PARHAF, comptes rendus fictifs en français : 4 254 patients, 3 586 au développement (5 plis stratifiés de 717 à 718), 633 au test scellé ; 17 chapitres CIM-10 évalués (`AUTRE` exclue de la macro-F1) ; 104 auteurs. Estimand du test : nouveaux patients du même corpus (non groupé par auteur). Écart patient contre auteur : le leave-one-author-out du TF-IDF (0,6185, 66 auteurs) place la signature d'auteur à environ 2 points ; les plis groupés par auteur donnent un écart de 5,06 points (rétrécissement de l'entraînement compris).

## 3. Résultats (macro-F1, développement)
| Système | macro-F1 | Périmètre | Coût d'inférence |
|---|---|---|---|
| TF-IDF, référence v1 | 0,6844 [0,657 ; 0,709] | 5 plis | quelques ms |
| TF-IDF caractères 3 à 5, poids équilibrés | 0,7202 (+3,65 [+1,94 ; +5,48] contre v1) | 5 plis | p50 1,9 ms, 20 Mo |
| CamemBERT-bio, 2 époques (recette gelée) | 0,448 | pli 0 | |
| CamemBERT-bio, 10 époques, 5 graines | 0,7293 ± 0,0256 (pli 0), 0,7475 (pli 1) | plis 0 et 1 | p50 191 ms, 443 Mo (CPU, 8 threads) |
| Encodeur, moyenne de 5 graines | 0,7331 (pli 0), 0,7532 (pli 1) | plis 0 et 1 | 5 × 191 ms |
| Qwen3.5-4B LoRA, 2 époques | 0,587 | pli 0 | p50 117 ms, GPU, 15,5 Gio |
| **Qwen3.5-4B LoRA, 10 époques** | **0,7795** (une graine ; +6,4 [+2,0 ; +11,4] contre le meilleur TF-IDF, +4,9 [−0,35 ; +10,5] contre l'encodeur moyenné) | pli 0 | 12 467 s d'entraînement, GPU, p50 117 ms (à 2 époques, même architecture) |

Écarts de l'encodeur moyenné contre le meilleur TF-IDF : +1,5 point (pli 0, non résolu) et +6,4 [+0,8 ; +12,1] (pli 1). L'ensemble 50/50 encodeur et TF-IDF n'apporte rien sur l'encodeur moyenné (+3,0 puis −0,2). L'ensemble LoRA mûr + encodeur moyenné fait 0,7926 (+6,1 [+1,2 ; +11,4] contre l'encodeur moyenné). Qwen3.5-9B, Gemma-4-E4B : 0,565 et 0,456 à 2 époques ; le 31B à 2 époques a été annulé (durée projetée 6 h).

## 4. Ce qui n'a pas marché (publié)
Perte pondérée 1/√n sur le 4B (−2,3 [−5,3 ; +1,5]) ; hiérarchie des blocs CIM-10 comme supervision (−4,0 ou −1,05) ; ensembles de modèles sous-entraînés ; encodeur par fenêtres sur tout le dossier (+0,3 à 6 époques, −6,8 à 10) ; taux 2e-4 ; quantification INT8 dynamique naïve (macro-F1 0,336) ; test de taille 31B à 2 époques (arrêt anticipé).

## 5. Incertitude et abstention
Encodeur 10 époques : ECE 0,106 brute, 0,050 après température ; conforme LAC 90 % : couverture 0,901 avec 1,53 classe par ensemble ; exactitude 0,946 à 70 % de couverture. TF-IDF : 0,931 à 70 %. Couverture par famille de chapitres (TF-IDF) : 0,56 à 0,99 derrière 0,90 marginal : l'ensemble marginal trompe sur les familles ambiguës (endocrinien et mental, symptômes et lésions, nerveux). Étalonner par plis d'auteurs donne 0,900 de couverture sous décalage d'auteur. Mesuré en développement, jamais sur le test.

## 6. Robustesse
TF-IDF : sans accents −5,6 points ; fautes de frappe −0,7 ; hors spécialité 0,522 d'exactitude. Les erreurs traversent les familles (96 %) ; au moins un des six modèles est juste pour 91,8 % des patients, tous se trompent pour 8,2 % (probable ambiguïté d'étiquette). La robustesse des modèles appris n'est pas mesurée.

## 7. Ce que nous ne savons pas
Si l'avantage du LoRA mûr tient sur d'autres graines et un second pli (pli 1 en cours) ; si un modèle plus grand change la conclusion (non testé à recette mûre) ; si l'avantage de l'encodeur tient sur les trois autres plis et sur le test ; la généralisation à de nouveaux auteurs de l'encodeur ; la latence et la qualité d'un encodeur quantifié correctement ; l'apport de données synthétiques ciblées (fiche écrite, non exécutée).

## 8. Limites
Un pli ou deux, quelques graines ; cinq chapitres de 27 à 63 patients portent 85 % de la variance de la macro-F1 (écart-type bootstrap de 1,3 point sur 3 586 prédictions) ; non-déterminisme GPU (à graine égale, 0,7714 puis 0,7362) ; corpus fictif.

## 9. Tableau de preuve
| Affirmation | Preuve (`RESULTATS.md`) | Statut |
|---|---|---|
| TF-IDF caractères et poids 0,7202, +3,65 | `tfidf-variant-char-balanced`, `tfidf-variants-minus-reference` | prouvé (EXPLORE) |
| Encodeur 10 époques : 0,7293 ± 0,0256 (pli 0), 0,7475 (pli 1) | `camembert-recette-lr1e-4-ep10`, `camembert-graine-ep10-s*`, `camembert-pli1-ep10-s*` | prouvé (EXPLORE) |
| Règle de puissance sur l'encodeur : 12,2 contre 4,0 | `rm-17-power-rule-encodeur-ep10` | prouvé |
| Service TF-IDF : p50 1,9 ms, 20,4 Mo | `bench-serving-tfidf-charbal-v1` | prouvé |
| LOAO TF-IDF 0,6185 ; écart sur partitions répétées 5,06 | `tfidf-loao`, `split-discretization-check` | prouvé (un modèle) |
| 85 % de la variance de la macro-F1 portée par cinq classes | `split-discretization-check` | prouvé |
| Qwen3.5-4B LoRA à 10 époques : 0,7795, +19,3 points sur 2 époques, +6,4 [+2,0 ; +11,4] contre le meilleur TF-IDF | `llm-mur2-qwen3-5-4b-ep10-lr1e-4`, `llm-mur2-minus-tfidf-fold0`, `llm10-et-ensembles-minus-*` | prouvé (pli 0, une graine, EXPLORE) |
| Perte pondérée, hiérarchie, fenêtres, INT8 : sans bénéfice | runs `q19-*`, `tfidf-hier-*`, `camembert-fenetres-*`, `quantization-*` | prouvé (EXPLORE) |
