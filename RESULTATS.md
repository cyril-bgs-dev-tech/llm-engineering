# RESULTATS

Un chiffre sans `run_id` n'existe pas ici. Résultats négatifs et positifs au même titre. Tout est **développement (exploratoire)** : le test scellé n'a jamais été ouvert, aucun verdict confirmatoire n'existe (protocole gelé, premier cycle classé EXPLORE, ADR-004 et ADR-007). Données : PARHAF, textes cliniques fictifs français, 17 chapitres CIM-10 évalués. Tenu à jour à la main avec `claim-gate` ; mise à jour du 03/10/2026.

## Chapitre CIM-10 (macro-F1, 17 classes, `AUTRE` exclue de la moyenne)

| Mesure | Valeur | Intervalle ou dispersion | run_id | Remarque |
|---|---|---|---|---|
| Classe majoritaire (borne) | 0,0252 | écart-type sur 5 plis dans le run | `p1-03-bounds` | plancher sans modèle |
| Tirage selon la prévalence (borne) | 0,058 | idem | `p1-03-bounds` | plancher sans modèle |
| TF-IDF + régression logistique, plis par patient | 0,6844 | IC 95 % [0,6573 ; 0,7089], 5 plis | `20261003-121942-p1-06-tfidf-chapter` | C = 100, bord de la grille ; la prédiction de la fiche (0,20 à 0,50) était fausse |
| Même, grille de C étendue (v2) | 0,6889 | [0,6629 ; 0,7130] | `p1-06-tfidf-chapter-v2` | différence avec v1 +0,45 point [−1,21 ; +2,11] : non résolu ; v1 fait référence |
| TF-IDF, plis groupés par auteur | 0,6457 | [0,6203 ; 0,6688] | `20261003-121959-p1-06-tfidf-chapter-author-folds` | |
| **Écart patient moins auteur (RM-14)** | **+3,87 points** | **[+1,27 ; +6,31]** | `20261003-122037-rm-14-author-shortcut-tfidf` | « signalé » par la règle préenregistrée ; v2 : +3,42 [+1,17 ; +5,78] ; lecture non tranchée (ADR-011, Q18) |
| CamemBERT-bio affiné, pli 0, 2 époques, meilleur taux (1e-4) | 0,4484 | un pli, une graine | `p1-07-camembert-bio-lr1e-4` | bord de la grille ; **résultat négatif** : 24,9 points sous le TF-IDF sur le pli 0 [−30,3 ; −17,9] (`p1-07-camembert-minus-tfidf-fold0`) ; sous-entraîné (perte encore en baisse), non lisible comme la limite d'un encodeur |

Taux d'apprentissage de l'encodeur (pli 0) : 1e-5 0,0665 ; 2e-5 0,2793 ; 5e-5 0,4267 ; 1e-4 0,4484 (runs `p1-07-camembert-bio-lr*`).

## Autres tâches (niveau de la référence TF-IDF)

| Tâche | macro-F1 | IC 95 % | run_id | Remarque |
|---|---|---|---|---|
| Type de document (P1-04) | 0,9914 | [0,9849 ; 0,9968] | `20261003-115659-p1-04-tfidf-doctype` | quasi triviale (balises de type dans le texte) |
| Spécialité (P1-05, grille v2) | 0,9868 | [0,9817 ; 0,9912] | `p1-05-tfidf-specialty-v2` | quasi triviale |

## Mesures de service et de mémoire (pas de qualité)

Pic de mémoire réservé, LoRA r = 16, 4 096 tokens, micro-lot 1 : Qwen3.5-4B 11,5 Gio, Qwen3.5-9B 19,7 Gio, Gemma-4-E4B 19,8 Gio ; débit moyen 0,54, 0,87 et 0,65 s par exemple (runs `debit-*`, `preflight-*`).

## Criblage des élèves LLM, pli 0 (P1-11, 2 runs sur 6 terminés, comparaison entre candidats impossible tant que les deux taux manquent)

| Run | macro-F1 | Remarque | run_id |
|---|---|---|---|
| Qwen3.5-4B, LoRA, 1e-5 | 0,193 | taux le plus bas, sous-entraîné ; exactitude 0,439 | `20261003-141041-p1-11-qwen3-5-4b-lr1e-5` |
| Gemma-4-E4B, LoRA, 1e-4 | 0,4558 | exactitude 0,689 ; **24,1 points sous le TF-IDF** du pli 0 [−29,6 ; −17,5] ; **non distinct du CamemBERT-bio** (+0,73 point [−3,19 ; +4,40]) | `20261003-152759-p1-11-gemma-4-e4b-lr1e-4`, `…-minus-tfidf-fold0`, `…-minus-camembert-fold0` |

Quatre runs restent (Qwen 9B 1e-4 en cours, puis Gemma 1e-5, Qwen 9B 1e-5, Qwen 4B 1e-4 après un plantage du tokenizer corrigé).
