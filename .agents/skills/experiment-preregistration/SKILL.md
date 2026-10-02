---
name: experiment-preregistration
description: Préenregistre une expérience avant tout lancement. À utiliser avant d'entraîner, d'évaluer ou de comparer un modèle, avant d'ajouter un levier (L1 à L12) au programme, ou quand une vague V0 à V5 démarre.
---

# Préenregistrement d'expérience

Une expérience **préenregistrée** fixe sa question, sa mesure et son critère de décision avant de voir un seul résultat. C'est ce qui sépare une mesure d'une recherche de résultat flatteur, et c'est le livrable que le CHU demande (« protocoles d'évaluation de la performance »).

## Étapes

1. **Relire `PROTOCOLE.md`** (règles communes figées en P0) et la vague concernée dans `PLAN_PROJET_V3.md`.
2. **Écrire la fiche** `experiments/<AAAA-MM-JJ>-<slug>.md` avec ces champs, tous remplis :
   - `question` : une phrase fermée (« DoRA bat-il la LoRA réglée sur MorFITT ? »).
   - `référence` : l'identifiant de run de la meilleure configuration actuelle (voir `run-registry`).
   - `variante` : le seul changement par rapport à la référence.
   - `jeux et découpage` : jeu, plis, graines, empreinte SHA-256 du test scellé.
   - `métrique principale` et `métriques secondaires` (macro-F1, log loss, ECE, Spearman, latence, VRAM).
   - `critère de décision` : seuil de gain et test statistique (voir `paired-comparison`), écrit en chiffres.
   - `budget` : heures GPU maximum, nombre de runs, arrêt anticipé éventuel.
   - `prédiction` : ce que tu attends, avec une probabilité.
3. **Figer** : calculer l'empreinte SHA-256 de la fiche et l'inscrire dans son pied, puis la commiter (ou la consigner dans `experiments/INDEX.md` si le dépôt n'existe pas encore).
4. **Lancer** seulement ensuite.

**Terminé quand** la fiche existe, chaque champ porte une valeur chiffrée ou un identifiant, et son empreinte est consignée avant la première ligne de log du run.

## Après coup

Une fiche figée ne se modifie plus. Un changement de plan devient une nouvelle fiche qui cite l'ancienne et dit pourquoi. Un résultat contraire à la prédiction est un résultat : il va dans `RESULTATS.md` comme les autres.
