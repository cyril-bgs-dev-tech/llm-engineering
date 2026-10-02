# ADR-004 : cap du premier cycle (micro-tâche RM-02)

## Status
**Valeurs chiffrées fixées** (B, N, seuil utile, 02 et 03/10/2026) ; la définition de « local » reste provisoire. Les valeurs chiffrées ont été fixées avec Cyril à partir des mesures de P0-08 et P0-45, avant le gel du protocole (P0-46).

## Date
2026-10-01

## Context
Les deux audits (GLM 5.3 et ChatGPT 5.6) relèvent que « le meilleur niveau mesurable » n'est pas testable et que le livrable présupposait un gagnant. La feuille de route (section 3) reformule le cap. Cette ADR en fixe les paramètres du premier cycle.

## Decision

| Paramètre | Valeur | Statut |
|---|---|---|
| Objectif | Neutre quant au vainqueur : le projet réussit s'il produit une conclusion fiable sous contraintes, même si TF-IDF ou un encodeur bat le LLM distillé. Distillation et tâche voisine restent des expériences **obligatoires** (demande de Cyril), pas des vainqueurs présumés | Adopté |
| Question principale | À budget de réglage égal, sur `parhaf_cim10_chapter`, la distillation au niveau des classes améliore-t-elle la LoRA de référence d'une ampleur pratiquement utile, au-delà de la variance entre graines ? | Adopté |
| Métrique primaire | **macro-F1 au niveau chapitre CIM-10** (robuste au déséquilibre) ; secondaires : log loss, ECE, exactitude, coût | Adoptée (ratifiée avec ADR-007 le 03/10/2026) |
| Définition de « local » | **local-données** (aucun texte ni artefact dérivé ne quitte la machine ; téléchargements de poids et de documentation autorisés) et **local-calcul** (RTX 5090 seule) pendant le premier cycle ; **local-démonstration** | Provisoire ; la location de GPU reste fermée sans déclencheur accepté |
| Budget de calcul B (heures GPU du premier cycle) | **90 h** | Fixé par Cyril le 02/10/2026, à partir des hypothèses de P0-45 (48 à 73 h, 85 h en pessimiste) ; un recalage après RM-16 est une nouvelle version de la section 5 du protocole (6.10, règle 4), décidée par lui |
| Essais de réglage N par famille de méthodes | **4** | Fixé par Cyril le 03/10/2026 : les quatre taux d'apprentissage de P1-13, même budget de réglage pour la référence et chaque variante (règle d'égalité adoptée) |
| Seuil « pratiquement utile » | **2,0 points de macro-F1** (fixé par Cyril le 02/10/2026, voir ADR-007) | Fixé avec RM-11 (ADR-007, acceptée le 03/10/2026) ; sa forme générale : un gain doit dépasser un minimum utile choisi par Cyril ET la variabilité entre graines mesurée en P1-19 |

## Alternatives Considered

### « Le meilleur niveau mesurable sur une RTX 5090 »
- Écarté : ni espace de recherche, ni budget, ni arrêt ; invite à optimiser sans fin.

### Fixer B et N maintenant par estimation
- Écarté : aucune mesure de débit n'existe ; une valeur inventée serait citée ensuite comme un fait.

### Métrique primaire : exactitude
- Écarté : trompeuse sur des classes déséquilibrées ; sur PARHAF la prévalence est celle de scénarios échantillonnés, pas du réel.

## Consequences
- B = 90 h, N = 4 et le seuil utile 2,0 sont fixés (02 et 03/10/2026) : la condition « B et N avant P0-46 » est remplie.
- Les estimations de durée restent absentes jusqu'à la mesure pilote RM-16.
- Un changement de métrique primaire après le premier run comparatif exige une nouvelle ADR qui remplace celle-ci, motivée.
