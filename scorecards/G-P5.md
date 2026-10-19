# Scorecard G-P5 (17/10/2026) : jalon B, fin du MVP

Une note par catégorie, une preuve par note (schéma RM-12), planchers de la porte G-P5 lus dans `PLAN_PROJET_V6.md` (3 partout). **Défaut de processus déclaré** : les scorecards G-P1 à G-P4 n'ont pas été écrites à leurs portes ; cette scorecard dit l'état au 17/10/2026, sans les reconstituer. Notes posées par l'assistante : une note 3 n'est donnée que lorsqu'une confirmation indépendante existe, avec son degré ; une relecture par des sous-agents du même modèle n'est jamais comptée comme confirmation de personne. **Huit catégories sous le plancher**, chacune avec son plan de rattrapage : la porte n'est pas franchie. Le lot RM-61 puis RM-62 (en cours) touche Q4 et Q5 : la scorecard sera relue à sa fin. Toutes les commandes ont été rejouées le 17/10/2026 ; aucune ne lit le test scellé.

## Q1

```yaml
q: Q1
note: 2
requirement: "Licence lue à la source, provenance, étiquettes dérivées par script déterministe, aucune fuite (patient, auteur, gabarit, doublon), raccourcis mesurés"
artifact: experiments/frozen/splits_summary.json
artifact_sha256: "edcbfb76b09cb2a6da946b4de2d8781c2b1a62e2ccf58612f3f76e5e21e225b2"
command: ".venv/bin/python -m pytest tests/test_leakage.py tests/test_leakage_lib.py tests/test_sealed_access.py tests/test_splits_real.py tests/test_splits.py -q -p no:cacheprovider"
expected: "28 passés : aucun patient dans deux partitions, aucune paire de quasi-doublons à 0,8 entre partitions, test scellé à porte unique"
observed: "28 passés ; raccourci d'auteur mesuré (runs p0-30-author-shortcut-v2 et rm-14-author-shortcut-tfidf-v2) ; données personnelles : aucun courriel, NIR, adresse ni IBAN sur 200 patients (run 20261001-215726-p0-17-pii-scan) ; audit de 65 erreurs confiantes : ambiguïté de codage établie, bruit d'étiquette non établi (RESULTATS.md, P2-06)"
date: "2026-10-17"
residual_defect: "L'audit d'étiquettes est lu par l'assistante, pas par un codeur médical ; le gabarit d'auteur n'est pas mesuré au-delà du trigramme"
justification: "Satisfait et reproductible par commande, mais sans confirmation indépendante de la qualité des étiquettes : 2, pas 3"
remediation: "Contre-expertise des 30 cas préenregistrés de l'audit par un codeur médical, sur décision de Cyril (docs/SUIVI_NOTES_ET_LEVIERS.md, section 6) ; sans codeur, la note reste 2 et la limite est écrite dans le rapport"
```

## Q2

```yaml
q: Q2
note: 3
requirement: "Préenregistrement, test scellé, références fortes et réglées, ablation levier par levier, budgets égaux"
artifact: experiments/frozen/PROTOCOLE-V2-2026-10-05.md
artifact_sha256: "ead26b3879986e6c9b56fe4d295c113c77dab7aa34deefab15caa1f649e61848"
command: ".venv/bin/python scripts/check_frozen.py && python3 -c \"import hashlib,json; print(json.load(open('results/runs/20261006-210015-ouverture-test-scelle-g.json'))['metrics']['sha256_resultat'] == hashlib.sha256(open('results/sealed_result.json','rb').read()).hexdigest())\""
expected: "instantanés conformes à l'index ; empreinte du résultat scellé identique à celle consignée à l'ouverture"
observed: "gel : instantanés conformes à l'index ; True ; 60 fiches préenregistrées hachées dans experiments/INDEX.md, chaque écart déclaré par une ligne datée ; test scellé ouvert une seule fois (run 20261006-210015-ouverture-test-scelle-g, système G gelé par ADR-016 avant l'ouverture)"
date: "2026-10-17"
residual_defect: "Budgets égaux non tenus pour les ensembles face aux modèles seuls publiés (déclaré dans la fiche de RM-61) ; une seule graine pour le LoRA final"
justification: "Protocole v2 relu et accepté par Cyril (RM-37, 05/10/2026), personne distincte de l'assistante, et ouverture unique du test scellé prouvée par empreinte : 3"
independent_confirmation: "Cyril a accepté le protocole v2 le 05/10/2026 (roadmap_unifié.md, RM-37) ; trois relectures adversariales en contexte neuf classées au journal de nuit"
independence_degree: "personne ou contexte"
```

