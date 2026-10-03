---
title: Automated Medical Coding on MIMIC-III and MIMIC-IV, étude de réplicabilité (Edin et al., 2023)
category: Sources
summary: Réévaluation de huit modèles de codage CIM sur MIMIC ; la macro-F1 des travaux antérieurs était faussée par les codes absents du test (maximum possible 46 %), d'où moyenne arithmétique des F1 par classe, plis stratifiés et réglages identiques
tags: [macro-f1, evaluation, codage-cim, stratification, replicabilite, source-arxiv]
sources: [automated-medical-coding-mimic-replicability]
created: 2026-10-03
updated: 2026-10-03
---

# Automated Medical Coding on MIMIC-III and MIMIC-IV, étude de réplicabilité (Edin et al., 2023)

**Source:** raw/arxiv-2304.10909.txt (texte extrait du PDF arXiv 2304.10909 par `pypdf` ; https://arxiv.org/abs/2304.10909, SIGIR 2023)
**Date ingested:** 2026-10-03
**Type:** paper

Les numéros `L…` renvoient aux lignes de `raw/arxiv-2304.10909.txt`. Les chiffres sont ceux des auteurs, sur des notes cliniques anglaises de MIMIC (étiquetage multi-étiquette de codes CIM-9/10), pas des résultats de notre projet. Ingestion de nuit (contrat R-j), sans discussion préalable des points clés.

## Résumé

Les auteurs reproduisent et comparent des modèles de codage médical automatique et montrent que plusieurs sous-performent à cause de configurations faibles, de découpages entraînement-test mal échantillonnés et d'une évaluation insuffisante.[^1] Leur correction principale touche la macro-F1 : les travaux précédents la calculaient comme moyenne harmonique de la macro-précision et du macro-rappel, ce qui récompense les classifieurs biaisés sur des données déséquilibrées ; ils recommandent la moyenne arithmétique des F1 de chaque classe.[^2]

Deuxième correction : 54 % des codes de MIMIC-III full sont absents du jeu de test, et les travaux antérieurs leur attribuaient une F1 de zéro, ce qui plafonne la macro-F1 à 46 %. Les auteurs ignorent ces codes dans la moyenne ; avec cette correction, PLM-ICD passe de 12,7 % à 22,8 % de macro-F1 sur le même découpage.[^3] Ils reprennent aussi la comparaison avec un échantillonnage stratifié et des réglages identiques entre modèles.[^1]

## Relation à notre projet (mon analyse)

- **Notre macro-F1 est déjà de la forme recommandée** : moyenne arithmétique des F1 par classe (`src/llmft/metrics.py`, PROTOCOLE 6.1). Vérifié à la lecture du code, non par ce papier.
- **Classes absentes** : notre test est stratifié et les 17 chapitres évalués y sont tous présents, donc le problème des codes absents ne se pose pas ; le risque voisin est l'effectif minuscule (4 patients pour le chapitre XXII), traité par le drapeau « effectif très faible » de `evaluation.py`.
- **Confirme trois choix du protocole** : plis stratifiés, réglage identique pour toutes les recettes, et exclusion explicite d'une classe de la moyenne (`AUTRE`) plutôt qu'un zéro silencieux. Le papier ne traite ni la classification multi-classe à étiquette unique ni le français.
- Complète [[tripod-llm-reporting-guideline](pages/tripod-llm-reporting-guideline.md)] côté rigueur d'évaluation et [[protocole-gele-2026-10-03](pages/protocole-gele-2026-10-03.md)] côté métriques.

[^1]: raw/arxiv-2304.10909.txt L32-L41 [synthesis] — résumé : modèles sous-performants (configurations, découpages, évaluation), comparaison refaite en échantillonnage stratifié et réglages identiques
[^2]: raw/arxiv-2304.10909.txt L272-L279 [synthesis] — macro-F1 historique par moyenne harmonique de macro-précision et macro-rappel ; moyenne arithmétique des F1 par classe recommandée
[^3]: raw/arxiv-2304.10909.txt L279-L286 [synthesis] — 54 % des codes absents du test, F1 mise à zéro, maximum possible 46 % ; codes absents ignorés ; PLM-ICD 12,7 % à 22,8 % (conclusion L640-L647)
