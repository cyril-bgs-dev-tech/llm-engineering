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

## Mesure de service du TF-IDF déployable (audit : efficience et déploiement ; `bench-serving-tfidf-charbal-v1`, `scripts/bench_serving.py`, 200 patients du pli 0, un processus CPU)

Bundle `artifacts/models/tfidf_chapter_charbal_v1` (TF-IDF caractères 3 à 5, poids équilibrés, C = 10 ; température 0,855, quantile conforme LAC 0,893 et seuil d'abstention 0,703 calculés sur des prédictions hors pli groupées par auteur ; empreinte SHA-256 vérifiée au chargement) : **20,4 Mo, chargement 0,87 s, latence par patient p50 1,9 ms et p95 4,0 ms, 568 patients par seconde par lot de 300, pic de mémoire 484 Mo** (inclut le chargement des textes de mesure). À comparer avec le Qwen3.5-4B en bf16 : médiane 117 ms, p95 environ 290 ms sur GPU (P0-09), 15,5 Gio. Le TF-IDF est 60 fois plus rapide, sans GPU, et 700 fois plus léger.

Fiabilité de l'incertitude de CamemBERT-bio à 10 époques (`q5-uncertainty-camembert-ep10-fold0`, pli 0, étalonnage croisé en deux moitiés stratifiées du pli, EXPLORE) : ECE brute 0,106, **0,050 après température** (log loss 0,739 → 0,682) ; conforme LAC à 90 % : couverture 0,901 avec 1,53 classe par ensemble, par classe 0,922 (minimum 0,789) ; exactitude **0,865 à 90 %, 0,906 à 80 %, 0,946 à 70 % de couverture** (TF-IDF 0,931, 4B à 2 époques 0,892), AURC 0,049 (CamemBERT 6 époques 0,058, 4B 0,063). Plus long entraînement : modèle plus sur-confiant avant étalonnage, mais mieux calibré et plus sélectif après température ; le même périmètre limité s'applique (un pli, une graine, 358 patients d'étalonnage).

## Correction de priorité à l'inférence (audit GLM v4, A-c1 ; `prior-correction-fold0`, `results/measures/prior_correction.json` ; p' ∝ p / q^τ, q = prévalence d'entraînement, τ choisi sur une moitié du pli 0, évalué sur l'autre, rôles échangés ; EXPLORE)

| Modèle (pli 0) | macro-F1 τ = 0 | meilleur τ fixe | macro-F1 avec τ choisi par moitié |
|---|---|---|---|
| Qwen3.5-4B, 2 époques (rejeu) | 0,5756 | 0,5887 (τ = 0,25) | 0,5821 (+0,65) |
| Qwen3.5-4B, perte pondérée | 0,5632 | 0,5632 (τ = 0) | 0,5547 |
| CamemBERT-bio, 10 époques | 0,7677 | 0,7781 (τ = 0,75) | 0,7781 (+1,0) |
| **CamemBERT-bio, 6 époques** | 0,5510 | **0,6889 (τ = 1)** | **0,6889 (+13,8)** |

La conjecture de GLM (+2 à +8 points sur le 4B) **n'est pas soutenue** : la correction n'apporte que +0,65 au 4B à 2 époques et rien à la version pondérée. En revanche, elle récupère **+13,8 points** pour l'encodeur à 6 époques (0,551 → 0,689) et c'est le même mécanisme que le saut de 6 à 10 époques : un modèle qui n'a pas fini d'apprendre les chapitres rares les sous-prédit, et la correction de prévalence (gratuite) en récupère une partie ; à 10 époques le modèle a appris et la correction ne sert presque plus (+1,0). Lecture : le déficit des petits chapitres vient d'un sous-apprentissage de la queue de distribution, que l'entraînement plus long ou la correction de priorité peuvent combler ; le 4B à 2 époques n'en bénéficie pas parce que son déficit est plus général (0,59 contre 0,77).

## Saturation de la durée, rejeu et quantification de l'encodeur (fiches `2026-10-04-encodeur-saturation-et-graines` et `2026-10-04-encodeur-recette-mure`, EXPLORE, pli 0, 1e-4, 508 tokens)

| Run | graine | macro-F1 | exactitude | ECE | run_id |
|---|---|---|---|---|---|
| 10 époques (premier) | 1000 | 0,7714 | 0,833 | 0,107 | `camembert-recette-lr1e-4-ep10` |
| 10 époques (rejeu pour sauvegarde du modèle) | 1000 | 0,7362 | 0,830 | 0,111 | `camembert-deploy-ep10-lr1e-4` |
| 10 époques | 1001 | 0,7079 | 0,813 | 0,110 | `camembert-graine-ep10-s1` |
| 15 époques | 1000 | 0,7425 | 0,824 | 0,140 | `camembert-saturation-ep15` |
| 20 époques | 1000 | 0,7384 | 0,834 | 0,140 | `camembert-saturation-ep20` |

**Le 0,7714 était un tirage favorable** : à graine égale, le rejeu fait 0,7362 (−3,5 points, non-déterminisme GPU) et la graine 1001 donne 0,7079. Les écarts entre runs atteignent 6 points, bien plus que le bruit d'un point mesuré sur le 4B : les chapitres rares, appris ou non selon le tirage, rendent la macro-F1 de l'encodeur très variable. La durée sature : 10, 15 et 20 époques sont équivalentes (0,74 environ). Lecture honnête : l'encodeur à 10 époques et plus vaut environ 0,71 à 0,77 contre 0,6971 pour le TF-IDF du pli 0 et 0,72 pour sa meilleure recette ; **l'avantage de l'encodeur existe en moyenne probable mais n'est pas établi par un tirage** ; les cinq graines tranchent. Prédictions de la fiche : 15 époques ≥ 10 époques (0,55) : faux de justesse selon la graine ; saturation avant 20 époques (0,65) : vrai.

**Quantification INT8 dynamique de l'encodeur** (`quantization-camembert-deploy-ep10-lr1e-4`, PyTorch `quantize_dynamic` sur toutes les couches linéaires, CPU, 8 threads, pli 0) : flottant 32 bits macro-F1 0,7362, latence p50 190,8 ms et p95 210,0 ms, 443 Mo ; **INT8 : macro-F1 0,3356, exactitude 0,527 (effondrement)**, latence p50 118,4 ms, p95 137,4 ms, 25 Mo. La quantification dynamique naïve détruit la qualité (probablement les couches d'embeddings et de normalisation, ou le comportement sur-confiant de ce modèle) : **non utilisable telle quelle** ; une quantification statique avec étalonnage ou la quantification sélective des seules couches de la partie dense resterait à tester. Le TF-IDF déployable fait p50 1,9 ms : 100 fois plus rapide que l'encodeur en flottant.

## Table d'abstention par modèle (audit GLM v4, E-c2, E-c3 ; `results/measures/abstention_table.json`, pli 0, 717 patients, confiance = probabilité maximale, exactitude des patients traités avec Wilson 95 %)

| Modèle | 100 % de couverture | 90 % | 80 % | 70 % (30 % renvoyés) | 50 % |
|---|---|---|---|---|---|
| TF-IDF | 0,824 | 0,868 | 0,902 | 0,940 [0,916 ; 0,958] | 0,975 |
| TF-IDF caractères et poids équilibrés | 0,828 | 0,870 | 0,906 | 0,934 [0,909 ; 0,953] | 0,978 |
| CamemBERT-bio 10 époques (graine 1000) | 0,833 | 0,865 | 0,906 | 0,946 [0,923 ; 0,963] | 0,961 |
| CamemBERT-bio 10 époques (rejeu) | 0,830 | 0,860 | 0,904 | 0,930 [0,905 ; 0,949] | 0,964 |
| Qwen3.5-4B, 2 époques | 0,781 | 0,823 | 0,868 | 0,892 [0,862 ; 0,917] | 0,969 |

Les trois premières familles bien réglées ne se distinguent pas par la politique d'abstention (intervalles qui se recouvrent) : ce que l'encodeur gagne en macro-F1 vient des chapitres rares, pas du tri des cas faciles. Un renvoi de 30 % des patients à l'humain amène l'exactitude des cas traités à 0,93 environ ; mesuré en développement, jamais validé sur le test, et c'est la politique du modèle, non du système complet.

« Classe jamais couverte » du TF-IDF (`q5-uncertainty-tfidf-chapter`, LAC 90 %) : c'est la classe `AUTRE` (18 patients au développement), couverture 0/18, Wilson [0 ; 0,176]. C'est la classe fourre-tout (chapitres VII, VIII, XVI et XVII fusionnés), **exclue de la macro-F1** ; ce n'est pas un défaut de couverture sur un chapitre évalué (les plus basses sont XXI avec 0,21 et IV avec 0,40, effectifs de 49 et 56 au développement : leurs intervalles de Wilson sont larges).

## Cinq graines de l'encodeur à 10 époques et règle de puissance (fiche `2026-10-04-encodeur-saturation-et-graines`, EXPLORE, pli 0, 1e-4, graines 1000 à 1004)

macro-F1 : 0,7714 ; 0,7079 ; 0,7175 ; 0,7148 ; 0,7349. **Moyenne 0,7293, écart-type 0,0256, étendue 6,4 points.** Prédiction de la fiche (écart-type entre 1,5 et 6 points, probabilité 0,7) : réalisée ; la moyenne des cinq graines reste au-dessus du TF-IDF du pli 0 (0,6971, probabilité 0,8) : réalisée en moyenne (+3,2 points) mais **aucune graine individuelle sauf la première n'est résolue** :

| Graine | macro-F1 | contre TF-IDF v1 (0,6971) [IC 95 %] | contre TF-IDF caractères et poids équilibrés (0,7184) [IC 95 %] |
|---|---|---|---|
| 1000 | 0,7714 | +7,75 [+2,5 ; +13,4], p Holm 0,02 | +5,5 [+0,6 ; +10,7], p Holm 0,13 |
| 1001 | 0,7079 | +1,3 [−4,8 ; +7,5] | −0,9 [−7,4 ; +5,3] |
| 1002 | 0,7175 | +2,2 [−5,3 ; +9,5] | −0,0 [−7,0 ; +6,9] |
| 1003 | 0,7148 | +2,2 [−3,9 ; +8,4] | −0,1 [−5,9 ; +5,9] |
| 1004 | 0,7349 | +4,0 [−2,5 ; +10,6] | +1,8 [−4,1 ; +7,6] |

**Correction de l'affirmation précédente** : à recette mûre, l'encodeur (0,73 en moyenne) et la meilleure recette du TF-IDF (0,72 sur le même pli) sont **équivalents** ; seul le premier tirage de l'encodeur sort du lot. Le « retournement » de la nuit est donc surtout : (1) la recette gelée à 2 époques sous-estimait fortement l'encodeur et les LLM (de 0,45 à 0,73) ; (2) le TF-IDF bien réglé est un concurrent à 20 Mo et 2 ms qui n'est pas dépassé de façon établie par un encodeur de 443 Mo à 190 ms.

**Règle de puissance sur les cinq graines de l'encodeur** (`rm-17-power-rule-encodeur-ep10`, R = 10 000, graine de bootstrap 20261002, effectifs de strate du test scellé, EXPLORE ; ce n'est pas la règle du protocole, qui vise la LoRA de référence) : largeurs d'IC par paire de 10,4 à 14,1 points, **largeur moyenne 12,2 points contre un seuil de 4,0 : la règle échoue**, comme les simulations l'annonçaient (7,8 à 13,7). Conséquence : les comparaisons confirmatoires de cette famille seraient classées EXPLORE ; la largeur provient de la variabilité entre graines (écart-type 2,6 points) et de la taille des petits chapitres.

