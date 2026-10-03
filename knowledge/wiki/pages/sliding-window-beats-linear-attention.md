---
title: Sliding-window beats linear attention (Jolicoeur-Martineau et al., 2026)
category: Sources
summary: La fenêtre glissante avec « sinks », sans post-entraînement, égale ou dépasse les modèles linéarisés après coup, surtout en contexte long ; pertinence faible pour notre classification de comptes rendus (modèles hybrides natifs, texte entier nécessaire)
tags: [attention, fenetre-glissante, attention-lineaire, qwen3-5, source-arxiv]
sources: [sliding-window-beats-linear-attention]
created: 2026-10-03
updated: 2026-10-03
---

# Sliding-window beats linear attention (Jolicoeur-Martineau et al., 2026)

**Source:** raw/arxiv-2608.28444.txt (texte extrait du PDF arXiv 2608.28444, 14 pages, par `pypdf` ; https://arxiv.org/abs/2608.28444)
**Date ingested:** 2026-10-03
**Type:** paper

Les numéros `L…` renvoient aux lignes de `raw/arxiv-2608.28444.txt`. Les chiffres sont ceux des auteurs ; aucun n'est un résultat de notre projet. Ingestion faite pendant la nuit du 03/10 (contrat de nuit R-k) sur demande de Cyril, sans la discussion préalable des points clés que prévoit `wiki-ingest` : la note de pertinence ci-dessous est ma lecture, à confirmer.

## Résumé

Les auteurs comparent, sur onze modèles de 1,3 à 70 milliards de paramètres, des méthodes qui « linéarisent » un modèle déjà entraîné (post-entraînement vers une attention linéaire) à une référence très simple : la fenêtre glissante (SWA) où chaque token ne regarde que les w derniers tokens plus quatre tokens d'ancrage (« sinks »), **sans aucun post-entraînement**.[^1] Ils trouvent que cette référence égale ou dépasse les méthodes linéarisées sur des tâches de court contexte et fait 2 à 10 fois mieux sur deux tests de contexte long.[^1]

Sur le court contexte, la SWA récupère 99 % de la performance moyenne du modèle complet, autant que les méthodes de post-entraînement les plus chères.[^2] Sur le contexte long, à 256 tokens, elle récupère 20 % et 25 % de la référence sur S-NIAH-3 et BABILong, contre 2,2 % et 5 % pour LoLCATs.[^2] Le coût est nul en entraînement et borné en mémoire (cache clés-valeurs fixe), d'où la recommandation d'adopter la SWA plutôt que de linéariser.[^3]

## Limites déclarées par les auteurs

Le travail porte sur la SWA sans entraînement ; l'effet d'un post-entraînement avec SWA reste à étudier. **Les modèles hybrides, dont certaines couches utilisent l'attention complète, ne sont pas considérés.**[^4] Les évaluations sont des tests de raisonnement et de récupération, pas de la classification de textes.

## Relation à notre projet (note de pertinence, mon analyse)

- **Pas la même situation.** Nos modèles Qwen3.5 sont des hybrides natifs à couches d'attention linéaire à porte (delta-net), préentraînés ainsi ; le papier traite des modèles à attention complète linéarisés après coup, et écarte explicitement les hybrides.[^4] Ses conclusions ne se transfèrent pas telles quelles à Qwen3.5.
- **Notre besoin est le contraire du gain visé.** Le papier gagne en mémoire d'inférence au prix d'une fenêtre courte (64 à 512 tokens) ; notre entrée est un compte rendu patient de jusqu'à 4 096 tokens, avec le diagnostic souvent en fin de texte (PROTOCOLE section 1), et une classification qui lit le texte entier en une passe. Le coût mémoire dominant chez nous est l'entraînement (activations), pas le cache d'une génération.
- **Les chiffres de contexte long sont pour la récupération d'un fait, pas pour la classification** ; l'effondrement de la SWA à 4 000 tokens (17 à 25 % de la référence) incite à ne pas la tester comme remplaçante d'une attention complète sur nos textes.
- **Utilité possible, non engagée** : repère méthodologique (comparer à une référence simple avant de payer une méthode coûteuse), cohérent avec la comparaison TF-IDF de P1-04 et P1-06. Aucune expérience n'est ajoutée à la feuille de route ; si Cyril veut une ablation « fenêtre glissante » sur un élève, elle serait une fiche préenregistrée à part. Mesures de vitesse et mémoire des Qwen3.5 : [[compatibilite-modeles-p0-06](pages/compatibilite-modeles-p0-06.md)].

[^1]: raw/arxiv-2608.28444.txt L20-L33 [synthesis] — résumé de l'article : référence SWA sans post-entraînement contre attention linéaire post-entraînée, 2 à 10 fois mieux sur NIAH et BABILong
[^2]: raw/arxiv-2608.28444.txt L383-L387 [synthesis] — 99 % de la moyenne de référence en court contexte ; à la longueur 256, 20 % et 25 % contre 2,2 % et 5 % pour LoLCATs
[^3]: raw/arxiv-2608.28444.txt L387-L389 — "we strongly recommend practitioners to use SWA with attention sinks in order"
[^4]: raw/arxiv-2608.28444.txt L366-L371 — "We did not consider hybrid models with some tokens or entire layers using full-attention (FA)."