## Q3

```yaml
q: Q3
note: 2
requirement: "Variance entre graines mesurée, intervalles de confiance, tests appariés, correction des comparaisons multiples, verdict en trois valeurs"
artifact: results/runs/20261006-210015-ouverture-test-scelle-g.json
artifact_sha256: "a50628fc926323588fbe08ea6c1ac336f184d77a40aabc5e41bc5420415296ec"
command: ".venv/bin/python -m pytest -q -p no:cacheprovider tests/test_paired.py tests/test_durcissement_paired.py tests/test_cluster_bootstrap.py tests/test_durcissement_cluster_bootstrap.py tests/test_power_rule.py tests/test_durcissement_power_rule.py"
expected: "tous passés, dont McNemar et Holm recoupés avec SciPy et statsmodels"
observed: "47 passés ; question primaire au test scellé : G moins TF-IDF +7,28 [+1,55 ; +12,62] par blocs d'auteurs, verdict « non résolu » à δ = 2,0 publié tel quel"
date: "2026-10-17"
residual_defect: "Variance entre graines non mesurée pour le LoRA final et donc pour G (une graine) ; règle de puissance v2 non tenue au format du test scellé (largeur 7,7 à 10,2 contre 4,0, déclaré d'avance)"
justification: "Outils statistiques confirmés par une seconde implémentation (SciPy, statsmodels), mais l'exigence de variance entre graines n'est pas remplie pour le système final : 2"
remediation: "P1-19 : cinq graines du LoRA de G (environ 17 h de GPU) sur décision de budget de Cyril (B à environ 79 % après RM-62) ; à défaut, la limite reste écrite dans le rapport et la carte de modèle"
```

## Q4

```yaml
q: Q4
note: 2
requirement: "Erreurs par classe, spécialité, auteur, longueur ; perturbations ; hors distribution ; relecture d'échantillons"
artifact: results/runs/20261006-213214-encodeur-plis-auteurs-analyse.json
artifact_sha256: "bdaa116538e165af633bb9b238aea762d3ce8aa78a7f3bf43d3157ef9b72ef1f"
command: "python3 -c \"import json; print(json.load(open('results/runs/20261006-213214-encodeur-plis-auteurs-analyse.json'))['summary'])\""
expected: "encodeur en plis groupés par auteur comparé au TF-IDF, perte mesurée"
observed: "Encodeur en plis d'auteurs contre TF-IDF : non résolu, perte 5.23 points (comparable) ; confusions par chapitre, perturbations et ablations de l'encodeur et du LoRA, fragilité du LoRA à la fin du texte et sa correction au pli 0 (RM-39), 65 erreurs confiantes relues (RESULTATS.md)"
date: "2026-10-17"
residual_defect: "Robustesse du LoRA aux nouveaux auteurs et réplication de la correction de fin de texte sur cinq plis : en cours (RM-62) ; relecture des erreurs par l'assistante seule"
justification: "Analyses faites et reproductibles, mais la partie LoRA en plis d'auteurs n'est pas encore mesurée et aucune relecture n'est indépendante : 2"
remediation: "RM-62 en cours (lancé le 17/10/2026, fin attendue vers le 18/10/2026 04:00Z) : relire Q4 à sa fin ; relecture humaine des erreurs avec la contre-expertise de Q1"
```

## Q5

