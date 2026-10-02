---
name: distillation-pipeline
description: Construit et vérifie la chaîne de distillation professeur vers élève. À utiliser pour entraîner les professeurs en plis, produire et stocker leurs probabilités hors pli, écrire la perte de distillation, combiner plusieurs professeurs, ou distiller des justifications.
---

# Chaîne de distillation

Le cœur de la recette de la 1re place de LMSYS : les gros modèles enseignent, le petit modèle est déployé.

## Étapes

1. **Professeurs en K plis** (K=5) avec `lora-classifier-recipe` ; chaque professeur de pli `k` prédit **uniquement** les exemples du pli `k`.
2. **Stocker les logits** : `teachers/<teacher_id>/oof_logits.parquet`, colonnes `example_id`, `fold`, `logits[]`, plus un `manifest.json` (modèle, `run_id`, température brute, empreinte des données). Les logits sont stockés bruts, avant toute température.
3. **Vérifier** avec `leakage-guard` (contrôle 3, strictement hors pli) avant tout entraînement de l'élève.
4. **Perte de l'élève** : `alpha · CE(étiquette) + (1 - alpha) · T² · KL(professeur_T ‖ élève_T)`. La direction de la KL (directe, inverse, asymétrique), `alpha` et la température `T` sont des réglages consignés, balayés dans la vague V3.
5. **Plusieurs professeurs** : moyenne des probabilités (pas des logits) par défaut ; pondération par score hors pli en variante.
6. **Justifications** (« Distilling step-by-step ») : le professeur produit étiquette et explication courte ; l'élève apprend les deux avec une tête de classification et une perte de génération pondérée. L'explication n'est jamais utilisée comme preuve de la qualité du classement : seul le score compte.
7. **Professeurs relus** (recette WSDM 2025) : les exemples où les professeurs contredisent fortement l'étiquette humaine vont dans une liste `relabel_queue.csv` pour relecture humaine. Rien n'est réétiqueté automatiquement.

**Terminé quand** chaque exemple d'entraînement a ses probabilités hors pli de chaque professeur, le contrôle hors pli est vert, et l'élève distillé est enregistré dans le registre avec la référence non distillée comparée par `paired-comparison`.
