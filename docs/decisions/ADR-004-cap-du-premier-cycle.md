# ADR-004 : cap du premier cycle (micro-tâche RM-02)

## Status
Proposée, **valeurs provisoires**. Les valeurs chiffrées (budget B, essais N, seuil utile) ne sont volontairement pas inventées : elles se fixent avec Cyril à partir des mesures de P0-08 et P0-45, avant le gel du protocole (P0-46).

## Date
2026-10-01

## Context
Les deux audits (GLM 5.3 et ChatGPT 5.6) relèvent que « le meilleur niveau mesurable » n'est pas testable et que le livrable présupposait un gagnant. La feuille de route (section 3) reformule le cap. Cette ADR en fixe les paramètres du premier cycle.

## Decision

| Paramètre | Valeur | Statut |
|---|---|---|
| Objectif | Neutre quant au vainqueur : le projet réussit s'il produit une conclusion fiable sous contraintes, même si TF-IDF ou un encodeur bat le LLM distillé. Distillation et tâche voisine restent des expériences **obligatoires** (demande de Cyril), pas des vainqueurs présumés | Adopté |
| Question principale | À budget de réglage égal, sur `parhaf_cim10_chapter`, la distillation au niveau des classes améliore-t-elle la LoRA de référence d'une ampleur pratiquement utile, au-delà de la variance entre graines ? | Adopté |
| Métrique primaire | **macro-F1 au niveau chapitre CIM-10** (robuste au déséquilibre) ; secondaires : log loss, ECE, exactitude, coût | Provisoire |
| Définition de « local » | **local-données** (aucun texte ni artefact dérivé ne quitte la machine ; téléchargements de poids et de documentation autorisés) et **local-calcul** (RTX 5090 seule) pendant le premier cycle ; **local-démonstration** | Provisoire ; la location de GPU reste fermée sans déclencheur accepté |
| Budget de calcul B (heures GPU du premier cycle) | **Non fixé** | À proposer à Cyril à partir de P0-45 (mesure du pas de calcul du plus gros professeur), obligatoire avant P0-46 |
| Essais de réglage N par famille de méthodes | **Non fixé** | À proposer avec B ; la règle d'égalité de budget entre méthodes est, elle, adoptée |
| Seuil « pratiquement utile » | **Non fixé** | À fixer avec RM-11 (estimand) ; sa forme générale : un gain doit dépasser un minimum utile choisi par Cyril ET la variabilité entre graines mesurée en P1-19 |

## Alternatives Considered

### « Le meilleur niveau mesurable sur une RTX 5090 »
- Écarté : ni espace de recherche, ni budget, ni arrêt ; invite à optimiser sans fin.

### Fixer B et N maintenant par estimation
- Écarté : aucune mesure de débit n'existe ; une valeur inventée serait citée ensuite comme un fait.

### Métrique primaire : exactitude
- Écarté : trompeuse sur des classes déséquilibrées ; sur PARHAF la prévalence est celle de scénarios échantillonnés, pas du réel.

## Consequences
- Le gel de `PROTOCOLE.md` (P0-46) est bloqué tant que B, N et le seuil utile ne sont pas fixés par Cyril.
- Les estimations de durée restent absentes jusqu'à la mesure pilote RM-16.
- Un changement de métrique primaire après le premier run comparatif exige une nouvelle ADR qui remplace celle-ci, motivée.
