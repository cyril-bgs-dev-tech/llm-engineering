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

## Criblage des élèves LLM, pli 0 (P1-11, six runs terminés ; élève retenu par P1-12 : Qwen3.5-4B, ADR-014)

| Run | macro-F1 | Remarque | run_id |
|---|---|---|---|
| Qwen3.5-4B, LoRA, 1e-5 | 0,193 | taux le plus bas, sous-entraîné ; exactitude 0,439 | `20261003-141041-p1-11-qwen3-5-4b-lr1e-5` |
| **Qwen3.5-4B, LoRA, 1e-4** | **0,5867** | 3 024 s, pic 12,9 Gio ; **11,1 points sous le TF-IDF** du pli 0 [−16,4 ; −4,8] ; **+2,16 points contre le 9B au même taux, IC [−1,78 ; +5,90] : non résolu** (donc le moins coûteux est retenu) | `20261003-194530-p1-11-qwen3-5-4b-lr1e-4`, `…-minus-tfidf-fold0`, `…-qwen4b-minus-qwen9b-1e-4-fold0` |
| Gemma-4-E4B, LoRA, 1e-5 | 0,1416 | taux le plus bas, sous-entraîné ; exactitude 0,378, log loss 2,02, ECE 0,037, 3 706 s, pic 24,8 Gio ; probabilités conservées | `20261003-174127-p1-11-gemma-4-e4b-lr1e-5` |
| Gemma-4-E4B, LoRA, 1e-4 | 0,4558 | exactitude 0,689 ; **24,1 points sous le TF-IDF** du pli 0 [−29,6 ; −17,5] ; **non distinct du CamemBERT-bio** (+0,73 point [−3,19 ; +4,40]) | `20261003-152759-p1-11-gemma-4-e4b-lr1e-4`, `…-minus-tfidf-fold0`, `…-minus-camembert-fold0` |
| Qwen3.5-9B, LoRA, 1e-5 | 0,2128 | taux le plus bas, sous-entraîné ; exactitude 0,448, log loss 1,86, ECE 0,080, 3 690 s ; probabilités et adaptateur LoRA (196 Mo) conservés ; première sauvegarde d'adaptateur réussie | `20261003-185103-p1-11-qwen3-5-9b-lr1e-5` |
| Qwen3.5-9B, LoRA, 1e-4 | **0,565** | exactitude 0,788, log loss 0,723, 3 623 s, pic 21,6 Gio ; **13,2 points sous le TF-IDF** [−18,4 ; −7,0] ; **10,9 points au-dessus du Gemma-4-E4B au même taux** [+6,4 ; +15,3] | `20261003-163427-p1-11-qwen3-5-9b-lr1e-4`, `…-minus-tfidf-fold0`, `…-minus-gemma-1e-4-fold0` |

Le criblage est complet (six runs). Aucun LLM ne dépasse le TF-IDF au pli 0 ; le Qwen3.5-4B à 1e-4 est le meilleur LLM (0,5867, non distinct du 9B), retenu comme élève par la règle d'ADR-009 (ADR-014). Les meilleurs taux des trois candidats sont au bord supérieur de la grille : les taux 2e-5 et 5e-5 du 4B sont dans la file (P1-13). La prédiction de la fiche P1-11 selon laquelle le 9B serait le meilleur était fausse.

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

Patients tronqués à 4 096 tokens (audit GLM, C3-A6 ; `results/measures/glm_v3_truncated.json`, tokenizer Qwen3.5, développement) : 9 patients sur 3 586 (0,25 %), répartis en IX (4), II, I, XVIII, X, V (1 chacun). **Aucun dans les chapitres rares (XII, XXI, XXII)** : la troncature n'explique pas le déficit des petits chapitres, et l'ablation de troncature (A8 de GLM) a peu de chances de changer le résultat ; elle passe en priorité basse.

