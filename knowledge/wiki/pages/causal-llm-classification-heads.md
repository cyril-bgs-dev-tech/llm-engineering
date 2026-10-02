---
title: Affiner des LLM causaux pour la classification, tête sur embedding contre invite (Yousefiramandi et Cooney, 2026)
category: Sources
summary: Comparaison, sur brevets et sous 24 Go, d'une tête de classification sur le dernier token d'un LLM causal contre l'affinage par invite et réponse ; la tête égale ou dépasse BERT, la différence avec l'invite n'est pas significative
tags: [classification, tete-de-classification, invite, verbaliseur, lora, distillation, source-arxiv]
sources: [causal-llm-classification-heads]
created: 2026-10-02
updated: 2026-10-02
---

# Affiner des LLM causaux pour la classification : tête sur embedding contre invite

**Source:** raw/arxiv-2512.12677.txt (texte extrait du PDF arXiv 2512.12677v3, 25 mai 2026 ; https://arxiv.org/abs/2512.12677)
**Date ingested:** 2026-10-02
**Type:** paper

Les numéros `L…` des notes renvoient aux lignes de `raw/arxiv-2512.12677.txt` (texte extrait du PDF par `pypdf`, retours à la ligne selon la mise en page). Les chiffres sont ceux des auteurs, pas des résultats de notre projet : aucun `run_id` ne les concerne. Les auteurs appellent « A1 » l'approche à tête et « A2 » l'approche par invite.

## Résumé

Les auteurs comparent deux façons d'adapter un LLM décodeur seul à la classification : poser une tête de classification sur l'embedding du dernier token, ou l'affiner à produire l'étiquette en réponse à une invite.[^1] Les deux utilisent une base quantifiée en 4 bits (NF4) et LoRA (une exception, un modèle de 270 millions de paramètres affiné en entier), sous une contrainte stricte d'un seul GPU de 24 Go.[^2][^3][^47] La tête (A1) prend l'état caché du dernier token, ajoute un jeton de fin de séquence si besoin, et applique une couche linéaire ou un petit réseau à deux couches ;[^4][^5] seuls la tête et les adaptateurs sont entraînés.[^6] L'approche par invite (A2) convertit chaque exemple en invite et l'étiquette en réponse cible, avec une perte appliquée aux seuls jetons de l'étiquette et un décodage contraint à l'inférence.[^7][^8]

Deux jeux de brevets servent de test : un corpus interne à 5 classes à étiquette unique (CLV) et le jeu public WIPO-Alpha à étiquettes multiples (14 catégories).[^9] Résultat : la tête égale ou dépasse les références BERT sur CLV avec des dizaines de millions de paramètres entraînables.[^10] Mais la différence A1 contre A2 n'est pas certifiée statistiquement : les tests de McNemar donnent p = 0,24 sur CLV et p = 0,51 sur WIPO, intervalles à 95 % contenant zéro.[^11]

Les auteurs ajoutent trois mesures utiles pour nous : la fragilité de l'invite face au choix du verbaliseur,[^12] l'échec de convergence de certaines graines,[^13] et une distillation du professeur à tête vers un élève ModernBERT.[^14]

## Méthode

- **Tête (A1).** Rang LoRA balayé dans {8, 16}, α = 16, dropout de 5 % ; adaptateurs sur les projections requête, clé, valeur, sortie et les couches de propagation avant.[^6][^15]
- **Invite (A2).** LoRA de rang 64 ; invites de type « Text … Question … Answer: » avec identifiants courts (A, B, C, …) pour les étiquettes uniques, et liste de type JSON pour les étiquettes multiples.[^16][^17]
- **Réglages.** Tableau d'hyperparamètres : un seul taux d'apprentissage de 2e-4 pour les deux approches ; 5 époques pour A2 contre 20 au maximum avec arrêt précoce pour A1 ; optimiseurs différents.[^18] Les auteurs reconnaissent l'asymétrie d'optimiseur comme un facteur de confusion mineur pour la comparaison directe.[^19]
- **Équité du réglage.** Seul le rang est balayé ; le papier ne rapporte pas de balayage du taux d'apprentissage dans le texte lu.[^20]

## Résultats chiffrés

- **Tête contre BERT (CLV, étiquette unique).** Meilleure tête : Llama-3.2-3B, r = 8, 0,86 contre 0,854 pour PatentBERT (346 millions de paramètres entraînables contre quelques dizaines de millions pour la tête).[^21]
- **Invite (WIPO, étiquettes multiples).** Mistral-7B-v0.3 avec 167,8 millions de paramètres entraînables atteint 0,819 : l'invite ne gagne qu'avec son plus gros budget entraînable.[^22]
- **Significativité.** Les auteurs disent que l'avantage de A1 sur A2 n'est pas statistiquement certifié.[^23]
- **Pooling.** Dernier token (0,853 sur CLV, 0,866 sur WIPO) et moyenne sont à 0,014 de F1 l'un de l'autre ; un jeton `[CLS]` appris s'effondre sur WIPO.[^24][^25]
- **Verbaliseur de A2 (Mistral-7B-v0.3, une graine).** Sur CLV : 0,753 avec identifiants d'une lettre, 0,785 avec noms complets, 0,850 en JSON ; sur WIPO : 0,262, 0,277 et 0,838.[^26] Les auteurs recommandent de traiter le verbaliseur comme un hyperparamètre de premier rang avec sa propre ablation.[^27]
- **Calibration.** Pour la tête (Llama-3.2-3B, r = 8, graine 1), sur CLV : ECE de 0,094 et Brier de 0,232.[^28]
- **Invite sans affinage.** Llama-3.2-3B-Instruct en zéro coup : 0,21 sur CLV et 0,17 sur WIPO.[^29] Le meilleur modèle fermé testé en invite (Claude Opus 4.6, cinq exemples) atteint 0,823 sur CLV et 0,752 sur WIPO, derrière la tête LoRA de 3,7 et 3,3 points.[^30]
- **Distillation.** Professeur A1 Llama-3.2-3B (gelé) vers élève ModernBERT-base, avec cibles douces à température T = 4 et α = 0,7 ;[^31][^32] l'élève obtient 0,845 sur CLV et 0,851 sur WIPO contre 0,873 et 0,858 pour le professeur (graine 1).[^33]
- **Débit.** Les auteurs annoncent un écart de débit d'environ 45 fois à l'inférence entre ModernBERT-base et le professeur,[^34] mais la section Limitations parle d'environ 20 fois.[^35]

## Limites déclarées par les auteurs

- La moitié des chiffres principaux repose sur un corpus interne non redistribuable.[^36]
- Domaine unique (brevets) ; AG News sert de validation externe.[^37]
- L'écart A1 contre A2 est de même sens mais non certifié.[^38]
- Instabilité entre graines : Llama-3.2-3B en A1 a échoué à converger sur 3 graines sur 4 pour WIPO et 1 sur 4 pour CLV ; les auteurs recommandent six graines ou plus et de ne rapporter que le sous-ensemble convergé.[^13][^39]

## Incohérences relevées dans le texte

- Le coût de F1 de la distillation est annoncé « au plus 1,5 point »,[^40] alors que le tableau donne −0,028 sur CLV, soit 2,8 points.[^33]
- L'élève « retient au moins 97 % » du F1 du professeur :[^41] sur CLV, 0,845 / 0,873 donne 0,968 (calcul du wiki), un peu moins.
- Sur CLV, l'élève (0,845) est sous ModernBERT-base entraîné seul (0,852 dans le tableau 1), alors que les auteurs écrivent « parité ou mieux ».[^42][^43] Les deux chiffres viennent de campagnes différentes (note du tableau 10) et aucun test n'est fourni.
- Le titre du tableau 1 parle de « 4 graines » mais cite des graines jusqu'à 5.[^44]

## Ce que cela change pour notre projet

*Cette section est notre lecture ; ce sont des propositions, pas des affirmations de l'article.*

1. **Tête ou verbaliseur.** Le chapitre CIM-10 est un problème à étiquette unique et à catégories fermées. Pour ce régime, le papier montre la tête au moins égale à l'invite sans écart certifié,[^10][^11] et une invite sensible au verbaliseur (0,753 contre 0,850 selon le format, sur une graine).[^26] Nous proposons de mener les deux sur PARHAF, de préenregistrer le verbaliseur parmi les facteurs, et de conclure par une comparaison appariée avec intervalle, comme le papier l'a fait pour A1 contre A2.[^23]
2. **Ne pas exclure les graines divergentes en silence.** Le papier propose de rapporter seulement les graines convergées ;[^39] dans notre protocole, nous proposons de rapporter aussi le nombre de graines divergentes, car les écarter améliore l'estimation sans le dire.
3. **Taux d'apprentissage.** Les deux approches partagent un taux fixé à 2e-4,[^18] sans balayage rapporté :[^20] c'est le cas dénoncé par [[learning-rate-matters](pages/learning-rate-matters.md)]. Détail dans [[reglage-taux-apprentissage-lora](pages/reglage-taux-apprentissage-lora.md)].
4. **Distillation.** La distillation du papier va d'un professeur LLM à tête vers un élève encodeur ModernBERT, sans changement de tâche et avec une seule graine.[^31][^33] Elle ne règle pas notre question (distillation contre LoRA de référence entre modèles décodeurs) ; elle suggère surtout d'inclure une référence « encodeur entraîné seul » et de mesurer les écarts avec un test apparié, car même l'écart A1 contre A2 du papier a un intervalle de confiance contenant zéro.[^11]
5. **Matériel.** Le papier tient sous 24 Go avec une base en 4 bits, 8 milliards de paramètres compris.[^2][^45] La RTX 5090 offre davantage de mémoire ; le choix de précision et de modèle passe par `vram-preflight` (voir [[env-blackwell](pages/env-blackwell.md)]), le papier ne dit rien de Blackwell.
6. **Transposabilité.** Le domaine du papier est celui des brevets :[^37] aucun résultat n'y est établi pour le français ni pour le texte médical.
7. **Calibration.** La tête sort un softmax directement exploitable pour un routage par seuil de confiance, alors que l'invite exigerait une passe de calibration selon les auteurs.[^46] Utile pour l'abstention prévue en fin de parcours.

## Entités et concepts

- [[reglage-taux-apprentissage-lora](pages/reglage-taux-apprentissage-lora.md)]
- Autres sources du lot : [[learning-rate-matters](pages/learning-rate-matters.md)] et [[parhaf-corpus-paper](pages/parhaf-corpus-paper.md)].

## Relation aux autres pages du wiki

Le jeu PARHAF et ses limites sont décrits dans [[parhaf-corpus-paper](pages/parhaf-corpus-paper.md)] ; les formulations permises dans [[regles-de-formulation](pages/regles-de-formulation.md)].

[^1]: [[causal-llm-classification-heads](pages/causal-llm-classification-heads.md)] §Abstract L16-17 — "attaching a classification head to a pre-trained causal LLM and fine-tuning on the task"
[^2]: [[causal-llm-classification-heads](pages/causal-llm-classification-heads.md)] §1 L59-60 — "under a strict 24 GB single-GPU constraint"
[^3]: [[causal-llm-classification-heads](pages/causal-llm-classification-heads.md)] §2 L90-91 — "We pair LoRA with 4-bit NF4 quantization for both approaches"
[^4]: [[causal-llm-classification-heads](pages/causal-llm-classification-heads.md)] §3.1 L108-109 — "we append the end-of-sequence token (if not already present) and obtain the hidden state of the final token"
[^5]: [[causal-llm-classification-heads](pages/causal-llm-classification-heads.md)] §3.1 L111-112 — "We attach a simple linear layer (or two-layer feed-forward network) on top of this embedding to predict the class label."
[^6]: [[causal-llm-classification-heads](pages/causal-llm-classification-heads.md)] §3.1 L117-118 — "only the classification head and LoRA adaptersψ injected into the query/key/value/output projections and feed-forward layers are updated"
[^7]: [[causal-llm-classification-heads](pages/causal-llm-classification-heads.md)] §3.2 L152-153 — "we convert each training example into a prompt for the LLM, and the label into a target response"
[^8]: [[causal-llm-classification-heads](pages/causal-llm-classification-heads.md)] §3.2 L196-198 — "we mask the prompt (answer-only loss) in all experiments" ; "requires constrained decoding"
[^9]: [[causal-llm-classification-heads](pages/causal-llm-classification-heads.md)] §Abstract L21-22 — "a 5-class single-label internal corpus and the public WIPO-Alpha multi-label dataset (14 categories)"
[^10]: [[causal-llm-classification-heads](pages/causal-llm-classification-heads.md)] §4.1 L252-253 — "matches or exceeds the BERT-class baselines on the single-label CLV dataset"
[^11]: [[causal-llm-classification-heads](pages/causal-llm-classification-heads.md)] §4.1 L259-260 — "The A1-vs-A2 headline advantage is not statistically certified" ; "yieldp=0.24 on CLV andp=0.51 on WIPO, with both CIs straddling zero"
[^12]: [[causal-llm-classification-heads](pages/causal-llm-classification-heads.md)] §4.10 L518-519 — "F1 ranges from 0.753 (single-letter IDs) through 0.785 (full names) to 0.850 (JSON)"
[^13]: [[causal-llm-classification-heads](pages/causal-llm-classification-heads.md)] §Limitations L651-653 — "failed to converge during fine-tuning despite identical"
[^14]: [[causal-llm-classification-heads](pages/causal-llm-classification-heads.md)] §4.9 L483-484 — "We distill the A1 Llama-3.2-3B teacher (frozen at inference) into a ModernBERT-base student"
[^15]: [[causal-llm-classification-heads](pages/causal-llm-classification-heads.md)] §3.1 L121 — "We sweep LoRA rankr∈{8,16} withα= 16 and 5% adapter dropout"
[^16]: [[causal-llm-classification-heads](pages/causal-llm-classification-heads.md)] §3.2 L159 — "we apply 4-bit quantization and LoRA adapters (r=64)"
[^17]: [[causal-llm-classification-heads](pages/causal-llm-classification-heads.md)] §3.2 [synthesis] L154-172 — identifiants d'une lettre pour les étiquettes uniques, réponse de type liste JSON sous la clé labels pour les étiquettes multiples
[^18]: [[causal-llm-classification-heads](pages/causal-llm-classification-heads.md)] App. 8 Table 14 [synthesis] L703-730 — taux d'apprentissage 2×10^-4 pour les deux approches, 5 époques pour A2 et 20 au plus avec patience de 2 pour A1, optimiseurs Paged AdamW 32 bits contre AdamW 8 bits
[^19]: [[causal-llm-classification-heads](pages/causal-llm-classification-heads.md)] App. 8 Table 14 L733-734 — "the asymmetry is acknowledged as a minor confounder for direct head-to-head comparison"
[^20]: [[causal-llm-classification-heads](pages/causal-llm-classification-heads.md)] §3.1 [synthesis] L121 — seul le rang LoRA est balayé ; aucun balayage du taux d'apprentissage n'apparaît dans le texte extrait (taux unique en Table 14, L717)
[^21]: [[causal-llm-classification-heads](pages/causal-llm-classification-heads.md)] §4.1 L253 — "best A1: Llama-3.2-3Br=8 at 0.86, vs. PatentBERT 0.854 at 346M trainable"
[^22]: [[causal-llm-classification-heads](pages/causal-llm-classification-heads.md)] §4.1 L254-255 — "Mistral-7B-v0.3 at 167.8M trainable reaches WIPO F1=0.819"
[^23]: [[causal-llm-classification-heads](pages/causal-llm-classification-heads.md)] §4.11 L535-537 — "Neither contrast reaches p<0.05 and both bootstrap CIs include zero"
[^24]: [[causal-llm-classification-heads](pages/causal-llm-classification-heads.md)] §4.7 L410-411 — "last-token (0.853 CLV / 0.866 WIPO) and mean-pool (0.864 / 0.851) are within≤0.014 F1 of each other on each dataset"
[^25]: [[causal-llm-classification-heads](pages/causal-llm-classification-heads.md)] §4.7 L413-414 — "collapses entirely on WIPO (F1=0.000)"
[^26]: [[causal-llm-classification-heads](pages/causal-llm-classification-heads.md)] §4.10 Table 11 [synthesis] L511-514 — identifiants d'une lettre 0,753 et 0,262, noms complets 0,785 et 0,277, liste JSON 0,850 et 0,838 (CLV puis WIPO)
[^27]: [[causal-llm-classification-heads](pages/causal-llm-classification-heads.md)] §4.10 L526-527 — "treat verbalizer choice as a first-class hyperparameter requiring its own ablation"
[^28]: [[causal-llm-classification-heads](pages/causal-llm-classification-heads.md)] §4.8 L470 — "the 5-way softmax achieves ECE=0.094 and Brier=0.232"
[^29]: [[causal-llm-classification-heads](pages/causal-llm-classification-heads.md)] §4.4 L353-354 — "Zero-shot F1 reaches only 0.21 on CLV and 0.17 on WIPO"
[^30]: [[causal-llm-classification-heads](pages/causal-llm-classification-heads.md)] §4.5 L366-367 — "reaches 0.823 micro-F1 on CLV and 0.752 on WIPO, trailing our Approach-1 LoRA Llama-3.2-3B by 3.7 and 3.3 points respectively"
[^31]: [[causal-llm-classification-heads](pages/causal-llm-classification-heads.md)] §4.9 L483-484 — "using temperature-scaled soft targets"
[^32]: [[causal-llm-classification-heads](pages/causal-llm-classification-heads.md)] §4.9 L490 — "withT =4 andα=0.7"
[^33]: [[causal-llm-classification-heads](pages/causal-llm-classification-heads.md)] §4.9 Table 10 [synthesis] L492-495 — professeur 0,873 et 0,858, élève 0,845 et 0,851, écart de −0,028 et −0,007 (CLV puis WIPO)
[^34]: [[causal-llm-classification-heads](pages/causal-llm-classification-heads.md)] §4.9 L481 — "a∼45× gap (Table 13)"
[^35]: [[causal-llm-classification-heads](pages/causal-llm-classification-heads.md)] §Limitations L642 — "Approach 1 is ∼20× slower at inference than ModernBERT-base at parity F1"
[^36]: [[causal-llm-classification-heads](pages/causal-llm-classification-heads.md)] §Limitations L584-585 — "Half of our headline numbers rest on an internal corpus (DatasetCLV) that cannot be redistributed"
[^37]: [[causal-llm-classification-heads](pages/causal-llm-classification-heads.md)] §Limitations L587 — "Headline numbers are on patent text"
[^38]: [[causal-llm-classification-heads](pages/causal-llm-classification-heads.md)] §Limitations L592-593 — "The numerical advantage of A1 is consistent in direction but not statistically certified."
[^39]: [[causal-llm-classification-heads](pages/causal-llm-classification-heads.md)] §Limitations L655-656 — "we recommend running each cell with 6+ seeds and reporting only the converged subset"
[^40]: [[causal-llm-classification-heads](pages/causal-llm-classification-heads.md)] §4.9 L503-504 — "at a≤1.5-point F1 cost relative to the LLM teacher"
[^41]: [[causal-llm-classification-heads](pages/causal-llm-classification-heads.md)] §4.9 L500 — "The student retains≥97% of teacher F1 on both datasets"
[^42]: [[causal-llm-classification-heads](pages/causal-llm-classification-heads.md)] Table 1 L239 — "MB-base 149M 149M 0.852 0.806"
[^43]: [[causal-llm-classification-heads](pages/causal-llm-classification-heads.md)] §4.9 L504-505 — "at parity or above relative to fine-tuned BERT baselines trained from scratch on the same data"
[^44]: [[causal-llm-classification-heads](pages/causal-llm-classification-heads.md)] Table 1 L243-244 — "(CLV seed 5; WIPO seeds 3, 4, 5) failed to converge"
[^45]: [[causal-llm-classification-heads](pages/causal-llm-classification-heads.md)] §3.1 L119-120 — "fitting 8B-parameter models on a 24 GB GPU"
[^46]: [[causal-llm-classification-heads](pages/causal-llm-classification-heads.md)] §4.8 L477-478 — "would require a calibration pass for A2 even when its accuracy is competitive"
[^47]: [[causal-llm-classification-heads](pages/causal-llm-classification-heads.md)] §3 L210-211 — "Single exception: Gemma-3-270m fits a 24 GB GPU under full fine-tuning at 270M parameters"
