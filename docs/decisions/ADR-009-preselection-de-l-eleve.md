# ADR-009 : présélection de l'élève du premier cycle (micro-tâche RM-13)

## Status
**Acceptée** : écrite le 02/10/2026, ratifiée par Cyril le 03/10/2026. La règle est écrite **avant tout résultat de macro-F1** sur la tâche principale : aucun n'existe à cette date (seuls des spikes de mémoire et de compatibilité ont tourné). Elle ne s'applique qu'au premier cycle.

## Date
2026-10-02

## Context
P1-11 crible deux à trois points de départ, P1-12 choisit l'élève. Le spike P0-06 donne les modèles qui se chargent, classent et tiennent en mémoire (page `compatibilite-modeles-p0-06`). Le wiki rappelle qu'un taux d'apprentissage unique peut avantager un modèle sans que cela se voie : une comparaison de points de départ à un seul taux est une comparaison biaisée.

## Decision

**Candidats admis au criblage (trois).**

| Candidat | Voie | Pic de mémoire mesuré | Pourquoi |
|---|---|---|---|
| Qwen3.5-4B | A | 11,9 Gio | le plus petit élève de la famille du professeur Qwen |
| Qwen3.5-9B | A | 19,9 Gio | taille intermédiaire, même famille |
| Gemma-4-E4B | B | 17,7 Gio | autre famille de tokenizer, pour tester si la famille compte |

Tous sont des modèles **généralistes** : aucun modèle médical ne figure dans la liste tant que Cyril n'a pas accepté les conditions de MedGemma (ADR-001, Q6). S'il l'accepte, MedGemma-4B s'ajoute comme quatrième candidat. Mistral Small 3.2 24B et les professeurs ne sont pas candidats élèves (coût hors de proportion). La distillation se faisant **au niveau des classes** (probabilités sur les 18 sorties : 17 chapitres plus `AUTRE`), une différence de vocabulaire entre professeur et élève ne gêne pas.

**Protocole du criblage (P1-11).** Un seul pli de développement (pli 0), même rang, même nombre d'époques, même longueur maximale, même graine pour les trois candidats ; **deux taux d'apprentissage par candidat**, les deux bornes de la grille de P1-13 (1e-5 et 1e-4), le meilleur des deux est retenu pour chacun. Les valeurs exactes et le nombre d'époques sont fixés dans la fiche préenregistrée de P1-11, avant le premier run.

**Règle de choix (P1-12).** L'élève est le candidat de plus haute macro-F1 (17 classes, `AUTRE` exclue) sur le pli 0, **sous contrainte** que son pic de mémoire réservé à 4 096 tokens reste sous 28 Gio (`vram_budget_gib` du profil `hardware/rtx5090.yaml`). **Règle d'égalité** : si l'intervalle apparié à 95 % de la différence entre les deux meilleurs contient 0, on retient le moins coûteux (le plus petit).

## Alternatives Considered
- **Un seul taux pour tous** : écarté, biais connu (page `reglage-taux-apprentissage-lora`).
- **Cribler quatre à six modèles** : réservé au chemin complet (R12) ; ici l'objectif est un premier résultat honnête.
- **Choisir le plus grand élève par défaut** : écarté, un gain de taille doit être mesuré, pas présumé.
- **Intégrer un modèle médical** : bloqué par une décision de Cyril.

## Consequences
- Coût estimé du criblage, hypothèse non annoncée comme durée : environ 5,8 heures de GPU (3 candidats × 2 taux × 2 époques d'un pli ; voir PROTOCOLE.md section 5), à recaler par RM-16 ; la section 5 du protocole l'a repris à 5,8 h le 03/10/2026.
- **Limites dites** : un pli, une graine : le criblage choisit un point de départ, il ne démontre aucune supériorité ; le choix de l'élève reste ouvert si le balayage de P1-13 le contredit nettement, par une nouvelle ADR et non en silence.
- Le résultat remplace la ligne « ADR-élève » de l'index.
