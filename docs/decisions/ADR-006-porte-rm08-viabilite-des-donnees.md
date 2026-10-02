# ADR-006 : porte RM-08, viabilité des données

## Status
Acceptée **provisoirement** le 02/10/2026 (décision prise en autonomie sur l'instruction de Cyril « avance de manière autonome et efficace ») ; réversible : rien de coûteux n'a été lancé. Cyril peut la renverser.

## Date
2026-10-02

## Context
La porte RM-08 décide, avant tout téléchargement de gros modèle, si la tâche principale `parhaf_cim10_chapter` est exploitable. Conditions d'arrêt de la feuille de route : classes trop rares, groupes d'auteurs insolubles, étiquette inadéquate.

## Evidence (chiffres du 02/10/2026, tous au registre `results/runs/`)

| Critère | Mesure | Source |
|---|---|---|
| Présence de l'étiquette | 100 % des 4 254 patients, un diagnostic principal chacun ; 1 code invalide (N571) mis en quarantaine | `data/cards/parhaf.md`, P0-22 |
| Classes (chapitre) | 21 chapitres présents ; 4 sous le seuil de 20 patients (18 patients au total) fusionnés en `AUTRE` ; **17 classes évaluées, la plus petite a 31 patients** | P0-23, `results/measures/splits_summary.json` |
| Taille | jeu de travail 4 219 patients ; test scellé 633 ; 5 plis de 717 à 718 ; 9 paires de quasi-doublons (seuil 0,8), toutes du même auteur, gardées dans la même partition (PROTOCOLE.md section 4) | P0-28, P0-40 |
| Tolérance de stratification | respectée (aucun écart relevé) | `check_tolerance` |
| Groupes d'auteurs | 104 auteurs ; plis de contrôle de 704 à 759 patients, aucun auteur dans deux plis ; 26 auteurs (21 % des patients) n'écrivent que dans une classe | P0-29 |
| Raccourci d'auteur | macro-F1 « auteur seul » 0,377 contre « spécialité seule » 0,385 : différence -0,9 point, intervalle à 95 % [-2,2 ; +0,4] ; **seuil de +3 points non atteint, raccourci non signalé** (mesure refaite sur le découpage corrigé des quasi-doublons ; la première mesure donnait 0,370 contre 0,391, même conclusion) | P0-30, seuil figé dans `experiments/INDEX.md` avant la mesure |
| Référence sans texte | la spécialité seule donne macro-F1 0,385 et exactitude 61,9 % ; classe majoritaire 0,025 (27,9 % d'exactitude) | P0-30 |

## Decision
**GO** : on continue au niveau chapitre CIM-10 (17 classes plus `AUTRE`), plis stratifiés comme métrique principale, plis par auteur en contrôle. Aucun gros modèle n'est téléchargé avant P0-06 (R4).

## Alternatives Considered
- **Simplifier davantage** (regrouper en moins de classes) : écarté, aucune classe évaluée n'est trop rare.
- **Changer de tâche** : écarté ; les tâches de contrôle `parhaf_doctype` et `parhaf_specialty` restent prévues pour la transposabilité (P0-36, P0-37).

## Consequences
- **Barre à battre** : un modèle utile doit dépasser nettement macro-F1 0,385, la référence qui n'utilise que la spécialité. TF-IDF sur le texte (R6) est la référence suivante.
- L'étiquette reste le diagnostic du scénario suggéré, pas un codage médical (`regles-de-formulation`).
- Au niveau bloc et trois caractères, la majorité des classes a moins de 20 exemples : ces niveaux restent exploratoires.
- Si la mesure de TF-IDF (RM-14, RM-15) montre que le texte n'apporte presque rien au-delà de la spécialité, la porte RM-15 le dira.
