# ADR-005 : jeu de travail PARHAF, intersection des deux formats

## Status
Proposée, **valeur provisoire** appliquée le 01/10/2026 ; à confirmer par Cyril.

## Date
2026-10-01

## Context
La fiche de PARHAF dit que le JSON canonique et le parquet Hugging Face contiennent des informations identiques. La mesure (`data/cards/parhaf.md`) montre 4 220 patients identiques, 39 patients présents seulement dans le JSON (4 259 au total) et 34 seulement dans le parquet (4 254 au total), tous du pool CU 5a, avec des textes différents.

## Decision
Le jeu de travail est l'**intersection** : les 4 220 patients dont l'identifiant et le texte sont identiques dans les deux formats. Les 34 patients exclusifs du parquet sont mis en quarantaine. Le script de préparation des données (P0-35 et suivants) lit le parquet épinglé et filtre sur la liste d'identifiants communs, qui sera versionnée.

## Alternatives Considered

### Parquet entier (4 254)
- Avantage : c'est le format le plus simple à charger.
- Inconvénient : contient 34 patients absents de la version canonique, de provenance non expliquée.
- Écarté : la fiche déclare le JSON canonique.

### JSON canonique entier (4 259)
- Avantage : version officielle.
- Inconvénient : 39 patients absents de la version publiée sur Hugging Face, que les autres utilisateurs et l'évaluation CodaBench connaissent.
- Écarté pour l'instant : l'intersection est le plus petit ensemble que les deux versions confirment.

## Consequences
- Perte de 34 patients (0,8 % du parquet), tous hors de la tâche principale par construction (pool CU 5a).
- La fiche de données et le wiki citent l'écart ; l'écart n'est pas signalé aux auteurs tant que Cyril n'a pas donné son accord (action publique).
- Toute reprise de la décision passe par une nouvelle ADR qui remplace celle-ci.