Reconstruction à froid (audit GLM, C6-A1 ; `scripts/cold_rebuild.sh`, `results/measures/cold_rebuild.txt`) : clone neuf, aucune donnée brute (0 dossier), `uv sync --frozen` 6 s (cache d'`uv` chaud), 261 tests réussis dont 6 ignorés faute de données et 2 désélectionnés (GPU), fil synthétique réussi, 26 s au total. Limite : le cache d'`uv` était chaud et les tests dépendant des données brutes sont ignorés ; une machine vierge sans cache n'est pas simulée.

Sous-groupes au pli 0 (audit GLM, C8-A3 ; `results/measures/glm_v3_subgroups_bayes.json`, exactitude, TF-IDF puis Qwen3.5-9B 1e-4) : volume d'auteur dans le développement, auteurs à peu de patients 0,833 puis 0,757, moyen 0,811 puis 0,783, beaucoup 0,829 puis 0,825. L'écart entre les deux modèles est le plus grand sur les auteurs peu représentés (−7,6 points) et nul sur les auteurs très représentés : le TF-IDF profite de la reconnaissance du style d'auteurs bien connus, ce qui va dans le sens d'un effet d'auteur (RM-14) ; lecture non tranchée. Longueur : voir plus haut (effet de composition). Spécialités de moins de 30 patients au pli 0 non interprétables (réanimation : 7 patients).

Lecture complémentaire EXPLORE de l'écart (audit GLM, C2-A8 ; bootstrap stratifié du pli 0, 5 000 répliques, graine 20261002) : écart moyen 9B moins TF-IDF −12,7 points ; probabilité d'un écart positif 0,0002 ; probabilité que le 9B soit inférieur de plus de δ = 2 points 0,9998. Ce n'est pas un verdict (criblage, un pli, une graine) et elle ne remplace pas l'intervalle apparié de la fiche ; elle dit seulement que l'écart actuel du 9B à 1e-4 contre le TF-IDF n'est pas du bruit d'échantillonnage du pli.

Erreurs par familles de chapitres (audit GLM, C5-A2 ; `results/measures/glm_v3_families.json`, pli 0, neuf familles du projet, regroupement non normatif) : seulement 4,8 % des erreurs du TF-IDF (6 sur 126), 3,9 % de celles du Qwen3.5-9B (6 sur 152) et 10,3 % de celles du Gemma-4-E4B (23 sur 223) restent dans la même famille. Les erreurs traversent donc les familles : elles reflètent surtout des cas où un second diagnostic (symptômes, lésions, autre organe) rivalise avec le diagnostic principal, pas des confusions entre chapitres voisins. Un score hiérarchique à pénalité par distance (Lanus et al.) n'adoucirait donc presque aucune erreur, sous cette définition des familles.

## Diagnostic d'époques de CamemBERT-bio (audit GLM C1-A6/A7, fiche `2026-10-03-camembert-epoques-diagnostic`, EXPLORE, pli 0, taux 1e-4, une graine)

| Époques | macro-F1 | exactitude | durée | run_id |
|---|---|---|---|---|
| 2 (référence gelée) | 0,4484 | 0,770 | 43 s | `p1-07-camembert-bio-lr1e-4` |
| 4 | 0,5255 | 0,803 | 86 s | `camembert-epoques-lr1e-4-ep4` |
| 6 | **0,5527** | 0,809 | 128 s | `camembert-epoques-lr1e-4-ep6` |

Critère de la fiche (gain de plus de 2,0 points sur 2 époques) : **sous-entraînement confirmé** (+7,7 puis +10,4 points). À 6 époques, CamemBERT-bio est 14,4 points sous le TF-IDF [−19,9 ; −7,4] (`camembert-ep6-minus-tfidf-fold0`) et **non distinct du Qwen3.5-4B** (−3,4 points [−8,2 ; +2,1], `camembert-ep6-minus-qwen4b-fold0`). Conséquences : (1) le déficit de l'encodeur à 2 époques était en bonne partie du sous-entraînement, le chiffre 0,448 sous-estime l'encodeur ; (2) à effort bien moindre (128 s contre 3 024 s), un encodeur plus longuement entraîné n'est pas résolu plus bas que l'élève LoRA : l'argument de la porte RM-17 (« la LoRA est-elle dominée par l'encodeur ? ») reste ouvert. Ces runs sortent des 2 époques gelées pour les recettes confirmatoires : ils sont EXPLORE, sans verdict, la valeur de 2 époques de la référence encodeur du protocole n'est pas modifiée. Prédictions de la fiche : macro-F1 à 4 époques entre 0,50 et 0,62 (réalisé) ; écart au TF-IDF supérieur à 8 points à 6 époques (réalisé).

