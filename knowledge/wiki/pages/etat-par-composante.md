---
title: État du projet par composante de qualité (04/10/2026)
category: Analyses
summary: Pour chacune des huit composantes de la grille de notation (performance, rigueur, données, incertitude, erreurs, reproductibilité, efficience, honnêteté) ce qui est prouvé, ce qui manque et la prochaine action, avec renvoi aux preuves
tags: [composantes, notation, etat, audit]
sources: [audit-glm-v3, audit-glm-v4, resultats]
created: 2026-10-03
updated: 2026-10-04
---

# État du projet par composante de qualité

Notes de la présentation : estimations de l'assistante, non mesurées ; elles ne remplacent pas une scorecard.[^1] Les actions viennent du triage de l'audit GLM v3.[^2]

## Performance
À recette mûre (10 époques), l'ordre s'est inversé : TF-IDF caractères équilibré 0,720, encodeur moyenné 0,73 à 0,76 selon le pli, LoRA du 4B 0,78 (pli 0) et 0,74 (pli 1), ensemble encodeur + TF-IDF 0,75 à 0,79 aux cinq plis, soit **+5,20 points [+3,69 ; +6,78] sur le TF-IDF** (3 586 patients).[^3][^7] Le LoRA sur les plis 2 à 4 (professeur hors pli) est en cours ; l'ancrage zéro-shot est préparé.[^8]

## Rigueur statistique et protocole
Protocole v1 gelé, premier cycle EXPLORE ; règle de puissance v1 échouée (12,2 contre 4,0), **règle v2 réussie pour l'ensemble contre le TF-IDF sur cinq plis à 95 % (3,09 par patients, 3,39 par blocs d'auteurs), non à 98,33 % par blocs d'auteurs (4,24)** ; l'acceptation du protocole v2 est une décision de Cyril.[^4][^7]

## Données et anti-fuite
Auteur identifiable par le style (0,917) ; effet d'auteur pur d'environ 2 points ; plis par patient et par auteur côte à côte ; leave-one-author-out mesuré ; réserve de second ordre de la distillation consignée.[^3][^9]

## Fiabilité de l'incertitude
Température, conforme marginal et par famille, Wilson, abstention : sur cinq plis, l'ensemble garde une couverture minimale par famille de 0,89 avec 1,89 classes par ensemble (TF-IDF : 2,69), et 0,948 d'exactitude à 70 % de couverture.[^7] Le LoRA mûr a une ECE de 0,03 après température (plis 0 et 1).[^3]

## Analyse d'erreurs et robustesse
Taxonomie des erreurs (96 % hors famille), perturbations et ablations de contenu mesurées sur le TF-IDF et le LoRA mûr ; non mesuré : robustesse de l'encodeur et leave-one-author-out du LoRA.[^3]

## Reproductibilité et ingénierie
Registre, protocole haché, fiches hachées, contrôle des références de runs, fonction de lancement partagée testée (`scripts/lib/lot.sh`), ensembles reconstruits par script, déterminisme GPU mesuré (même graine : 0,7714 vers 0,7362).[^3]

## Efficience et déploiement
TF-IDF 1,9 ms et 20 Mo ; encodeur 191 ms sur processeur ; LoRA 117 ms sur GPU ; INT8 dynamique naïf effondré ; cascade encodeur vers LoRA à seuil 0,8 : 77 à 79 % des patients sans appel au LoRA, sans perte de macro-F1 (plis 0 et 1, non validé).[^3][^8] Mesure de service du LoRA fusionné, énergie par 1 000 patients et zéro-shot : préparées, après le LoRA.[^8]

## Sûreté, conformité, honnêteté
Résultats négatifs publiés, claim-gate, carte de modèle v3 mise à jour, gabarit de rapport, journal des accès au test scellé.[^6]

[^1]: docs/presentation/projet_llm_finetuning.html [synthesis] — dernière diapositive, notes par composante
[^2]: docs/AUDIT_GLM_v3_TRIAGE.md [synthesis] — statut des actions par composante
[^3]: RESULTATS.md [synthesis] — tableaux, audits, auteur, robustesse, cascade
[^4]: experiments/INDEX.md [synthesis] — instantanés du gel du 03/10/2026
[^6]: docs/CARTE_DE_MODELE_V3.md [synthesis] — périmètres, Pareto, limites
[^7]: RESULTATS.md [synthesis] — plis 3 et 4, règle v2 à cinq plis, conforme par famille, abstention à cinq plis
[^8]: roadmap_unifié.md [synthesis] — tâches RM-28 à RM-40 et fiches associées
[^9]: src/llmft/distill.py [synthesis] — réserve de second ordre dans l'en-tête
