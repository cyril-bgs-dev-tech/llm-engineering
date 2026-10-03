---
title: Contrats des modules du chemin court (registre, test scellé, métriques, budget)
category: Méthodes
summary: Ce que garantit chaque module critique (entrées, sorties, erreurs, invariants) et le test qui le prouve, pour un relecteur externe
tags: [modules, contrats, registre, test-scelle, metriques]
sources: [code-llmft]
created: 2026-10-03
updated: 2026-10-03
---

# Contrats des modules du chemin court

## Registre de runs (`src/llmft/mini_registry.py`)
`register_run(runs_dir, record)` écrit `<run_id>.json` une seule fois et renvoie le chemin. Champs obligatoires et statuts fermés ; slug en minuscules, chiffres, tiret et tiret bas ; ouverture en mode exclusif, donc jamais d'écrasement. Un identifiant généré qui existe déjà (même seconde) reçoit un suffixe `-2`, `-3` ; un identifiant fourni qui existe déjà est une erreur.[^1] Un chiffre sans `run_id` n'existe pas dans `RESULTATS.md`.

## Porte du test scellé (`src/llmft/sealed.py`)
Deux temps. Temps A (`sealed_inputs`) : identifiants et textes, aucune étiquette, aucun marqueur. Temps B (`sealed_labels_and_score`) : vérifie que les prédictions couvrent exactement les identifiants du test, écrit le marqueur avant de lire les étiquettes, calcule, écrit le résultat par remplacement atomique ; une panne après le marqueur laisse le test consommé sans résultat (`ConsumedWithoutResultError`) et aucune seconde ouverture n'est possible (`AlreadyOpenedError`). Toute opération peut être consignée dans le journal des accès (opération, date, nombre d'identifiants, jamais de contenu).[^2]

## Métriques gelées (`src/llmft/metrics.py`, copie gelée dans `experiments/frozen/metrics.py`)
`macro_f1(y_true, y_pred, labels)` : moyenne arithmétique des F1 par classe sur les classes données ; `accuracy`, `log_loss`, `ece` (probabilités et indices de classes). Le contrôle `check_frozen.py` refuse toute dérive entre la copie gelée et le code.[^3]

## Budget (`src/llmft/budget.py`)
`consumed_hours(runs_dir)` additionne `seconds_train` et `seconds_tokenize` des runs du registre ; `alert(hours)` vaut vrai à 80 % de B = 90 h.[^4]

## Règle de puissance (`src/llmft/power_rule.py`)
`pair_widths` : une largeur par paire de graines, un seul flux PCG64 de graine 20261002, tirage stratifié aux effectifs du test, percentile à 98,33 % ; `mean_width` renvoie `None` (règle échouée) avec moins de trois graines. Vérifié contre une réplique scikit-learn.[^5]

[^1]: src/llmft/mini_registry.py [synthesis] — `_validate`, `register_run`, mode d'ouverture exclusif
[^2]: src/llmft/sealed.py [synthesis] — `sealed_inputs`, `sealed_labels_and_score`, `log_access`
[^3]: src/llmft/metrics.py [synthesis] — fonctions publiques de métriques
[^4]: src/llmft/budget.py [synthesis] — `consumed_hours`, `alert`
[^5]: tests/test_power_rule.py [synthesis] — réplique scikit-learn du calcul des largeurs
