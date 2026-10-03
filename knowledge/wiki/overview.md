---
title: Overview
tags: [overview, synthesis]
sources: [spike-p0-04-torch-blackwell, rm06-machine-wsl, parhaf-readme-60426cc, spike-p0-06-gemma-4-31b, limited-impact-medical-adaptation, lmsys-first-place-distillation-readme, tripod-llm-reporting-guideline, protocole-gele-2026-10-03, sliding-window-beats-linear-attention]
updated: 2026-10-03
---

# Fine-tuning de LLM sur textes cliniques français : vue d'ensemble

> Synthèse évolutive de tout le wiki. Mise à jour par wiki-ingest quand une source change la compréhension.

## Current Understanding

**Mesuré sur ce projet (02/10/2026).** La pile PyTorch 2.11 (CUDA 12.8) exécute bf16, attention fusionnée et LoRA sur modèle 4 bits sur la RTX 5090 (sm_120), mais le disque `/mnt/d` lit environ 30 fois plus lentement qu'ext4 et la RAM visible dans WSL est de 68,7 Gio : voir [[env-blackwell](pages/env-blackwell.md)]. Les conditions d'usage de PARHAF interdisent toute allégation clinique ou de généralisation ; les formulations permises sont dans [[regles-de-formulation](pages/regles-de-formulation.md)].

**Modèles candidats mesurés (02/10/2026).** Les Qwen3.5 et Qwen3.8 ont une classe de classification utilisable ; Gemma 4 n'en a pas et passe par une tête maison ; le plus gros professeur candidat (Gemma-4-31B, QLoRA 4 bits) tient sous 30 Gio de VRAM au batch effectif 64. Le padding et la qualité de classification ne sont pas encore mesurés : voir [[compatibilite-modeles-p0-06](pages/compatibilite-modeles-p0-06.md)].

**Trois papiers ingérés (02/10/2026)** : le corpus [[parhaf-corpus-paper](pages/parhaf-corpus-paper.md)], le réglage du taux d'apprentissage [[learning-rate-matters](pages/learning-rate-matters.md)] (synthèse pratique : [[reglage-taux-apprentissage-lora](pages/reglage-taux-apprentissage-lora.md)]) et la tête de classification contre l'invite [[causal-llm-classification-heads](pages/causal-llm-classification-heads.md)]. **Sources encore à ingérer** : Sources prévues pour les premières ingestions : solution 1re LMSYS (distillation), solution 5e LMSYS Team Danube (pré-entraînement sur tâche voisine), solution 1re WSDM Cup 2025, DrBenchmark, « Learning Rate Matters » (2026). Elles sont listées dans `../PLAN_PROJET_V3.md`, section Sources.

**Deux sources de plus (02/10/2026, RM-18 en cours).** [[limited-impact-medical-adaptation](pages/limited-impact-medical-adaptation.md)] : des LLM médicaux adaptés gagnent peu, voire rien, sur leur modèle de base une fois les invites réglées par modèle et l'incertitude prise en compte (questions-réponses fermées, pas de classification) ; elle justifie de garder les généralistes au criblage et de comparer chaque modèle médical à sa base. [[lmsys-first-place-distillation-readme](pages/lmsys-first-place-distillation-readme.md)] : la recette de distillation du 1er LMSYS d'après le README de son dépôt (cinq pertes, cinq plis, fusion de LoRA, GPTQ 8 bits) ; le texte de la solution n'est pas ingéré. [[tripod-llm-reporting-guideline](pages/tripod-llm-reporting-guideline.md)] (A8, RM-23) : le guide de rapport TRIPOD-LLM, dont les items qui touchent une étude de fine-tuning pour la classification sont listés. Les papiers A2 et A3 restent à ingérer (leurs pages Kaggle ne sont pas lisibles hors navigateur). [[sliding-window-beats-linear-attention](pages/sliding-window-beats-linear-attention.md)] (03/10/2026) : la fenêtre glissante avec sinks, sans entraînement, égale ou dépasse les modèles linéarisés après coup ; pertinence faible pour nous (nos Qwen3.5 sont des hybrides natifs, que les auteurs excluent, et nos textes demandent l'attention complète).

**Protocole gelé (03/10/2026).** `PROTOCOLE.md` est gelé avec neuf instantanés hachés : voir [[protocole-gele-2026-10-03](pages/protocole-gele-2026-10-03.md)]. Aucune règle ne change en place ; le premier cycle risque de rendre « non résolu » (largeur d'intervalle attendue supérieure à 4 points sur 633 patients de test).

## Open Questions

- La distillation garde-t-elle son intérêt quand le professeur n'est que 3 fois plus gros que l'élève (24-27B vers 7-9B) ?
- Distillation (1re LMSYS) contre pré-entraînement sur tâche voisine (5e LMSYS) : laquelle tient sur des textes médicaux français, et se cumulent-elles ?
- Les LLM affinés battent-ils les encodeurs médicaux français (DrBERT, CamemBERT-bio) sur des jeux de quelques centaines à quelques milliers d'exemples ?
- Quelle quantification est la plus rapide pour une classification (un seul token produit) sur Blackwell : INT8 bitsandbytes, GPTQ, FP8, NVFP4 ?

## Key Entities / Concepts

*Rempli au fil des pages.*