Fiabilité de l'incertitude de CamemBERT-bio à 6 époques (audit GLM C4-A1/A2/A4, première mesure d'un modèle appris ; `q5-uncertainty-camembert-ep6-fold0`, pli 0 seulement, 717 patients, validation croisée en deux moitiés stratifiées du pli : étalonnage sur une moitié, évaluation sur l'autre ; EXPLORE) : ECE 0,049 (0,050 après température ; TF-IDF 0,028 sur cinq plis), log loss 0,713 ; conforme LAC à 90 % : couverture 0,902 avec 1,56 classe par ensemble, par classe 0,929 (minimum 0,842) ; APS 0,904 mais 9,0 classes par ensemble ; sélectif : exactitude 0,860 à 90 % de couverture, 0,897 à 80 %, **0,934 à 70 %** (TF-IDF 0,931), AURC 0,058. La couverture marginale conforme est tenue, et l'encodeur donne des ensembles courts avec LAC. Périmètre à rappeler : un pli, une graine, étalonnage sur 358 patients ; ces chiffres ne s'appliquent pas à un LLM. La mesure du Qwen3.5-4B suit avec les probabilités du rejeu.

## Grille de taux du Qwen3.5-4B (P1-13, fiche `2026-10-03-p1-13-grille-eleve-qwen4b`, pli 0, une graine)

| Taux | macro-F1 | exactitude | durée | run_id |
|---|---|---|---|---|
| 1e-5 | 0,193 | 0,439 | 2 515 s | `20261003-141041-p1-11-qwen3-5-4b-lr1e-5` |
| 2e-5 | 0,306 | 0,561 | 2 515 s | `p1-13-qwen3-5-4b-lr2e-5` |
| 5e-5 | 0,4733 | 0,724 | 2 509 s | `20261003-204018-p1-13-qwen3-5-4b-lr5e-5` |
| 1e-4 | **0,5867** | 0,789 | 3 024 s | `20261003-194530-p1-11-qwen3-5-4b-lr1e-4` |