```yaml
q: Q5
note: 3
requirement: "Calibration (ECE), prédiction conforme avec couverture mesurée, politique d'abstention chiffrée, recalibration après quantification"
artifact: results/runs/20261006-210015-ouverture-test-scelle-g.json
artifact_sha256: "a50628fc926323588fbe08ea6c1ac336f184d77a40aabc5e41bc5420415296ec"
command: "python3 -c \"import json; c=json.load(open('results/runs/20261006-210015-ouverture-test-scelle-g.json'))['metrics']['incertitude_systeme_final']['conforme']; print(c['marginal'], c['par_famille']['couverture'], c['par_famille']['couverture_minimale'])\" && .venv/bin/python -m pytest -q -p no:cacheprovider tests/test_conformal_proprietes.py tests/test_durcissement_conformal.py"
expected: "couverture marginale au moins égale au niveau visé de 0,90 sur le test scellé ; tests de propriétés conformes verts"
observed: "couverture marginale 0,924 (1,096 classe par ensemble), par famille 0,916, famille minimale 0,821 ; abstention : exactitude 0,951 sur 80 % des patients traités [0,928 ; 0,966] ; 21 tests passés (bornes d'échantillon fini, quantile exact, Mondrian, rupture d'échangeabilité, RM-22)"
date: "2026-10-17"
residual_defect: "Une famille à 0,821 sur 56 patients ; couverture sous groupement par auteur non mesurée pour G (TF-IDF : −1,3 à −2,0 points) ; aucun modèle quantifié retenu, donc aucune recalibration à refaire"
justification: "Étalonnage et quantiles fixés en développement, couverture confirmée sur 633 patients jamais lus avant l'ouverture : 3"
independent_confirmation: "Test scellé interne de 633 patients, ouvert une seule fois après le gel (ADR-016) : la couverture visée tient sur des données que l'étalonnage n'a jamais vues"
independence_degree: "données"
```

## Q6

```yaml
q: Q6
note: 3
requirement: "Environnement verrouillé, graines, déterminisme mesuré, empreintes, reconstruction à froid testée"
artifact: results/runs/20261006-230806-reconstruction-a-froid-chiffre-cle.json
artifact_sha256: "20364d75d1792fd93714d1dc3a47ca404fa44d76bfb5bdc962015c35a2c6b500"
command: "python3 -c \"import json; m=json.load(open('results/runs/20261006-230806-reconstruction-a-froid-chiffre-cle.json'))['metrics']; print(m['identique_1e-9'], m['macro_f1_origine'], m['macro_f1_reconstruite'])\""
expected: "True : le chiffre clé reconstruit depuis un clone neuf est identique à 1e-9"
observed: "True 0.7201565961621372 0.7201565961621372 (clone neuf du commit 7741ebe, uv sync --frozen, données retéléchargées par scripts avec empreintes) ; image de développement reconstruite, 514 tests verts dans le conteneur (run 20261007-102010-image-de-developpement-reconstruite)"
date: "2026-10-17"
residual_defect: "Machine instable (Q26 : pannes sporadiques, un résultat divergent sur 120 au 07/10) ; lanceurs de .venv/bin avec un ancien chemin ; dix jours de travail non commités (gitleaks impossible, Q27)"
justification: "Reconstruction depuis un clone neuf, à l'identique : 3"
independent_confirmation: "Clone neuf, environnement reconstruit par uv sync --frozen, données retéléchargées et vérifiées par empreinte : macro-F1 identique à 1e-9"
independence_degree: "reconstruction à froid"
```

## Q7

```yaml
q: Q7
note: 2
requirement: "Typage strict, tests, CI, revue indépendante, code sans logique propre à une tâche"
artifact: results/runs/20261007-102010-image-de-developpement-reconstruite.json
artifact_sha256: "3b1114b138da0518385a48c4902534edf5bd9d62c5774ad85ec8c72ea4d7afbe"
command: ".venv/bin/python -m ruff check . && .venv/bin/python -m mypy src && .venv/bin/python -m pytest -q -p no:cacheprovider -m 'not gpu'"
expected: "ruff et mypy propres, suite complète verte"
observed: "ruff propre ; mypy : aucune erreur sur 66 fichiers ; suite complète verte le 17/10/2026 (690 tests réussis, 0 échec, après RM-22 et le mode de charge ; les 2 tests du guide de transposition, écrits ensuite, verts à part) ; revue P5-10 du 06/10 (trois sous-agents en contexte neuf, 0 bloquant, 12 constats importants corrigés)"
date: "2026-10-17"
residual_defect: "Aucune CI (dépôt distant non créé) ; gitleaks impossible côté WSL (Docker, Q27), donc crochet de commit incomplet ; revue sans indépendance de personne ni de modèle"
justification: "Typage, tests et revue en contexte neuf présents, mais l'exigence de CI n'est pas remplie : 2"
remediation: "Q27 (intégration WSL de Docker Desktop) pour rétablir gitleaks et les commits ; P5-06 (CI) dès que Cyril autorise un dépôt distant ; relecture humaine du code critique (registre, test scellé, comparaisons appariées)"
```

