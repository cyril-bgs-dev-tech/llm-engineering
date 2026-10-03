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

## Fiabilité de l'incertitude, TF-IDF chapitre (Q5, développement, validation croisée par pli, run `q5-uncertainty-tfidf-chapter`)

| Mesure | Valeur | Remarque |
|---|---|---|
| ECE (15 intervalles) | 0,029 ; après température ajustée hors pli 0,034 | déjà calibré (température ≈ 0,95) : **la recalibration n'améliore rien** (perte logarithmique 0,600 puis 0,604) |
| ECE moyenne par classe | 0,0086 | |
| Prédiction conforme LAC à 90 %, marginale | couverture 0,901, taille moyenne 1,30 | **au moins une classe jamais couverte** (couverture minimale par classe 0,0) : garantie marginale seulement |
| LAC à 90 %, par classe | couverture 0,904, couverture minimale par classe 0,893, taille moyenne 2,57 | garantie par classe, prix : ensembles deux fois plus grands |
| APS à 90 % | couverture 0,892 (marginale) à 0,897 (par classe), taille moyenne 11,8 et 8,0 | APS déterministe trop conservateur sur ces probabilités : LAC préféré |
| Prédiction sélective | AURC 0,0503 pour un taux d'erreur de 0,182 ; exactitude 0,818 → 0,862 (90 % de couverture), 0,897 (80 %), 0,931 (70 %) | |
| **Décalage** : étalonnage sur les plis par patient, évaluation sur les plis par auteur (mêmes patients) | LAC marginal 0,887 contre 0,900 ; LAC par classe 0,880 (classe la plus basse 0,802) ; APS 0,900 | **la couverture baisse de 1,3 à 2,0 points sous groupement par auteur**, cohérent avec RM-14 ; sous 90 % |

Limites : un seul modèle (TF-IDF), pas le test scellé, pas de politique d'abstention chiffrée, probabilités des LLM non conservées pour les runs déjà faits (N24).

## Criblage des élèves LLM, pli 0 (P1-11, 4 runs sur 6 terminés, comparaison entre candidats impossible tant que les deux taux manquent)

| Run | macro-F1 | Remarque | run_id |
|---|---|---|---|
| Qwen3.5-4B, LoRA, 1e-5 | 0,193 | taux le plus bas, sous-entraîné ; exactitude 0,439 | `20261003-141041-p1-11-qwen3-5-4b-lr1e-5` |
| Gemma-4-E4B, LoRA, 1e-5 | 0,1416 | taux le plus bas, sous-entraîné ; exactitude 0,378, log loss 2,02, ECE 0,037, 3 706 s, pic 24,8 Gio ; probabilités conservées | `20261003-174127-p1-11-gemma-4-e4b-lr1e-5` |
| Gemma-4-E4B, LoRA, 1e-4 | 0,4558 | exactitude 0,689 ; **24,1 points sous le TF-IDF** du pli 0 [−29,6 ; −17,5] ; **non distinct du CamemBERT-bio** (+0,73 point [−3,19 ; +4,40]) | `20261003-152759-p1-11-gemma-4-e4b-lr1e-4`, `…-minus-tfidf-fold0`, `…-minus-camembert-fold0` |
| Qwen3.5-9B, LoRA, 1e-4 | **0,565** | exactitude 0,788, log loss 0,723, 3 623 s, pic 21,6 Gio ; **13,2 points sous le TF-IDF** [−18,4 ; −7,0] ; **10,9 points au-dessus du Gemma-4-E4B au même taux** [+6,4 ; +15,3] | `20261003-163427-p1-11-qwen3-5-9b-lr1e-4`, `…-minus-tfidf-fold0`, `…-minus-gemma-1e-4-fold0` |

Deux runs restent (Qwen 9B 1e-5, Qwen 4B 1e-4, relancés après un plantage du tokenizer corrigé). Aucun LLM ne dépasse encore le TF-IDF ; les comparaisons entre candidats restent provisoires tant que les deux taux de chacun manquent.

## Mesures sans GPU issues de l'audit GLM v3 (pli 0, 717 patients, développement ; `results/measures/glm_v3_cpu.json`)

| Modèle | macro-F1 | F1 pondérée | micro-F1 (exactitude) | chapitres à F1 nulle |
|---|---|---|---|---|
| TF-IDF | 0,697 | 0,813 | 0,824 | aucun |
| Qwen3.5-9B, 1e-4 | 0,565 | 0,775 | 0,788 | XII, XXI, XXII |
| Gemma-4-E4B, 1e-4 | 0,456 | 0,673 | 0,689 | IV, XII, XXII |

Les chapitres à F1 nulle du 9B n'ont que 6 (XII), 8 (XXI) et 5 (XXII) patients au pli 0 : le zéro vaut quelques patients, pas une certitude. Les cinq patients du XXII sont tous classés en X. L'écart de macro-F1 avec le TF-IDF (13 points) est bien plus grand que celui de la F1 pondérée (4 points) : le déficit vient des petits chapitres, ce qui est la lecture de l'audit (levier : perte pondérée, sous réserve de Q19). Périmètre : un pli, une graine pour les LLM, TF-IDF 0,697 au même pli (0,684 sur cinq plis). Aucun verdict : criblage inachevé.

Composition des plis (audit GLM, C3-A8) : les plis par patient comptent 717 à 718 patients, les plis groupés par auteur 663 à 763. Chapitres rares par pli, par patient puis par auteur : XXII 5 à 6 contre 3 à 9, XII 6 contre 5 à 7, XXI 8 à 9 contre 7 à 10, IV 9 à 10 contre 6 à 12. Les plis groupés sont donc plus déséquilibrés sur les petits chapitres, ce qui peut compter dans l'écart de RM-14 : un facteur de plus, la lecture reste non tranchée.

