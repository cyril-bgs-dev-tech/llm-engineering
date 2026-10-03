# ADR-011 : écart entre plis par patient et plis par auteur sur la référence TF-IDF (RM-14)

## Status
**Proposée, non ratifiée.** Écrite le 03/10/2026 par l'assistant de nuit ; **ne modifie aucune règle du protocole gelé** (PROTOCOLE.md, empreinte `aba89842…`). Toute modification de la métrique primaire exige une nouvelle version du protocole, une ADR acceptée et la décision de Cyril (Q18).

## Date
2026-10-03

## Context
La fiche `experiments/2026-10-03-rm-14-raccourci-tfidf.md` (empreinte dans `experiments/INDEX.md`, figée avant le run) posait : « raccourci signalé » si l'écart de macro-F1 (plis par patient moins plis par auteur) est d'au moins 3 points avec une borne basse d'IC à 95 % strictement positive. La section 3 du protocole dit que, si un raccourci d'auteur est signalé, les plis groupés par auteur deviennent la métrique principale ; cette clause visait la mesure P0-30 (auteur seul contre spécialité seule, non signalée), pas RM-14, mais la logique est la même.

Résultat (runs `p1-06-tfidf-chapter` `20261003-121942` et `p1-06-tfidf-chapter-author-folds` `20261003-121959`, verdict `20261003-122037-rm-14-author-shortcut-tfidf`) : macro-F1 regroupée 0,6844 [0,6573 ; 0,7089] par patient, 0,6457 [0,6203 ; 0,6688] par auteur ; écart **+3,87 points, IC 95 % [+1,27 ; +6,31]**, verdict préenregistré **« signalé »**. La prédiction de la fiche (écart dans ±3 points, probabilité 0,8) est donc **infirmée**.

## Lectures possibles (à départager, non départagées)
1. **Fuite par auteur** : des patients du même auteur se ressemblent (style, gabarit, thème), et des plis par patient les mélangent entre entraînement et évaluation ; le chiffre par patient est optimiste.
2. **Recouvrement thématique légitime** : l'auteur est corrélé à la spécialité (P0-30 : auteur seul 0,377, spécialité seule 0,385, quasi égaux), donc des plis groupés retirent aussi de l'information thématique légitimement présente dans un nouveau corpus.
3. **Artefact de découpage** : `StratifiedGroupKFold` stratifie moins bien (plis de 663 à 763 patients), et la grille TF-IDF est à son bord haut (C = 100 retenu dans les 10 plis), donc les deux chiffres sont sous-réglés de façon possiblement différente.

## Decision (proposition, pas une décision)
- Ne rien changer au protocole gelé ni à la métrique primaire cette nuit.
- **Rapporter les deux chiffres** pour toute référence : métrique par patient (primaire gelée) et métrique par auteur (sensibilité), avec cette ADR.
- Le **test scellé est stratifié par patient**, jamais groupé : il hérite donc du même optimisme éventuel pour toutes les recettes ; l'effet sur les **comparaisons appariées** est probablement plus faible que sur le niveau absolu, mais ce n'est pas mesuré (une recette qui exploite le style d'auteur plus qu'une autre fausserait aussi l'écart).
- Option à décider par Cyril : passer à une v2 du protocole avec plis groupés par auteur comme métrique de développement, au prix d'un test scellé non groupé (non refaisable sans le détruire).

## Alternatives Considered
- **Passer aussitôt en plis groupés** : écarté pour la nuit, c'est une modification du protocole gelé.
- **Ignorer l'écart** : écarté, il est significatif par la règle écrite avant le run.

## Consequences
- Q18 posée à Cyril ; le gel et son contrôle (`check_frozen.py`) restent verts.
- **Mesuré le 03/10 (grille v2, fiche `2026-10-03-tfidf-v2-grille-etendue.md`)** : écart +3,42 points [+1,17 ; +5,78], toujours « signalé » ; la lecture 3 (grille bornée) n'explique donc pas l'écart à elle seule. Restent les lectures 1 et 2 (fuite par auteur ou recouvrement thématique).
- À mesurer ensuite (sans test scellé) : avec le premier encodeur ou la LoRA de référence (l'écart persiste-t-il pour un modèle appris ?).
- Aucune affirmation publique sur « un raccourci d'auteur » tant que les lectures 1 et 2 ne sont pas départagées (`claim-gate`).
