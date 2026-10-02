---
title: Régler le taux d'apprentissage de la LoRA de référence avant toute comparaison
category: Méthodes
summary: Règle de comparaison équitable tirée de deux sources : un gain annoncé sous un taux d'apprentissage fixe ne prouve rien, la référence LoRA doit avoir son propre balayage, préenregistré
tags: [lora, taux-apprentissage, comparaison-equitable, baseline]
sources: [learning-rate-matters, causal-llm-classification-heads]
created: 2026-10-02
updated: 2026-10-02
---

# Régler le taux d'apprentissage de la LoRA de référence avant toute comparaison

Cette page est une synthèse méthodologique ; ses affirmations factuelles renvoient aux deux pages sources.

## Ce que disent les sources

- Une fois les taux d'apprentissage bien réglés, neuf variantes de LoRA et LoRA standard atteignent des performances de pic similaires.[^1] Les variantes diffèrent par la plage de taux où elles opèrent.[^2]
- Le réglage du taux compte nettement plus que celui de la taille de lot, et les auteurs conseillent de le régler en premier avec un lot petit ou moyen.[^3][^4]
- Quand on change de rang, il faut ré-régler le taux.[^5]
- Dans la comparaison tête de classification contre invite, un taux unique de 2e-4 sert aux deux approches, et seul le rang LoRA est balayé.[^6][^7] Les auteurs reconnaissent par ailleurs l'asymétrie d'optimiseur comme un facteur de confusion mineur.[^8]

## Conséquence pour le protocole de ce projet

*Proposition, non issue des sources.* Toute comparaison où l'une des branches est une LoRA de référence (distillation contre référence, tête contre invite, pré-entraînement voisin contre référence) préenregistre la grille de taux d'apprentissage, le budget de balayage et le jeu de validation qui sert à choisir. La même grille s'applique aux deux branches, sinon on ne sait pas si l'écart vient de la méthode ou du réglage. Voir [[learning-rate-matters](pages/learning-rate-matters.md)] pour la grille et l'ordre des leviers, [[causal-llm-classification-heads](pages/causal-llm-classification-heads.md)] pour le cas d'un taux unique.

## Pages liées

- [[learning-rate-matters](pages/learning-rate-matters.md)]
- [[causal-llm-classification-heads](pages/causal-llm-classification-heads.md)]
- [[limited-impact-medical-adaptation](pages/limited-impact-medical-adaptation.md)]
- [[lmsys-first-place-distillation-readme](pages/lmsys-first-place-distillation-readme.md)] : la recette de distillation à laquelle cette référence LoRA sera comparée.
- [[protocole-gele-2026-10-03](pages/protocole-gele-2026-10-03.md)] : le protocole gelé applique cette règle (4 taux, une graine, même budget de réglage pour la référence et chaque variante).

[^1]: [[learning-rate-matters](pages/learning-rate-matters.md)] §Abstract L18-19 — "once learning rates are properly tuned, all methods achieve similar peak performance"
[^2]: [[learning-rate-matters](pages/learning-rate-matters.md)] §1 L156-157 — "different methods operate within disparate learning rate ranges"
[^3]: [[learning-rate-matters](pages/learning-rate-matters.md)] §3.3.1 L409-410 — "tuning the learning rate is significantly more critical than tuning the batch size"
[^4]: [[learning-rate-matters](pages/learning-rate-matters.md)] App. H L2671-2672 — "under limited computational resources, practitioners may prioritize learning rate tuning while fixing the batch size"
[^5]: [[learning-rate-matters](pages/learning-rate-matters.md)] App. H L2694-2695 — "one should still perform learning rate tuning to elicit the best achievable performance at that rank"
[^6]: [[causal-llm-classification-heads](pages/causal-llm-classification-heads.md)] App. 8 Table 14 [synthesis] L703-730 — taux d'apprentissage de 2×10^-4 pour les deux approches
[^7]: [[causal-llm-classification-heads](pages/causal-llm-classification-heads.md)] §3.1 L121 — "We sweep LoRA rankr∈{8,16} withα= 16 and 5% adapter dropout"
[^8]: [[causal-llm-classification-heads](pages/causal-llm-classification-heads.md)] App. 8 Table 14 L733-734 — "the asymmetry is acknowledged as a minor confounder for direct head-to-head comparison"
