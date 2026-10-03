---
title: Hierarchical Scoring for Machine Learning Classifier Error Impact Evaluation (Lanus et al., 2025)
category: Sources
summary: Métriques à crédit partiel fondées sur un arbre de notation qui pondère les confusions selon leur distance dans une taxonomie ; démontrées sur des modèles abstraits seulement, hors texte clinique
tags: [classification-hierarchique, metrique, taxonomie, source-arxiv]
sources: [hierarchical-scoring-classifier-error-impact]
created: 2026-10-03
updated: 2026-10-03
---

# Hierarchical Scoring for Machine Learning Classifier Error Impact Evaluation (Lanus et al., 2025)

**Source:** raw/arxiv-2508.04489.txt (texte extrait du PDF arXiv 2508.04489, 8 pages, par `pypdf` ; https://arxiv.org/abs/2508.04489)
**Date ingested:** 2026-10-03
**Type:** paper

Les numéros `L…` renvoient aux lignes de `raw/arxiv-2508.04489.txt`. Les affirmations sont celles des auteurs, aucune n'est un résultat de notre projet. Ingestion de nuit (contrat R-j), sans discussion préalable des points clés.

## Résumé

Le papier part du constat que l'évaluation de classification compte toute erreur pareil, alors que les classes forment souvent une taxonomie dont les distances reflètent l'importance des confusions. Les auteurs construisent des métriques hiérarchiques qui donnent un crédit partiel selon la distance entre prédiction et vérité dans un « arbre de notation » dont les poids d'arête sont réglables.[^1] Trois stratégies de poids sont comparées sur un cas d'usage abstrait ; changer la stratégie fait préférer des prédictions prudentes ou audacieuses.[^2]

Limites déclarées : l'expérimentation porte sur des **modèles abstraits**, sans données réelles ; la macro-moyenne des précisions et rappels hiérarchiques reste à explorer ; la méthode ne vaut que pour des hiérarchies en arbre.[^3]

## Relation à notre projet (mon analyse)

- **Lien thématique, pas d'usage immédiat.** Nos 17 chapitres CIM-10 sont le niveau supérieur d'une hiérarchie (chapitre, bloc, catégorie) ; une métrique à crédit partiel pourrait distinguer une confusion entre chapitres voisins d'une confusion lointaine. Le papier n'apporte ni validation sur du texte clinique ni gestion de la macro-moyenne, qu'il laisse en travail futur.
- **Ne remplace aucune règle gelée** : la macro-F1 plate à 17 chapitres reste le critère confirmatoire (PROTOCOLE 6.1). Une version hiérarchique relèverait d'un diagnostic exploratoire à préenregistrer à part ; rien n'est ajouté à la feuille de route.
- Voir [[protocole-gele-2026-10-03](pages/protocole-gele-2026-10-03.md)] pour les règles gelées.

[^1]: raw/arxiv-2508.04489.txt L1-L33 [synthesis] — résumé : pass/fail traite toutes les erreurs pareil ; métriques hiérarchiques à crédit partiel via arbres de notation
[^2]: raw/arxiv-2508.04489.txt L678-L684 [synthesis] — la stratégie de poids fait préférer des prédictions agressives ou prudentes
[^3]: raw/arxiv-2508.04489.txt L693-L703 [synthesis] — macro-moyenne laissée au travail futur, expériences sur modèles abstraits seulement, méthode conçue pour des arbres
