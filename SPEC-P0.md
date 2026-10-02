# SPEC-P0 : spécification courte du socle (micro-tâche RM-04)

Statut : **brouillon à valider par Cyril** (02/10/2026). Il condense ce que `PLAN_PROJET_V6.md` (quoi et pourquoi), `MICROTACHES.md` (détail et preuves) et `roadmap_unifié.md` (ordre et portes) disent pour l'étape P0. En cas de désaccord, le plan gagne sur le quoi, la feuille de route sur l'ordre.

## 1. Objectif

Construire, sur une RTX 5090, une chaîne d'expériences **reproductible et honnête** pour affiner et distiller des LLM sur des comptes rendus cliniques français fictifs (corpus PARHAF), de façon que Cyril puisse dire vrai : « j'ai affiné et évalué un LLM, voici le protocole et les chiffres ». Cible : poste « Ingénieur.e Data Science » du CHU Grenoble Alpes (projet PARTAGES).

- **Utilisateur** : Cyril, qui n'avait jamais affiné de LLM ; le projet comble ce trou.
- **Succès du socle (P0)** : `make check` et `make smoke` verts ; tâche principale `parhaf_cim10_chapter` chargeable et partitionnée sans fuite ; protocole figé avant le premier run comparatif.
- **Ce que le projet n'est pas** : un outil clinique, un produit déployable, une preuve de performance sur de vrais comptes rendus (usages exclus par PARHAF).

## 2. Commandes canoniques

Voir `docs/COMMANDES.md` (statut « existe » ou « cible » de chaque commande). Résumé :

| Intention | Commande |
|---|---|
| Après chaque édition | `make check-fast` (types, lint, plancher, secrets, moins de 90 s) |
| Fin de tâche | `make check` (plus tests, couverture des lignes modifiées, backlog, feuille de route, wiki, citations, scorecards, règles) |
| Avant tout partage | `make check-full` (plus tests GPU, fil `make smoke`, audit des dépendances) |
| Régénérer `tasks/` | `python3 scripts/check_roadmap.py --export` |

Les sorties sont en UTF-8 (`PYTHONUTF8=1` côté Windows).

## 3. Structure

```
src/llmft/        noyau sans rien de propre à une tâche (taskspec, loader, splits, leakage, metrics, models, pipeline, registry, sealed, cim10)
src/llmft/adapters/   seul endroit où un code de tâche peut apparaître
task_specs/       contrats YAML générés par scripts/gen_task_contracts.py
data/             cards/, scripts/, manifests/, splits/ versionnés ; raw/ et processed/ ignorés
results/          runs/ (registre), measures/ (mesures versionnées), smoke_report.md
experiments/      INDEX.md des empreintes de gel
docs/             decisions/ (ADR), COMMANDES.md, LICENCES.md, offre/
knowledge/        wiki du projet (sources, méthodes, décisions)
scorecards/       G-P0 à G-P5 et TEMPLATE.md
tests/            tests ; GPU marqués `gpu`
```

## 4. Style de code

Python 3.12, types stricts sur `src/` (mypy), lint ruff, lignes de 110 caractères, identifiants en anglais, documentation et messages en français. Une fonction fait une chose et se teste par un cas piégé qui doit échouer. Exemple de l'esprit attendu :

```python
def check_out_of_fold(fold_of, teacher_trained_on) -> list[str]:
    """Le professeur qui a produit les probabilités de l'exemple i ne doit pas avoir vu le pli de i."""
    return [f"{i} : le professeur a vu le pli {f}" for i, f in fold_of.items() if f in teacher_trained_on[i]]
```

## 5. Tests

`pytest` ; chaque contrôle de fuite a un test réel et un test sur cas piégé ; deux variantes de la chaîne (`cpu` sans GPU, `gpu`). Couverture des lignes modifiées de `src/` à 80 % au moins ; couverture du paquet à ne pas laisser baisser (97 % le 02/10/2026).

## 6. Limites

**Toujours** : écrire le test avant le code ; `make check-fast` après chaque édition ; un `run_id` pour tout chiffre ; consigner les résultats négatifs ; relire la source avant de citer un chiffre ; charger les skills de l'étape (`roadmap_unifié.md`).

**Demander d'abord à Cyril** : tout commit, tout dépôt distant, tout partage, toute dépense (location de GPU, API payante), tout envoi de contenu vers un service externe (revue croisée Codex ou Gemini), toute modification de `CONSTRAINTS.md`, l'acceptation d'une licence, les décisions de la section 9 de la feuille de route.

**Jamais** : donnée de patient réel ; secret dans le dépôt ; nom de modèle, de classe ou de tâche dans le noyau ; relever un seuil pour faire passer un test ; ouvrir le test scellé hors de `llmft.sealed` ; écraser un run ou un fichier figé ; allégation clinique ; tiret cadratin dans un texte de candidature ; lire hors du dossier du projet sans l'accord de Cyril.

## 7. Critères de succès du socle (porte G-P0)

1. Données : PARHAF épinglé, empreintes, fiche, contrats, partitions sans fuite (fait au 02/10/2026).
2. Garde-fous : `make check` vert ; cas piégés détectés (fait).
3. Matériel : spikes PyTorch, LoRA, reprise, compatibilité des modèles, mémoire du plus gros professeur (spikes P0-04, P0-05, P0-13 faits ; P0-06 et P0-08 en cours).
4. Protocole : `PROTOCOLE.md` figé, budget par vague, estimand statistique (reste P0-45, RM-11, P0-46).
5. Scorecard G-P0 au plancher, une preuve par note (reste).

## 8. Questions ouvertes (pour Cyril)

1. Date limite de candidature et jalon visé (A, B, ou chemin complet) : jamais donnés ; ADR-002 suppose le jalon B en passant par A.
2. Validation de ce document, et premier commit (RM-03) : `git init` est fait, **aucun commit** n'a été créé.
3. Accord pour demander aux auteurs de PARHAF (action externe) l'accès au test embargoé et signaler l'écart entre le parquet et le JSON.
4. MedGemma : accepter ou non les conditions d'accès (ADR-001).
5. Valeurs de B, N et du seuil utile (voir `docs/decisions/` une fois l'ADR écrite).
