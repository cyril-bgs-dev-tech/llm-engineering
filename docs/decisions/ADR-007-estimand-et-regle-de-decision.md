# ADR-007 : estimand, rééchantillonnage et règle de décision des comparaisons (micro-tâche RM-11)

## Status
**Proposée, non figée**, brouillon du 02/10/2026. Elle remplace la « règle des deux écarts-types » du plan V6. Trois valeurs restent à Cyril (question Q5 de `tasks/QUESTIONS_POUR_CYRIL.md`) : le seuil « pratiquement utile » δ, le nombre de graines K et le budget B. Aucune comparaison ne se lance avant leur fixation et le gel de `PROTOCOLE.md` (P0-46).

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
| Plus petites classes évaluées | XXII : 31 patients ; XII : 36 ; XXI : 49 ; IV : 56 ; soit environ 5, 5, 7 et 8 patients dans un test de 15 % |
| Auteurs | 104 ; raccourci d'auteur non signalé (ADR-006) |

Conséquence : la macro-F1 pèse autant une classe de 5 patients de test qu'une de 170 ; l'incertitude sur le test scellé sera large. Ce n'est pas un défaut à cacher, c'est ce que la règle doit rendre visible.

## Decision (proposition)

**1. Estimand.** Δ = différence entre la macro-F1 moyenne de la recette testée et celle de la recette de référence, la moyenne portant sur les graines d'entraînement, évaluée sur de nouveaux patients du **même corpus fictif**. La macro-F1 est celle de ADR-004 (niveau chapitre, 17 classes, `AUTRE` rapportée à part). Aucune conclusion hors de ce corpus, de cette tâche et de ce découpage.

**2. Rééchantillonnage hiérarchique** (K ≥ 5 graines par recette). Par réplique, avec B = 10 000 et une graine fixée :
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

**5. Seuil utile δ : défaut proposé 2,0 points de macro-F1, à confirmer par Cyril.** C'est un jugement de valeur sur ce qui compte en pratique, pas un résultat de données. **Règle de puissance, vérifiée par RM-15 avant tout run confirmatoire** : on calcule, sur les prédictions hors pli des références (P1-04, P1-06, P1-07), la largeur de l'intervalle apparié à 98,33 %. Si elle dépasse 2 × δ, le test scellé ne peut pas séparer « gain utile » de « pas de gain utile » ; on le dit avant de lancer et on choisit : réduire l'ambition (δ plus grand), augmenter K, ou déclarer la comparaison exploratoire. On ne lance pas un test dont le verdict est « non résolu » par construction.

**6. Phase de développement.** Les plis (exploratoires) servent au réglage et au choix de l'élève. L'appariement se fait sur les prédictions hors pli, un patient prédit une seule fois par graine. Aucun verdict n'en est tiré.

**7. Vérification de l'implémentation (P1-02).** Bootstrap apparié, McNemar, permutation et Holm sont comparés à SciPy et statsmodels sur des cas à réponse connue ; la couverture de l'intervalle hiérarchique est vérifiée par simulation (environ 95 % attendus sur données synthétiques où Δ est connu). Les résultats de ces vérifications vont au registre.

## Alternatives Considered
- **Règle des deux écarts-types** : écartée, elle ne tient pas compte du bruit d'échantillonnage des patients ni de la dépendance entre graines.
- **Bootstrap sur patients seulement, graines ignorées** : écarté pour le verdict ; gardé comme présentation séparée quand K < 5.
- **Test de McNemar sur l'exactitude comme verdict principal** : écarté, la métrique principale est la macro-F1 (ADR-004) ; McNemar reste un contrôle complémentaire.
- **Holm seul sur l'intervalle** : plus puissant mais plus lourd à expliquer pour un intervalle simultané ; Bonferroni est conservateur avec m = 3.
- **δ dérivé des données** : écarté, ce serait fixer le critère après avoir vu l'incertitude.

## Consequences
- Bloque, tant que Cyril n'a pas fixé δ, K et B : P0-46 (gel de `PROTOCOLE.md`), G-P0, et tout run comparatif.
- Ajoute à RM-15 la règle de puissance du point 5.
- Un seuil δ très bas rendra presque toute comparaison « non résolue » sur 633 patients : c'est une information sur le corpus, à publier comme telle.
- Le plan statistique reste lisible pour un lecteur non statisticien : trois mots de verdict, un intervalle, une règle écrite avant les chiffres.
