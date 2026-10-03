---
title: Statistical Inference of the Matthews Correlation Coefficient for Multiclass Classification (Tamura et al., 2025)
category: Sources
summary: Définit un MCC macro et deux MCC micro pour plus de deux classes, avec intervalles asymptotiques (méthode delta, transformation de Fisher) y compris pour une différence en plan apparié ; reposent sur la théorie des grands échantillons
tags: [mcc, intervalle-de-confiance, plan-apparie, multiclasse, source-arxiv]
sources: [mcc-multiclass-statistical-inference]
created: 2026-10-03
updated: 2026-10-03
---

# Statistical Inference of the Matthews Correlation Coefficient for Multiclass Classification (Tamura et al., 2025)

**Source:** raw/arxiv-2503.06450.txt (texte extrait du PDF arXiv 2503.06450v1, 9 mars 2025, par `pypdf` ; https://arxiv.org/abs/2503.06450)
**Date ingested:** 2026-10-03
**Type:** paper

Les numéros `L…` renvoient aux lignes de `raw/arxiv-2503.06450.txt` (l'extraction coupe parfois les mots). Les affirmations sont celles des auteurs, aucune n'est un résultat de notre projet. Ingestion de nuit (contrat R-j), sans discussion préalable des points clés.

## Résumé

Les auteurs formalisent le coefficient de corrélation de Matthews (MCC) pour plus de deux classes. Le MCC macro est la moyenne des MCC de chaque classe, toutes classes comptant pareil ; le MCC micro existe en deux versions, l'une agrégeant les contributions de toutes les classes, l'autre reposant sur les variances et covariances de la corrélation de Pearson.[^1] Ils notent que la première version micro n'utilise que la diagonale et reste proportionnelle à l'exactitude, donc qu'elle perd l'avantage du MCC et peut être aussi optimiste que l'exactitude ou la F1 dans les situations où celles-ci le sont.[^2]

Pour chaque métrique, ils dérivent des intervalles de confiance asymptotiques par la méthode delta, avec une variante par transformation de Fisher, et étendent la construction aux **différences entre deux modèles en plan apparié**. Les simulations montrent une couverture qui s'approche du niveau nominal quand l'échantillon grandit, sans départager clairement les deux méthodes.[^3] **Limite déclarée : les procédures reposent sur la théorie des grands échantillons.**[^4]

## Relation à notre projet (mon analyse)

- **Même famille que notre besoin** : une moyenne par classe à poids égaux (comme notre macro-F1) et un intervalle de différence apparié. Cela renforce, sans le remplacer, notre choix d'un bootstrap stratifié apparié (`src/llmft/paired.py`) : notre jeu a des classes de 4 à 9 patients au test, loin du régime des grands échantillons que les formules supposent ; le papier ne dit rien de ces petits effectifs.
- **MCC comme métrique de repère** : déjà simulé comme point de comparaison dans `scripts/spikes/metric_widths.py` (run `20261003-113946-metric-widths-candidates`) ; le MCC micro (proportionnel à l'exactitude) n'est pas une alternative à la macro-F1 pour notre besoin de poids égaux par chapitre.
- **Piste non engagée** : comparer l'IC asymptotique du MCC macro au bootstrap sur les plis de développement, en contrôle de couverture ; rien n'est ajouté à la feuille de route.
- Voir la note de synthèse [[protocole-gele-2026-10-03](pages/protocole-gele-2026-10-03.md)] pour les règles de décision gelées.

[^1]: raw/arxiv-2503.06450.txt L585-L589 [synthesis] — définitions : MCC macro (moyenne des MCC de classe), deux MCC micro
[^2]: raw/arxiv-2503.06450.txt L589-L593 [synthesis] — le MCC micro diagonal est proportionnel à l'exactitude et peut la surestimer comme elle
[^3]: raw/arxiv-2503.06450.txt L594-L599 [synthesis] — variances asymptotiques par la méthode delta, transformation de Fisher, différences en plan apparié, couverture proche du nominal avec l'effectif
[^4]: raw/arxiv-2503.06450.txt L600-L601 [synthesis] — procédures fondées sur la théorie des grands échantillons
