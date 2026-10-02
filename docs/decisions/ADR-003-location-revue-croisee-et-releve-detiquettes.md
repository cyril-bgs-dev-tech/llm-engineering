# ADR-003 : location de GPU, revue croisée externe, relecture d'étiquettes (micro-tâche P0-03)

## Status
**Non décidé** par Cyril à la date du 02/10/2026 ; la feuille de route accepte « non décidé » s'il est daté. Les défauts ci-dessous sont les plus prudents et ne dépensent ni n'envoient rien.

## Date
2026-10-02

## Context
Trois décisions du plan (7 à 9) engagent de l'argent, des données ou l'intégrité des étiquettes. Aucune n'est nécessaire avant R9 pour la première, ni avant le jalon A pour les deux autres.

## Decision

| Décision | Valeur au 02/10/2026 | Ce qui la déclencherait |
|---|---|---|
| Fournisseur et plafond de location de GPU | **Aucune location.** Pas de fournisseur choisi, plafond non fixé | Un déclencheur de la section 5.2 du plan, une fiche préenregistrée et un plafond validé par Cyril avant toute dépense ; idem pour une API payante |
| Revue croisée externe (Codex, Gemini) | **Demander à Cyril à chaque fois** (règle de `CLAUDE.md`) ; rien n'est envoyé | Une demande explicite de Cyril pour un contenu précis |
| Relecture des étiquettes | **Aucune correction automatique.** `cleanlab` signale, une liste de cas est présentée à Cyril, aucune étiquette n'est modifiée ; l'étiquette du scénario fait foi | Une limite de relecture fixée par Cyril (nombre de cas, qui tranche) |

## Alternatives Considered
- **Fixer un plafond de location par défaut** : écarté, une valeur inventée serait traitée comme un accord.
- **Utiliser une revue croisée externe par défaut** : écarté, le contenu quitterait la machine.

## Consequences
- Le calcul reste sur la RTX 5090 ; les travaux au-delà de sa capacité (professeurs de plus de 31 milliards) sont différés, pas rendus possibles par une dépense.
- Les corrections d'étiquettes ne faussent pas la mesure : tout écart entre texte et scénario se lit, ne se corrige pas.
