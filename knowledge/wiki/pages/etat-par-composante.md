---
title: État du projet par composante de qualité (03/10/2026)
category: Analyses
summary: Pour chacune des huit composantes de la grille de notation (performance, rigueur, données, incertitude, erreurs, reproductibilité, efficience, honnêteté) ce qui est prouvé, ce qui manque et la prochaine action, avec renvoi aux preuves
tags: [composantes, notation, etat, audit]
sources: [audit-glm-v3, resultats]
created: 2026-10-03
updated: 2026-10-03
---

# État du projet par composante de qualité

Notes de la présentation : estimations de l'assistante, non mesurées ; elles ne remplacent pas une scorecard.[^1] Les actions viennent du triage de l'audit GLM v3.[^2]

## Performance
Le TF-IDF fait 0,684 de macro-F1 sur cinq plis ; le meilleur LLM (Qwen3.5-9B) 0,565 sur le pli 0, soit 13,2 points sous le TF-IDF.[^3] Le déficit vient des petits chapitres : écart de 4 points seulement en F1 pondérée.[^3] Prochaine action : fin du criblage, puis grille complète de l'élève retenu, puis exploration à perte pondérée.

## Rigueur statistique et protocole
Protocole gelé en neuf instantanés ; premier cycle classé EXPLORE ; verdict en trois valeurs.[^4] Manque : P1-19 (cinq graines) et la règle de puissance RM-17. Alerte à 80 % de B codée.[^5]

## Données et anti-fuite
L'identifiant d'auteur n'est présent dans le texte que pour un patient sur 4 254, mais le style identifie l'auteur à 0,917 (confondu avec le thème) : la lecture de RM-14 reste non tranchée.[^3]

## Fiabilité de l'incertitude
Mesurée sur le TF-IDF seulement (ECE 0,028, couverture conforme 0,901) ; rien n'est hérité par les LLM.[^3][^6] Prochaine action : `q5_uncertainty.py` sur les probabilités du 9B dès qu'elles existent.

## Analyse d'erreurs et robustesse
Creux de longueur expliqué par la composition ; confusions par chapitre ; TF-IDF perd 5,6 points sans accents et 0,52 d'exactitude hors spécialité.[^3] Manque : robustesse du 9B (adaptateur à sauvegarder au prochain run).

## Reproductibilité et ingénierie
Registre append-only, protocole haché, tests, `floor_guard`. Manque : reconstruction à froid, déterminisme GPU (P1-26), release testée sur tag.[^2]

## Efficience et déploiement
Durées et pics mémoire mesurés par run ; front de Pareto provisoire dans la carte de modèle.[^6] Manque : latence p50/p95, vLLM, quantification, débit à 4 096 tokens.

## Sûreté, conformité, honnêteté
Résultats négatifs publiés, claim-gate, carte de modèle provisoire, gabarit de rapport, journal des accès au test scellé.[^6]

[^1]: docs/presentation/projet_llm_finetuning.html [synthesis] — dernière diapositive, notes par composante
[^2]: docs/AUDIT_GLM_v3_TRIAGE.md [synthesis] — statut des actions par composante
[^3]: RESULTATS.md [synthesis] — tableaux du chapitre, mesures de l'audit GLM, traces d'auteur, robustesse
[^4]: experiments/INDEX.md [synthesis] — neuf instantanés du gel du 03/10/2026
[^5]: src/llmft/budget.py [synthesis] — seuil d'alerte à 80 % de 90 h
[^6]: docs/CARTE_DE_MODELE_PROVISOIRE.md [synthesis] — périmètres, Pareto, limites
