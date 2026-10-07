---
title: Incidents d'exécution et audits indépendants
category: Expériences
summary: Segfault du tokenizer pendant P1-11 (3 runs sur 6), correctifs insuffisants et contournement par sous-processus épinglé (LoRA final), journal de lot faux, audits GLM v2 et v3 avec leurs écarts classés
tags: [incident, audit, tokenizer, glm]
sources: [journal-nuit-2026-10-02, audit-glm-v3]
created: 2026-10-03
updated: 2026-10-07
---

# Incidents d'exécution et audits indépendants

## Incident du tokenizer (P1-11, 03/10/2026 ; LoRA final, 05/10/2026)

Trois des six runs du criblage (Gemma-4-E4B 1e-5, Qwen3.5-9B 1e-5, Qwen3.5-4B 1e-4) sont morts en une minute sans sortie : erreurs de segmentation dans `tokenizers.abi3.so`, lues dans `dmesg`. Deux plantages plus anciens du même type avaient eu lieu.[^1] Le journal du premier lot affichait `code=0` à tort, parce que `$(date)` remet `$?` à zéro avant l'affichage : ce lot ne rapporte pas les vrais codes de sortie.[^1]

Correctifs : `TOKENIZERS_PARALLELISM=false` et `RAYON_NUM_THREADS=2` dans `scripts/p1_finetune.py` et dans la seconde passe `scripts/run_p1_11_missing.sh`, qui relance les runs absents du registre avec le vrai code de sortie et trois essais.[^1] Le Gemma 1e-5 relancé a abouti sans plantage.[^2]

Ces correctifs ne suffisent pas. Le 05/10/2026, le LoRA final (tokenizer de Qwen3.5-4B, 3 586 textes) a échoué plus de dix fois de suite : 25 plantages sur 31 runs sans épinglage, à un indice différent chaque fois, même avec `RAYON_NUM_THREADS=1`.[^4] Aucun échec sur 78 runs épinglés sur un cœur dès le lancement, contre 8 sur 34 avec un épinglage partiel ou tardif ; la mémoire, le disque Windows, un cœur précis et un texte précis sont écartés.[^4] Contournement : `build_inputs` délègue la tokenisation à un sous-processus épinglé, relancé jusqu'à 6 fois.[^5] Le défaut reste en amont, dans `tokenizers` 0.23.2, et la cause (une course entre threads) est une piste, pas un fait établi.

Leçon : un lot de nuit calcule le code de sortie avant tout affichage et relance les runs absents du registre plutôt que de se fier à son propre journal. Réduire le nombre de threads du tokenizer ne protège pas ; ce qui a marché est de confiner tout le processus sur un cœur dès son lancement.

## Instabilité de calcul de la machine (07/10/2026)

Un test de charge du TF-IDF caractères (même calcul déterministe répété dans un processus fils par essai, sans relance) donne 15 pannes sur 135 essais (11 %) : 6 segfaults et 9 `TypeError` d'opérandes impossibles en Python correct ; l'épinglage sur un cœur ne change pas le taux (12 % libre contre 16 % épinglé, non résolu) et les pannes ne se concentrent sur aucun cœur[^6]. Sur 120 essais réussis, un résultat diffère silencieusement des 119 autres (même entrée, aucune erreur)[^7]. La cause n'est pas établie ; l'hypothèse d'une instabilité matérielle est cohérente mais non prouvée, la vérification du BIOS et d'un test de mémoire est demandée à Cyril (Q26). Conséquence pour les chiffres : double exécution (`agree_twice`) des chiffres publiés.

## Audits indépendants de GLM

- **v2** : mypy représente environ 96 % du temps du crochet de commit (entrée-sortie sur disque Windows) ; mesuré, non appliqué.[^1]
- **v3** (`audit_GLM_5_3_v3.md`, 80 actions) : triage et statut de chaque action dans `docs/AUDIT_GLM_v3_TRIAGE.md`.[^3] Écarts classés : un jugement de GLM était erroné sur les durées de run (les secondes de Gemma et du 9B étaient permutées dans son tableau : 4 226 s pour Gemma, 3 623 s pour le 9B, d'après le registre).[^2]

[^1]: tasks/JOURNAL_NUIT_2026-10-02.md [synthesis] — entrées du 03/10 à 14:30Z (incident) et 14:45Z (retour de GLM)
[^2]: results/runs/20261003-174127-p1-11-gemma-4-e4b-lr1e-5.json [synthesis] — run abouti ; durées dans les métriques de `p1-11-*`
[^3]: docs/AUDIT_GLM_v3_TRIAGE.md [synthesis] — statut par action
[^4]: results/runs/20261005-224632-tokenizers-course-threads-qwen35.json [synthesis] : décomptes par condition, diagnostic exploratoire non préenregistré
[^5]: src/llmft/tokenizer_guard.py [synthesis] : docstring du module et fonction `isolated_build_inputs`
[^6]: results/runs/20261007-044852-stress-tfidf-par-coeur.json [synthesis] : 5 pannes sur 65 essais, arrêt N31
[^7]: results/runs/20261007-050906-stress-tfidf-libre-contre-epingle.json [synthesis] : 10 pannes sur 70 essais, une empreinte divergente
