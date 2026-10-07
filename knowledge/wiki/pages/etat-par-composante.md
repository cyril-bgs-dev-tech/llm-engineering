---
title: État du projet par composante de qualité (04/10/2026)
category: Analyses
summary: Pour chacune des huit composantes de la grille de notation (performance, rigueur, données, incertitude, erreurs, reproductibilité, efficience, honnêteté) ce qui est prouvé, ce qui manque et la prochaine action, avec renvoi aux preuves
tags: [composantes, notation, etat, audit]
sources: [audit-glm-v3, audit-glm-v4, resultats]
created: 2026-10-03
updated: 2026-10-07
---

# État du projet par composante de qualité

Notes de la présentation : estimations de l'assistante, non mesurées ; elles ne remplacent pas une scorecard.[^1] Les actions viennent du triage de l'audit GLM v3.[^2]

## Performance
À recette mûre (10 époques), l'ordre s'est inversé : TF-IDF caractères équilibré 0,720, encodeur moyenné 0,73 à 0,76 selon le pli, LoRA du 4B 0,78 (pli 0) et 0,74 (pli 1), ensemble encodeur + TF-IDF 0,75 à 0,79 aux cinq plis, soit **+5,20 points [+3,69 ; +6,78] sur le TF-IDF** (3 586 patients).[^3][^7] Le LoRA aux cinq plis donne 0,7673 (+4,71 sur le TF-IDF, non distinct de l'encodeur ni de l'ensemble), le zéro-shot 4B 0,49 ; **la distillation vers un encodeur, apparemment +3,47, ne résiste pas au contrôle de fuite de second ordre (élève imbriqué 0,7528, −4,24 contre l'élève non imbriqué)** ; la règle de sélection retient l'ensemble LoRA + encodeur + TF-IDF (0,7799).[^8][^10]

## Rigueur statistique et protocole
Protocole v1 gelé, premier cycle EXPLORE ; règle de puissance v1 échouée (12,2 contre 4,0), **règle v2 réussie pour l'ensemble contre le TF-IDF sur cinq plis à 95 % (3,09 par patients, 3,39 par blocs d'auteurs), non à 98,33 % par blocs d'auteurs (4,24)** ; l'acceptation du protocole v2 est une décision de Cyril.[^4][^7]

## Données et anti-fuite
Auteur identifiable par le style (0,917) ; effet d'auteur pur d'environ 2 points ; plis par patient et par auteur côte à côte ; leave-one-author-out mesuré ; la fuite de second ordre de la distillation a été **mesurée** (significative, RM-56) et le gain correspondant retiré.[^3][^10]

## Fiabilité de l'incertitude
Température, conforme marginal et par famille, Wilson, abstention : sur cinq plis, l'ensemble garde une couverture minimale par famille de 0,89 avec 1,89 classes par ensemble (TF-IDF : 2,69), et 0,948 d'exactitude à 70 % de couverture.[^7] Le LoRA mûr a une ECE de 0,03 après température (plis 0 et 1).[^3]

## Analyse d'erreurs et robustesse
Taxonomie des erreurs (96 % hors famille), perturbations et ablations de contenu mesurées sur le TF-IDF et le LoRA mûr ; non mesuré : robustesse de l'encodeur et leave-one-author-out du LoRA.[^3]

## Reproductibilité et ingénierie
Registre, protocole haché, fiches hachées, contrôle des références de runs, fonction de lancement partagée testée (`scripts/lib/lot.sh`), ensembles reconstruits par script, déterminisme GPU mesuré (même graine : 0,7714 vers 0,7362).[^3]

## Efficience et déploiement
TF-IDF 1,9 ms et 20 Mo ; encodeur 191 ms sur processeur ; LoRA fusionné 61 ms et 8,6 Wh pour 1 000 patients ; encodeur sur GPU en bf16 4,3 ms et 0,31 Wh (28 fois moins que le LoRA) ; INT8 dynamique naïf effondré ; cascade encodeur vers LoRA validée hors pli : 93,4 % sans LoRA, non-infériorité à 2 points, environ 26 à 34 ms contre 61 ms ; fiche de déploiement par contrainte écrite ; recette d'encodeur v2 : bf16 équivalent et 2,25 fois plus rapide, lissage, EMA et curriculum sans gain.[^3][^8][^11] **Mise à jour du 07/10/2026 (note 6 vers 7, estimation à plus ou moins 1)** : G mesuré d'un seul tenant (p50 91,6 ms, 10,3 Gio, 10,5 Wh pour 1 000 patients, quatre clients : p95 0,8 s), ensemble E sur processeur seul 801 ms, frontière coût-qualité (le LoRA seul et les cascades sont dominés par E ; G coûte 7,9 fois l'entraînement et 3,2 fois la latence de E pour +0,78 point non résolu), image de service du TF-IDF durcie et testée (démarrage 2,6 s, 470 patients par seconde ; un défaut de file de connexions trouvé et corrigé). Pas 8 : compression jamais réussie, G servi par un banc seulement.[^12][^13]

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
[^10]: RESULTATS.md [synthesis] — section « Distillation à professeur imbriqué »
[^11]: docs/FICHE_DE_DEPLOIEMENT.md [synthesis] — arbre de décision par contrainte
[^12]: docs/FICHE_DE_DEPLOIEMENT.md [synthesis] — version du 07/10/2026, règle de décision par contrainte avec les mesures d'un seul tenant
[^13]: docs/FRONTIERE_COUT_QUALITE.md [synthesis] — tableau de dominance, runs `20261007-094900-frontiere-cout-qualite` et `20261007-094117-service-g-bout-en-bout-gpu`
