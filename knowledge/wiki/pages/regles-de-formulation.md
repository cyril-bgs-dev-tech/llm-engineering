---
title: Règles de formulation tirées des conditions d'usage de PARHAF
category: Décisions
summary: Ce que le CV, LinkedIn, la démo et toute publication peuvent affirmer ou doivent taire, déduit des usages exclus de PARHAF ; page consultée par claim-gate
tags: [claim-gate, parhaf, licence, formulation]
sources: [parhaf-readme-60426cc]
created: 2026-10-01
updated: 2026-10-02
---

# Règles de formulation tirées des conditions d'usage de PARHAF

Page consultée par `claim-gate` avant toute sortie du dépôt (CV, LinkedIn, lettre, démo, publication). Elle traduit les conditions du jeu en phrases permises et interdites. Elle ne remplace pas une relecture des conditions à la source si la fiche du jeu change (révision lue : `60426cc`, 01/10/2026).

## Ce que la fiche du jeu interdit

La fiche exclut : « Clinical decision-making or patient care (no diagnostic, prognostic, or therapeutic use) », « Clinical validation or performance claims (models trained on this data are not clinically validated) », « Generalization to unseen hospitals, regions, or practices », « Epidemiological or population-level inference (≠ real-world prevalence or distributions) » et « Replacing real clinical data for deployment (research-only) ».[^1] Elle autorise le « Benchmarking French medical LLMs » et la recherche reproductible.[^2] Les licences sont CC BY 4.0 et Etalab 2.0.[^3]

## Règles

| Support | Permis | Interdit |
|---|---|---|
| CV, LinkedIn, lettre | « J'ai affiné et évalué des LLM sur un corpus français de comptes rendus **fictifs** (PARHAF), protocole préenregistré, chiffres reproductibles » ; un chiffre seulement s'il a un `run_id` | « modèle prêt pour l'hôpital », « performance clinique », « validé », « déployable », tout chiffre présenté comme valable sur de vrais comptes rendus, toute allusion à des données de patients réels |
| Démo | Locale, sur textes fictifs du corpus ou synthétiques, avec la bannière « données fictives, recherche seulement » | Démo publique avec saisie libre, démo suggérant une aide au codage ou au diagnostic |
| Publication (dépôt, rapport, billet) | Résultats avec intervalles et résultats négatifs, mesurés sur un corpus fictif, citation de l'article PARHAF et attribution CC BY 4.0 | Généralisation à un hôpital, une région ou une pratique ; inférence de prévalence ; usage du mot « clinique » pour qualifier la validité |
| Rapport au CHUGA | Dire que le jeu est fictif, que l'étiquette est le diagnostic du scénario suggéré aux rédacteurs et non un codage médical, que le test officiel n'a pas été utilisé | Présenter l'étiquette comme une vérité clinique ou le test interne scellé comme le test officiel |

## Pour aller plus loin

L'article de présentation du corpus, avec son protocole et ses limites déclarées, est résumé dans [[parhaf-corpus-paper](pages/parhaf-corpus-paper.md)].

## Règles de forme

- Aucun tiret cadratin dans les textes de candidature.
- Chaque affirmation chiffrée renvoie à un `run_id` du registre ; un résultat négatif se dit au même titre qu'un résultat positif.
- L'objectif est neutre quant au vainqueur : « la distillation améliore la référence de X points » ne s'écrit que si l'intervalle exclut le seuil utile fixé en ADR-004.

[^1]: raw/parhaf-readme-60426cc.md L209-L214 [synthesis] — liste des usages exclus citée mot à mot : décision clinique, validation ou performance clinique, généralisation à d'autres hôpitaux, inférence épidémiologique, remplacement de données réelles pour un déploiement
[^2]: raw/parhaf-readme-60426cc.md L192-L198 [synthesis] — usages visés, dont « Benchmarking French medical LLMs »
[^3]: raw/parhaf-readme-60426cc.md L547-L548 — "- CC BY 4.0" et "- Etalab 2.0"