## Discrétisation des petites classes (hypothèse de Cyril du 04/10 ; `scripts/split_discretization_check.py`, `results/measures/split_discretization_check.json`, prédictions hors pli du TF-IDF sur cinq plis par patient, bootstrap stratifié de 2 000 répliques)

**Les cinq plus petites classes (IV, V, XII, XXI, XXII) portent 85,1 % de la variance bootstrap de la macro-F1** : XXII 26,1 %, XII 20,8 %, XXI 16,5 %, IV 13,6 %, V 8,2 % ; les douze autres classes se partagent les 14,9 % restants (le chapitre II seul : 0,1 %). L'écart-type bootstrap de la macro-F1 regroupée est de **1,3 point** (n = 3 586 prédictions) : pour un seul pli de 717 patients il est environ deux fois plus grand. La métrique est donc surtout une mesure de cinq classes de 27 à 63 patients ; chaque patient de ces classes déplace la macro-F1 de 0,2 à 0,5 point, et c'est la source principale du bruit entre graines (écart-type de l'encodeur : 2,6 points). Conséquence de conception : comparer deux recettes sur un pli unique ne distingue pas moins de 3 points ; la log loss équilibrée par chapitre (secondaire) et les plis répétés réduisent ce bruit. L'écart patient moins auteur sur partitions répétées est en calcul.

## Couverture conforme par famille de chapitres (audit GLM v4, E-c1 sous forme de familles ; `coverage-by-family-tfidf`, TF-IDF, LAC 90 %, étalonnage croisé par plis par patient, développement, 3 586 patients, Wilson 95 %)

| Famille | patients | couverture | Wilson 95 % |
|---|---|---|---|
| Grossesse | 148 | 0,993 | [0,963 ; 0,999] |
| Digestif | 312 | 0,978 | [0,954 ; 0,989] |
| Circulatoire et respiratoire | 704 | 0,970 | [0,955 ; 0,980] |
| Infectieux, tumeurs, sang | 1 254 | 0,951 | [0,938 ; 0,962] |
| Peau, muscle, urinaire | 513 | 0,932 | [0,907 ; 0,951] |
| Nerveux | 108 | 0,759 | [0,671 ; 0,830] |
| Symptômes, lésions, facteurs | 432 | 0,662 | [0,616 ; 0,705] |
| Endocrinien et mental | 101 | 0,564 | [0,467 ; 0,657] |
| Autre (`AUTRE`) | 14 | 0,000 | [0 ; 0,215] |

**La couverture marginale de 0,90 est une moyenne qui cache des familles à 0,56 et 0,66** : les familles faciles sont sur-couvertes (0,93 à 0,99) et les difficiles sous-couvertes (endocrinien et mental, symptômes et lésions, nerveux), exactement celles où le diagnostic est ambigu. Une politique d'abstention ou d'ensembles qui s'appuierait sur la couverture marginale tromperait l'utilisateur sur ces familles ; l'étalonnage conditionnel (par classe ou par famille, de type Mondrian) corrige le niveau, au prix d'ensembles plus grands, déjà mesuré par classe (0,904, minimum 0,893 sur les classes de plus de 20 patients). À rapporter dans tout résultat d'incertitude : couverture par famille avec Wilson, pas seulement la marginale.

Écart patient contre auteur sur partitions répétées (`split-discretization-check`, TF-IDF mots (1, 2), C = 100 fixe, 5 plis, trois graines de partition ; `StratifiedKFold` par patient contre `StratifiedGroupKFold` par auteur) : macro-F1 par patient 0,6364 ; 0,6408 ; 0,6428 ; par groupes d'auteurs 0,5894 pour les trois graines ; **écart de 4,7 ; 5,1 ; 5,3 points, moyenne 5,06**. Avec des classes réparties au mieux sous la contrainte de groupe, **l'écart n'est donc pas un artefact de composition des plis** : il est même plus grand que celui de RM-14 (3,9 points, plis de contrôle non optimisés). Limite : le découpage par groupes donne la même partition pour les trois graines (les groupes de tailles distinctes sont placés de façon déterministe), la répétition ne vaut que pour le schéma par patient. La discrétisation des petites classes explique le bruit des mesures (85 % de la variance), pas la direction de l'écart d'auteur.

## Leave-one-author-out du TF-IDF : estimation « nouveaux auteurs » (audit GLM v4, F-c1 ; run `tfidf-loao`, `scripts/loao_tfidf.py`, 66 auteurs d'au moins 20 patients, 3 234 patients, TF-IDF mots (1, 2), C = 100 fixe, EXPLORE)

macro-F1 **0,6185**, exactitude 0,804, log loss 0,675. Repères : sur les mêmes patients, le TF-IDF de référence (configuration choisie par pli) fait 0,6996 par patient et 0,6555 par plis d'auteurs ; à configuration fixe égale (C = 100, mots (1, 2)), les plis par patient donnent 0,636 à 0,643 et les plis de groupes d'auteurs 0,589. **À configuration égale, nouveaux auteurs (0,6185) se situe 2,2 à 2,4 points sous patients et 3 points au-dessus de cinq groupes d'auteurs** : une grande part de l'écart des plis groupés vient du rétrécissement de l'entraînement (on retire 20 % des auteurs, donc des chapitres entiers pour les auteurs spécialisés), non de la signature d'auteur seule ; retirer un seul auteur isole mieux l'effet d'auteur. **Lecture départagée (provisoire, un modèle, une configuration)** : la fuite par signature d'auteur existe mais pèse environ 2 points, pas 4 à 5. Prudence : les sous-ensembles diffèrent (66 auteurs de plus de 20 patients, 90 % des patients), la comparaison est approchée. Conséquence pour ADR-013 : le déclencheur « écart supérieur à 3 points » du candidat final se mesure en leave-one-author-out, pas en plis groupés.

## Ensemble encodeur (cinq graines) et TF-IDF à recette mûre (EXPLORE, pli 0, 717 patients ; `ensembles-minus-tfidf-charbal`, `results/measures/ensemble_fold0.json` pour les ensembles de la première nuit)

| Système | macro-F1 | contre le TF-IDF caractères et poids équilibrés (0,7184) |
|---|---|---|
| Encodeur, une graine (0,708 à 0,771) | 0,7293 en moyenne | non résolu |
| Encodeur, moyenne des probabilités des 5 graines | 0,7331 | +1,53 [−4,43 ; +7,51], non résolu |
| **Encodeur (5 graines) + TF-IDF caractères et poids équilibrés, moyenne 50/50** | **0,7626** | **+4,54 [+1,43 ; +8,00], p Holm 0,005, résolu** |

Les pondérations essayées : 0,3 (0,7271), 0,5 (0,7626), 0,7 (0,7618) et une moyenne géométrique 50/50 (0,7692) ; seule la pondération 0,5 est comparée ci-dessus (essai le plus simple, deuxième sur trois : optimisme de sélection faible mais non nul). **Les deux familles bien réglées sont complémentaires** : leur moyenne dépasse chacune d'au moins 3 à 4 points, alors que les ensembles de la première nuit (encodeur à 6 époques ou LLM à 2 époques, sous-entraînés) ne battaient pas le TF-IDF. C'est la première amélioration résolue de la meilleure référence bon marché. Coût : environ 20 minutes de GPU pour cinq encodeurs, 13 minutes de CPU pour le TF-IDF, et une inférence d'environ 1 s par patient en CPU (cinq encodeurs de 190 ms). À confirmer par un second pli avant toute affirmation ; EXPLORE, hors famille confirmatoire.

## Qwen3.5-4B à 10 époques : premier lancement interrompu (fiche `2026-10-04-llm-recette-mure-qwen4b`, run `20261004-030327-llm-mur-qwen3-5-4b-ep10-lr1e-4`, statut `aborted`)

Arrêt anticipé par la règle écrite d'avance après 90 pas (une époque, 43 minutes) : durée projetée 23 383 s au-delà de la limite de 22 700 s. Pas moyen de 28,6 s contre 16,8 s pour le run à 2 époques sur GPU libre : le lancement a partagé la carte avec des runs d'encodeur et le processeur avec des calculs lourds. Aucune macro-F1 produite. Relance en exclusivité décidée (fiche v2 hachée, un seul essai) après les runs d'encodeur du pli 1. Leçon (N25) : un lot d'estimation serrée ne partage ni le GPU ni le processeur.

## Confirmation de l'ensemble au pli 1 (fiche `2026-10-04-confirmation-ensemble-pli1`, EXPLORE, pli 1, 718 patients, cinq encodeurs graines 1000 à 1004 entraînés sur les plis 0, 2, 3, 4 ; `pli1-encodeur-ensembles-minus-tfidf-charbal`)

| Système (pli 1) | macro-F1 | contre le TF-IDF caractères et poids équilibrés (0,6886) [IC 95 %] |
|---|---|---|
| Encodeur, graines 1000 à 1004 | 0,7605 ; 0,7763 ; 0,7679 ; 0,7080 ; 0,7247 (moyenne 0,7475) | +7,3 [+1,4 ; +13,2] ; +8,9 [+3,7 ; +14,2] ; +8,0 [+2,6 ; +13,4] ; +2,0 [−3,7 ; +7,7] ; +3,6 [−2,3 ; +9,5] |
| Encodeur, moyenne des 5 graines | 0,7532 | +6,4 [+0,8 ; +12,1] |
| **Ensemble 50/50 encodeur (5 graines) + TF-IDF** | **0,7512** | **+6,2 [+1,4 ; +11,2]**, p Holm 0,052 sur les sept comparaisons du tableau |

**Critère de la fiche satisfait** (borne basse de l'IC 95 % de « ensemble moins TF-IDF » supérieure à 0 au pli 1). **Mais l'apport propre de l'ensemble n'est pas confirmé** : au pli 1 le TF-IDF n'ajoute rien à l'encodeur moyenné sur cinq graines (0,7512 contre 0,7532), alors qu'au pli 0 l'ensemble gagnait 3 points sur l'encodeur moyenné (0,7626 contre 0,7331). Synthèse sur les deux plis : l'encodeur mûr (moyenne de cinq graines) bat le meilleur TF-IDF de +1,5 (pli 0, non résolu) et +6,4 (pli 1) points, soit environ +4 points en moyenne ; l'ensemble encodeur + TF-IDF le bat de +4,5 et +6,2, soit environ +5,4 points ; le gain de l'ensemble sur l'encodeur moyenné est +3,0 puis −0,2. **Conclusion mesurée** : le meilleur système bon marché est une moyenne de graines d'encodeurs mûrs, à compléter éventuellement par le TF-IDF ; l'avantage de l'encodeur sur le TF-IDF est positif aux deux plis mais plus faible et plus variable qu'annoncé la nuit. Prédictions de la fiche : l'ensemble dépasse le TF-IDF (0,8) : vrai ; IC entièrement positif (0,5) : vrai ; écart plus petit qu'au pli 0 (0,65) : faux (plus grand) ; l'ensemble dépasse l'encodeur seul (0,75) : faux contre la moyenne de 5 graines (−0,2).

## Qwen3.5-4B LoRA à 10 époques (fiche `2026-10-04-llm-recette-mure-qwen4b-v2`, EXPLORE, pli 0, graine 1000, taux 1e-4, 4 096 tokens, GPU libre ; run `20261004-070113-llm-mur2-qwen3-5-4b-ep10-lr1e-4`)

**macro-F1 0,7795**, exactitude 0,858, log loss 0,817, ECE brute 0,108, 12 467 s d'entraînement (3,5 h, pic 12,9 Gio) ; probabilités et adaptateur conservés (`adapter_sha256` au registre). **Aucun chapitre à F1 nulle** (XXII 1,00, IV 0,75, V 0,75, XXI 0,46, XII 0,55). Pour mémoire : même modèle à 2 époques 0,587 ; **le passage de 2 à 10 époques vaut +19,3 points [+14,0 ; +25,0]** (`llm-mur2-minus-4b-2ep-fold0`).

| Comparaison appariée (pli 0, 717 patients) | écart | IC 95 % | p Holm |
|---|---|---|---|
| LoRA 10 époques moins TF-IDF v1 (0,6971) | +8,2 points | [+3,6 ; +14,3] | résolu (`llm-mur2-minus-tfidf-fold0`) |
| moins TF-IDF caractères et poids (0,7184) | +6,4 | [+2,0 ; +11,4] | 0,005 |
| moins encodeur moyenné sur 5 graines (0,7331) | +4,9 | [−0,35 ; +10,5] | 0,15, non résolu |
| Ensemble 50/50 LoRA + encodeur (0,7926) moins encodeur moyenné | +6,1 | [+1,2 ; +11,4] | 0,06 |
| Ensemble 50/50 LoRA + encodeur (0,7926) moins TF-IDF caractères et poids | +7,6 | [+3,5 ; +12,0] | 0,001 |
| Ensemble des trois (0,7937) moins TF-IDF caractères et poids | +7,7 | [+4,2 ; +11,7] | 0,000 |

**À recette mûre le LLM LoRA est le meilleur modèle unique mesuré du pli 0 (une graine), au-dessus du meilleur TF-IDF de façon résolue et non distinct de l'encodeur moyenné sur cinq graines.** La phrase « les LLM perdent contre le TF-IDF » est définitivement réfutée pour la recette gelée à 2 époques : le déficit de 11 points était du sous-entraînement. Précautions : une seule graine (l'écart-type entre graines de l'encodeur est de 2,6 points, un tirage favorable de 5 points est possible, comme pour l'encodeur 0,7714), un pli, un coût de 3,5 h contre 4 minutes pour l'encodeur. L'ensemble LoRA + encodeur monte à 0,7926 (+6,1 sur l'encodeur moyenné, Holm 0,06).

**Incertitude du LoRA mûr** (`q5-uncertainty-llm-mur2-fold0`, étalonnage croisé en deux moitiés du pli) : ECE 0,110 brute et **0,028 après température** (la meilleure des modèles mesurés), log loss 0,817 → 0,478 ; conforme LAC 90 % : couverture 0,909 avec **1,15 classe par ensemble**, par classe 0,923 (minimum 0,864) ; exactitude **0,905 à 90 %, 0,937 à 80 %, 0,960 à 70 % de couverture** (encodeur 0,946, TF-IDF 0,931–0,940), AURC 0,037 (encodeur 0,049). Pour la politique d'abstention, le LoRA mûr est le meilleur des modèles mesurés (30 % de renvois à l'humain : 0,960 d'exactitude sur les cas traités), mêmes réserves de périmètre.

Prédictions de la fiche : macro-F1 entre 0,65 et 0,80 (0,6) : réalisé (0,7795, juste sous la borne haute) ; égal ou supérieur à l'encodeur à 10 époques (0,35) : réalisé (IC contenant 0) ; supérieur au TF-IDF du pli 0 avec IC entièrement positif (0,45) : réalisé ; au moins un des chapitres XII, XXI, XXII quitte zéro (0,85) : réalisé ; l'arrêt anticipé ne se déclenche pas sur GPU libre (0,8) : réalisé.

## Confirmation du Qwen3.5-4B LoRA à 10 époques au pli 1 (fiche `2026-10-04-llm-mur-pli1`, EXPLORE, pli 1, 718 patients, graine 1000 ; run `20261004-104947-llm-mur-pli1-qwen3-5-4b-ep10-lr1e-4`)

**macro-F1 0,7415**, exactitude 0,855, log loss 0,814, 12 421 s d'entraînement. Comparaisons appariées au pli 1 (`pli1-llm10-et-ensembles-minus-*`) :

| Système (pli 1) | macro-F1 | contre TF-IDF caractères et poids (0,6886) | contre l'encodeur moyenné (0,7532) |
|---|---|---|---|
| LoRA 10 époques | 0,7415 | **+5,3 [+0,75 ; +9,95], Holm 0,02, résolu** | −1,1 [−6,0 ; +4,0], non résolu |
| Ensemble 50/50 LoRA + encodeur moyenné | 0,7603 | +7,2 [+2,6 ; +11,9] | +0,8 [−3,9 ; +5,6] |
| Ensemble des trois (LoRA, encodeur, TF-IDF) | 0,7643 | +7,6 [+3,1 ; +12,0] | +1,2 [−3,2 ; +5,6] |

**Synthèse sur les deux plis (une graine pour le LoRA, cinq graines moyennées pour l'encodeur)** :
- LoRA mûr contre le meilleur TF-IDF : +6,4 puis +5,3 points, **résolu aux deux plis** (moyenne +5,9).
- LoRA mûr contre l'encodeur moyenné : +4,9 puis −1,1, **non résolu** (moyenne +1,9) : le LoRA rattrape l'encodeur moyenné sans le dépasser de façon établie.
- Encodeur moyenné contre le meilleur TF-IDF : +1,5 puis +6,4 (moyenne +4,0).
- Les ensembles n'apportent pas de gain établi par rapport au meilleur composant (+6,1 puis +0,8 pour LoRA + encodeur sur l'encodeur moyenné).

**Rapport qualité par coût** : le LoRA mûr coûte 3,5 h de GPU par pli contre 20 minutes pour cinq encodeurs (environ 10 fois plus) pour un score statistiquement équivalent ; son avantage mesuré est dans l'incertitude : au pli 1 ECE 0,111 brute et 0,034 après température, couverture conforme LAC 0,9025 avec 1,17 classe par ensemble, exactitude 0,904 à 90 %, 0,937 à 80 % et **0,964 à 70 % de couverture** (pli 0 : 0,960 ; encodeur : 0,946), AURC 0,033 : **la sélectivité du LoRA est la meilleure des modèles mesurés sur les deux plis**. Prédictions de la fiche : macro-F1 du pli 1 entre 0,70 et 0,82 (0,7) : réalisé ; le LoRA dépasse le TF-IDF, IC entièrement positif (0,75) : réalisé ; le LoRA au moins égal à l'encodeur moyenné (0,55) : réalisé (IC contenant 0) ; le LoRA dépasse l'encodeur moyenné, IC entièrement positif (0,15) : non.

## Robustesse du LoRA mûr aux perturbations de texte (audit GLM v4, C5-A5 ; `robustness-llm-mur2-qwen3-5-4b-ep10-lr1e-4`, inférence sur l'adaptateur sauvegardé, pli 0, 717 patients, mêmes perturbations et même graine que pour le TF-IDF ; EXPLORE)

| Variante du texte | macro-F1 du LoRA mûr | écart avec le texte propre | TF-IDF (même perturbation) |
|---|---|---|---|
| Propre (contrôle : redonne exactement le score du run) | 0,7795 | | 0,697 |
| Accents retirés | 0,7744 | −0,5 | **−5,6** (0,641) |
| Fautes de frappe sur 5 % des mots | 0,7950 | +1,6 | −0,7 |
| Majuscules sur 5 % des mots | 0,7663 | −1,3 | 0 (casse normalisée) |

Les écarts du LoRA restent dans le bruit de mesure d'un pli (écart-type bootstrap de 1,3 point sur 3 586 prédictions, environ le double sur 717) : **le LoRA mûr est insensible à ces trois perturbations, là où le TF-IDF perd 5,6 points sans accents**. Limite : perturbations douces (5 % des mots), un pli, une graine ; ni abréviations réelles, ni autre style d'auteur. Le contrôle de cohérence (texte propre = 0,7795 = macro-F1 du run d'entraînement) valide le rechargement de l'adaptateur.

## Troisième pli de l'encodeur (fiche `2026-10-04-confirmation-pli2-et-graine-lora`, EXPLORE, pli 2, 717 patients, cinq graines 1000 à 1004 entraînées sur les plis 0, 1, 3, 4 ; `pli2-encodeur-minus-tfidf-charbal`)

| Système (pli 2) | macro-F1 | contre le TF-IDF caractères et poids (0,7483) [IC 95 %] |
|---|---|---|
| Encodeur, graines 1000 à 1004 | 0,7392 ; 0,7428 ; 0,7705 ; 0,7675 ; 0,7481 (moyenne 0,7536) | −0,9 ; −0,6 ; +2,4 ; +1,9 ; +0,0 (tous non résolus) |
| Encodeur moyenné sur 5 graines | 0,7613 | +1,2 [−3,6 ; +5,9], non résolu |
| **Ensemble 50/50 encodeur (5 graines) + TF-IDF** | **0,7923** | **+4,3 [+1,2 ; +7,5], Holm 0,042, résolu** |

**Synthèse sur les trois plis** (contre le TF-IDF caractères et poids équilibrés, même pli) :

| Système | pli 0 | pli 1 | pli 2 | moyenne |
|---|---|---|---|---|
| Encodeur moyenné (5 graines) | +1,5 | +6,4 | +1,2 | +3,0 |
| Ensemble encodeur + TF-IDF | +4,5 | +6,2 | +4,3 | **+5,0 (résolu aux trois plis)** |
| LoRA mûr (une graine, deux plis) | +6,4 | +5,3 | n/a | +5,9 |

Le gain de l'ensemble sur l'encodeur moyenné seul : +3,0 ; −0,2 ; +3,0 (moyenne +2,0). **L'ensemble encodeur + TF-IDF est le système bon marché le plus constant : son avantage de 4,3 à 6,2 points sur le meilleur TF-IDF est résolu à chacun des trois plis**, ce que l'encodeur moyenné seul n'obtient pas (non résolu aux plis 0 et 2). Coût : 20 minutes de GPU par pli pour cinq encodeurs plus 13 minutes de CPU pour le TF-IDF. Prédictions de la fiche : l'encodeur moyenné dépasse le TF-IDF au pli 2 (0,8) : réalisé en valeur ; IC entièrement positif (0,45) : non.

## Plafond d'ambiguïté (top-k) et étalonnage conditionnel par famille (brainstorm du 04/10 ; pli 0, 717 patients, EXPLORE ; calculs de contrôle sans run enregistré, à rejouer par script avant toute citation externe)

Exactitude top-1, top-2 et top-3 : LoRA mûr 0,858 / 0,950 / 0,975 ; encodeur moyenné 0,835 / 0,936 / 0,968 ; ensemble LoRA + encodeur + TF-IDF 0,870 / 0,958 / 0,983 ; TF-IDF 0,823 / 0,916 / 0,961. **Le bon chapitre est dans les deux premiers dans 95 % des cas** : la confusion est surtout entre deux diagnostics rivaux.

**Correction (04/10, après relecture de mon propre calcul)** : le calcul de contrôle précédent de l'étalonnage « par famille » utilisait la famille de la **vraie** classe du patient pour choisir le quantile au moment de la prédiction, ce qui revient à lire l'étiquette : ses chiffres (couverture 0,87 avec 1,59 classe par ensemble) sont **invalides et retirés**. La version correcte (`conformal.fit_by_group`, `predict_sets_by_group` : une classe candidate entre dans l'ensemble si son score est sous le quantile de sa famille ; test synthétique ; `scripts/conformal_by_family.py`, run `conformal-by-family`) donne :

| Jeu | couverture marginale | taille | couverture minimale par famille | par famille : couverture | taille | couverture minimale par famille |
|---|---|---|---|---|---|---|
| TF-IDF 5 plis | 0.901 | 1.3 | 0.564 | 0.901 | 2.05 | 0.896 |
| LoRA mûr pli 0 | 0.909 | 1.15 | 0.647 | 0.894 | 2.74 | 0.8 |
| LoRA mûr pli 1 | 0.903 | 1.17 | 0.663 | 0.905 | 2.74 | 0.864 |
| Encodeur moyenné pli 0 | 0.902 | 1.2 | 0.682 | 0.905 | 3.56 | 0.85 |

L'étalonnage conditionnel par famille relève la couverture de la famille la moins bien couverte de 0,56 à 0,90 (TF-IDF, cinq plis), de 0,65 à 0,80 et de 0,66 à 0,86 (LoRA mûr, plis 0 et 1), de 0,68 à 0,85 (encodeur moyenné), **mais multiplie la taille des ensembles par 1,6 à 3** (de 1,15 à 2,74 pour le LoRA, de 1,2 à 3,56 pour l'encodeur) : le coût de l'équité par famille est élevé. Arbitrage à poser avec l'utilisateur (renvoi à l'humain d'un cas à deux candidats contre un cas à trois ou quatre) ; l'option intermédiaire est de n'appliquer la correction qu'aux deux ou trois familles ambiguës (symptômes et lésions, nerveux, endocrinien et mental).

## Taxonomie d'erreurs sur cinq plis (brainstorm, point 5 ; `error-taxonomy-tfidf-5plis`, `results/measures/error_taxonomy.json`, TF-IDF caractères et poids équilibrés, 3 586 prédictions hors pli, agrégats seulement)

Exactitude top-1 0,822, top-2 0,926 ; 638 erreurs. **Paires de confusion les plus fréquentes** : II → XIV (36), XVIII → X (27), XVIII → VI (27), XVIII → IX (26), II → XI (25), XVIII → XIV (22) : le chapitre XVIII (symptômes et signes non classés) et le II (tumeurs) sont les sources. **Erreurs confiantes** (probabilité de la bonne classe sous 0,10 pour une classe prédite au-dessus de 0,90) : 65 patients, soit 1,8 % des patients et 10,2 % des erreurs, dont XVIII 25, II 11, XXI 8, VI 6 : candidats à un audit d'étiquette (cas où le modèle est sûr et « faux »), à instruire sur l'étiquette source sans lire de texte dans une sortie. **Par spécialité**, les plus difficiles (top-1 / top-2) : pédiatrie 0,52 / 0,69, gériatrie 0,54 / 0,68, neurologie 0,59 / 0,84, médecine interne 0,68 / 0,83, néphrologie 0,64 / 0,84 : dans les spécialités à diagnostics multiples, même le top-2 est faible (0,68 à 0,69 pour pédiatrie et gériatrie). **Par longueur** : court 0,877, moyen 0,774, long 0,815 (effet de composition déjà expliqué).

## Entraînement débiaisé par auteur du TF-IDF (fiche `2026-10-04-debiaisage-auteur-tfidf`, EXPLORE, TF-IDF mots (1, 2), C = 100, cinq plis, graine 1 ; `author-debias-tfidf`)

| Poids d'exemples | par patient | par groupes d'auteurs | écart patient moins auteur |
|---|---|---|---|
| Aucun | 0,6364 | 0,5894 | 4,70 |
| ∝ 1 / volume d'auteur (« inv ») | 0,6381 | 0,5855 | 5,26 |
| ∝ 1 / √volume d'auteur (« invsqrt ») | 0,6412 | 0,5872 | 5,40 |

**Aucun effet** : la généralisation à de nouveaux auteurs ne progresse pas (−0,4 et −0,2 point sur plis groupés), l'écart patient moins auteur grandit légèrement. Les trois prédictions de la fiche sont fausses (gain d'au moins 1 point sur plis groupés : probabilité 0,3 ; perte de plus d'un point par patient : 0,45 ; réduction de l'écart : 0,5). La part « signature d'auteur » de l'écart ne se corrige pas par une pondération d'exemples ; elle est liée au contenu (thèmes d'auteurs spécialisés), non à la seule fréquence. Piste fermée.

## Perturbations et ablations du TF-IDF caractères et poids équilibrés (audit GLM v4, C5 ; `ablation-tfidf-charbal-fold0`, pli 0, entraînement sur les plis 1 à 4, EXPLORE)

| Variante du texte | macro-F1 | écart avec le texte propre (0,7135) |
|---|---|---|
| Accents retirés | 0,7235 | +1,0 |
| Fautes de frappe sur 5 % des mots | 0,7125 | −0,1 |
| Majuscules sur 5 % des mots | 0,7135 | 0 |
| **Fin retirée (30 % des mots)** | 0,7122 | −0,1 |
| Début retiré (30 % des mots) | 0,7071 | −0,6 |

**Rectification de la comparaison de robustesse** : la perte de 5,6 points sans accents mesurée plus haut concerne le **TF-IDF à mots (référence v1)**, pas la meilleure recette. Le TF-IDF à n-grammes de caractères est insensible à toutes les perturbations de forme (±1 point) et aux ablations de contenu (retirer 30 % de la fin ou du début ne coûte que 0,1 à 0,6 point : l'information diagnostique est répartie dans le texte, pas concentrée en conclusion). Le LoRA mûr (−0,5, +1,6, −1,3 sur les trois perturbations de forme) n'est donc pas plus robuste que le meilleur TF-IDF ; l'avantage de robustesse du LoRA est face au TF-IDF à mots seulement. Les ablations de contenu sur le LoRA et l'encodeur restent à mesurer (script `robustness_llm.py` étendu, GPU libre).

## Aperçu de la règle de puissance du protocole v2 (brouillon ; `v2-power-preview-3-plis`, `scripts/v2_power_preview.py`, `power_rule.pooled_width`, 2 152 prédictions hors pli des plis 0 à 2, encodeur moyenné sur cinq graines, TF-IDF caractères et poids équilibrés, EXPLORE)

Largeur de l'IC de la différence appariée de macro-F1 (bootstrap stratifié de patients, même tirage pour les deux systèmes, R = 10 000) : **ensemble encodeur + TF-IDF moins TF-IDF : 4,29 points à 95 % et 5,24 à 98,33 %** ; encodeur moyenné moins TF-IDF : 6,32 à 95 %. À comparer à 12,2 points pour la règle v1 (un pli, cinq graines) et au seuil de 4,0. **Extrapolation à cinq plis (3 586 patients), en 1/√n : environ 3,3 points à 95 % et 4,1 à 98,33 %** (estimation, à mesurer quand les plis 3 et 4 de l'encodeur seront entraînés, environ 50 minutes de GPU) : avec une question primaire unique (95 %), la règle v2 devrait **passer** ; avec trois comparaisons Bonferroni (98,33 %) elle serait à la limite. C'est le résultat qui rend un verdict confirmatoire possible pour la famille bon marché.

## Front de Pareto qualité contre coût (audit GLM v4, C7-A3 ; tous chiffres issus des runs et mesures cités ; moyennes sur les plis disponibles ; EXPLORE)

| Système | macro-F1 (moyenne, plis) | Coût d'entraînement par pli | Inférence par patient | Taille |
|---|---|---|---|---|
| TF-IDF à mots, référence v1 | 0,684 (5 plis) | environ 2 minutes de CPU | quelques ms (CPU) | quelques Mo |
| **TF-IDF caractères et poids équilibrés** | 0,720 (5 plis) | environ 3 minutes de CPU | **1,9 ms (CPU)** | **20,4 Mo** |
| Encodeur moyenné sur 5 graines | 0,749 (plis 0 à 2) | 18 minutes de GPU (5 × 215 s) | 5 × 191 ms (CPU, 8 threads) ; GPU non mesuré | 5 × 443 Mo |
| Ensemble encodeur (5) + TF-IDF | 0,769 (plis 0 à 2) | 18 minutes de GPU + 3 de CPU | environ 1 s (CPU) ; GPU non mesuré | environ 2,2 Go |
| Qwen3.5-4B LoRA 10 époques (une graine) | 0,761 (plis 0 et 1) | 12 450 s de GPU (3,5 h) | 117 ms (GPU) | adaptateur 196 Mo + modèle de base |

**Non dominés** : le TF-IDF caractères et poids (le plus rapide et le plus léger, à 0,72) et l'ensemble encodeur + TF-IDF (le plus élevé, à 0,77) ; le LoRA mûr n'est dominé ni en qualité (équivalent à l'encodeur moyenné, plus sélectif) ni en latence GPU, mais coûte environ dix fois plus à entraîner que cinq encodeurs. Sur une machine sans GPU seuls les deux premiers sont déployables. Les périmètres diffèrent (plis, nombre de graines) : ce tableau est une aide de lecture, pas un classement.

## Seconde graine du Qwen3.5-4B LoRA à 10 époques, pli 0 (fiche `2026-10-04-confirmation-pli2-et-graine-lora`, EXPLORE ; run `20261004-150718-llm-mur-s1001-qwen3-5-4b-ep10-lr1e-4`)

Graine 1001 : **macro-F1 0,7893**, exactitude 0,863, log loss 0,770, 12 665 s ; **écart avec la graine 1000 (0,7795) : +1,0 point [−3,1 ; +5,0], non résolu** (`llm-s1001-minus-s1000-fold0`). La variabilité du LoRA entre graines est faible au pli 0 (1,0 point entre deux graines, à comparer à l'écart-type de 2,6 points de l'encodeur sur cinq graines) ; deux graines ne suffisent pas à estimer un écart-type. Moyenne des deux graines : 0,7844 ; moyenne des probabilités des deux graines : 0,7947.

| Système (pli 0) | macro-F1 | contre TF-IDF caractères et poids (0,7184) | contre l'encodeur moyenné (0,7331) |
|---|---|---|---|
| LoRA graine 1001 | 0,7893 | +7,3 [+1,6 ; +13,1], Holm 0,014 | **+5,75 [+1,1 ; +10,6], Holm 0,027, résolu** |
| LoRA moyenné sur 2 graines | 0,7947 | +7,8 [+3,6 ; +12,6] | +6,3 [+1,0 ; +11,8], Holm 0,027 |
| Ensemble 50/50 LoRA (2 graines) + encodeur (5 graines) | 0,7959 | +8,0 [+3,8 ; +12,5] | +6,4 [+2,2 ; +11,0], Holm 0,004 |
| Ensemble des trois (LoRA 2 graines, encodeur, TF-IDF) | 0,7819 | +6,5 [+3,1 ; +10,5] | n/a |

**Au pli 0, avec la graine 1001 comme avec la moyenne de deux graines, le LoRA mûr dépasse l'encodeur moyenné de façon résolue (+5,75 à +6,4 points)**, ce que la graine 1000 seule ne montrait pas (+4,9, non résolu) ; au pli 1 (une graine) le LoRA était équivalent à l'encodeur (−1,1). Lecture mesurée : le LoRA mûr est **au moins équivalent et probablement meilleur** que l'encodeur moyenné d'environ +2 à +6 points selon le pli et la graine ; il reste dix fois plus coûteux à entraîner. Incertitude de la graine 1001 : ECE 0,107 brute et 0,033 après température, couverture conforme LAC 0,897 avec 1,135 classe par ensemble, exactitude 0,899 à 90 %, 0,939 à 80 %, 0,964 à 70 % de couverture, comme la graine 1000. Prédictions de la fiche : l'écart entre les deux graines inférieur à 3 points (0,6) : réalisé ; la graine 1001 donne moins que la graine 1000 (0,6) : non ; encodeur moyenné au-dessus du TF-IDF au pli 2 (0,8) : réalisé en valeur.

## Allocation dynamique du calcul à l'inférence : cascade par seuil de confiance (`cascade-eval`, `scripts/cascade_eval.py`, hors ligne sur prédictions hors pli existantes, plis 0 et 1, EXPLORE ; remarque de Cyril sur la gestion dynamique du contexte)

Un modèle bon marché répond quand sa probabilité maximale dépasse τ ; sinon le cas passe au modèle suivant. Latences de référence mesurées : TF-IDF 1,9 ms (CPU), encodeur 191 ms par modèle (CPU), LoRA 117 ms (GPU).

| Cascade (seuil τ) | pli 0 : part traitée par le premier / macro-F1 | pli 1 : part traitée par le premier / macro-F1 |
|---|---|---|
| LoRA seul (référence) | 0,7947 (deux graines moyennées) | 0,7415 |
| TF-IDF → LoRA, τ = 0,8 | 69 % / 0,7791 | 48 % / **0,7443** |
| TF-IDF → LoRA, τ = 0,9 | 58 % / 0,7857 | 34 % / 0,7415 |
| **Encodeur moyenné → LoRA, τ = 0,8** | **77 % / 0,7978** | **79 % / 0,7604** |
| Encodeur moyenné → LoRA, τ = 0,7 | 83 % / **0,8018** | 87 % / 0,7538 |
| Encodeur moyenné seul | 0,7331 | 0,7532 |

**Entre 50 % et 80 % des patients n'ont pas besoin du LoRA, sans perte de macro-F1** : la cascade encodeur → LoRA à τ = 0,8 est au niveau du LoRA seul ou au-dessus (0,7978 contre 0,7947 ; 0,7604 contre 0,7415) en appelant le LoRA pour 21 à 23 % des patients ; la cascade TF-IDF → LoRA perd de 0,6 à 1,4 point au pli 0 mais fait mieux au pli 1 en n'appelant le LoRA que pour 31 à 66 % des cas. Un seuil de 0,8 est « bon » aux deux plis ; **il n'a pas été choisi sur un pli et appliqué à l'autre** (exploratoire) : la validation propre choisit τ sur un pli et le rapporte sur les autres. Cela signale une piste d'efficience peu coûteuse (aucun entraînement) pour le déploiement : routage selon la confiance, avec l'abstention conforme comme garde-fou. À confirmer sur cinq plis quand le LoRA mûr y sera (RM-28).

### Gestion dynamique du contexte : ce que les mesures existantes disent déjà (lecture, sans nouveau run)

- **Gain de qualité attendu faible** : seuls 9 patients sur 3 586 dépassent la fenêtre du modèle (aucun dans les chapitres rares) ; l'encodeur lisant tout le dossier par fenêtres de 510 tokens ne s'améliore pas (gain nul à 6 époques, perte à 10 époques, `camembert-fenetres-ep6-minus-ep6-fold0`, `camembert-fenetres-ep10-minus-ep10-fold0`).
- **Gain d'efficience possible, non mesuré** : regroupement des dossiers par longueur (bucketing) et troncature adaptative réduisent le calcul inutile à l'entraînement et au service ; ils changent le budget de la comparaison, donc à tester sur un lot jouet avant tout run préenregistré (déjà noté en C7-A5 de l'audit v3).
- **Piste nouvelle plus rentable** : l'allocation dynamique du calcul entre modèles (cascade, section précédente), qui économise 50 à 80 % des appels au LoRA sans perte de macro-F1 sur les deux plis mesurés. Un test de longueur de contexte du LoRA (P1-15, 512 contre 1 024 tokens) reste dans le chemin complet ; il ne sera lancé que si la cascade ne suffit pas à la cible d'efficience.

## Plis 3 et 4 de l'encodeur, évaluation à cinq plis et règle de puissance v2 (fiche `2026-10-04-encodeur-plis-3-et-4`, EXPLORE ; runs `camembert-pli3-ep10-s0` à `camembert-pli3-ep10-s4`, `camembert-pli4-ep10-s0` à `camembert-pli4-ep10-s4`, `pli3-encodeur-ensembles`, `pli4-encodeur-ensembles`, `v2-power-preview-5-plis`)

| Pli | TF-IDF caractères équilibré | encodeur moyenné (5 graines) | ensemble 50/50 | ensemble moins TF-IDF [IC 95 %] |
|---|---|---|---|---|
| 3 | 0,7073 | 0,7428 (+3,66 [−0,77 ; +8,25], non résolu) | 0,7746 | **+6,71 [+3,61 ; +10,42]** |
| 4 | 0,7248 | 0,7684 (+4,20 [+0,51 ; +7,91]) | 0,7735 | **+4,69 [+1,85 ; +7,68]** |

**Cinq plis regroupés (3 586 patients)** : ensemble moins TF-IDF **+5,20 points [+3,69 ; +6,78]** ; encodeur moyenné seul moins TF-IDF +3,27 [+1,00 ; +5,55]. **Règle de puissance v2** (largeur de l'IC de la différence appariée entre deux systèmes, seuil 4,0) : ensemble contre TF-IDF **3,09 points à 95 %, 3,78 à 98,33 %** : **la règle passe** (l'extrapolation depuis trois plis annonçait 3,3 et 4,1) ; encodeur moyenné contre TF-IDF 4,55 à 95 % : elle ne passe pas pour cette paire. L'ensemble bat le TF-IDF à chacun des cinq plis (résolu aux plis 1 à 4 d'après les IC par pli ; non résolu au pli 0), et sur l'agrégat l'IC est entièrement au-dessus de δ = 2,0 (borne basse 3,69). Prédictions de la fiche : largeur < 4,0 (probabilité 0,7) : réalisée ; ensemble > TF-IDF aux plis 3 et 4 (0,85) : réalisée ; IC entièrement positif aux deux (0,35) : réalisée. Réserve : EXPLORE, protocole v2 non accepté (RM-37) ; le mélange 50/50 a été fixé avant ces plis, mais le TF-IDF de référence et l'encodeur ont été choisis sur les plis de développement 0 à 2.

## Prédiction conforme sur cinq plis : marginale contre conditionnelle par famille (RM-33, run `conformal-by-family` du 04/10 16:26, EXPLORE, niveau visé 0,90, 3 586 patients hors pli)

Étalonnage croisé par plis, sans étiquette de test ; « min famille » est la plus basse couverture parmi les familles de chapitres.

| Système (cinq plis) | marginal : couverture / taille moyenne / min famille | par famille (Mondrian) : couverture / taille moyenne / min famille |
|---|---|---|
| Ensemble encodeur + TF-IDF | 0,901 / 1,14 / 0,655 | 0,901 / **1,89** / **0,892** |
| Encodeur moyenné | 0,900 / 1,17 / 0,685 | 0,898 / 2,50 / 0,831 |
| TF-IDF caractères équilibré | 0,900 / 1,30 / 0,646 | 0,900 / 2,69 / 0,897 |

La couverture marginale de 0,90 cache des familles à 0,65 ; l'étalonnage par famille ramène le minimum à 0,89 pour l'ensemble au prix d'ensembles plus grands (1,14 vers 1,89 classes). **À couverture minimale égale (0,89 à 0,90), les ensembles de l'ensemble sont 30 % plus petits que ceux du TF-IDF seul (1,89 contre 2,69)** : l'ensemble améliore l'incertitude utile, pas seulement la macro-F1. Réserve : l'étalonnage par plis n'est pas un test indépendant (EXPLORE) ; la couverture de la classe AUTRE (0/18 sur le développement) reste hors de portée de toute méthode sans exemple.

## Table d'abstention sur cinq plis (run `abstention-cinq-plis`, 3 586 patients hors pli, confiance = probabilité maximale, Wilson 95 %)

| Couverture (part traitée automatiquement) | Ensemble encodeur + TF-IDF | Encodeur moyenné | TF-IDF caractères équilibré |
|---|---|---|---|
| 100 % | 0,858 [0,846 ; 0,869] | 0,846 | 0,822 [0,809 ; 0,834] |
| 90 % | 0,896 | 0,886 | 0,864 |
| 80 % | 0,925 | 0,919 | 0,896 |
| 70 % | **0,948** [0,938 ; 0,956] | 0,950 | 0,925 [0,914 ; 0,935] |
| 50 % | 0,979 | 0,970 | 0,963 |

En renvoyant 30 % des patients à un humain, l'ensemble classe correctement 94,8 % du reste (contre 92,5 % pour le TF-IDF seul, intervalles disjoints) : exactitude **conditionnelle à la confiance, non à la correction de l'étiquette** (l'étiquette vient du scénario, pas d'un codage humain). L'encodeur seul égale l'ensemble à 70 % de couverture (0,950 contre 0,948) : l'apport de l'ensemble se concentre sur les cas faciles à moyens.

## Quantification INT8 sélective de l'encodeur (RM-38, run `quantization-selective-camembert-deploy-ep10-lr1e-4`, pli 0, graine 1000, EXPLORE)

Quantification dynamique PyTorch par groupes de couches ; 3 threads sur processeur **en concurrence avec l'entraînement du LoRA** (latences gonflées : fp32 à 256 ms au lieu de 191 ms mesurés seul, comparaisons valables entre lignes de ce tableau seulement) ; 100 latences.

| Variante | macro-F1 | exactitude | latence p50 / p95 (ms) |
|---|---|---|---|
| fp32 (référence) | 0,7362 | 0,8298 | 255,6 / 281,0 |
| INT8 toutes les couches | 0,337 | 0,526 | 163,2 / 185,0 |
| INT8 sans la tête | 0,342 | 0,529 | 158,0 / 183,8 |
| INT8 réseau feed-forward seulement | 0,353 | 0,543 | 190,0 / 223,5 |
| **INT8 attention seulement** | **0,723** (−1,3) | 0,824 | 227,8 / 261,6 (−11 %) |

**L'effondrement vient des couches du réseau feed-forward, pas de la tête** (la tête quantifiée seule ne change rien). L'INT8 de l'attention seule garde presque toute la qualité (−1,3 point, au-delà du seuil de 1 point fixé dans RM-38) pour un gain de latence de 11 % : **verdict, la quantification dynamique INT8 n'est pas retenue pour cet encodeur** ; les pistes restantes sont la quantification statique avec étalonnage des activations (les sorties du feed-forward ont vraisemblablement des valeurs extrêmes) ou le service sur GPU, où l'encodeur coûte environ 5 minutes d'entraînement et quelques millisecondes par patient. Hypothèse sur les valeurs extrêmes non vérifiée.

### Précision sur la cascade (04/10/2026, 17h55Z) : ce que l'économie mesure et ne mesure pas

La cascade encodeur moyenné puis LoRA évite des **appels au LoRA** (GPU), non de la **latence** : l'ensemble de cinq encodeurs coûte 5 × 191 ms sur processeur (environ 955 ms par patient), plus que le LoRA seul à 117 ms sur GPU. Le gain de latence n'existe que pour (a) le premier étage TF-IDF (1,9 ms), au prix d'une perte de macro-F1 au pli 0 dans l'aperçu, ou (b) un premier étage encodeur servi sur GPU (mesure `bench_encoder_gpu.py` en file). L'économie en énergie et en occupation du GPU reste réelle si le GPU est le goulot. La fiche `2026-10-04-cascade-cinq-plis` déclare ce modèle de coût avant les runs ; l'évaluation à cinq plis avec seuil choisi hors pli (`scripts/cascade_cv.py`) attend les plis 2 à 4 du LoRA.

## Élève TF-IDF à étiquettes souples, professeur ensemble, cinq plis (RM-46, fiche `2026-10-04-tfidf-souple`, EXPLORE ; runs `tfidf-souple-ens`, `tfidf-souple-moins-dur`, `professeur-ensemble-moins-tfidf-souple`)

TF-IDF caractères (3 à 5, poids équilibrés), cible `0,5 × étiquette + 0,5 × professeur` (ensemble encodeur + TF-IDF, probabilités strictement hors pli), aucun réglage, C par pli repris de la référence dure ; 285 s de processeur sur un thread ; latence et taille du service inchangées.

| Système (3 586 patients regroupés) | macro-F1 | exactitude | exactitude à 70 % de couverture |
|---|---|---|---|
| TF-IDF dur (référence) | 0,7202 | 0,822 | 0,925 |
| **TF-IDF souple (professeur ensemble)** | **0,7271** | 0,827 | 0,934 |
| Professeur : ensemble encodeur + TF-IDF | 0,7721 | 0,858 | 0,948 |

Souple moins dur : **+0,69 point [−1,03 ; +2,29]** : **non résolu** (l'IC dépasse δ = 2,0 par le haut et inclut zéro) ; l'élève reste **4,5 points [+2,31 ; +6,72] sous son professeur**. Les prédictions de la fiche : gain entre 0,5 et 3 points (réalisée, +0,69), IC entièrement positif (non), gain ≥ 2,0 (non), reste à plus de 2 points sous le professeur (réalisée). **La distillation d'un professeur fort vers le TF-IDF ne transmet que 15 % de l'écart** (0,69 sur 5,2) : un modèle linéaire sur n-grammes de caractères n'a pas la capacité de reproduire la frontière de l'ensemble ; la compression utile est à chercher vers un élève de type encodeur (RM-32, RM-45). Le bras LoRA reste à lancer quand les prédictions du LoRA sur les cinq plis existeront. Réserve de second ordre : voir la fiche de distillation vers l'encodeur.

## LoRA mûr au pli 2 (RM-28, fiche `2026-10-04-llm-mur-plis-2-3-4`, EXPLORE ; runs `llm-mur-pli2-qwen3-5-4b-ep10-lr1e-4`, `pli2-llm-mur`, `pli2-llm-mur-vs-encodeur`)

Qwen3.5-4B LoRA r = 16, 10 époques, taux 1e-4, graine 1000, 13 329 s d'entraînement, pic réservé 12,37 Gio. **macro-F1 0,7785**, exactitude 0,8536, log loss 0,913, ECE brute 0,110.

| Comparaison appariée au pli 2 | différence | IC 95 % | verdict |
|---|---|---|---|
| LoRA moins meilleur TF-IDF (0,7483) | +3,02 | [−1,48 ; +7,31] | non résolu |
| LoRA moins encodeur moyenné (0,7613) | +1,78 | [−2,79 ; +6,41] | non résolu |

Incertitude (étalonnage croisé sur deux moitiés du pli, un seul pli : exploratoire) : ECE de 0,112 à 0,044 après température (T = 2,4 et 2,6), Brier 0,257 vers 0,229, log loss 0,913 vers 0,534 ; conforme LAC à 90 % : couverture 0,904 avec 1,17 classe par ensemble, mais les classes rares ne sont pas couvertes en marginal (couverture minimale par classe 0,0) ; exactitude à 70 % de couverture 0,946. Même ordre de grandeur qu'aux plis 0 et 1. Prédictions de la fiche : macro-F1 entre 0,68 et 0,82 (réalisée) ; avantage sur le TF-IDF à IC entièrement positif (non réalisé à ce pli, 1 pli sur 3 vus). Note de registre : le post-traitement a enregistré l'analyse d'incertitude sous le même nom de run que l'entraînement (deux identifiants distincts, 194722 et 194822) ; à lire par identifiant.

## Quatre mesures sans GPU issues de l'audit GLM v6 (fiche `2026-10-05-audit-glm-v6-mesures-cpu`, EXPLORE, cinq plis, 3 586 patients, 104 auteurs ; runs `glm-v6-blocs-auteurs`, `glm-v6-blocs-auteurs-niveaux`, `glm-v6-empilement`, `glm-v6-variance`, `glm-v6-par-pool`)

**A. Bootstrap par blocs d'auteurs (levier 1 de GLM).** Les intervalles par patients sous-estiment légèrement l'incertitude ; la corrélation d'auteur est faible mais non nulle.

| Différence regroupée | observée | IC 95 % par patients (largeur) | **IC 95 % par blocs d'auteurs (largeur)** | IC 98,33 % par patients | **IC 98,33 % par blocs d'auteurs** |
|---|---|---|---|---|---|
| Ensemble moins TF-IDF | +5,20 | [+3,69 ; +6,78] (3,09) | **[+3,84 ; +7,23] (3,39)** | (3,78) | **[+3,57 ; +7,81] (4,24)** |
| Encodeur moyenné moins TF-IDF | +3,27 | [+1,00 ; +5,55] (4,55) | **[+1,24 ; +5,94] (4,70)** | (5,51) | **[+0,75 ; +6,61] (5,86)** |

Verdict de la fiche : **« résiste »** à 95 % (borne basse +3,84 > 0, largeur 3,39 ≤ 4,0). **Correction importante** : à 98,33 % (famille de trois comparaisons) la largeur par blocs d'auteurs est **4,24, au-dessus du seuil de 4,0** : la règle de puissance v2 passe pour **une question primaire unique à 95 %**, pas pour trois comparaisons corrigées ; notre phrase « 3,78 à 98,33 %, atteinte » ne valait que pour le bootstrap par patients. Prédictions de la fiche : intervalle par blocs plus large (réalisée), borne basse > 0 (réalisée), largeur ≤ 4,0 (réalisée à 95 %, probabilité 0,45).

**B. Empilement et décision (leviers 4 et 15).** Validation croisée par pli, comparaison avec le mélange 50/50 par blocs d'auteurs :

| Variante | macro-F1 regroupée | contre S0 [IC 95 % par blocs] | verdict |
|---|---|---|---|
| S0 : 50/50 | 0,7721 | : | référence |
| S1 : poids global appris (0,6 pour l'encodeur à chacun des cinq plis) | 0,7763 | +0,41 [−0,25 ; +1,13] | sans gain |
| S2 : régression logistique sur les log-probabilités | 0,7124 | −5,98 [−8,19 ; −3,45] | **dégrade** (surajustement ; non-convergence à 500 itérations) |
| S4 : S0 plus biais par classe | 0,7670 | −0,51 [−1,58 ; +1,14] | sans gain |

**Le mélange 50/50 est quasiment au mélange optimal** (le poids appris est 0,6 à chaque pli, stable ; gain +0,4 non résolu) : **le levier « empilement appris, +1 à +2,5 points » de GLM est réfuté**, et la trajectoire de gain par le haut s'en trouve abaissée. Prédictions : S1 entre 0,0 et +0,5 (réalisée), S2 entre −1,0 et +1,5 (**non réalisée**, −5,98), S4 entre −0,5 et +1,0 (**non réalisée de peu**, −0,51), aucun gain ≥ 2,0 (réalisée).

**C. Décomposition de variance de l'encodeur (levier 11).** Macro-F1 par pli et par graine (5 × 5). Écarts-types de composantes (points) : pli 0,9 ; effet principal de graine 0,0 ; **reste (interaction pli × graine et non-déterminisme du GPU) 2,32**. Écart-type entre graines par pli : 2,55 ; 2,95 ; 1,44 ; 1,57 ; 2,48. **La variance d'un run isolé est presque entièrement du « reste »** : aucune graine n'est systématiquement meilleure, l'écart entre deux runs d'un même pli est du bruit d'interaction et de noyau GPU ; d'où la nécessité des moyennes de graines et des prédictions regroupées. (La prédiction « pli supérieur à 1,5 fois graine » est vraie de façon triviale, la composante de graine étant nulle.)

**D. Mesure par sous-ensemble d'usage (`pool`).** Le champ `pool` désigne les sous-ensembles d'usage annotés du corpus (général 3 048 patients de développement, codage CIM-10 245, infectiologie 110, oncologie réponse au traitement 92, oncologie biomarqueurs 91), **tous présents dans les plis de développement** ; ce n'est pas une piscine hors distribution (erreur de notre cahier GLM v6, corrigée). Exactitude de l'ensemble [Wilson 95 %] : général 0,844 [0,831 ; 0,856] ; **codage CIM-10 0,918 [0,877 ; 0,947]** (au-dessus du général) ; infectiologie 0,864 [0,787 ; 0,916] ; oncologie (deux sous-ensembles) 1,000 : ils ne contiennent qu'un chapitre (le II), donc la macro-F1 y est sans objet. **Toute la difficulté est dans le sous-ensemble général** ; les sous-ensembles d'usage sont faciles. Prédictions : codage au-dessus du général (réalisée), au moins un sous-ensemble plus difficile (**non réalisée**).

## Audit des erreurs confiantes du TF-IDF et sensibilité aux chapitres de symptômes (P2-06, levier 3 de l'audit GLM v6 ; fiche `2026-10-05-audit-erreurs-confiantes`, EXPLORE ; run `sensibilite-xviii-xxi`)

**Lecture** (65 erreurs confiantes : probabilité de la classe prédite > 0,90, de la vraie classe < 0,10 ; échantillon reproductible de 30 cas : 10 en pilote déclaré avant la fiche, 20 préenregistrés ; relecteur : l'assistante, non un codeur médical, **à contre-expertiser** avant toute citation externe ; aucune étiquette modifiée ; agrégats seulement). Verdicts : (E) étiquette contestable, (R) rivale défendable, (M) erreur du modèle.

| Échantillon | (E) étiquette contestable | (R) rivale défendable | (M) erreur du modèle |
|---|---|---|---|
| 20 cas préenregistrés | 5 (25 %) | 14 (70 %) | 1 (5 %) |
| 10 cas pilotes | 3 | 6 | 1 |
| Ensemble des 30 | 8 (27 %) | 20 (67 %) | 2 (7 %) |

Critères de la fiche appliqués aux 20 cas : « ambiguïté de codage établie » (E + R = 95 % ≥ 60 %) **atteint** ; « bruit d'étiquette établi » (E ≥ 40 %) **non atteint** ; « erreur du modèle dominante » (M ≥ 50 %) **non atteint**. Prédictions de la fiche : E + R ≥ 60 % (réalisée, 0,75), E ≥ 40 % (non réalisée, 0,35), M ≥ 50 % (non réalisée, 0,1). **Dans 93 % des cas lus, la réponse confiante du modèle est défendable d'après le texte** : la majorité des « erreurs confiantes » sont des conventions de choix du diagnostic principal (étiquette de symptôme R du chapitre XVIII alors que le compte rendu conclut à un diagnostic précis ; tumeur bénigne ou polype contre pathologie digestive ; maladie d'Alzheimer codée F ou G ; état de greffe contre complication). Cela quantifie une part du plafond d'ambiguïté (8,2 % d'erreurs communes) et suggère que le plafond de macro-F1 est inférieur à ce que la capacité des modèles laisserait espérer.

**Sensibilité de la macro-F1 aux chapitres de symptômes** (descriptif ; `sensibilite-xviii-xxi`, ensemble 50/50, cinq plis) : F1 du chapitre XVIII (221 patients) 0,46 et du XXI (42 patients) 0,377 ; macro-F1 regroupée : 17 chapitres 0,7721 (TF-IDF 0,7202, encodeur 0,7528) ; **sans XVIII 0,7917** (TF-IDF 0,744, encodeur 0,7691) ; **sans XVIII ni XXI 0,8193** (TF-IDF 0,7743, encodeur 0,7932) ; l'écart ensemble moins TF-IDF reste de +5,20, +4,76 puis +4,50 [+3,41 ; +6,36] (blocs d'auteurs) : **le classement des systèmes ne dépend pas de ces chapitres**, mais le niveau absolu de la macro-F1 en dépend de 2 à 5 points. À rapporter comme analyse de sensibilité, jamais comme remplacement de la métrique gelée.

### Complément : lecture des 35 erreurs confiantes restantes (05/10/2026, hors fiche, extrait de conclusion de 300 caractères, lecture plus rapide ; à traiter comme indicatif)

Sur les 35 cas non couverts par l'échantillon préenregistré : (E) étiquette contestable 10 (29 %), (R) rivale défendable 25 (71 %), (M) erreur du modèle 0. **Sur les 65 erreurs confiantes lues (30 de la fiche, 35 en complément) : E 18 (28 %), R 45 (69 %), M 2 (3 %)** : 97 % des réponses confiantes du modèle sont défendables d'après le texte. Les étiquettes contestables sont presque toutes des codes de symptôme du chapitre XVIII (douleur thoracique, dyspnée, hématurie, nausées, rétention d'urine, gangrène) alors que le compte rendu conclut à un diagnostic précis (syndrome coronarien aigu, pneumopathie, maladie de Crohn probable, nécrose sur artériopathie) relevant d'un autre chapitre ; les rivales défendables sont des conventions (tumeur bénigne ou polype contre pathologie digestive, adénome de prostate, Alzheimer en F ou G, état de greffe ou de grossesse contre complication, traumatisme contre séquelle orthopédique). Même réserve : relecteur non codeur, aucune étiquette modifiée, contre-expertise par un professionnel du codage avant toute citation externe. **Conséquence de méthode** : le choix du diagnostic principal du scénario n'est pas toujours celui qu'un lecteur du compte rendu ferait ; la macro-F1 mesure donc aussi l'accord avec une convention de codage, et le chapitre XVIII (symptômes, F1 de 0,46) en est le point faible structurel.

## LoRA mûr au pli 3 (RM-28, fiche `2026-10-04-llm-mur-plis-2-3-4`, EXPLORE ; runs `llm-mur-pli3-qwen3-5-4b-ep10-lr1e-4`, `pli3-llm-mur`, `pli3-llm-mur-vs-encodeur`)

Qwen3.5-4B LoRA r = 16, 10 époques, taux 1e-4, graine 1000, 12 791 s d'entraînement (3 h 33), pic réservé 12,94 Gio. **macro-F1 0,7676**, exactitude 0,848, log loss 0,943, ECE brute 0,118.

| Comparaison appariée au pli 3 | différence | IC 95 % | Holm | verdict |
|---|---|---|---|---|
| LoRA moins meilleur TF-IDF (0,7073) | **+6,10** | [+2,15 ; +10,39] | 0,0008 | **résolu** |
| LoRA moins encodeur moyenné (0,7428) | +2,45 | [−1,90 ; +7,12] | 0,276 | non résolu |

Incertitude (étalonnage croisé sur deux moitiés du pli, exploratoire) : ECE de 0,118 à 0,043 après température ; conforme LAC 90 % : couverture 0,900 avec 1,21 classe par ensemble ; exactitude à 70 % de couverture 0,948. **Bilan des quatre premiers plis du LoRA mûr** (une graine par pli, graine 1000 au pli 0) : 0,7795, 0,7415, 0,7785, 0,7676 ; contre le meilleur TF-IDF +6,4, +5,3, +3,0, +6,1 (résolu à trois plis sur quatre) ; contre l'encodeur moyenné +4,9, −1,1, +1,8, +2,5 (jamais résolu pour la graine 1000 ; résolu pour la graine 1001 au pli 0). Le pli 4 (fin attendue vers 03h00Z) fournira l'agrégat à cinq plis. Même remarque de registre que pour le pli 2 : l'analyse d'incertitude porte le même nom de run que l'entraînement (identifiants distincts).

## LoRA mûr aux cinq plis : agrégat, comparaisons, incertitude, sélection, cascade (RM-28 terminé ; fiche `2026-10-04-llm-mur-plis-2-3-4` ; runs `llm-mur-pli4-qwen3-5-4b-ep10-lr1e-4`, `cinq-plis-llm-mur-moins-tfidf-variant-char-balanced`, `cinq-plis-llm-mur-moins-cinq-plis-ensemble-encodeur5`, `cinq-plis-llm-mur-moins-cinq-plis-ensemble-encodeur5-tfidf-charbal`, `abstention-cinq-plis`, `conformal-by-family`, `apercu-selection-systeme-final`, `cascade-cinq-plis-encodeur-lora`, `cascade-cinq-plis-tfidf-lora`, EXPLORE)

**Pli 4** (12 536 s d'entraînement) : macro-F1 0,7636 ; +3,88 [+0,25 ; +7,58] contre le TF-IDF (Holm 0,037) ; −0,32 [−3,96 ; +3,34] contre l'encodeur moyenné ; ECE 0,121 vers 0,027 après température ; conforme 90 % : 0,905 avec 1,26 classe. **Macro-F1 du LoRA par pli** : 0,7795, 0,7415, 0,7785, 0,7676, 0,7636 ; **regroupée 0,7673** (3 586 patients, une graine par pli).

| Différence regroupée (patients) | observée | IC 95 % | largeur | verdict |
|---|---|---|---|---|
| LoRA moins meilleur TF-IDF | **+4,71** | [+2,40 ; +7,18] | 4,78 | résolu |
| LoRA moins encodeur moyenné | +1,45 | [−1,10 ; +4,09] | 5,19 | **non résolu** |
| LoRA moins ensemble encodeur + TF-IDF | −0,49 | [−2,51 ; +1,74] | 4,26 | non résolu (équivalents) |

**Verdict de la conclusion C3** : à cinq plis, le LoRA mûr n'est **pas distinct de l'encodeur moyenné** (+1,45, non résolu) et **n'est pas au-dessus de l'ensemble 50/50** (−0,49) pour un coût d'entraînement environ dix fois supérieur ; il bat le TF-IDF de +4,7. La largeur des intervalles du LoRA (4,3 à 5,2) dépasse 4,0 : une graine par pli ne suffit pas pour une comparaison confirmatoire du LoRA (variance d'un run isolé de l'ordre de 2,3 points). **Règle de bifurcation (b) de la feuille de route** (LoRA au moins 2 points au-dessus de l'ensemble avec borne basse positive) : **non remplie** ; le LoRA reste un professeur et un système de qualité maximale, pas le système final.

**Incertitude du LoRA à cinq plis** : conforme marginal : couverture 0,900, taille 1,16, **famille la moins couverte 0,62** (symptômes, lésions, facteurs), endocrinien et mental 0,75, nerveux 0,80 ; par famille (Mondrian) : couverture minimale 0,894 avec **2,17 classes par ensemble** (ensemble encodeur + TF-IDF : 0,892 avec 1,89 ; TF-IDF : 0,897 avec 2,69) : à couverture minimale égale, **l'ensemble donne les plus petits ensembles de classes**. Abstention : exactitude 0,953 à 70 % de couverture [0,944 ; 0,960] (ensemble 0,948, TF-IDF 0,925), 0,851 à 100 %.

**Aperçu de la règle de sélection du système final** (`llmft.selection`, δ = 2,0, bootstrap d'auteurs ; n'engage rien) : macro-F1 : A TF-IDF 0,7202 ; B TF-IDF souple 0,7271 ; D encodeur 0,7528 ; E ensemble 0,7721 ; F LoRA 0,7673 ; **G ensemble LoRA + encodeur + TF-IDF 0,7799 (meilleur)**. Bornes basses contre G : E −2,79, F −2,47, D −5,35 : **aucun autre candidat n'est admissible**, la règle retient donc G, le plus coûteux. **Observation** : avec des IC de largeur 4 à 5 points, la règle de non-infériorité à δ = 2 ne peut certifier aucun candidat moins coûteux même quand l'écart ponctuel est petit (G contre E : +0,78) ; elle retient mécaniquement le meilleur. À arbitrer avant le gel (RM-50) : moyennes de plusieurs graines pour rétrécir les IC, ou règle modifiée (décision de Cyril, ADR).

**Cascade validée hors pli** (fiche `cascade-cinq-plis`, seuil choisi sur les quatre autres plis) : **encodeur puis LoRA** : seuil 0,5 à chaque pli, 93,4 % des patients traités par l'encodeur, macro-F1 0,7685 contre 0,7673 pour le LoRA seul : +0,12 [−1,74 ; +1,90] : **non-infériorité atteinte, économie d'appels au LoRA de 93 % atteinte** (prédiction « part entre 50 et 85 % » non réalisée : 93,4 %). La latence modélisée reste défavorable (963 ms contre 117 ms) tant que l'encodeur est servi sur processeur ; l'économie est une économie de GPU. **TF-IDF puis LoRA** : seuils 0,6 à 0,8, 67,2 % traités, macro-F1 0,7558 : −1,14 [−2,40 ; −0,04] : **non-infériorité non atteinte**.

Prédictions de la fiche RM-28 : macro-F1 de chaque pli entre 0,68 et 0,82 (réalisée aux trois plis) ; LoRA au-dessus du TF-IDF à IC entièrement positif à au moins deux plis sur trois (réalisée : plis 3 et 4, pas le pli 2) ; LoRA au moins équivalent à l'encodeur sur l'agrégat (réalisée au sens du point estimé, +1,45, non résolu) ; moyenne à cinq plis entre 0,73 et 0,79 (réalisée : 0,766).

## Ancrage externe : zéro-shot de Qwen3.5-4B et 9B sans affinage, pli 0 (RM-30, fiche `2026-10-04-ancrage-zero-shot-et-service-lora`, EXPLORE ; runs `zero-shot-qwen3-5-4b-pli0`, `zero-shot-qwen3-5-9b-pli0`, `zero-shot-contre-lora-pli0`, `zero-shot-9b-contre-4b`)

Invite construite depuis le contrat de tâche (nom et définition des 18 chapitres, lettres A à R, document tronqué tête et fin à 3 500 tokens, gabarit de conversation sans réflexion), aucune étiquette ni exemple ; probabilités lues sur les lettres de réponse ; 717 patients du pli 0.

| Modèle (aucun affinage) | macro-F1 | exactitude | log loss | durée d'inférence |
|---|---|---|---|---|
| Qwen3.5-4B zéro-shot | **0,4929** | 0,6625 | 1,457 | 117 s |
| Qwen3.5-9B zéro-shot | 0,4725 | 0,6234 | 1,614 | 229 s |
| *Pour mémoire* : meilleur TF-IDF (pli 0) | 0,7184 | : | : | : |
| *Pour mémoire* : LoRA 4B mûr (pli 0, graine 1000) | 0,7795 | 0,858 | 0,91 | : |

**L'affinage apporte +28,8 points au Qwen3.5-4B** (zéro-shot moins LoRA mûr : −28,79 [−35,0 ; −22,5], Holm < 0,001) ; le 9B zéro-shot est à −30,7 [−36,8 ; −24,3] du même LoRA du 4B ; le zéro-shot est environ 22 points sous le meilleur TF-IDF. Le 9B n'est pas meilleur que le 4B en zéro-shot (−1,96 [−6,6 ; +2,85], non résolu). **Lecture** : un LLM de 4 à 9 milliards de paramètres sans affinage ne sait pas faire ce choix de diagnostic principal selon la convention du corpus ; la valeur de l'affinage n'est pas un effet de recette. Prédictions de la fiche : zéro-shot du 4B entre 0,15 et 0,45 (**non réalisée**, 0,49) ; du 9B entre 0,25 et 0,55 (réalisée, 0,47) ; le 9B dépasse le 4B (**non réalisée**) ; aucun n'atteint le meilleur TF-IDF (réalisée). Réserve : l'invite est un choix d'auteur, une seule invite a été essayée ; ce n'est pas un état de l'art du zéro-shot mais un repère.

## Service de l'encodeur sur GPU (RM-34, run `bench-encoder-gpu-camembert-deploy-ep10-lr1e-4`, `scripts/bench_encoder_gpu.py`, 200 patients du pli 0, RTX 5090, lot de 16 ; mesure descriptive hors hypothèse)

| Précision | latence p50 / p95 (lot de 1) | débit en lot de 16 | mémoire de pointe |
|---|---|---|---|
| fp32 | **6,0 ms** / 6,8 ms | 323 patients par seconde | 0,68 Gio |
| bf16 | **4,5 ms** / 5,9 ms | **1 325 patients par seconde** | 0,35 Gio |

**Contre 191 ms sur processeur (8 threads) : un facteur 32 en latence (fp32) et 42 (bf16)**. Cinq encodeurs en série sur GPU coûtent environ 30 ms (fp32) ou 22 ms (bf16) par patient, **moins que le LoRA seul (117 ms)** : le modèle de coût de la cascade change (voir ci-dessous). Précisions : (1) l'énergie rapportée par le script (0,57 Wh pour 1 000 patients en fp32, 0,27 en bf16) est **non fiable** : la mesure de puissance échantillonne une fois par seconde et le calcul dure moins d'une seconde (200 patients à 1 325 par seconde) ; à refaire sur au moins 10 secondes de charge (RM-42) ; (2) la qualité en bf16 n'est pas mesurée par ce banc (équivalence à établir, facteur A de la fiche `2026-10-05-encodeur-recette-v2`) ; (3) latence mesurée hors tokenisation.

**Conséquence pour la cascade encodeur puis LoRA** (RM-40, estimation arithmétique à partir des mesures) : latence moyenne ≈ 5 × 6,0 ms + (1 − 0,934) × 117 ms ≈ **38 ms par patient** contre 117 ms pour le LoRA seul, soit environ 3 fois moins, à macro-F1 non inférieure (+0,12 [−1,74 ; +1,90]) ; l'économie n'est donc plus seulement une économie d'appels au GPU : **c'est une économie de latence si l'encodeur est servi sur GPU**. La précision de la section « ce que l'économie mesure et ne mesure pas » plus haut vaut pour un encodeur servi sur processeur.

## Distillation vers l'encodeur : verdict à cinq plis (RM-32, fiche `2026-10-04-distillation-vers-encodeur` ; runs `distill-lora-pli0-s0` à `distill-lora-pli4-s2`, `distill-ens-pli0-s0` à `distill-ens-pli4-s2`, `distillation-analyse-cinq-plis` ; EXPLORE, 30 runs, alpha 0,5 et T = 2 fixés, non réglés)

Moyenne de trois graines par pli, prédictions regroupées (3 586 patients), différence par **bootstrap d'auteurs**. Référence : encodeur non distillé, mêmes graines 1000 à 1002.

| Bras (professeur) | élève distillé (macro-F1) | encodeur non distillé | professeur | élève moins non distillé [IC 95 %] | élève moins professeur [IC 95 %] | verdict de la fiche |
|---|---|---|---|---|---|---|
| **Ensemble encodeur + TF-IDF** | **0,7952** | 0,7605 | 0,7721 | **+3,47 [+2,25 ; +5,08]** | **+2,31 [+0,46 ; +4,48]** | **gain confirmé** |
| LoRA 4B | 0,7350 | 0,7605 | 0,7673 | −2,55 [−4,78 ; +0,02] | −3,22 [−6,52 ; −0,03] | non résolu |

| Mesures complémentaires | élève (ensemble) | élève (LoRA) | non distillé | professeur ensemble | professeur LoRA |
|---|---|---|---|---|---|
| exactitude | **0,8714** | 0,8625 | 0,8469 | 0,8575 | 0,8514 |
| log loss | **0,433** | 0,589 | 0,609 | 0,497 | 0,895 |
| macro-F1 après correction de priorité | **0,7868** | 0,7533 | 0,7519 | 0,7558 | 0,7679 |

**Un élève isolé** (par run, quinze runs par bras) : macro-F1 moyenne **0,7876** (écart-type 0,012) pour l'élève distillé de l'ensemble contre 0,7446 (0,027) pour l'encodeur non distillé, soit +4,3 points et une variabilité entre graines divisée par plus de deux ; élève distillé du LoRA : 0,722 (0,023).

**Lecture** : (1) **distiller l'ensemble encodeur + TF-IDF dans un seul encodeur est un gain confirmé et dépasse même le professeur** (+2,31 [+0,46 ; +4,48]) ; l'élève (6 ms sur GPU, 1 modèle de 443 Mo) remplace un ensemble de cinq encodeurs et d'un TF-IDF, en mieux sur la macro-F1, l'exactitude et la calibration. (2) **Distiller le LoRA dégrade la macro-F1** (−2,55) : l'élève hérite de l'exactitude et de la calibration mais décale la décision vers les classes majoritaires (après correction de priorité l'écart disparaît : 0,7533 contre 0,7519). (3) Prédictions de la fiche : gain ≥ 2,0 contre l'encodeur non distillé (probabilité 0,35) : réalisé pour le bras ensemble seulement ; élève à plus de 2 points sous le LoRA (0,6) : réalisé ; bras ensemble n'apportant pas plus que le bras LoRA (0,6) : **non réalisé** (écart de 6 points entre bras). **Réserve majeure, déclarée dans la fiche** : chaque professeur a vu, pour entraîner ses prédictions hors pli, le pli de validation de l'élève (fuite de second ordre) ; le fait que le bras LoRA ne profite pas du même effet plaide contre une fuite dominante, mais **seul un professeur imbriqué (entraîné sans le pli évalué) ou le test scellé lèvera le doute** : RM-56.

## Recette d'encodeur v2, facteur A : bf16 par autocast (RM-41 partie encodeur ; fiche `2026-10-05-encodeur-recette-v2`, EXPLORE ; runs `enc2-bf16-pli0-s0` à `enc2-bf16-pli4-s2`)

Quinze runs (cinq plis, graines 1000 à 1002), moyenne de trois graines par pli, prédictions regroupées, différence avec l'encodeur fp32 de référence par bootstrap d'auteurs : macro-F1 regroupée **0,7598 contre 0,7605** : **−0,07 [−1,67 ; +1,69]** : **équivalent** (l'IC tient dans ±δ = 2,0). Par run isolé : moyenne 0,7476, écart-type 0,017 (référence fp32 : 0,7446 et 0,027). **Vitesse : 95 s par run contre 214 s (×2,25, −55 %)**, pic mémoire 5,3 Gio, **11,9 Wh par run**. Prédictions de la fiche : équivalent (probabilité 0,8, réalisée) ; durée réduite d'au moins 20 % (0,6, réalisée). **Conséquence** : l'entraînement de l'encodeur en bf16 est adopté pour les expériences de développement du second cycle (même qualité, deux fois et quart moins de temps et d'énergie) ; pour le service, la qualité en bf16 à l'inférence (déjà 4,5 ms) reste à mesurer séparément. Les trois autres facteurs (lissage, EMA, curriculum) sont en cours.
