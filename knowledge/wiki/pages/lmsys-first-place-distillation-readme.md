---
title: Recette du 1er du concours LMSYS (sayoulala) : README du dépôt LMSYS_BlackPearl
category: Sources
summary: Pipeline de distillation de deux professeurs de 70 milliards vers un élève de 9 milliards avec cinq pertes, cinq plis, fusion des LoRA et quantification GPTQ 8 bits, tel que documenté dans le README du dépôt ; ne remplace pas le texte de la solution
tags: [distillation, lmsys, lora, fusion, gptq, source-code]
sources: [lmsys-first-place-distillation-readme]
created: 2026-10-02
updated: 2026-10-02
---

# Recette du 1er du concours LMSYS (sayoulala) : README du dépôt LMSYS_BlackPearl

**Source:** raw/lmsys-blackpearl-readme.md (README téléchargé le 02/10/2026 depuis https://github.com/shyoulala/LMSYS_BlackPearl ; licence non vérifiée)
**Date ingested:** 2026-10-02
**Type:** code (documentation d'un dépôt)

**Ce que cette page est, et n'est pas.** C'est le README du dépôt, pas le texte de la solution : l'auteur y renvoie lui-même à un document de synthèse soumis au concours (« Model SUMMARY proposal »).[^1] Ce document, publié sur Kaggle, n'a pas pu être récupéré (page rendue par JavaScript, aucun texte accessible hors navigateur). Tout ce qui suit se limite donc à ce que le README affirme ; les résultats de classement, les scores et les choix d'ablation de la solution **ne sont pas** ingérés. Les numéros `L…` renvoient aux lignes de `raw/lmsys-blackpearl-readme.md`.

## Résumé

La recette distille la sortie de deux gros modèles « professeurs » (Llama-3 70B et Qwen2 72B) vers un « élève » de la famille Gemma-2 9B, dans une configuration à cinq plis.[^2][^3] Chaque pli entraîne les deux professeurs, leur fait prédire la distribution de probabilité sur l'ensemble d'entraînement, puis affine l'élève avec ces distributions.[^4]

La perte de l'élève est la moyenne de cinq termes : l'entropie croisée contre l'étiquette, deux divergences de Kullback-Leibler (une par professeur) et deux pertes de similarité cosinus (une par professeur), toutes calculées sur des softmax à température T.[^5][^6] Les logits des professeurs sont découpés par colonnes (les trois premières pour Qwen2, le reste pour Llama-3), ce qui suppose un problème à trois classes.[^7]

Avant l'affinage, les trois modèles reçoivent un pré-entraînement supplémentaire (« post-pretrain ») sur des données dites UT, annoncé à 2,5 jours sur huit A100 80 Go.[^8] Après les cinq plis, les couches LoRA des cinq modèles élèves sont **fusionnées** puis quantifiées en 8 bits par GPTQ.[^9] Pour éviter d'entraîner un 70B, le dépôt fournit des échantillons dont les probabilités des professeurs sont déjà calculées, de sorte qu'on peut distiller l'élève seul.[^10]

## Ce qui sert à ce projet

- **Forme de la perte** : le spike de distillation miniature (RM-19) doit documenter l'écart avec cette recette exacte (CE, deux KL, deux cosinus) ;[^5] le projet ne retient que ce que le README montre, pas les gains annoncés ailleurs.
- **Distillation hors pli** : les probabilités des professeurs sont calculées pour l'ensemble d'entraînement de chaque pli ;[^4] pour nous, cela impose la règle « un professeur ne voit jamais les patients de validation de son pli » (leakage-guard).
- **Fusion et quantification** : pistes de la vague V4 (P4), à comparer à un ensemble ; rien n'est démontré ici sur ces points.[^9]

## Limites et incohérences relevées

- La température T n'est pas définie dans le README (aucune valeur dans le texte ni dans l'extrait de code).[^5]
- Le README nomme l'élève « Gemma2-9b » à plusieurs endroits mais « Gemma-2b » à un autre : incohérence interne, que nous ne tranchons pas.[^3][^4]
- Matériel : 8 A100 80 Go, 768 Go de RAM ;[^11] la recette n'est pas faite pour une carte unique de 32 Go, d'où l'usage de QLoRA et de professeurs plus petits dans ce projet (ADR-009).
- La tâche d'origine (prédire la préférence entre deux réponses, trois classes) n'est pas la nôtre (chapitre CIM-10, 17 classes plus `AUTRE`).

## Pages liées

- [[reglage-taux-apprentissage-lora](pages/reglage-taux-apprentissage-lora.md)] : la référence LoRA se règle avant toute comparaison à une distillation.
- [[compatibilite-modeles-p0-06](pages/compatibilite-modeles-p0-06.md)] : coûts mesurés des professeurs sur la RTX 5090.

[^1]: [[lmsys-first-place-distillation-readme](pages/lmsys-first-place-distillation-readme.md)] §Explanation L19 — "Model SUMMARY proposal I submitted"
[^2]: [[lmsys-first-place-distillation-readme](pages/lmsys-first-place-distillation-readme.md)] §Model Download L45-L47 [synthesis] L45-L47 — Llama3 70B, Qwen2 72B et Gemma2-9b à télécharger
[^3]: [[lmsys-first-place-distillation-readme](pages/lmsys-first-place-distillation-readme.md)] §Fine-Tune L64-L70 [synthesis] L64-L70 — affinage en cinq plis, un script par pli
[^4]: [[lmsys-first-place-distillation-readme](pages/lmsys-first-place-distillation-readme.md)] §Fine-Tune L101 — "predicting to obtain the probability distribution for the training set"
[^5]: [[lmsys-first-place-distillation-readme](pages/lmsys-first-place-distillation-readme.md)] §Fine-Tune L74-L98 [synthesis] L74-L98 — entropie croisée, KLDivLoss et CosineEmbeddingLoss sur des softmax divisés par T, moyenne de cinq termes ; T n'y est pas défini
[^6]: [[lmsys-first-place-distillation-readme](pages/lmsys-first-place-distillation-readme.md)] §Fine-Tune L98 — "loss = (loss_ce + loss_grad1 + cos_loss1 + loss_grad2 + cos_loss2) / 5."
[^7]: [[lmsys-first-place-distillation-readme](pages/lmsys-first-place-distillation-readme.md)] §Fine-Tune L79-L81 [synthesis] L79-L81 — découpage des logits des professeurs : trois premières colonnes pour Qwen2, le reste pour Llama-3
[^8]: [[lmsys-first-place-distillation-readme](pages/lmsys-first-place-distillation-readme.md)] §Post-Pretrain L59-L63 — "which takes 2.5 days"
[^9]: [[lmsys-first-place-distillation-readme](pages/lmsys-first-place-distillation-readme.md)] §Merge L102-L106 — "quantized to 8-bit using GPTQ"
[^10]: [[lmsys-first-place-distillation-readme](pages/lmsys-first-place-distillation-readme.md)] §fast train L122 [synthesis] L122 — échantillons à probabilités de professeurs déjà prédites, distillation de l'élève seul
[^11]: [[lmsys-first-place-distillation-readme](pages/lmsys-first-place-distillation-readme.md)] §Hardware L2-L6 [synthesis] L2-L6 — 128 cœurs, 768 Go de RAM, huit A100 80 Go