## Q8

```yaml
q: Q8
note: 2
requirement: "VRAM de pointe, latence p50 et p95, débit, énergie ou coût réel, front de Pareto qualité contre coût"
artifact: results/runs/20261017-030538-frontiere-cout-qualite.json
artifact_sha256: "2c7f0812a0e040242cfbd3299d0c86add0241d41033768e881fb9ac0d99b26f2"
command: "python3 -c \"import json; [print(p['systeme'], p['macro_f1'], p['latence_ms'], p['domine_par']) for p in json.load(open('results/runs/20261017-030538-frontiere-cout-qualite.json'))['metrics']['points']]\""
expected: "frontière lue dans le registre, chaque point avec sa source"
observed: "TF-IDF 1,9 ms, E sur GPU 28,8 ms, G servi en cascade inclus ; service de G en cascade : 38,4 ms attendus, 10,29 Gio, quatre clients 37,57 patients par seconde, p95 121,8 ms (run 20261017-015754-service-g-cascade) ; énergie 3,06 Wh pour 1 000 patients contre 10,67 pour G complet (run 20261017-025855-energie-service-g-cascade)"
date: "2026-10-17"
residual_defect: "Mesures sur une seule machine par le même code, sans confirmation indépendante ; aucune charge prolongée ; aucune image GPU ; énergie de la carte seulement"
justification: "Toutes les grandeurs exigées sont mesurées et reproductibles, sans confirmation indépendante : 2"
remediation: "Charge prolongée après le lot RM-61 puis RM-62 (fiche 2026-10-17-charge-prolongee-service-g hachée) ; latence et énergie remesurées dans une image GPU reconstruite (Q27), ce qui donnerait le degré « reconstruction à froid »"
```

## Q9

```yaml
q: Q9
note: 2
requirement: "Service testé, quantification vérifiée sur la tâche, surveillance de dérive, règles de maintenance, retour arrière"
artifact: results/runs/20261017-015754-service-g-cascade.json
artifact_sha256: "5e642b223fdc4e45bedb270e1a146c111f15fb0bb7a41a63559dd56812321365"
command: ".venv/bin/python -m pytest -q -p no:cacheprovider tests/test_http_service.py tests/test_drift_monitor.py tests/test_reference_prevalence.py tests/test_dockerfile_serve_imports.py tests/test_service_g_cascade.py"
expected: "tests du service, du moniteur de dérive, des lanceurs et de la liste des modules de l'image verts"
observed: "38 passés ; G servi par HTTP en cascade (run 20261017-015754-service-g-cascade) ; image TF-IDF construite et testée (07/10) ; quantification INT8 dynamique mesurée sur la tâche : effondrée, non retenue ; seuils de dérive mesurés et GET /drift branché (run 20261017-090325-simulation-derive), échantillon étiqueté dimensionné (run 20261017-091931-taille-echantillon-etiquete), maintenance et retour arrière écrits (docs/SURVEILLANCE_DERIVE.md)"
date: "2026-10-17"
residual_defect: "Pas d'image GPU, pas de charge prolongée, pas de reprise automatique sur panne du GPU, alerte de dérive lue et non poussée ; un changement d'auteurs reste invisible sans étiquettes"
justification: "Service, surveillance et retour arrière présents et testés, mais l'exploitation n'est pas éprouvée dans la durée : 2"
remediation: "Charge prolongée après le lot ; image GPU (Q27) ; une confirmation indépendante viendrait d'un rejeu du service dans cette image"
```

## Q10