Traces d'auteur dans le texte (audit GLM, C3-A1, A2 ; `results/measures/glm_v3_authors.json`, développement, 3 586 patients, 104 auteurs) :
- L'identifiant d'auteur apparaît dans le texte pour 1 patient seulement (le relecteur pour 2) : la fuite par identifiant explicite est exclue.
- En revanche, un TF-IDF + régression logistique retrouve l'auteur à **0,917** d'exactitude (66 auteurs d'au moins 20 patients, 5 plis stratifiés ; hasard 0,015, classe majoritaire 0,038). Le style porte donc une signature d'auteur très forte. Elle est confondue avec le thème, puisque chaque auteur couvre un nombre limité de chapitres : ce chiffre n'arbitre pas la lecture « fuite » de RM-14 contre la lecture « thématique », il montre que la fuite stylistique est possible. Lecture non tranchée.
- Auteurs par chapitre : 9 (XV) à 56 (II) ; part du premier auteur de 8 % (XVIII) à 49 % (XV). Chapitres rares : XII 18 auteurs, XXII 11, XXI 23.

Robustesse du TF-IDF aux perturbations (audit GLM, C5-A4 ; `results/measures/glm_v3_perturb_tfidf.json`, pli 0, 717 patients, développement, modèle entraîné sur du texte propre ; EXPLORE) : texte propre 0,697 ; **accents retirés 0,641 (−5,6 points)** ; fautes de frappe sur 5 % des mots 0,690 (−0,7) ; majuscules sur 5 % des mots 0,697 (0, la casse est normalisée par le vectoriseur). Un jeu fictif accentué rend le modèle fragile à un texte sans accents. La comparaison avec le 9B suppose son adaptateur sauvegardé.

Couverture par classe attendue aux effectifs du test (audit GLM, C4-A8 ; `results/measures/glm_v3_coverage_sim.json`, effectifs = prévalence du développement × 633, aucune étiquette de test) : pour une couverture vraie de 90 %, l'intervalle de Wilson d'une couverture observée à 90 % va de [0,38 ; 0,96] pour les chapitres de 5 patients (XII, XXII) à [0,85 ; 0,94] pour le chapitre II (173 patients). Neuf chapitres sur dix-sept ont moins de 30 patients attendus : leur couverture individuelle ne sera pas vérifiable au test.

Hors distribution par spécialité exclue, TF-IDF du chapitre (audit GLM, C5-A8 ; `results/measures/glm_v3_loso_tfidf.json`, développement, 20 spécialités, 3 586 patients, EXPLORE) : exactitude moyenne pondérée **0,522** contre 0,818 en validation croisée usuelle. Plus bas : obstétrique 0,013 (le chapitre XV n'existe presque que dans cette spécialité), néphrologie 0,149, chirurgie viscérale 0,161. Plus haut : anatomopathologie et chirurgie cardio-vasculaire 1,000 (un seul chapitre). La spécialité détermine en grande partie le chapitre ; sans elle dans l'entraînement, le modèle ne connaît pas le chapitre. Ce résultat borne la généralisation à de nouvelles spécialités ; il ne concerne pas le test scellé (même corpus, mêmes spécialités).

Creux d'exactitude selon la longueur (audit GLM, C5-A7 ; pli 0, terciles de longueur en mots) : tercile court (médiane 341 mots) TF-IDF 0,870, 9B 0,862 ; moyen (547) 0,766 et 0,690 ; long (896) 0,837 et 0,812. **Le creux du tercile moyen existe aussi pour le TF-IDF** : c'est un effet de composition, le tercile court contient 48 % de chapitre II (facile) contre 18 % et 16 % ailleurs, et le tercile moyen a la part la plus basse de ce chapitre facile. Aucune troncature n'est en jeu (900 mots restent bien sous 4 096 tokens). Pas de défaut propre au 9B.

Confusions les plus fréquentes au pli 0 (audit GLM, C5-A6, agrégats) : TF-IDF 126 erreurs, surtout XVIII→X (9), XVIII→VI (6), VI→XVIII (6) ; Qwen3.5-9B 152 erreurs, surtout V→VI (7), VI→IX (7), II→XIV (6), XXII→X (5). Le XVIII (symptômes et signes non classés) est le chapitre « fourre-tout » du TF-IDF ; le 9B confond plutôt des chapitres voisins par organe (V, VI, IX) et rate les petits chapitres.

Cache mypy sur disque rapide (audit GLM, C6-A3) : 33 s contre 40 s en tiède, dans le bruit (le processeur était partagé avec un run GPU) : neutre, non adopté, aucun contrôle modifié.

Sensibilité du contrôle de quasi-doublons (audit GLM, C3-A3 ; `results/measures/glm_v3_neardup_sensitivity.json`, seuil figé 0,8 non modifié) : 9 paires à 0,8 (toutes du même auteur), 45 à 0,7 (44 du même auteur), 171 à 0,6 (169 du même auteur). **Les quasi-doublons sont presque tous écrits par le même auteur** : un auteur réutilise ses gabarits. C'est un argument de plus pour un effet d'auteur dans le texte (RM-14), et le découpage groupé par auteur le neutralise ; le test scellé, non groupé, garde les mêmes auteurs que le développement. Le contrôle de fuite ne dépend pas d'un seuil ajusté : le nombre de paires croît vite en dessous de 0,8, mais le seuil du protocole est gelé.
