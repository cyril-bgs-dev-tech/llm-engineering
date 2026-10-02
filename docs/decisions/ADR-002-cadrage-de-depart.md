# ADR-002 : cadrage de départ (micro-tâche P0-02)

## Status
Proposée. Défauts recommandés de `roadmap_unifié.md` appliqués le 01/10/2026 sur l'instruction de Cyril « avance de manière autonome et efficace ». **À confirmer ou corriger par Cyril** ; la question sur la date limite et le jalon est restée sans réponse à ce jour.

## Date
2026-10-01

## Context
La feuille de route autorise des réponses provisoires datées pour les décisions de cadrage, pour ne pas bloquer le travail sans risque (rien d'irréversible n'en dépend avant l'étape R6). Les cinq décisions de P0-02 sont : emplacement du dossier, dépôt Git, périmètre, date limite de candidature, démo.

## Decision

| # | Décision | Valeur provisoire | Statut |
|---|---|---|---|
| 1 | Emplacement du dossier | Reste `D:\Projet Assistante IA\LLM_finetuning` (chemin WSL `/mnt/d/Projet Assistante IA/LLM_finetuning`) | Déduit de la consigne de Cyril : « tu travailles dans le répertoire du projet LLM finetuning » |
| 2 | Dépôt Git | Dépôt **local** seulement ; aucun dépôt distant créé ; GitLab privé envisagé plus tard, création sur demande explicite | Défaut de la feuille de route |
| 3 | Périmètre | Viser le **jalon B** (MVP complet), en passant par le **jalon A** (premier résultat honnête) ; chemin complet seulement si le temps le permet | Défaut ; dépend de la date limite |
| 4 | Date limite de candidature | **Inconnue** : aucune date n'a été donnée ; l'annonce archivée n'en contient pas | **Non décidé** ; à fournir par Cyril |
| 5 | Démo | **Locale** (machine de Cyril), jamais publique par défaut | Défaut, prudent au regard des usages interdits de PARHAF |

## Alternatives Considered

### Déplacer le dossier sous `D:\Projets persos\`
- Avantage : regroupe les projets.
- Inconvénient : déplacement d'un dossier de travail en cours pour un gain d'organisation seul.
- Écarté pour l'instant : réversible plus tard, `git` suivra.

### Créer tout de suite le dépôt GitLab privé
- Avantage : sauvegarde distante, CI.
- Inconvénient : action externe qui ne se défait pas proprement ; l'offre cite GitLab sans que cela presse.
- Écarté : sur demande explicite de Cyril seulement (règle de `CLAUDE.md`).

### Viser directement le chemin complet
- Écarté : le chemin complet n'a de sens que si la date limite le permet, et le jalon A donne déjà un premier moment où l'on peut dire vrai.

## Consequences
- Rien ne se publie, ne se pousse ni ne se dépense sur la base de cette ADR.
- Si Cyril a une date limite proche, la décision 3 se resserre vers le jalon A et les étapes R8 à R11 deviennent optionnelles.
- L'ADR sera mise à jour (nouvelle ADR qui la remplace) quand Cyril répondra.
