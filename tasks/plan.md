# Plan d'exécution (généré)

Fichier généré depuis `roadmap_unifié.md`. L'ordre, les portes et les arrêts y sont définis ; le détail des tâches est dans `MICROTACHES.md`.

## Étape R0 : cadrage et fondations légères

- **Objectif** : poser le cadre avant toute installation lourde.
- **Skills à charger** : interview-me, documentation-and-adrs, git-workflow-and-versioning, spec-driven-development, planning-and-task-breakdown.
- **Porte de sortie** : décisions de cadrage datées ; dépôt local initialisé ; SPEC-P0 validée par Cyril.
- **Arrêt ou repli si** : une décision bloquante reste ouverte, on pose la question et on n'avance pas sur une supposition.

## Étape R1 : socle machine minimal

- **Objectif** : lever le risque matériel le plus bloquant avec le moins de téléchargement.
- **Skills à charger** : vram-preflight, debugging-and-error-recovery, ci-cd-and-automation, security-and-hardening, run-registry.
- **Porte de sortie** : PyTorch voit `sm_120` ; bibliothèques de fine-tuning vérifiées ; machine mesurée ; environnement figé ; licences des dépendances auditées.
- **Arrêt ou repli si** : PyTorch ne s'exécute pas sur SM120, plan B du plan V6 section 9 présenté à Cyril avant de continuer.

## Étape R2 : viabilité des données (CPU seulement)

- **Objectif** : savoir si la question principale peut réellement être posée, avant d'installer un gros modèle.
- **Skills à charger** : dataset-intake, leakage-guard, experiment-preregistration, source-driven-development.
- **Porte de sortie** : révision PARHAF épinglée ; comptages sourcés ; présence et distribution du diagnostic principal ; splits par patient et par auteur ; raccourci d'auteur mesuré ; décision RM-08.
- **Arrêt ou repli si** : classes trop rares, groupes auteur insolubles ou étiquette inadéquate : simplifier la cible (niveau chapitre, regroupements) ou changer de tâche. Ne pas installer de gros modèle.

## Étape R3 : fil synthétique de bout en bout

- **Objectif** : valider l'architecture minimale sans coût GPU significatif.
- **Skills à charger** : spec-driven-development, test-driven-development, constraint-driven-development, api-and-interface-design, incremental-implementation, run-registry.
- **Porte de sortie** : `make smoke` enchaîne contrat, chargeur, split, modèle trivial CPU, métriques, registre, reprise, rapport, et se rejoue sur environnement propre ; un cas de fuite piégé est détecté ; un contrat invalide est rejeté.
- **Arrêt ou repli si** : le fil ne tient pas sur la tâche jouet, on corrige avant de toucher un modèle réel.

## Étape R4 : compatibilité des modèles et budget

- **Objectif** : savoir quels modèles se chargent, classent et tiennent en mémoire, puis préciser le budget.
- **Skills à charger** : vram-preflight, lora-classifier-recipe, doubt-driven-development, experiment-preregistration.
- **Porte de sortie** : tableau de compatibilité par modèle ; élève du premier cycle présélectionné par règle écrite ; pic de mémoire du plus gros professeur mesuré ; budget par vague.
- **Arrêt ou repli si** : aucun professeur de 24 à 31 milliards ne tient ou n'accepte une tête de classification, repli verbaliseur, ou professeur plus petit, ou déclencheur de location (plan V6, section 5.2).

## Étape R5 : geler le protocole

- **Objectif** : écrire et figer tout ce qui doit l'être avant le premier run comparatif.
- **Skills à charger** : experiment-preregistration, doubt-driven-development, paired-comparison, claim-gate, wiki-ingest.
- **Porte de sortie** : `PROTOCOLE.md` figé, empreinte aussi consignée dans une page wiki ; scorecard G-P0 au plancher, une preuve par note.
- **Arrêt ou repli si** : B, N, la métrique primaire ou le seuil utile manquent, on ne fige pas.

## Étape R6 : références sur la tâche principale

- **Objectif** : obtenir le premier résultat scientifique utile et décider s'il justifie un LLM.
- **Skills à charger** : paired-comparison, run-registry, leakage-guard, experiment-preregistration, vram-preflight.
- **Porte de sortie** : références avec intervalles de confiance et coût ; harnais et tests statistiques validés ; raccourci d'auteur mesuré sur les références ; décision RM-15.
- **Arrêt ou repli si** : les références rendent la comparaison non informative (variance, puissance, raccourcis) : simplifier avant d'engager un LLM.

## Étape R7 : une LoRA de référence (jalon A)

- **Objectif** : prouver le fine-tuning LLM avec le plus petit espace de recherche défendable.
- **Skills à charger** : lora-classifier-recipe, vram-preflight, run-registry, paired-comparison, claim-gate, wiki-ingest.
- **Porte de sortie** : élève choisi par la règle écrite ; taux d'apprentissage réglé ; variance de graines mesurée ; configuration gelée ; premier `RESULTATS.md` ; G-P1.
- **Arrêt ou repli si** : la LoRA est dominée par l'encodeur en qualité et en coût, la distillation se poursuit comme expérience d'apprentissage limitée, et non comme candidat présumé (RM-17).

