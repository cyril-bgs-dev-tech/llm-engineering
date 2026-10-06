# Brouillon de la fiche de gel du système final (RM-50), **remplacé le 06/10/2026 par `docs/decisions/ADR-016-gel-du-systeme-final.md` et `results/frozen_final.json`** (document d'historique)

Statut : **brouillon préparé le 05/10/2026**, à compléter après les plis 3 et 4 du LoRA et la distillation, et à figer (hachage, ADR) **seulement après l'acceptation du protocole v2 par Cyril (RM-37)**. Rien ici ne décide à sa place. Le test scellé n'est pas lu.

## 1. Candidats (liste fermée, écrite avant lecture des cinq plis du LoRA)
Par ordre de coût d'inférence croissant : (A) TF-IDF caractères équilibré ; (B) TF-IDF souple (professeur ensemble) ; (C) élève encodeur distillé (RM-32, si fait) ; (D) encodeur moyenné sur cinq graines ; (E) ensemble 50/50 encodeur moyenné + TF-IDF ; (F) LoRA 4B seul ; (G) ensemble LoRA + encodeur + TF-IDF. Aucun autre candidat ne s'ajoute après lecture.

## 2. Règle de sélection (non-infériorité puis coût)
1. Calculer, sur les prédictions hors pli regroupées des cinq plis, la macro-F1 de chaque candidat et, pour chaque candidat X, la différence avec le meilleur candidat B par `power_rule.pooled_interval` (IC 95 %).
2. X est **admissible** si la borne basse de (X moins B) est strictement supérieure à −δ = −2,0 point.
3. Le système final est **l'admissible le moins cher** (ordre de la section 1). Égalité de coût : le plus haut en macro-F1.
4. Si aucun autre que B n'est admissible, B est le système final.
5. La règle s'applique une seule fois ; aucune recette n'est modifiée ni ajoutée entre ce gel et RM-20 (règle d'ordonnancement 3 de la feuille de route).

## 3. Ce qui est figé avec le système
Composition exacte (graines, poids de l'ensemble 50/50 ou autres), seuil de température, niveaux conformes et familles pour l'étalonnage par famille, seuil d'abstention, empreintes SHA-256 des modèles et de la fiche ; hypothèse d'échangeabilité énoncée ; étalonnage conforme fait sur le développement seulement.

## 4. Prédiction chiffrée du test scellé (à remplir avant le hachage)
- Macro-F1 attendue du système final sur le test scellé : valeur centrale = macro-F1 regroupée hors pli du système final ; intervalle à 80 % : ± 3,0 points (écart-type bootstrap de 1,3 point sur 3 586 patients, plus l'effet d'un entraînement sur tout le développement et le décalage d'auteurs) ; **à remplir : ___ [___ ; ___]**.
- Probabilité que la macro-F1 du test scellé soit au moins égale à la macro-F1 hors pli moins 2,0 points : 0,75 (hypothèse à réviser).
- Différence attendue avec le meilleur TF-IDF : valeur centrale = différence hors pli ; probabilité d'un verdict « gain confirmé » à δ = 2,0 : à calculer par la simulation de `rm17_power_rule.py` sur les largeurs mesurées.
- Couverture conforme par famille : attendue au niveau visé moins 0,03 pour la famille la moins couverte (probabilité 0,6).

## 5. Procédure d'ouverture (rappel)
Deux temps de PROTOCOLE.md 6.8 : code `sealed.py` à deux fonctions écrit avant, répétition générale du temps B réussie avant l'ouverture, un seul accès journalisé ; RM-51 lit l'incertitude sur la même ouverture ; RM-49 (benchmark public) se lit après.

## 6. Conditions d'arrêt
Si RM-37 n'est pas accepté, ou si la règle de puissance v2 échoue pour la paire choisie, l'évaluation du test scellé se fait **sans verdict** (évaluation du candidat final seulement), conformément au protocole.

## 7. Mise à jour du 05/10/2026 après RM-56 (le brouillon reste non figé et non haché)
- **Candidats C1 et C2 sortis** de la liste fermée (PROTOCOLE_V2.md section 4 : gain non préservé, fuite significative). Règle rejouée sur A, B, D, E, F, G (run `selection-systeme-final-apres-rm56`) : **système final retenu : G**, ensemble LoRA 4B + encodeur moyenné (5 graines) + TF-IDF caractères équilibré, parts égales ; seul admissible (macro-F1 de développement 0,7799 ; bornes basses contre G : E −2,79, F −2,47).
- **À figer dans l'ADR-016** : graine du LoRA final (1000, une seule : réserve déclarée), cinq graines d'encodeur (1000 à 1004), TF-IDF final, parts égales (un tiers chacun), empreintes des modèles entraînés sur les 3 586 patients, température et quantile conforme à recalculer sur les prédictions hors pli de G, familles de Mondrian de `glm_v3_families.py`, seuil d'abstention.
- **Prédiction à hacher** (valeurs de départ, à réviser au gel) : macro-F1 du test scellé centrée sur 0,78 (développement 0,7799), intervalle à 80 % de ± 3,0 points ; différence avec le meilleur TF-IDF centrée sur +6,0 (développement +5,98) ; **probabilité d'un « gain confirmé » à δ = 2,0 : environ 0,47** (largeur attendue 8,23 au format du test, run `puissance-au-format-du-test-scelle-g`) ; probabilité de « non résolu » environ 0,5 ; probabilité d'une « absence de gain utile » inférieure à 0,05 ; couverture conforme minimale par famille au moins égale à la cible moins 0,03 (probabilité 0,6).
- **Réserve** : le LoRA final n'est entraîné qu'une fois (variance entre graines du LoRA non mesurée) ; G a un écart de développement à E de seulement +0,78 : si la différence avec E ou F devait être rapportée, elle serait « non résolue ».
- **Ordre restant** : LoRA final (en file) puis temps A (prédictions sur les textes du test, sans étiquette), puis ce gel, puis `sealed_evaluation.py check`, puis l'ouverture unique.

## 8. Mise à jour du 06/10/2026 (le brouillon reste non figé et non haché)
- **LoRA final fait** : run `20261006-022716-final-lora-s1000` (16 035 s au total, empreinte du dossier de l'adaptateur `c2a0963aea7a5767…`, graine 1000, 3 586 patients) ; temps A `20261006-023402-temps-a-lora-s1000` (`7c85a097aeca66ca…`). Réserve inchangée : un seul LoRA final, variance entre graines non mesurée.
- **Composition de G, avec les runs à citer dans l'ADR-016** (empreintes tronquées à 16 caractères, complètes dans le registre) :

| Composant | Run d'entraînement | Empreinte | Run du temps A | Empreinte |
|---|---|---|---|---|
| TF-IDF caractères équilibré | `final-tfidf` | `90dbcd5d1af5b168` | `temps-a-tfidf` | `853de1b12fbedf30` |
| Encodeur, graine 1000 | `final-encoder-s1000` | `4e342178a8bbf091` | `temps-a-encoder-s1000` | `4c267da9eef5b5fc` |
| Encodeur, graine 1001 | `final-encoder-s1001` | `3312bd9539663e2c` | `temps-a-encoder-s1001` | `c7de5d149f000c03` |
| Encodeur, graine 1002 | `final-encoder-s1002` | `d7bf22c9eb20dae6` | `temps-a-encoder-s1002` | `bf858081fa95204b` |
| Encodeur, graine 1003 | `final-encoder-s1003` | `2703e46127f0ae45` | `temps-a-encoder-s1003` | `7e4905272ebe40c3` |
| Encodeur, graine 1004 | `final-encoder-s1004` | `bab852c5bd289380` | `temps-a-encoder-s1004` | `93a9b44a58aa584d` |
| LoRA 4B, graine 1000 | `final-lora-s1000` | `c2a0963aea7a5767` | `temps-a-lora-s1000` | `7c85a097aeca66ca` |

Les trois élèves distillés (`final-student-s1000` à `s1002`) sont entraînés et ont leur temps A, mais **ne font pas partie de G** (C1 et C2 sortis après RM-56).
- **Contrôle de cohérence des prédictions du temps A** (sans étiquette, sans ouverture du test scellé) : les dix fichiers `results/sealed_temps_a/*.probs.npz` portent les mêmes 633 identifiants, 18 colonnes, des lignes de somme 1 et des valeurs finies.
- **Reste avant le gel** : (1) décision de Cyril (question Q22 de `tasks/QUESTIONS_POUR_CYRIL.md`) ; (2) recalcul de la température et du quantile conforme de G sur les prédictions hors pli (la lecture du 05/10 donne ECE 0,016 et couverture 0,901 par famille, à rejouer avec le LoRA final comme composant) ; (3) valeurs de la prédiction chiffrée de la section 4, à réviser puis hacher ; (4) rédaction de l'ADR-016 ; (5) `sealed_evaluation.py check`. L'ouverture des étiquettes (RM-20) reste une décision séparée.
