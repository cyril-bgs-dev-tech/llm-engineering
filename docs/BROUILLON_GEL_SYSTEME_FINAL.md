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
