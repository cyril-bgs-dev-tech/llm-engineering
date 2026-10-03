---
title: Incidents d'exécution et audits indépendants
category: Expériences
summary: Segfault du tokenizer pendant P1-11 (3 runs sur 6) et ses correctifs, journal de lot faux, audits GLM v2 et v3 avec leurs écarts classés
tags: [incident, audit, tokenizer, glm]
sources: [journal-nuit-2026-10-02, audit-glm-v3]
created: 2026-10-03
updated: 2026-10-03
---

# Incidents d'exécution et audits indépendants

## Incident du tokenizer (P1-11, 03/10/2026)

Trois des six runs du criblage (Gemma-4-E4B 1e-5, Qwen3.5-9B 1e-5, Qwen3.5-4B 1e-4) sont morts en une minute sans sortie : erreurs de segmentation dans `tokenizers.abi3.so`, lues dans `dmesg`. Deux plantages plus anciens du même type avaient eu lieu.[^1] Le journal du premier lot affichait `code=0` à tort, parce que `$(date)` remet `$?` à zéro avant l'affichage : ce lot ne rapporte pas les vrais codes de sortie.[^1]

Correctifs : `TOKENIZERS_PARALLELISM=false` et `RAYON_NUM_THREADS=2` dans `scripts/p1_finetune.py` et dans la seconde passe `scripts/run_p1_11_missing.sh`, qui relance les runs absents du registre avec le vrai code de sortie et trois essais.[^1] Le Gemma 1e-5 relancé a abouti sans plantage.[^2]

Leçon : un lot de nuit calcule le code de sortie avant tout affichage et relance les runs absents du registre plutôt que de se fier à son propre journal.

## Audits indépendants de GLM

- **v2** : mypy représente environ 96 % du temps du crochet de commit (entrée-sortie sur disque Windows) ; mesuré, non appliqué.[^1]
- **v3** (`audit_GLM_5_3_v3.md`, 80 actions) : triage et statut de chaque action dans `docs/AUDIT_GLM_v3_TRIAGE.md`.[^3] Écarts classés : un jugement de GLM était erroné sur les durées de run (les secondes de Gemma et du 9B étaient permutées dans son tableau : 4 226 s pour Gemma, 3 623 s pour le 9B, d'après le registre).[^2]

[^1]: tasks/JOURNAL_NUIT_2026-10-02.md [synthesis] — entrées du 03/10 à 14:30Z (incident) et 14:45Z (retour de GLM)
[^2]: results/runs/20261003-174127-p1-11-gemma-4-e4b-lr1e-5.json [synthesis] — run abouti ; durées dans les métriques de `p1-11-*`
[^3]: docs/AUDIT_GLM_v3_TRIAGE.md [synthesis] — statut par action
