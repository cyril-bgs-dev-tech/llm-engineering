# LLM-Engineering

**Faire rendre à un LLM la bonne réponse, au format attendu, et mesurer quelle stratégie d'optimisation paie
vraiment.** Cas d'étude : à partir d'un compte rendu clinique fictif (corpus PARHAF), prédire le chapitre CIM-10
du diagnostic (17 classes), sur une seule RTX 5090. Affinage LoRA, distillation, compression, ensembles et
cascade sont comparés à des références fortes et réglées (TF-IDF, encodeur CamemBERT-bio, zéro-shot), sous un
protocole gelé et haché avant la première mesure.

> Données fictives : aucune donnée de patient réel n'est utilisée ni versionnée.

**[Ouvrir le plan interactif](https://cyril-bgs-dev-tech.github.io/llm-engineering/)** : les 38 tests du projet dans une big picture,
chacun coloré par son verdict et rattaché à son run, avec un scénario pas à pas, des flux isolables et le zoom ;
puis les notes par composante face au SOTA open source et au SOTA absolu (estimations à plus ou moins 1 point).
Fichier : `docs/presentation/plan_llm_engineering.html`.

## Ce qui a été mesuré

| Question | Résultat | Verdict |
|---|---|---|
| Test scellé (633 patients, ouvert une seule fois) : système final G (LoRA + encodeur + TF-IDF) contre le meilleur TF-IDF | macro-F1 0,8131 contre 0,7402, +7,28 points [+1,55 ; +12,62] par blocs d'auteurs | **non résolu** au seuil d'utilité de 2 points, comme annoncé d'avance |
| Gain de l'affinage LoRA sur Qwen3.5-4B en zéro-shot (pli 0) | +28,8 points [+22,5 ; +35,0] | gain |
| MorFITT, benchmark public, G transposé sans réglage | F1 pondéré 72,30 [70,15 ; 74,35] contre 71,95 pour le meilleur chiffre publié | au niveau du meilleur publié, pas au-dessus |
| Cascade : l'ensemble E répond seul quand il est sûr, sinon G | même qualité que G (−0,10 [−0,23 ; +0,02]), 82 % des patients sans le LoRA, latence attendue 38,4 ms contre 97,4, énergie 3,06 contre 10,67 Wh pour 1 000 patients | retenue |
| Incertitude de G au test | couverture conforme 0,924 pour 0,90 visé ; exactitude 0,962 en renvoyant 30 % des cas à un humain | la pire famille de chapitres reste sous la cible (0,821) |
| Distillation vers un encodeur, INT8 statique, élagage, empilement appris, lissage, moyenne de poids, curriculum | aucun gain ne tient | **sept résultats négatifs publiés** |

Chaque chiffre renvoie à un run du registre. Lecture conseillée : `RESULTATS.md` (tous les résultats, avec leurs
runs), `docs/RAPPORT_FINAL_2026-10-07.md`, `docs/presentation/`, puis `PROTOCOLE.md` et `docs/decisions/` (ADR).

## Organisation

| Chemin | Contenu |
|---|---|
| `src/llmft/` | noyau : chargement, découpages, modèles, métriques, registre, service HTTP, surveillance de dérive |
| `scripts/` | une commande par expérience ou mesure |
| `experiments/` | une fiche par expérience, hachée avant le run (hypothèse, règle de décision, prédiction) ; `INDEX.md` |
| `results/runs/` | un fichier JSON par run, jamais réécrit ; `results/measures/`, `results/sealed_result.json` |
| `task_specs/` | contrats YAML des tâches : ajouter une tâche de même famille ne touche pas au noyau |
| `data/` | fiches, manifestes d'empreintes, scripts de téléchargement et découpages ; **aucune donnée** |
| `tests/` | tests automatiques (`make test`) ; `make check-fast` : lint, typage, plancher, secrets |
| `docs/`, `knowledge/wiki/` | protocole, cartes de modèle, fiche de déploiement, revue indépendante, wiki |

## Reproduire

```bash
uv sync --frozen
python data/scripts/download_parhaf.py   # PARHAF à la révision épinglée, contrôlé par empreintes
python data/scripts/download_cim10.py    # nomenclature CIM-10 de l'ATIH, téléchargée à l'exécution
bash scripts/reproduce_small.sh          # reconstruit le chiffre clé du TF-IDF (identique à 1e-9 près)
make check-fast && make test
```

Les entraînements LoRA demandent un GPU de 32 Go (RTX 5090, PyTorch cu128). `docs/COMMANDES.md` liste toutes les commandes.

## Données et licences

- **PARHAF** (Health Data Hub) : comptes rendus cliniques fictifs, CC BY 4.0 et Etalab 2.0. Les étiquettes sont
  le diagnostic du scénario, pas un codage hospitalier ; usages cliniques exclus par les conditions du corpus.
- **CIM-10** (ATIH) : sa licence interdit de redistribuer un dérivé ; elle est téléchargée à l'exécution, aucun fichier dérivé n'est versionné.
- **MorFITT** : CC BY-SA 4.0. Licences des dépendances : `docs/LICENCES.md`.

**Version publique** : deux dossiers ont été retirés de tout l'historique, les copies intégrales des articles
cités (`knowledge/raw/`, droits d'auteur) et l'archive d'une offre d'emploi (`docs/offre/`). Les pages du wiki
gardent leurs références ; la vérification des citations (`scripts/check_wiki_quotes.py`) demande ces copies en local.

## Méthode

Projet mené par une seule personne avec des agents de code, sous un protocole écrit (`AGENTS.md`, `CLAUDE.md`,
`CONSTRAINTS.md`) : fiches hachées avant chaque run, test scellé gardé par le code, revue indépendante, et une
porte `claim-gate` qui ne laisse sortir une affirmation qu'avec sa preuve.

Licence du code : pas encore choisie (tous droits réservés par défaut).

---
Cyril Bourgeois, Data Scientist et ingénieur ML ·
[Portfolio](https://cyril-bgs-dev-tech.github.io/Portfolio/) ·
[LinkedIn](https://www.linkedin.com/in/cyril-bourgeois-65a739150) ·
[Kaggle](https://www.kaggle.com/cyrilbourgeois)
