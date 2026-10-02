---
name: claim-gate
description: Contrôle qu'une affirmation sur le projet est prouvée avant qu'elle sorte du dépôt. À utiliser avant d'écrire un chiffre ou une capacité dans un README, le portfolio, le CV, LinkedIn, une lettre de motivation ou une réponse d'entretien, et avant de dire « j'ai fine-tuné », « bat », « état de l'art ».
---

# Porte des affirmations

Ce projet existe pour que Cyril puisse dire vrai en entretien. La porte garantit que tout ce qui sort du dépôt est **prouvé**, au mot près.

## Étapes

1. **Lister** chaque affirmation du texte à publier : chiffre, comparaison, capacité, nom de technique.
2. **Tracer** chacune vers sa preuve :
   - un chiffre → un `run_id` du registre (`run-registry`) dont la métrique, le jeu et le découpage correspondent exactement à la phrase ;
   - une comparaison (« bat », « meilleur », « gain ») → un verdict « gain confirmé » de `paired-comparison` ;
   - une capacité (« distillation », « QLoRA », « prédiction conforme ») → un run abouti qui l'emploie ;
   - une source externe (Kaggle, article) → l'URL et le passage.
3. **Réécrire** ce qui dépasse la preuve : préciser le jeu (« sur DiaMED, cas cliniques publiés », pas « sur des comptes rendus hospitaliers »), garder l'intervalle, dire « non résolu » quand c'est le verdict.
4. **Tableau de preuve** joint au texte : affirmation → preuve → statut (prouvé, reformulé, retiré).

**Terminé quand** chaque affirmation du texte a une ligne « prouvé » ou a été reformulée ou retirée, et que le tableau accompagne le texte.

## Style des textes destinés à Cyril

Prose sans tiret cadratin ; vérification par `grep -P "\x{2014}"` avant de rendre un texte de candidature.
