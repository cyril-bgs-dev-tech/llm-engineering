# Scorecard G-P0 (03/10/2026)
Une note par catégorie, une preuve par note (schéma RM-12). Notes **sans confirmation indépendante** : aucune note 3. Aucune note n'est gonflée ; les défauts résiduels sont dits. Artefacts : runs du registre (ajout seul), instantanés gelés ou mesures figées.

## Q1

```yaml
q: Q1
note: 2
requirement: "Licence lue à la source, provenance, étiquettes dérivées par script déterministe, aucune fuite (patient, auteur, quasi-doublon), raccourci d'auteur mesuré"
artifact: experiments/frozen/splits_summary.json
artifact_sha256: "edcbfb76b09cb2a6da946b4de2d8781c2b1a62e2ccf58612f3f76e5e21e225b2"
command: ".venv/bin/python -m pytest tests/test_leakage.py tests/test_leakage_lib.py tests/test_sealed_access.py tests/test_splits_real.py tests/test_splits.py -q -p no:cacheprovider"
expected: "28 passés, aucun patient dans deux partitions, aucune paire à 0,8 entre partitions, test scellé à porte unique"
observed: "28 passés ; partition d'empreinte 5c06b068 ; raccourci d'auteur non signalé (écart -0,86 point, run p0-30-author-shortcut-v2)"
date: "2026-10-03"
residual_defect: "Gabarit d'auteur non mesuré au-delà du trigramme ; fiche `data/cards/parhaf.md` non hachée ici (mutable)"
justification: "Preuve dans le dépôt, reproductible par commande, sans confirmation indépendante : 2, pas 3"
```

## Q2

```yaml
q: Q2
note: 2
requirement: "Préenregistrement, test scellé, budgets égaux ; références fortes et réglées exigées plus tard (P1)"
artifact: experiments/frozen/PROTOCOLE-2026-10-03.md
artifact_sha256: "aba89842a1c7da2cd500620cf7fdf47f7a345f3b2279cf87d50c148f07dac3a8"
command: ".venv/bin/python scripts/check_frozen.py"
expected: "instantanés conformes à l'index (neuf entrées)"
observed: "gel : instantanés conformes à l'index ; trois relectures adversariales en contexte neuf classées au journal"
date: "2026-10-03"
residual_defect: "Corrections postérieures à la troisième relecture relues par leur seul auteur ; références TF-IDF, encodeur et LoRA non encore mesurées"
justification: "2 : protocole figé et vérifié par commande ; 3 refusé faute de relecture indépendante des dernières corrections"
```

## Q3

```yaml
q: Q3
note: 1
requirement: "Variance mesurée, intervalles, verdict en trois valeurs : à ce stade règle et simulation seulement"
artifact: results/runs/20261002-225747-power-curves-audit.json
artifact_sha256: "31b58a4c0a7c6dcbb870b1436a7fa4a6ec01bf18c1f151f07b64334913ac5501"
command: ".venv/bin/python scripts/spikes/power_curves.py"
expected: "largeurs d'intervalle de 7,4 à 14,3 points à 629 patients (simulation)"
observed: "run enregistré 20261002-225747 : largeurs 7,4 à 14,3 (test), 3,8 à 6,7 (plis 1 à 4), 3,3 à 6,1 (dév.)"
date: "2026-10-03"
residual_defect: "Aucune variance entre graines mesurée ; outils de comparaison (P1-02) non écrits ; simulation à corrélations inventées"
justification: "1 : règle écrite (ADR-007) et puissance simulée, rien de mesuré sur des modèles"
```

## Q4

```yaml
q: Q4
note: 0
```

Aucune analyse d'erreurs avant les références (p1-23) ; plancher de G-P0 : 0.

## Q5

```yaml
q: Q5
note: 0
```

Aucune calibration ni prédiction conforme avant p4 ; plancher de G-P0 : 0.

## Q6

```yaml
q: Q6
note: 2
requirement: "Environnement verrouillé, graines, empreintes, reconstruction à froid testée"
artifact: results/runs/20261002-095934-rm-09-smoke-clean-env.json
artifact_sha256: "f3251ab4f6e7108d7ba1a8f069bba3161b993ad088ac8acb2150ccaf67a85df6"
command: "make smoke"
expected: "fil synthétique vert depuis un environnement reconstruit par uv sync --frozen"
observed: "vert dans une copie vierge (156 tests, 40 s d'installation) ; CI GitHub verte sur clone neuf (169 s au premier run vert)"
date: "2026-10-03"
residual_defect: "Déterminisme non mesuré (P1-26) ; pas de `make reproduce-small` ; la CI ne couvre ni GPU ni tests sur données"
justification: "2 : reconstruction à froid faite deux fois (copie et clone CI) mais sans chiffre clé reproduit"
```

## Q7

```yaml
q: Q7
note: 2
requirement: "Typage strict, tests, CI, code sans logique propre à une tâche"
artifact: results/measures/task_addition_cost.json
artifact_sha256: "bdfaaec4488a172288a31ebb8a3565465064e599cd59e30ecd04eb6853fd590c"
command: "make check"
expected: "ruff, mypy, 172 tests, couverture des lignes modifiées, contrôles du backlog, du wiki et du gel verts"
observed: "ruff et mypy propres, 172 passés (2 tests GPU exclus), test de transposabilité vert (ajout d'une tâche : 2 fichiers), CI verte"
date: "2026-10-03"
residual_defect: "Aucune revue indépendante du code (le relecteur n'a porté que sur le protocole) ; tests GPU hors CI"
justification: "2 : satisfait avec preuve ; pas de revue de code indépendante donc pas 3"
```

