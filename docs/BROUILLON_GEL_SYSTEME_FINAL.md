# Brouillon de la fiche de gel du système final (RM-50), non figé, non haché

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
