---
title: TRIPOD-LLM, guide de rapport des études utilisant des grands modèles de langage (Gallifant et al., Nature Medicine 2025)
category: Sources
summary: Liste de 19 items principaux et 50 sous-items, modulaire selon le type d'étude et la tâche, qui servira de squelette au rapport et à la carte de modèle du projet ; cette page dit quels items touchent une étude de fine-tuning pour la classification
tags: [tripod-llm, rapport, transparence, carte-de-modele, source-article]
sources: [tripod-llm-reporting-guideline]
created: 2026-10-02
updated: 2026-10-02
---

# TRIPOD-LLM, guide de rapport des études utilisant des grands modèles de langage

**Source:** raw/pmc-12104976-tripod-llm.txt (texte extrait de la page HTML du manuscrit d'auteur sur PubMed Central, https://pmc.ncbi.nlm.nih.gov/articles/PMC12104976/, téléchargée le 02/10/2026 ; publié dans Nat Med 2025 ; doi 10.1038/s41591-024-03425-5)[^1]
**Date ingested:** 2026-10-02
**Type:** paper (guide de rapport)

Les numéros `L…` renvoient aux lignes de `raw/pmc-12104976-tripod-llm.txt` (texte nettoyé de ses balises ; une cellule de tableau par ligne). La licence de réutilisation n'est pas dans le texte extrait et n'a pas été vérifiée : la liste des items n'est pas recopiée ici, seulement résumée et citée. Ce guide est une liste de **ce qu'il faut rapporter**, pas une preuve de qualité : cocher un item ne dit rien de la valeur des résultats.

## Résumé

TRIPOD-LLM étend TRIPOD+AI aux grands modèles de langage ; c'est un « document vivant », prévu pour évoluer avec le domaine.[^2] La liste compte 19 items principaux (titre 1, résumé 1, introduction 2, méthodes 8, science ouverte 1, implication des patients 1, résultats 3, discussion 2) découpés en 50 sous-items ; 14 items principaux et 32 sous-items valent pour toute étude, les 5 et 18 restants dépendent du type d'étude ou de tâche.[^3][^4]

Le guide est **modulaire** : chaque item porte les types d'étude (développement de novo, méthodes, évaluation, évaluation en contexte de soin) et les tâches (traitement de texte, classification, questions longues, recherche d'information, agent conversationnel, génération de documents, résumé, traduction, prévision) auxquels il s'applique.[^5] Il a été établi par un processus de type Delphi : 26 réponses sur 56 personnes invitées au premier tour, puis une réunion de consensus.[^6]

## Items qui touchent ce projet

Ce projet est une étude de fine-tuning (type « développement de novo » du guide, qui inclut l'affinage d'un modèle existant) sur une tâche de **classification** (« assigner des étiquettes prédéfinies à des textes »).[^7][^8] Les items suivants sont ceux que `model-card-calibration` et le rapport final devront couvrir ; le mot « couvert » n'est écrit nulle part avant d'avoir une preuve.

| Item | Ce que le guide demande (résumé) | Où cela se prépare dans le projet |
|---|---|---|
| 5a à 5e | Sources et description des données, dates du texte le plus ancien et le plus récent, prétraitement, données manquantes ou déséquilibrées[^9] | `dataset-intake` ; PROTOCOLE.md §1 à §3 ; les dates de PARHAF sont fictives, à dire |
| 6a à 6e | Nom et version du modèle, procédure de fine-tuning, réglages d'inférence (graine, température), sorties initiales et post-traitées, seuils de classification[^10] | registre des runs ; PROTOCOLE.md §6.4 (graines) |
| 7a à 7e | Métriques définies d'avance, lien avec l'usage visé, comparaison à d'autres modèles ou repères[^11] | PROTOCOLE.md §6.1, §6.2, ADR-007 |
| 12 | Calcul requis : temps, machines, coût, temps d'inférence[^12] | PROTOCOLE.md §5 (budget), runs `p0-08-*` |
| 13 | Comité d'éthique ou renonciation[^13] | corpus fictif PARHAF : à formuler (non-applicabilité), pas à supposer |
| 14c à 14f | Accès au protocole, enregistrement, disponibilité des données et du code[^14] | `experiments/INDEX.md` (empreintes), ADR-008 (dépôt privé), restrictions PARHAF |
| 16a à 16d | Flux des données, effectifs par partition et par analyse[^15] | `results/measures/splits_summary.json` |
| 19b, 19d | Limites (biais, incertitude, généralisation) ; usage visé, niveau d'autonomie et de supervision humaine[^16] | `claim-gate`, rapport final |

