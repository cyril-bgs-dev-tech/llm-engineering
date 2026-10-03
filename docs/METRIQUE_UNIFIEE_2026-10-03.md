# Métrique unifiée : dérivation, preuve simulée, limites (2026-10-03)

Réponse à la demande de Cyril : « unifies de manière mathématiquement optimale la métrique unifiée que tu proposes ». **Statut : proposition d'analyse, pas une modification du protocole.** La métrique primaire gelée (macro-F1 sur 17 chapitres, δ = 2,0) ne change pas ; changer une règle gelée exige une nouvelle version, un ADR et ta décision (Q15 reste ouverte).

## 1. Ce que « optimal » veut dire ici

Aucune métrique n'est optimale dans l'absolu. On dit « optimale » **relativement à huit critères écrits d'avance** et on prouve ce qui peut l'être :

| Critère | Exigence |
|---|---|
| D1 | Propre : le score est maximisé en moyenne par les vraies probabilités |
| D2 | Chaque chapitre pèse pareil (le besoin est une macro-moyenne, pas une exactitude globale) |
| D3 | Interprétable en unité d'information (nats par patient) |
| D4 | Variance minimale pour détecter un vrai écart (efficacité) |
| D5 | Robuste à la suréconfiance (queues lourdes) |
| D6 | Estimable sans biais d'optimisme (poids fixés sur données indépendantes) |
| D7 | Compatible avec la décision gelée (macro-F1 reste le juge confirmatoire) |
| D8 | Calculable avec une erreur-type fermée aux effectifs réels (chapitre XXII : 4 patients) |

## 2. Dérivation

**T1 (D1, Bernardo 1979).** Pour plus de deux classes, la seule règle de score propre et locale (qui ne dépend que de la probabilité de la classe réalisée) est le logarithme, à transformation affine près. Toute autre règle propre (Brier, sphérique) dépend aussi des probabilités des classes fausses.

**T2 (D2, D3).** Soit L_bal = (1/K) Σ_c E[ −log p(c | x) | y = c ]. Chaque terme est l'espérance de la log-vraisemblance de la classe sachant la classe : sous un a priori uniforme, c'est l'entropie croisée du modèle contre la vraie loi conditionnelle, minimisée par le vrai modèle. G = log K − L_bal est le gain d'information moyen par rapport au modèle sans information (0 pour l'uniforme, log K pour le parfait), en nats par patient. Une différence G(A) − G(B) = L_bal(B) − L_bal(A) est un rapport de vraisemblance moyen (Neyman-Pearson) : le test le plus puissant d'une recette contre l'autre, à chapitre équilibré.

**T3 (D4, combinaison).** Pour combiner plusieurs métriques d'écart d_j (macro-F1, G, …) en un score s = w·d, le rapport signal sur bruit est (w·μ)/√(wᵀΣw). Par Cauchy-Schwarz il est maximal pour w ∝ Σ⁻¹μ (méthode GLS/O'Brien). Contrainte nécessaire : w ≥ 0 (pas de métrique qui compte à l'envers) ; sous cette contrainte c'est un programme quadratique à solution unique.

**T4 (D6).** μ et Σ ne s'estiment pas sur les données qui servent ensuite à décider : le poids optimisé sur l'échantillon évalué est biaisé vers l'optimisme (le maximum de bruit corrélé). Les poids sont donc **fixés sur les plis de développement**, gelés, puis appliqués sans réestimation au test.

**T5 (D8).** Estimateur post-stratifié : Ĝ = (1/K) Σ_c ḡ_c ; variance Var(Ĝ) = (1/K²) Σ_c s_c²/n_c. Avec n_c = 4 (XXII) à 9, les petits chapitres dominent la variance ; on prend les degrés de liberté de Satterthwaite et on déclare « très petit support » sous 10, comme dans `evaluation.py`.

**Candidat unifié.** Trois couches, sans les mélanger en un seul nombre magique :
1. **Décision (confirmatoire, inchangée)** : macro-F1 sur 17 chapitres, δ = 2,0.
2. **Information (candidate)** : G, log loss moyennée par chapitre, en nats par patient, avec erreur-type T5 ; rapportée à côté, jamais substituée.
3. **Fiabilité (diagnostic)** : ECE et décomposition calibration + résolution (Bröcker 2009), queue à 95 % de la log loss.
Un score combiné GLS positif (T3) n'est envisagé qu'en exploration, avec poids gelés sur le développement (T4).

## 3. Preuve simulée (run `20261003-113946-metric-widths-candidates`)

Probabilités simulées par softmax, effectifs réels du test (629 patients, 17 chapitres), deux modèles de même niveau, bootstrap stratifié ; largeur de l'IC à 98,33 % de l'écart, rapportée à l'effet d'un vrai changement de compétence de 0,5 unité de marge (plus petit = mieux sépare le signal du bruit).

| Niveau, corrélation | macro-F1 | log loss par chapitre | MCC |
|---|---|---|---|
| 1,5 ; 0,5 | 0,649 | 0,622 | 0,709 |
| 1,5 ; 0,8 | 0,504 | 0,387 | 0,564 |
| 2,5 ; 0,5 | 0,784 | 0,566 | 0,650 |
| 2,5 ; 0,8 | 0,622 | 0,353 | 0,528 |

Lecture : dans ces quatre configurations simulées, la log loss par chapitre a un rapport bruit sur effet plus petit que la macro-F1, de 4 % à 43 % selon la configuration. Autrement dit, elle détecterait un vrai écart avec un intervalle relativement plus étroit.

## 4. Limites, dites explicitement

- **Le simulateur favorise la log loss.** Les probabilités sont des softmax bien calibrées par construction ; de vrais modèles affinés sont souvent suréconfiants, et une seule erreur confiante pèse très lourd dans le logarithme (D5 non testé). La preuve n'est donc qu'une borne optimiste.
- **L'échelle de l'effet est arbitraire** (0,5 unité de marge, pas un δ réel de 2 points de macro-F1) ; le rapport compare des métriques entre elles, il ne dit pas combien de vrais gains seraient confirmés.
- **Corrélations inventées** (0,5 et 0,8) ; les vraies sont inconnues avant les premiers runs.
- T3 et T4 sont des résultats standards appliqués ici, non redémontrés ; aucun poids GLS n'a été estimé (pas de données de développement avec deux recettes).
- Rien dans ce document n'est un résultat sur de vrais modèles ni ne justifie une affirmation de performance (claim-gate : aucune sortie du dépôt).

## 5. Ce que je propose, sans le décider

Garder la macro-F1 gelée comme juge confirmatoire, et préenregistrer G (log loss par chapitre) comme **métrique secondaire à rapporter** dans toutes les fiches de P1, avec son erreur-type. Le choix de la promouvoir en primaire, ou d'un score GLS, relève de la Q15.
