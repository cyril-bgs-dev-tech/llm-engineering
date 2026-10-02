# ADR-010 : écarts du protocole au plan V6 et au backlog (issus de la relecture adversariale du 03/10/2026)

## Status
**Acceptée** le 03/10/2026 par Cyril (confirmations C1 à C8 de `PROTOCOLE.md` 6.10).

## Date
2026-10-03

## Context
`CLAUDE.md` désigne `PLAN_PROJET_V6.md` comme spécification. La relecture adversariale de `PROTOCOLE.md` a montré que le plan et `MICROTACHES.md` contiennent des règles que le protocole ne peut pas suivre sans se contredire. Le protocole prévaut sur ces points ; cette ADR les liste pour qu'un exécutant qui suit le plan ne soit pas pris en défaut.

## Decision
| Point du plan ou du backlog | Écart | Raison |
|---|---|---|
| Plan V6, E5 et P1-13 : « trois graines par point » du balayage de taux | **Une graine** par taux, pour toutes les familles, référence comprise | Budget : trois graines pour la référence et chacune des trois variantes donnent 76 à 122 h pour B = 90 h (C2) |
| P2-08 et P3-07 : « verdict en trois valeurs », « table de verdicts » | Ces tâches **entraînent sans évaluer** ; le verdict n'est rendu que par RM-20 | Le test scellé s'ouvre une seule fois ; aucun modèle entraîné sur le développement entier n'a de prédiction hors pli |
| RM-20 : « verdict confirmatoire en trois valeurs » | Verdict **seulement si la règle de puissance de 6.3 a réussi** ; sinon évaluation du candidat final sans verdict | Simulation : la règle échouera probablement avec δ = 2,0 sur 633 patients |
| RM-15 (puissance sur les références P1-04, P1-06, P1-07) | La règle de puissance du protocole est calculée à la porte **RM-17** | Elle exige les cinq graines de la référence (P1-19) et sa configuration gelée (P1-20) |
| Plan V6 : « candidat final choisi après comparaison préenregistrée » entre référence non neuronale, encodeur, LoRA, distillation | Seuls H1, H2, H3 contre la LoRA sont confirmatoires ; TF-IDF et encodeurs sont EXPLORE ; le candidat final est **désigné par Cyril** avant l'ouverture (C5) | Famille de trois comparaisons (Bonferroni, ADR-007) |

## Alternatives Considered
- **Modifier le plan V6** : écarté, V6 est la spécification de référence et son historique reste lisible ; l'écart se documente ici.
- **Garder trois graines de réglage** : écarté par Cyril (C2) pour tenir le budget.

## Consequences
- `MICROTACHES.md` a été mis en accord (cellules de P1-13, P2-08, P3-07, RM-17, RM-20) sans renumérotation ; `tasks/todo.md` est régénéré.
- Le plan n'est pas modifié : un lecteur du plan doit lire cette ADR.