## Limites de la source

- Les items 8 à 11 (annotation, invites, résumé, alignement) ne s'appliquent que si l'étude les utilise ; le premier cycle du projet n'annote pas et ne fait pas de résumé.[^17]
- Le guide demande de rapporter, pas de faire : il ne fixe aucune valeur de seuil ni de métrique pour une classification.

## Pages liées

- [[parhaf-corpus-paper](pages/parhaf-corpus-paper.md)] : le corpus sur lequel le rapport portera.
- [[compatibilite-modeles-p0-06](pages/compatibilite-modeles-p0-06.md)] : exemple de mesure de calcul à rapporter (item 12).

[^1]: [[tripod-llm-reporting-guideline](pages/tripod-llm-reporting-guideline.md)] L44-L46 [synthesis] L44-L46 — revue Nat Med, manuscrit d'auteur, doi, parution du 8 janvier 2025
[^2]: [[tripod-llm-reporting-guideline](pages/tripod-llm-reporting-guideline.md)] §Introduction L211 — "designed to be a living checklist"
[^3]: [[tripod-llm-reporting-guideline](pages/tripod-llm-reporting-guideline.md)] Abstract L208 — "a comprehensive checklist of 19 main items and 50 subitems"
[^4]: [[tripod-llm-reporting-guideline](pages/tripod-llm-reporting-guideline.md)] §The TRIPOD-LLM Statement L264 — "14 main items and 32 subitems are applicable to all research designs and LLM tasks"
[^5]: [[tripod-llm-reporting-guideline](pages/tripod-llm-reporting-guideline.md)] Table 1 L215-L260 [synthesis] L215-L260 — types d'étude et catégories de tâche du format modulaire
[^6]: [[tripod-llm-reporting-guideline](pages/tripod-llm-reporting-guideline.md)] §Methods L683-L685 [synthesis] L683-L685 — premier tour de Delphi du 1er mars au 23 avril 2024, 26 réponses sur 56 invitations, réunion de consensus
[^7]: [[tripod-llm-reporting-guideline](pages/tripod-llm-reporting-guideline.md)] Table 1 L221-L222 [synthesis] L221-L222 — « développement de novo » : construire un modèle ou affiner de façon significative un modèle de base
[^8]: [[tripod-llm-reporting-guideline](pages/tripod-llm-reporting-guideline.md)] Table 1 L237-L238 — "Assigning predefined labels to text data."
[^9]: [[tripod-llm-reporting-guideline](pages/tripod-llm-reporting-guideline.md)] Table 2 items 5a-5e L300-L319 [synthesis] L300-L319 — sources, distribution, dates, prétraitement, données manquantes
[^10]: [[tripod-llm-reporting-guideline](pages/tripod-llm-reporting-guideline.md)] Table 2 items 6a-6e L321-L345 [synthesis] L321-L345 — modèle et version, développement, réglages d'inférence, sorties, seuils de classification
[^11]: [[tripod-llm-reporting-guideline](pages/tripod-llm-reporting-guideline.md)] Table 2 items 7a-7e L346-L372 [synthesis] L346-L372 — métriques, pertinence pour l'usage, définition du résultat, comparaison aux autres modèles
[^12]: [[tripod-llm-reporting-guideline](pages/tripod-llm-reporting-guideline.md)] Table 2 item 12 L406-L407 [synthesis] L406-L407 — calcul requis, temps, machines, coût, temps d'inférence
[^13]: [[tripod-llm-reporting-guideline](pages/tripod-llm-reporting-guideline.md)] Table 2 item 13 L413-L414 [synthesis] L413-L414 — comité d'éthique ou renonciation au consentement
[^14]: [[tripod-llm-reporting-guideline](pages/tripod-llm-reporting-guideline.md)] Table 2 items 14c-14f L426-L439 [synthesis] L426-L439 — protocole, enregistrement, disponibilité des données et du code
[^15]: [[tripod-llm-reporting-guideline](pages/tripod-llm-reporting-guideline.md)] Table 2 items 16a-16d L449-L465 [synthesis] L449-L465 — flux des données, caractéristiques et effectifs par partition
[^16]: [[tripod-llm-reporting-guideline](pages/tripod-llm-reporting-guideline.md)] Table 2 items 19b et 19d L487-L497 [synthesis] L487-L497 — limites et usage visé avec niveau de supervision humaine
[^17]: [[tripod-llm-reporting-guideline](pages/tripod-llm-reporting-guideline.md)] Table 2 items 8-11 L373-L405 [synthesis] L373-L405 — items conditionnels : annotation, invites, résumé, alignement
