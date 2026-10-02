# ADR-007 : estimand, rééchantillonnage et règle de décision des comparaisons (micro-tâche RM-11)

## Status
**Acceptée** le 03/10/2026 par Cyril (estimand, rééchantillonnage hiérarchique, famille confirmatoire de trois comparaisons, verdict en trois valeurs). Elle remplace la « règle des deux écarts-types » du plan V6. Valeurs fixées par Cyril le 02/10/2026 : seuil « pratiquement utile » **δ = 2,0 points** de macro-F1, graines **K = 5**, budget **B = 90 h** de GPU. L'alerte de puissance de la décision 5 reste suivie par RM-15 (question Q12) : l'acceptation n'engage pas à lancer une comparaison dont le verdict serait « non résolu » par construction. Aucune comparaison ne se lance avant le gel de `PROTOCOLE.md` (P0-46).

## Date
2026-10-02

## Context
ADR-004 a adopté la question principale (la distillation améliore-t-elle la LoRA de référence « d'une ampleur pratiquement utile, au-delà de la variance entre graines ? ») mais n'a défini ni l'estimand, ni le rééchantillonnage, ni la règle de décision. Faits mesurés qui contraignent le choix (`results/measures/splits_summary.json`) :

| Fait | Valeur |
|---|---|
| Patients du jeu de travail | 4 219 |
| Test scellé interne (confirmatoire, stratifié) | 633 patients |
| Plis de développement (exploratoires) | 5 plis de 717 à 718 |
| Classes évaluées | 17 (plus `AUTRE`, exclue de la macro-F1) |
| Plus petites classes évaluées | XXII : 31 patients ; XII : 36 ; XXI : 49 ; IV : 56 ; soit 4, 6, 7 et 9 patients dans le test scellé réel |
| Auteurs | 104 ; raccourci d'auteur non signalé (ADR-006) |

Conséquence : la macro-F1 pèse autant une classe de 5 patients de test qu'une de 170 ; l'incertitude sur le test scellé sera large. Ce n'est pas un défaut à cacher, c'est ce que la règle doit rendre visible.

## Decision

**1. Estimand.** Δ = différence entre la macro-F1 moyenne de la recette testée et celle de la recette de référence, la moyenne portant sur les graines d'entraînement, évaluée sur de nouveaux patients du **même corpus fictif**. La macro-F1 est celle de ADR-004 (niveau chapitre, 17 classes, `AUTRE` rapportée à part). Aucune conclusion hors de ce corpus, de cette tâche et de ce découpage.

**2. Rééchantillonnage hiérarchique** (K ≥ 5 graines par recette). Par réplique, avec R = 10 000 répliques (la lettre B est réservée au budget de GPU, ADR-004) et une graine fixée :
1. tirer les patients **avec remise, stratifié par classe** (les effectifs de classe restent ceux du test, aucune classe ne disparaît) ; le même tirage sert aux deux recettes (appariement) ;
2. tirer K graines **avec remise**, indépendamment pour chaque recette ;
3. calculer la macro-F1 de chaque (recette, graine) sur les patients tirés, la moyenner sur les graines, puis faire la différence Δ*.

Unité : le patient (PROTOCOLE.md § 3). Les 9 groupes de quasi-doublons sont d'un même auteur et déjà dans une seule partition ; si le raccourci d'auteur était signalé un jour, le tirage se ferait par auteur.
**Si K < 5** (budget serré) : présentation séparée. Intervalle par patients sur les prédictions moyennées sur graines, et écart-type entre graines rapporté à côté, avec la mention « non combiné ».

**3. Famille de comparaisons confirmatoires, fixée d'avance** (m = 3, P3-07), toutes contre la LoRA de référence gelée (P1-20) à budget de réglage égal :
H1 distillation, H2 tâche voisine, H3 les deux ensemble. Tout le reste est **exploratoire** (étiquette EXPLORE) : intervalle non ajusté, aucun verdict.
La correction de Holm porte sur les p-valeurs de la famille. Pour la règle de décision, l'intervalle est pris au niveau de Bonferroni, 1 − 0,05/3, soit 98,33 % : choix volontairement prudent et simple, qui contient celui de Holm.

**4. Règle de décision, verdict en trois valeurs, écrite avant les runs.** Avec [L, U] l'intervalle de Δ et δ > 0 le seuil utile :
- **gain confirmé** si L > δ ;
- **absence de gain utile** si U < δ ;
- **non résolu** sinon. La fiche dit alors combien de graines ou de patients il faudrait.
La variabilité entre graines est incluse dans l'intervalle (étape 2) ; le critère « au-delà de la variance entre graines » d'ADR-004 n'a donc pas besoin d'un second seuil.

**5. Seuil utile δ : 2,0 points de macro-F1, fixé par Cyril le 02/10/2026.** C'est un jugement de valeur sur ce qui compte en pratique, pas un résultat de données. **Règle de puissance, vérifiée à la porte RM-17 (après P1-19 et P1-20, avant P2-01) selon `PROTOCOLE.md` 6.3, avant tout run confirmatoire** : on calcule, sur les prédictions hors pli des références (P1-04, P1-06, P1-07), la largeur de l'intervalle apparié à 98,33 %. Si elle dépasse 2 × δ, le test scellé ne peut pas séparer « gain utile » de « pas de gain utile » ; on le dit avant de lancer et on choisit : réduire l'ambition (δ plus grand), augmenter K, ou déclarer la comparaison exploratoire. On ne lance pas un test dont le verdict est « non résolu » par construction.

*Alerte du 02/10/2026, corrigée le 03/10/2026 (run `20261002-221006-power-sketch-ic-width-v2`, simulation, pas la mesure de RM-17).* Avec les effectifs **réels** du test (629 patients évalués plus 4 `AUTRE` ; chapitres les plus petits : XXII 4, XII 6, XXI 7, IV 9, V 9), l'intervalle apparié à 98,33 % de la différence de macro-F1 entre deux modèles de même niveau mesure de **7,8 à 13,7 points** de large selon l'exactitude et la corrélation d'erreurs supposées (bootstrap sur patients seuls, donc borne basse), contre 4 points (2 × δ) admis par la règle. La première version de l'esquisse (run `20261002-200851-power-sketch-ic-width`, 7,5 à 13,5) utilisait des effectifs proportionnels et non réels, à tort décrits comme réels. Si les prédictions réelles se comportent ainsi, la règle de puissance échouera et la comparaison confirmatoire sera « non résolue par construction » avec δ = 2,0 : le repli est écrit dans `PROTOCOLE.md` 6.3 (condition C1 de Cyril). Limites : prédictions et corrélations inventées, erreurs réparties selon la prévalence ; des modèles d'une même famille ont des erreurs plus corrélées, ce qui rétrécit l'intervalle. La mesure de RM-17 (`PROTOCOLE.md` 6.3) tranche avec les vraies prédictions hors pli de P1-19.

**6. Phase de développement.** Les plis (exploratoires) servent au réglage et au choix de l'élève. L'appariement se fait sur les prédictions hors pli, un patient prédit une seule fois par graine. Aucun verdict n'en est tiré.

**7. Vérification de l'implémentation (P1-02).** Bootstrap apparié, McNemar, permutation et Holm sont comparés à SciPy et statsmodels sur des cas à réponse connue ; la couverture de l'intervalle hiérarchique est vérifiée par simulation (environ 95 % attendus sur données synthétiques où Δ est connu). Les résultats de ces vérifications vont au registre.

## Alternatives Considered
- **Règle des deux écarts-types** : écartée, elle ne tient pas compte du bruit d'échantillonnage des patients ni de la dépendance entre graines.
- **Bootstrap sur patients seulement, graines ignorées** : écarté pour le verdict ; gardé comme présentation séparée quand K < 5.
- **Test de McNemar sur l'exactitude comme verdict principal** : écarté, la métrique principale est la macro-F1 (ADR-004) ; McNemar reste un contrôle complémentaire.
- **Holm seul sur l'intervalle** : plus puissant mais plus lourd à expliquer pour un intervalle simultané ; Bonferroni est conservateur avec m = 3.
- **δ dérivé des données** : écarté, ce serait fixer le critère après avoir vu l'incertitude.

## Consequences
- Ne bloque plus P0-46 (estimand ratifié, valeurs fixées) : P0-46 (gel de `PROTOCOLE.md`), G-P0, et tout run comparatif.
- Ajoute à RM-17 la règle de puissance du point 5, précisée dans `PROTOCOLE.md` 6.3 (RM-15 reste la porte sur les références).
- Un seuil δ très bas rendra presque toute comparaison « non résolue » sur 633 patients : c'est une information sur le corpus, à publier comme telle.
- Le plan statistique reste lisible pour un lecteur non statisticien : trois mots de verdict, un intervalle, une règle écrite avant les chiffres.