## Étape R8 : spike de distillation miniature

- **Objectif** : vérifier le mécanisme, la mémoire et le signal avant cinq plis coûteux.
- **Skills à charger** : distillation-pipeline, test-driven-development, vram-preflight, wiki-ingest.
- **Porte de sortie** : perte testée sur cas analytiques ; un pli, une paire professeur élève ; écart avec la recette LMSYS exacte documenté ; coût du run complet mesuré ; règle go/no-go préenregistrée.
- **Arrêt ou repli si** : OOM, temps complet hors budget, aucune tendance utile : ne pas lancer les cinq plis.

## Étape R9 : expérience confirmatoire de distillation

- **Objectif** : répondre à la question scientifique centrale.
- **Skills à charger** : distillation-pipeline, leakage-guard, paired-comparison, lora-classifier-recipe, claim-gate.
- **Porte de sortie** : probabilités hors pli complètes avec manifeste ; configuration gelée ; **système final figé et prédiction du test scellé hachée (RM-50) avant l'ouverture** ; référence, tâche voisine, distillation et combinaison comparées ; verdict en trois valeurs ; test scellé ouvert une seule fois ; G-P2 et G-P3.
- **Arrêt ou repli si** : verdict non résolu et aucun budget pour lever l'incertitude.

## Étape R10 : fiabilité du meilleur candidat

- **Objectif** : calibrer, conformiser et documenter le meilleur point retenu, quelle que soit sa famille.
- **Skills à charger** : model-card-calibration, test-driven-development, doubt-driven-development, wiki-ingest.
- **Porte de sortie** : température et ECE ; couverture conforme avec hypothèses explicites et validations de RM-22 ; politique d'abstention ; carte de modèle ; TRIPOD-LLM remplie ; G-P4.
- **Arrêt ou repli si** : couverture hors cible sans cause identifiée.

## Étape R11 : livraison ciblée (jalon B)

- **Objectif** : ne livrer que ce qui sert la candidature et la démonstration de rigueur.
- **Skills à charger** : claim-gate, ci-cd-and-automation, documentation-and-adrs.
- **Porte de sortie** : reconstruction à froid d'un chiffre clé dans la tolérance ; rapport final ; tous les textes sortants (CV, LinkedIn, lettre) passés par `claim-gate` ; G-P5.
- **Arrêt ou repli si** : aucune affirmation ne peut être reliée à un run, on la retire.

## Étape R12 : compléments de références et de réglage (chemin complet)

- **Objectif** : étoffer les références et le réglage de la LoRA.
- **Skills à charger** : lora-classifier-recipe, paired-comparison, leakage-guard, performance-optimization.
- **Porte de sortie** : références complémentaires et réglage complet consignés avec verdicts.
- **Arrêt ou repli si** : le budget B est atteint.

## Étape R13 : leviers de données et de distillation

- **Objectif** : explorer les leviers du catalogue au-delà de la distillation simple.
- **Skills à charger** : dataset-intake, distillation-pipeline, lora-classifier-recipe, paired-comparison, wiki-update.
- **Porte de sortie** : verdict en trois valeurs pour chaque levier testé ; résultats négatifs publiés.
- **Arrêt ou repli si** : un levier sans gain sort du programme, publié comme résultat négatif.

## Étape R14 : compression et robustesse

- **Objectif** : mesurer ce que coûtent la fusion, la quantification et les perturbations.
- **Skills à charger** : performance-optimization, paired-comparison, model-card-calibration.
- **Porte de sortie** : front de Pareto qualité contre coût ; robustesse mesurée.
- **Arrêt ou repli si** : NVFP4 instable sur SM120, repli FP8 ou INT8.

## Étape R15 : industrialisation

- **Objectif** : n'industrialiser que ce qui sert un cas de démonstration explicite.
- **Skills à charger** : api-and-interface-design, ci-cd-and-automation, observability-and-instrumentation, shipping-and-launch, code-review-and-quality, security-and-hardening.
- **Porte de sortie** : service testé ; guide de transposition exécuté à blanc ; revue indépendante.
- **Arrêt ou repli si** : un composant ne sert qu'à cocher un mot de l'offre, on ne le construit pas.

## Étape R16 : options (sur décision de Cyril)

- **Objectif** : piste générative et location de GPU, chacune avec sa spécification propre.
- **Skills à charger** : experiment-preregistration, distillation-pipeline, doubt-driven-development, dataset-intake, security-and-hardening.
- **Porte de sortie** : selon l'option ouverte.
- **Arrêt ou repli si** : la décision de Cyril manque, l'option reste fermée.
