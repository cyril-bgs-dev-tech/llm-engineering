# ADR-012 : porte RM-15 après les références (décision de nuit, provisoire)

## Status
**Acceptée provisoirement, à confirmer ou casser par Cyril** (consigne de nuit N23 : trancher quand il dort). Réversible : elle autorise seulement des runs de criblage sur le pli 0 (P1-11) ; rien de confirmatoire, aucun test scellé.

## Date
2026-10-03

## Context
RM-15 demande, avec les chiffres de P1-04, P1-06, P1-07 et RM-14, si la comparaison est informative (variance, puissance, raccourcis) ou s'il faut arrêter ou simplifier avant les LLM.

| Élément | Résultat | Run |
|---|---|---|
| Plancher sans modèle (chapitre) | macro-F1 0,0252 à 0,058 | `p1-03-bounds` |
| TF-IDF, chapitre, par patient | 0,6844 [0,657 ; 0,709] ; v2 0,6889, non distinct (+0,45 [−1,21 ; +2,11]) | `20261003-121942`, `-125802` |
| TF-IDF, doctype et spécialité | 0,991 et 0,987 : tâches quasi triviales | `p1-04`, `p1-05-v2` |
| Encodeur CamemBERT-bio, pli 0, 2 époques | 0,4484 au meilleur taux (1e-4, bord de grille) ; 24,9 points sous le TF-IDF [−30,3 ; −17,9] | `p1-07-*`, `…-minus-tfidf-fold0` |
| Raccourci d'auteur | « signalé » : +3,87 [+1,27 ; +6,31] (v1), +3,42 [+1,17 ; +5,78] (v2) | RM-14, ADR-011 |
| Puissance du test scellé à δ = 2,0 | gain confirmé simulé 2,3 % à 2δ ; premier cycle classé EXPLORE (C1) | `power-curves-audit`, `coverage-hierarchical-interval` |

## Decision
**GO conditionnel** pour le criblage P1-11 sur le pli 0, avec ces réserves écrites :
1. La référence à battre est le **TF-IDF** (≈ 0,68), pas un plancher de 0,06 : un LLM qui ne le dépasse pas n'apporte rien sur cette tâche, et le rapport le dira.
2. L'encodeur est **sous-entraîné à 2 époques et au bord de la grille** : son score ne dit rien de ce qu'un encodeur bien réglé donnerait ; les époques (2) et la grille (4 taux) sont figées par le protocole, donc l'écart est publié tel quel avec ce statut.
3. Le raccourci d'auteur étant signalé, **tout résultat est rapporté en plis par patient et en plis par auteur** dès que les prédictions existent (Q18 reste ouverte pour Cyril).
4. Le premier cycle reste exploratoire (puissance) : aucune affirmation de gain confirmé n'est permise (`claim-gate`).

## Alternatives Considered
- **Arrêt** : écarté, la référence TF-IDF est informative (au-dessus du plancher, intervalle étroit) et le criblage coûte peu de B (≈ 6,6 h sur 90).
- **Simplifier à doctype ou spécialité** : écarté, quasi triviales (≥ 0,98), aucune place pour une amélioration mesurable.

## Consequences
- P1-11 lancé le 03/10/2026 à 13 h 25 UTC (fiche `experiments/2026-10-03-p1-11-criblage-eleves.md`).
- Si les LLM restent sous le TF-IDF sur le pli 0 : question stratégique pour Cyril (poursuivre la distillation comme exercice d'apprentissage, RM-17).
