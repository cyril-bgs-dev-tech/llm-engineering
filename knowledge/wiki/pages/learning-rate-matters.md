---
title: Learning Rate Matters, Vanilla LoRA May Suffice for LLM Fine-tuning (Lee et al., 2026)
category: Sources
summary: Réévaluation de neuf variantes de LoRA contre LoRA standard avec balayage du taux d'apprentissage : les pics de performance se valent à 1 à 2 % près, d'où la règle de régler la référence d'abord
tags: [lora, taux-apprentissage, hyperparametres, baseline, source-arxiv]
sources: [learning-rate-matters]
created: 2026-10-02
updated: 2026-10-02
---

# Learning Rate Matters : Vanilla LoRA May Suffice for LLM Fine-tuning

**Source:** raw/arxiv-2602.04998.txt (texte extrait du PDF arXiv 2602.04998v2, 19 mai 2026 ; https://arxiv.org/abs/2602.04998)
**Date ingested:** 2026-10-02
**Type:** paper

Les numéros `L…` des notes renvoient aux lignes de `raw/arxiv-2602.04998.txt` (texte extrait du PDF par `pypdf`, retours à la ligne selon la mise en page). Les chiffres sont ceux des auteurs, pas des résultats de notre projet : aucun `run_id` ne les concerne. Les tâches du papier sont des tâches de raisonnement, de code et d'instruction ; aucune n'est une classification (voir « Portée »).

## Résumé

Les auteurs observent que de nombreuses variantes de LoRA annoncent des gains sur LoRA standard, mais sous des hyperparamètres fixes ou peu réglés.[^1] Leur audit de 64 publications compte un seul article qui règle à la fois taux d'apprentissage, taille de lot et rang, et 46 qui présentent leurs résultats avec un taux d'apprentissage fixe.[^2] Ils réévaluent donc neuf variantes face à LoRA standard, avec un balayage du taux d'apprentissage pour chaque méthode.[^3]

Le résultat central : une fois les taux réglés, toutes les méthodes atteignent des performances de pic similaires.[^4] Sur Qwen3-0.6B, la meilleure méthode (GraLoRA) ne devance la deuxième (LoRA-GA) que de 0,02 %, et la moins bonne (OLoRA) est à 0,84 %.[^5] Les méthodes diffèrent en revanche par la plage de taux d'apprentissage où elles opèrent,[^38] si bien que, selon les auteurs, le succès sous une seule configuration ne prouve pas une amélioration robuste.[^39] Les auteurs relient ces plages à la valeur propre maximale de la hessienne de la perte, plus élevée pour PiSSA, OLoRA et LoRA-GA, qui exigent donc un taux plus bas.[^6]

La conclusion des auteurs : des taux d'apprentissage inadaptés donnent un faux sentiment de progrès sur LoRA.[^7]

## Méthode

- **Modèles et tâches.** Quatre modèles décodeurs seuls (Qwen3-0.6B, Gemma-3-1B, Llama-2-7B, Llama-2-13B) ; quatre tâches : raisonnement de bon sens, raisonnement mathématique, génération de code, suivi d'instructions.[^8][^9]
- **Grille.** Taux d'apprentissage de 1e-6 à 1e-3 en échelle logarithmique avec quatre valeurs par ordre de grandeur ; tailles de lot de 16 à 512 et rangs de 4 à 256, réglés seulement sur certaines combinaisons modèle-tâche.[^10][^11]
- **Métrique.** Exactitude moyenne sur les jeux de test, moyenne de trois exécutions pour les figures principales.[^12][^13] Le texte lu ne décrit pas de jeu de validation distinct pour choisir le taux d'apprentissage ; à vérifier dans l'annexe D si nous reprenons la méthode.[^14]
- **Réglages fixes.** Une époque, AdamW, décroissance cosinus avec échauffement de 3 %, pas de dropout ni de décroissance des poids, adaptateurs sur toutes les couches linéaires hors tête de langage, longueur maximale de 512, avec α égal au rang (facteur d'échelle égal à 1).[^15][^16]
- **Matériel des auteurs.** Quatre GPU, des RTX 3090 ou des A6000.[^17]

## Résultats chiffrés

- Écarts de pic entre méthodes : 0,52 % (Gemma-3-1B, maths), 0,43 % et 1,75 % (Llama-2-7B, maths et code), 1,81 % (Llama-2-13B, maths).[^18]
- Sur Gemma-3-1B, la parité persiste à tous les rangs testés, avec des écarts maximaux de 1,67 % en maths et 2,15 % en code.[^19]
- Régler le taux d'apprentissage compte nettement plus que régler la taille de lot.[^20] Avec PiSSA, fixer le taux à 2e-5 et ne régler que le lot donne au mieux 16,1 %, contre environ 20,6 % en réglant le taux.[^21]
- Le taux optimal croît proportionnellement à la taille de lot.[^22] À partir d'un lot de 256, la meilleure performance atteignable de LoRA et PiSSA commence à décroître même avec le taux réglé.[^23]
- Le taux optimal décroît généralement quand le rang augmente.[^24] Entre 5 000 et 395 000 exemples, le taux optimal ne varie que d'un facteur 3,1.[^25]

## Les cinq heuristiques des auteurs (annexe H)

1. Avec peu de calcul, régler d'abord le taux d'apprentissage en fixant un lot petit ou moyen.[^26]
2. Si l'on change le lot, garder la relation de proportionnalité taux-lot comme point de départ.[^22]
3. La valeur propre maximale de la hessienne peut indiquer la plage de taux d'une variante par rapport à LoRA ; elle n'a pas d'objet pour notre référence, qui est LoRA standard.[^40]
4. Si les résultats restent insuffisants au rang courant, augmenter le rang peut aider, mais il faut ensuite régler le taux à ce rang.[^27]
5. En dernier lieu, prolonger l'entraînement.[^28]

## Limites déclarées par les auteurs

- Modèles décodeurs de 0,6 à 13 milliards de paramètres ; la portée vers de plus gros modèles reste à vérifier.[^29][^30]
- Des réglages secondaires (planificateur, échauffement, placement des adaptateurs) sont restés fixes.[^31]
- Les résultats peuvent ne pas s'étendre aux architectures non testées, par exemple les modèles à encodeur seul.[^32]
- Certaines méthodes (par exemple LoRA-One) avaient annoncé un pic supérieur à LoRA sous balayage complet.[^33]
- L'exactitude sur des benchmarks standard n'est pas le seul critère : certaines variantes peuvent avoir d'autres avantages, par exemple contre l'oubli.[^34]

## Portée pour nous

Le papier ne porte ni sur de la classification, ni sur du français ou du médical, ni sur une tête de classification. Ses tâches sont du raisonnement, du code et de l'instruction.[^9] Ses valeurs de taux (de l'ordre de 2e-5 à 3,6e-3 pour Llama-2-7B)[^35] ne se transposent donc pas telles quelles à notre cas : ce qui se transpose est la méthode.

## Ce que cela change pour notre projet

*Cette section est notre lecture ; ce sont des propositions, pas des affirmations de l'article.*

1. **Régler la référence avant de la comparer.** La comparaison « distillation contre LoRA de référence » ne vaut que si la LoRA de référence a eu son propre balayage du taux d'apprentissage, sinon un gain attribué à la distillation peut venir d'une référence mal réglée. Le préenregistrement doit fixer la grille et le budget avant le premier run.
2. **Grille de départ.** Quatre valeurs par ordre de grandeur sur au moins deux ordres autour de 2e-4 (valeur utilisée sans balayage par [[causal-llm-classification-heads](pages/causal-llm-classification-heads.md)]), puis resserrement ; le papier montre que la performance s'effondre vers zéro aux taux les plus élevés.[^36]
3. **Ordre des leviers.** Suivre l'ordre des heuristiques : taux, puis rang (en rebalayant le taux), puis durée.[^26][^27][^28] Le lot reste petit ou moyen.[^23]
4. **Coût sur une RTX 5090.** Le papier ne rapporte pas le nombre d'heures GPU de son balayage dans le texte lu ; le budget de notre grille se mesure par un run court, avec `vram-preflight` (voir [[env-blackwell](pages/env-blackwell.md)]).
5. **Sélection sur validation.** Les auteurs rapportent l'exactitude sur les jeux de test ;[^12] chez nous, le taux se choisit sur les plis de validation et jamais sur le test scellé.
6. **Plusieurs graines.** Les auteurs moyennent trois exécutions ;[^13] notre protocole préenregistre son propre nombre de graines, indépendamment de ce papier.

Le concept qui relie ce papier et la page voisine est détaillé dans [[reglage-taux-apprentissage-lora](pages/reglage-taux-apprentissage-lora.md)].

## Entités et concepts

- [[reglage-taux-apprentissage-lora](pages/reglage-taux-apprentissage-lora.md)]
- Autres sources du lot : [[causal-llm-classification-heads](pages/causal-llm-classification-heads.md)] et [[parhaf-corpus-paper](pages/parhaf-corpus-paper.md)].

## Relation aux autres pages du wiki

[[env-blackwell](pages/env-blackwell.md)] décrit la pile LoRA sur modèle 4 bits qui permettra de rejouer un balayage de ce type sur la RTX 5090.

[^1]: [[learning-rate-matters](pages/learning-rate-matters.md)] §Abstract L11 — "these gains are often demonstrated under fixed or narrowly tuned"
[^2]: [[learning-rate-matters](pages/learning-rate-matters.md)] §1 L185-186 — "only 1 out of 64 papers simultaneously considers three hyperparameters, while 46 present results under a fixed learning rate"
[^3]: [[learning-rate-matters](pages/learning-rate-matters.md)] §1 L147-148 — "we select nine representative advanced LoRA variants"
[^4]: [[learning-rate-matters](pages/learning-rate-matters.md)] §Abstract L18-19 — "once learning rates are properly tuned, all methods achieve similar peak performance"
[^5]: [[learning-rate-matters](pages/learning-rate-matters.md)] §1 L190-192 — "the top-performing method (GraLoRA) leads the runner-up (LoRA-GA) by only 0.02%, and the least effective method (OLoRA) by 0.84%"
[^6]: [[learning-rate-matters](pages/learning-rate-matters.md)] §4.2 [synthesis] L576-587 — OLoRA et LoRA-GA exhibent jusqu'à 100 fois plus de courbure et un taux optimal plus bas, PiSSA environ 10 fois, Init[AB] et MiLoRA environ 2 fois
[^7]: [[learning-rate-matters](pages/learning-rate-matters.md)] §5 L594 — "improper learning rates give a false sense of LoRA advancements"
[^8]: [[learning-rate-matters](pages/learning-rate-matters.md)] §3.2 L331-332 — "We consider four decoder-only models spanning diverse scales"
[^9]: [[learning-rate-matters](pages/learning-rate-matters.md)] §3.2 L336-337 — "We train models on four canonical tasks"
[^10]: [[learning-rate-matters](pages/learning-rate-matters.md)] §3.2 L346-347 — "with four values per order of magnitude"
[^11]: [[learning-rate-matters](pages/learning-rate-matters.md)] §3.2 [synthesis] L345-351 — lots {16, 32, 64, 128, 256, 512}, rangs {4, 8, 16, 32, 64, 128, 256}, lot et rang réglés pour certaines combinaisons modèle-tâche seulement, taux réglé pour toutes
[^12]: [[learning-rate-matters](pages/learning-rate-matters.md)] §3.2 L344 — "we report mean accuracy over the testing datasets"
[^13]: [[learning-rate-matters](pages/learning-rate-matters.md)] Fig. 1 L91 — "Each point is averaged over three training runs."
[^14]: [[learning-rate-matters](pages/learning-rate-matters.md)] §3.2 [synthesis] L328-356 — la description de la configuration expérimentale ne mentionne qu'une métrique sur les jeux de test et aucun jeu de validation distinct
[^15]: [[learning-rate-matters](pages/learning-rate-matters.md)] App. D.3 Table 5 [synthesis] L2041-2052 — époque 1, AdamW, cosinus avec échauffement 3 %, sans dropout ni décroissance des poids, adaptateurs sur toutes les couches linéaires sauf la tête de langage, base en BFloat16, adaptateurs en Float32, longueur maximale 512
[^16]: [[learning-rate-matters](pages/learning-rate-matters.md)] §3.2 [synthesis] L354-356 — α fixé égal au rang, donc un facteur d'échelle égal à 1 pour tout rang
[^17]: [[learning-rate-matters](pages/learning-rate-matters.md)] App. D.4 L2070-2071 — "All experiments are conducted on four GPUs (either 4× Nvidia RTX 3090 or 4× Nvidia A6000)."
[^18]: [[learning-rate-matters](pages/learning-rate-matters.md)] §3.3.1 L398-400 — "0.52% for Gemma-3-1B on math, 0.43% and 1.75% for Llama-2-7B on math and code, respectively, and 1.81% for Llama-2-13B on math"
[^19]: [[learning-rate-matters](pages/learning-rate-matters.md)] §3.3.2 [synthesis] L503-506 — parité à tous les rangs avec 1,67 % d'écart maximal en maths (r = 32) et 2,15 % en code (r = 4) sur Gemma-3-1B
[^20]: [[learning-rate-matters](pages/learning-rate-matters.md)] §3.3.1 L409-410 — "tuning the learning rate is significantly more critical than tuning the batch size"
[^21]: [[learning-rate-matters](pages/learning-rate-matters.md)] §3.3.1 L412-414 — "yields a suboptimal maximum accuracy of 16.1%" ; "the model achieves substantially higher performance around 20.6%"
[^22]: [[learning-rate-matters](pages/learning-rate-matters.md)] §3.3.1 L415 — "the optimal learning rate scales proportionally with batch size"
[^23]: [[learning-rate-matters](pages/learning-rate-matters.md)] App. A.4 L1375-1376 — "the best achievable performance of both LoRA and PiSSA begins to decay"
[^24]: [[learning-rate-matters](pages/learning-rate-matters.md)] App. H L2697 — "the optimal learning rate generally decreases as the rank increases"
[^25]: [[learning-rate-matters](pages/learning-rate-matters.md)] App. H L2713 — "the optimal learning rates forN= 5k andN= 395k differ by only 3.1×"
[^26]: [[learning-rate-matters](pages/learning-rate-matters.md)] App. H L2671-2672 — "under limited computational resources, practitioners may prioritize learning rate tuning while fixing the batch size"
[^27]: [[learning-rate-matters](pages/learning-rate-matters.md)] App. H L2693-2695 — "increasing the LoRA rank can be a reliable way to further improve performance" ; "one should still perform learning rate tuning to elicit the best achievable performance at that rank"
[^28]: [[learning-rate-matters](pages/learning-rate-matters.md)] App. H L2707-2708 — "we suggest prolonging the training duration as a final step"
[^29]: [[learning-rate-matters](pages/learning-rate-matters.md)] §Limitations L605 — "we focused our investigation on decoder-only LLMs from 0.6B to 13B parameter scale"
[^30]: [[learning-rate-matters](pages/learning-rate-matters.md)] §Limitations L606 — "the scalability of our findings to larger foundation models remains to be verified"
[^31]: [[learning-rate-matters](pages/learning-rate-matters.md)] §Limitations L610-611 — "other secondary training setups, such as learning rate schedulers, warmup steps, and LoRA adapter placements, remained fixed"
[^32]: [[learning-rate-matters](pages/learning-rate-matters.md)] §Limitations L613-614 — "our findings may not extend to untested model architectures"
[^33]: [[learning-rate-matters](pages/learning-rate-matters.md)] §Limitations L615 — "several methods have originally reported higher peak"
[^34]: [[learning-rate-matters](pages/learning-rate-matters.md)] §Limitations L618-619 — "fine-tuned accuracy on standard benchmarks is not the sole criterion for evaluating PEFT algorithms"
[^35]: [[learning-rate-matters](pages/learning-rate-matters.md)] App. D Table 4 L2020-2023 [synthesis] L2020-2023 — plage de taux de 2,0e-5 à 3,5566e-3 pour Llama-2-7B (maths et code) et 2,0e-5 à 2,0e-3 pour Llama-2-13B
[^36]: [[learning-rate-matters](pages/learning-rate-matters.md)] Table 1 [synthesis] L361-384 — pour Gemma-3-1B, chaque méthode ne reste proche de son pic que sur une plage de taux limitée, et la précision tombe vers zéro aux taux les plus élevés
[^38]: [[learning-rate-matters](pages/learning-rate-matters.md)] §1 L156-157 — "different methods operate within disparate learning rate ranges"
[^39]: [[learning-rate-matters](pages/learning-rate-matters.md)] §1 L158 — "success under a single training configuration cannot be taken as evidence of robust"
[^40]: [[learning-rate-matters](pages/learning-rate-matters.md)] App. H L2681 — "eigenvalue of the loss Hessian can serve as a useful indicator of a"
