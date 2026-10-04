# Protocole v2 (BROUILLON du 04/10/2026, non appliqué, protocole v1 gelé inchangé)

À accepter par Cyril avant tout run du second cycle et avant toute ouverture du test scellé. Il met en œuvre l'ADR-015 ; il ne modifie aucun fichier de `experiments/frozen/`.

## 1. Ce que les mesures du premier cycle imposent
- Recettes mûres obligatoires (la recette gelée à 2 époques sous-estimait l'encodeur de 0,45 à 0,73 et le LoRA de 0,587 à 0,78).
- La macro-F1 est portée à 85 % par cinq classes de 27 à 63 patients ; le bruit d'un pli est de l'ordre de 2 points, entre graines de 2,6 points.
- La règle de puissance du protocole v1 (cinq graines sur un pli) donne 12,2 points de largeur : jamais confirmatoire. Sur plis, la largeur simulée est de 3,8 à 6,7.

## 2. Ce qui change
| Élément | v1 gelé | v2 proposé |
|---|---|---|
| Recette | 4 taux, 2 époques, une graine de réglage | grilles préenregistrées par famille, budget égal (même nombre de runs et d'heures) ; époques de 4 à 20 pour l'encodeur, 4 à 10 pour le LoRA |
| Unité d'évaluation | un pli de 717 patients, cinq graines | les **cinq plis** du développement (3 586 prédictions hors pli) × cinq graines pour les familles bon marché |
| Systèmes comparés | référence LoRA, H1 distillation, H2 tâche voisine, H3 les deux | référence bon marché (ensemble encodeur 5 graines + TF-IDF caractères et poids, TF-IDF seul, encodeur seul), LoRA mûr, puis H1 à H3 contre cette référence |
| Question primaire (une seule) | H1 à H3, trois comparaisons Bonferroni | **« l'ensemble encodeur + TF-IDF dépasse-t-il le meilleur TF-IDF de plus de δ ? »** (déjà +5,0 en moyenne sur trois plis, résolu à chacun) puis, secondaire, LoRA contre ensemble |
| δ | 2,0 point | 2,0 conservé ; réviser seulement si la largeur à cinq plis reste au-dessus de 4 points |
| Estimand du test scellé | nouveaux patients du même corpus | idem, plus mesure « nouveaux auteurs » par leave-one-author-out (secondaire, rapportée à côté) |
| Incertitude | LAC marginal | LAC marginal **et** conditionnel par famille rapportés (coût : ensembles 1,6 à 3 fois plus grands) ; étalonnage par plis d'auteurs |

## 3. Règle de puissance v2
Statistique : largeur de l'IC à 98,33 % (ou 95 % si une seule comparaison primaire) de la **différence appariée de macro-F1 entre les deux systèmes comparés** (pas entre graines), par bootstrap de patients stratifié par classe sur les 3 586 prédictions hors pli, R = 10 000, graine 20261002, moyenne des prédictions des graines avant la différence. Seuil : 4,0 points. Si elle échoue, les comparaisons restent EXPLORE sans changer δ (même repli que v1). Calcul : `scripts/rm17_power_rule.py` à étendre (mode « deux systèmes ») dès que les plis 3 et 4 de l'encodeur sont entraînés.

**Aperçu mesuré (04/10)** : sur trois plis (2 152 prédictions), largeur de « ensemble encodeur + TF-IDF moins TF-IDF » : 4,29 points à 95 %, 5,24 à 98,33 % ; extrapolation à cinq plis : environ 3,3 et 4,1. La règle v2 passerait avec une question primaire unique à 95 %.

## 4. Ouverture du test scellé (inchangée)
Une seule fois, en deux temps (`sealed.py`), journal des accès, temps A pour toutes les recettes gelées et le candidat final, temps B avec marqueur avant lecture des étiquettes, écriture atomique, répétition générale préalable. Aucun réglage sur le test.

## 5. Ce que Cyril doit accepter ou refuser
(1) Les recettes mûres et le budget de réglage égal par famille ; (2) l'évaluation à cinq plis et cinq graines pour les familles bon marché ; (3) la question primaire unique ci-dessus ; (4) le maintien de δ = 2,0 sous condition de largeur ; (5) le report de H1 à H3 (distillation, tâche voisine) à après la règle de puissance du second cycle.

## 6. Préenregistrement
Avant tout run du second cycle : une fiche par famille avec grille, budget, critère et prédictions probabilisées, hachée dans `experiments/INDEX.md` ; avant l'ouverture : la liste figée des recettes et des poids d'ensemble (le poids 0,5 est fixé ici, pas choisi sur le test).