5e-5 contre 1e-4 : −11,3 points [−15,6 ; −6,8] (`p1-13-4b-5e-5-minus-1e-4-fold0`) : **1e-4 est meilleur, résolu**. La macro-F1 croît de façon monotone avec le taux sur toute la grille testée, comme pour CamemBERT-bio : le meilleur taux est au **bord supérieur** de la grille gelée, signalé comme l'exige le protocole (6.5), et la grille ne s'étend jamais. Avec 2 époques, la recette est probablement encore sous-entraînée (même signe que l'encodeur, où quatre puis six époques ont aidé de 7,7 puis 10,4 points). Grille complète du 4B : 1e-5 0,193 ; 2e-5 0,306 ; 5e-5 0,473 ; 1e-4 0,587, strictement croissante.

## Exploration Q19 : perte pondérée 1/√n sur le Qwen3.5-4B (fiche `2026-10-03-q19-perte-ponderee-qwen4b`, EXPLORE, pli 0, taux 1e-4, une graine)

| Run | macro-F1 | exactitude | log loss | ECE | durée | run_id |
|---|---|---|---|---|---|---|
| Référence (perte non pondérée) | 0,5867 | 0,789 | n/a ici | n/a ici | 3 024 s | `20261003-194530-p1-11-qwen3-5-4b-lr1e-4` |
| Perte pondérée 1/√n | 0,5637 | 0,756 | 0,773 | 0,025 | 2 508 s | `20261003-213020-q19-qwen3-5-4b-lr1e-4-perte-ponderee` |

Écart pondérée moins référence : **−2,3 points, IC 95 % [−5,3 ; +1,5] : non résolu** (`q19-weighted-minus-unweighted-4b-fold0`). Aucune amélioration suggérée : la prédiction de la fiche (Δ > 0, probabilité 0,65) est fausse. Par chapitre : XXI sort d'une F1 nulle (0 → 0,17), XXII reste à 0, XII baisse (0,29 → 0,13), I baisse (0,57 → 0,36), V et VI montent (0,32 → 0,42 ; 0,44 → 0,49) ; l'exactitude baisse de 3,3 points et l'ECE est basse (0,025). La pondération déplace des erreurs entre petits chapitres sans améliorer la moyenne. Elle ne justifie pas de changer la référence ; l'hypothèse « l'entropie croisée non pondérée explique le déficit » n'est **pas soutenue** à cette longueur d'entraînement (2 époques, 5 à 8 patients par petit chapitre au pli 0) : le déficit semble plutôt venir de la rareté des données et du sous-entraînement. Reste non testé : perte équilibrée au niveau des logits, correction a posteriori par la prévalence.

## Rejeu de déterminisme du Qwen3.5-4B à 1e-4 (P1-26, fiche `2026-10-03-p1-13-grille-eleve-qwen4b`, pli 0, même graine 1000 ; `results/measures/p1_26_determinism.json`)

Le rejeu `20261003-221543-p1-26-rejeu-qwen3-5-4b-lr1e-4` **n'est pas identique** au run initial : écart maximal de la perte par pas 0,21 sur 180 pas, **40 prédictions différentes sur 717** (5,6 %), macro-F1 0,5807 contre 0,5867 (−0,6 point, IC [−1,85 ; +0,69] : non résolu, `p1-26-rejeu-minus-original-4b-fold0`). À graine égale, deux runs diffèrent donc à cause des noyaux GPU non déterministes ; le bruit d'un run isolé est de l'ordre du point de macro-F1, ce qui limite toute conclusion sur un écart de 2 points (δ) à un pli et une graine. Prédictions de la fiche : prédictions différentes (réalisé), écart de macro-F1 sous 1 point (réalisé).

Fiabilité de l'incertitude du Qwen3.5-4B (rejeu, `q5-uncertainty-qwen4b-1e-4-fold0`, pli 0, étalonnage croisé en deux moitiés, EXPLORE) : ECE 0,039 (0,038 après température) ; LAC à 90 % : couverture 0,898, 1,60 classe par ensemble, par classe 0,912 (minimum 0,839) ; exactitude 0,823 à 90 % de couverture, 0,868 à 80 %, 0,892 à 70 % (CamemBERT-bio 6 époques : 0,934 ; TF-IDF : 0,931) ; AURC 0,063. L'incertitude du 4B est correctement calibrée mais moins sélective que celle de l'encodeur et du TF-IDF.

## Ensembles par moyenne de probabilités (pli 0, `results/measures/ensemble_fold0.json`, EXPLORE, bootstrap stratifié)

TF-IDF 0,697 ; TF-IDF + CamemBERT-bio 6 époques 0,659 [différence avec le TF-IDF : −8,8 ; +0,7] ; TF-IDF + 4B 0,650 [−9,4 ; −0,8] ; les trois 0,654 [−9,3 ; 0,0] ; CamemBERT + 4B 0,596. **Aucun ensemble par simple moyenne ne dépasse le TF-IDF seul** : l'hypothèse de complémentarité des erreurs (A10 de GLM) n'est pas soutenue sous cette forme (moyenne non pondérée, probabilités non recalibrées) ; un empilement ou une pondération appris resterait à tester.

## Variantes de recette du TF-IDF (fiche `2026-10-04-tfidf-variantes-recette`, EXPLORE, 5 plis par patient, 3 586 patients ; `tfidf-variants-minus-reference`)

| Variante | macro-F1 | écart avec la référence (0,6844) | IC 95 % (points) | p Holm | run_id |
|---|---|---|---|---|---|
| Poids de classe équilibrés | 0,6805 | −0,38 | [−1,87 ; +1,17] | 1,0 | `tfidf-variant-balanced` |
| N-grammes de caractères (3 à 5) | 0,6874 | +0,33 | [−1,32 ; +2,04] | 1,0 | `tfidf-variant-char` |
| **Caractères (3 à 5) et poids équilibrés** | **0,7202** | **+3,65** | **[+1,94 ; +5,48]** | **0,0** | `tfidf-variant-char-balanced` |

La combinaison n'est pas la somme des effets : seule elle améliore la référence, de façon résolue (borne basse positive, gain supérieur à δ = 2,0). Critère de la fiche : « amélioration » (EXPLORE ; la référence confirmatoire v1 ne change pas, une promotion exige une nouvelle version du protocole). Prédiction de la fiche (une variante améliore de plus de δ avec borne basse positive : probabilité 0,2) : réalisée. **La référence bon marché la plus forte est donc à 0,720, et l'écart avec le Qwen3.5-4B (0,587 au pli 0, TF-IDF 0,697 au même pli) s'élargit.** Le réglage de C est sur la grille réduite {10, 100, 1 000} ; les plis sont les mêmes que pour la référence. Coût : 13 minutes de CPU.

## Plafond d'erreur par accord entre modèles (pli 0, 717 patients, développement, agrégats ; EXPLORE)

Exactitude au pli 0 : TF-IDF 0,824 ; TF-IDF caractères et poids équilibrés 0,828 ; CamemBERT-bio 6 époques 0,809 ; Qwen3.5-4B 0,789 ; 9B 0,788 ; Gemma-4-E4B 0,689. **Au moins un des six modèles est juste pour 91,8 % des patients ; tous se trompent pour 8,2 % ; tous sont justes pour 59,6 %.** Les 8,2 % d'erreurs communes représentent 48 % des erreurs du meilleur modèle : près de la moitié de ses erreurs ne sont corrigées par aucun autre modèle, ce qui évoque une ambiguïté d'étiquette (diagnostic principal rival) plutôt qu'un défaut de modèle. Un vote majoritaire des six modèles donne 0,824, sans gain. Plafond utile d'un empilement : entre 0,83 et 0,92 d'exactitude, à ne pas confondre avec un résultat.

## Étalonnage conforme par plis d'auteurs (audit : fiabilité de l'incertitude sous décalage ; TF-IDF, probabilités hors pli par auteur, α = 0,10)

Étalonner sur quatre plis groupés par auteur et évaluer sur le cinquième : couverture LAC par pli 0,869 ; 0,895 ; 0,920 ; 0,909 ; 0,907, **moyenne 0,900**, 1,44 classe par ensemble (APS : 0,899, 12,6 classes). Contre 0,887 quand l'étalonnage vient des plis par patient et l'évaluation des plis par auteur (décalage). Étalonner par auteur rétablit la couverture visée sous décalage d'auteur, au prix d'une variabilité entre plis de 5 points.

## Hiérarchie CIM-10 comme supervision (fiche `2026-10-04-hierarchie-comme-supervision`, EXPLORE, TF-IDF, 5 plis ; `tfidf-hier-minus-reference`)

Entraîner sur les blocs CIM-10 puis agréger par chapitre : sans poids 0,6448 (**−3,99 points [−5,95 ; −2,08], dégradation résolue**) ; avec poids équilibrés 0,6740 (−1,05 [−2,69 ; +0,58], non résolu). **Piste non soutenue** : la supervision plus fine ne remonte pas le chapitre avec un TF-IDF ; les blocs rares ont trop peu d'exemples. Prédictions de la fiche : gain entre 0 et 3 points (0,45) et gain d'au moins 2 points (0,15) : faux ; perte (0,35) : vrai pour la version sans poids.

## Recette mûre de l'encodeur CamemBERT-bio (fiche `2026-10-04-encodeur-recette-mure`, EXPLORE, pli 0, graine 1000, 508 tokens tête et fin)

| Run | macro-F1 | exactitude | log loss | ECE | durée | run_id |
|---|---|---|---|---|---|---|
| 2 époques, 1e-4 (recette gelée) | 0,4484 | 0,770 | 1,015 | 0,176 | 43 s | `p1-07-camembert-bio-lr1e-4` |
| 6 époques, 1e-4 | 0,5527 | 0,809 | n/a ici | 0,049 | 128 s | `camembert-epoques-lr1e-4-ep6` |
| **10 époques, 1e-4** | **0,7714** | 0,833 | 0,739 | 0,107 | 215 s | `camembert-recette-lr1e-4-ep10` |
| 6 époques, 2e-4 | 0,6291 | 0,819 | 0,653 | 0,067 | 133 s | `camembert-recette-lr2e-4-ep6` |

**À 10 époques, CamemBERT-bio dépasse le TF-IDF du même pli de 7,4 points [+2,6 ; +12,9]** (`camembert-ep10-minus-tfidf-fold0` : 0,7714 contre 0,6971, « A meilleur », borne basse supérieure à δ = 2,0) **et le Qwen3.5-4B à 2 époques de 18,5 points [+12,7 ; +24,1]** (`camembert-ep10-minus-qwen4b-fold0`) ; contre sa propre version à 6 époques : +21,9 points [+16,5 ; +26,4]. Précautions : un pli, une graine, bruit de run de l'ordre du point ; le calcul d'ECE (0,107) montre un modèle sur-confiant à cette durée. La macro-F1 passe de 0,553 à 0,771 entre 6 et 10 époques, un saut qui suggère que les petits chapitres sont enfin appris (à vérifier par chapitre). Prédictions de la fiche : au moins un run dépasse 0,60 (0,5) : réalisé ; **aucun ne dépasse le TF-IDF du pli 0 (0,75) : faux**. **Conclusion à retenir : la conclusion « aucun modèle appris ne bat le TF-IDF » est un artefact de la recette gelée à 2 époques.** Les LLM LoRA à 2 époques sont très probablement sous-entraînés dans la même mesure : leur comparaison n'a pas été faite à recette mûre.

Suite de la recette mûre de l'encodeur (même fiche) : **2e-4, 10 époques : 0,6486** (exactitude 0,819, ECE 0,074, `camembert-recette-lr2e-4-ep10`), nettement sous 1e-4 à 10 époques (0,7714) : un taux plus élevé n'aide pas ; 1e-4 reste le meilleur des taux testés pour cette durée. Prédictions de la fiche : un des trois runs dépasse 0,60 (réalisé) ; aucun ne dépasse le TF-IDF du pli 0 (faux, voir plus haut).

## Encodeur par fenêtres, tout le dossier (fiche `2026-10-04-encodeur-par-fenetres`, EXPLORE, pli 0, graine 1000, fenêtres de 510 tokens, jusqu'à 8, logits moyennés)

| Run | macro-F1 | exactitude | durée | pic | comparaison appariée avec la même recette sans fenêtres |
|---|---|---|---|---|---|
| Fenêtres, 6 époques, 1e-4 | 0,5554 | 0,809 | 410 s | 11,9 Gio | +0,3 point [−2,1 ; +2,8], non résolu (`camembert-fenetres-ep6-minus-ep6-fold0`) |
| Fenêtres, 10 époques, 1e-4 | 0,7033 | 0,824 | 656 s | 13,5 Gio | **−6,8 points [−12,3 ; −2,4]**, plus bas (`camembert-fenetres-ep10-minus-ep10-fold0`) ; contre le TF-IDF du pli 0 : +0,6 [−4,2 ; +5,5], non résolu |

**Lire tout le dossier n'améliore pas l'encodeur** : gain nul à 6 époques, perte à 10 époques (mais la comparaison à 10 époques sans fenêtres, 0,7714, vient peut-être d'un tirage chanceux, à départager par les graines en cours). La moyenne des logits de fenêtres dilue peut-être le signal des fenêtres décisives (le diagnostic est en fin de dossier) ; une agrégation par maximum ou par attention n'a pas été testée. Prédictions de la fiche : gain de la variante (a) entre +1 et +8 points (0,55) : faux ; (a) dépasse la référence (0,75) : faux de justesse (+0,3, non résolu) ; (b) dépasse 0,62 (0,4) : réalisé ; (b) atteint ou dépasse le TF-IDF du pli 0 (0,15) : atteint, non résolu. Coût : 3 fois la durée pour un résultat non meilleur.