## Q8

```yaml
q: Q8
note: 1
requirement: "VRAM de pointe, latence, débit, coût réel ; Pareto exigé plus tard"
artifact: results/runs/20261002-115733-p0-08-gemma-4-31b-qlora-bench.json
artifact_sha256: "9a78b6ef7c8441db580de2e2eba38909de410e9f638a733c8d57fee70142398e"
command: ".venv/bin/python scripts/spikes/p0_06_08_teacher.py google/gemma-4-31B-it SORTIE.json"
expected: "pic réservé inférieur à 30 Gio, temps par pas mesuré"
observed: "pic réservé 26,41 Gio, 102 s par pas ; latence 117 ms (p50) et p95 288 ms mesurées sur le 4B (P0-09) ; 72 ms avec fla"
date: "2026-10-03"
residual_defect: "Pas de front de Pareto, pas d'énergie, latence mesurée sur un seul modèle, qualité absente"
justification: "1 : mesures de coût partielles, aucune qualité associée"
```

## Q9

```yaml
q: Q9
note: 1
requirement: "Service testé, quantification vérifiée ; à ce stade, spike de service"
artifact: results/runs/20261002-233641-p0-09-transformers-baseline.json
artifact_sha256: "49a137d0f470bff84b6f9362e618b40019f0543ab912b472ac236bdc5d574817"
command: "HF_HOME=$PWD/artifacts/hf_cache HF_HUB_OFFLINE=1 .venv/bin/python scripts/spikes/p0_09_serving.py SORTIE.json"
expected: "latence p50 et p95 sur 100 requêtes, sorties cohérentes"
observed: "médiane 117 ms, p95 288 à 296 ms, 9,4 à 9,7 k tokens/s ; accord lot contre séquentiel 100 %"
date: "2026-10-03"
residual_defect: "vLLM non tenté ; service FastAPI non testé ; décision écrite de P0-09 non rendue ; aucune surveillance de dérive"
justification: "1 : spike partiel, runtime Transformers seul"
```

## Q10

```yaml
q: Q10
note: 2
requirement: "Usages permis et interdits du corpus respectés, aucune donnée de patient réel, limites écrites"
artifact: results/runs/20261001-215726-p0-17-pii-scan.json
artifact_sha256: "55a5cdc70806fa867807ebbee01afd3c0be0e0b08658776d775296630c49ddd5"
command: ".venv/bin/python -m pytest tests/test_manifest.py -q -p no:cacheprovider"
expected: "aucune donnée réelle repérée, manifeste cohérent"
observed: "balayage de 200 patients : aucun courriel, NIR, adresse, IBAN ; un téléphone manifestement fictif ; fiche et licences écrites (CC BY 4.0, Etalab 2.0) ; test manifeste vert"
date: "2026-10-03"
residual_defect: "Le balayage regex ne prouve pas l'absence de donnée réelle ; carte de modèle, bannière « données fictives » et TRIPOD-LLM remplie non faites"
justification: "2 : exigences du plancher satisfaites avec preuve ; checklist TRIPOD-LLM non remplie"
```

## Q11

```yaml
q: Q11
note: 1
requirement: "Wiki à jour avec citations vérifiées, décisions tracées, guide de transposition testé à blanc"
artifact: knowledge/wiki/pages/protocole-gele-2026-10-03.md
artifact_sha256: "aa48074eb6631b4a2153dc9d315758170f72555044c3395ee38b8da9cf6be0c2"
command: ".venv/bin/python scripts/check_wiki.py && .venv/bin/python scripts/check_wiki_quotes.py"
expected: "wiki propre, citations retrouvées"
observed: "wiki propre, citations retrouvées dans les lignes citées, aucune page orpheline, dix ADR"
date: "2026-10-03"
residual_defect: "Guide `docs/TRANSPOSER_AU_CHU.md` absent ; sources A2 et A3 non ingérées ; une page non hachée par nature"
justification: "1 : wiki et ADR en bon état, mais le guide de transposition n'existe pas"
```

## Q12

```yaml
q: Q12
note: 2
requirement: "Question claire, résultats négatifs publiés, affirmations tracées vers un run"
artifact: results/runs/20261002-221006-power-sketch-ic-width-v2.json
artifact_sha256: "77123e3bc3d895b951a4434918b5028bc79b39e6cf7f5c652ae9eddf10a6be3b"
command: "grep -c \"Tableau de preuve\" docs/AUDIT_STRATEGIQUE_2026-10-03.md"
expected: "1 tableau de preuve joint au texte sortant"
observed: "1 ; le résultat négatif attendu (règle de puissance probablement en échec) est publié ; une erreur propre (effectifs proportionnels présentés comme réels) est corrigée en clair avec ancien et nouveau run conservés"
date: "2026-10-03"
residual_defect: "`RESULTATS.md` absent (aucun résultat de modèle encore) ; texte du brief GLM non encore relu par un tiers"
justification: "2 : claim-gate appliqué au texte destiné à sortir ; pas de comparaison à l'état de l'art encore"
```