```yaml
q: Q10
note: 2
requirement: "Usages permis et interdits du corpus respectés, aucune donnée de patient réel, limites écrites, sous-groupes rapportés, checklist TRIPOD-LLM remplie"
artifact: results/runs/20261001-215726-p0-17-pii-scan.json
artifact_sha256: "55a5cdc70806fa867807ebbee01afd3c0be0e0b08658776d775296630c49ddd5"
command: ".venv/bin/python -m pytest -q -p no:cacheprovider tests/test_demo_locale.py"
expected: "démo conforme à la page regles-de-formulation (boucle locale, bannière, aucune saisie libre)"
observed: "18 passés ; balayage de 200 patients : aucun courriel, NIR, adresse ni IBAN, noms et dates fictifs par construction ; checklist TRIPOD-LLM remplie (docs/CHECKLIST_TRIPOD_LLM_2026-10-07.md) ; couverture et exactitude par famille rapportées ; carte de modèle v4 avec usages exclus"
date: "2026-10-17"
residual_defect: "Aucune relecture humaine de la checklist ni des règles de formulation ; la revue de sécurité P5-10 est faite par un sous-agent du même modèle"
justification: "Exigences remplies et vérifiées par tests, sans confirmation indépendante de personne : 2"
remediation: "Relecture par Cyril de la checklist TRIPOD-LLM, de la carte de modèle v4 et de la page regles-de-formulation avant toute sortie du dépôt"
```

## Q11

```yaml
q: Q11
note: 2
requirement: "Wiki à jour avec citations vérifiées, décisions tracées (ADR), guide de transposition testé à blanc"
artifact: experiments/frozen/ADR-010-ecarts-du-protocole-au-plan-v6.md
artifact_sha256: "21190acfacbc84d0ee03bdd3e61a08be8c78034e718834cba7c4c29b0adb245b"
command: ".venv/bin/python scripts/check_wiki.py && .venv/bin/python scripts/check_wiki_quotes.py"
expected: "wiki propre, citations retrouvées dans les lignes citées"
observed: "wiki : propre ; citations du wiki : toutes retrouvées ; 17 ADR (docs/decisions) dont quatre instantanés gelés ; guide docs/TRANSPOSER_AU_CHU.md écrit et exécuté à blanc sur une tâche factice à chaque make check (tests/test_transposer_guide.py, P5-07) ; propositions de mise à jour du wiki du 17/10 en attente de l'accord de Cyril"
date: "2026-10-17"
residual_defect: "Wiki en retard sur le 17/10 (propositions non appliquées) ; aucun README à la racine ; le guide n'a été suivi que par son auteur et seule la chaîne générique est exécutée à blanc"
justification: "Les trois exigences sont remplies et vérifiées mécaniquement, sans confirmation indépendante : 2"
remediation: "Relecture du guide par Cyril, ou exécution par une autre personne sur sa propre tâche factice (degré « personne ou contexte ») ; appliquer les propositions de wiki acceptées par Cyril"
```

## Q12

```yaml
q: Q12
note: 3
requirement: "Question claire, résultats négatifs publiés, comparaison à l'état de l'art, toute affirmation tracée vers un run"
artifact: results/runs/20261017-012310-verification-machine-bios-apres.json
artifact_sha256: "48ec5f75e01054ee556a67b0811e94615848c9df2019668c13f888cc5b42fd81"
command: ".venv/bin/python scripts/check_claims.py && .venv/bin/python scripts/check_deck_claims.py"
expected: "références de runs vérifiées ; chiffres balisés des présentations identiques au registre"
observed: "claim-gate : références de runs vérifiées ; 216 chiffres balisés vérifiés contre le registre, 0 erreur ; résultats négatifs publiés au même rang (BIOS sans effet, cascade sans gain de qualité, dérive des nouveaux auteurs invisible sans étiquettes, élagage, INT8) ; comparaison au meilleur chiffre publié sur MorFITT (run 20261006-223731-morfitt-final-resume)"
date: "2026-10-17"
residual_defect: "Les vérificateurs prouvent la traçabilité d'un chiffre, pas la justesse de sa formulation ; les textes de candidature (P5-12) ne sont pas écrits"
justification: "Chaque chiffre balisé est recalculé depuis le registre par un programme distinct de la rédaction : 3"
independent_confirmation: "scripts/check_deck_claims.py et scripts/check_claims.py relisent le registre et comparent chaque chiffre balisé ou cité, à chaque make check"
independence_degree: "code"
```
