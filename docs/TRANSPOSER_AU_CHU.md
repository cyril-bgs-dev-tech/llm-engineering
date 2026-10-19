# Transposer la chaîne à une tâche du CHU (P5-07)

État au 17/10/2026. Ce guide dit comment porter la chaîne du projet sur une nouvelle tâche de classification de textes, par exemple une tâche du CHU Grenoble Alpes. **Il a été exécuté à blanc sur une tâche factice** : les trois blocs marqués « contrat-factice », « adaptateur-factice » et « chaine-factice » ci-dessous sont extraits et exécutés tels quels par `tests/test_transposer_guide.py` à chaque `make check`. Si le guide cesse de fonctionner, le contrôle échoue. La tâche factice est synthétique ; rien ici ne vaut validation sur des textes réels.

## 0. Ce qui ne se transpose pas sans décision humaine

- **Données réelles** : elles ne quittent jamais l'infrastructure du CHU et n'entrent jamais dans ce dépôt. Le cadre réglementaire applicable aux données de santé et l'autorisation du traitement s'établissent avec le délégué à la protection des données du CHU, avant toute ligne de code sur ces données.
- **Définition des classes** : avec les cliniciens ou le département d'information médicale ; chaque classe a un nom en clair, une définition opérationnelle et ses exclusions (étape 1).
- **Validation locale avant toute mise en service** : un changement d'auteurs (autres médecins, autre hôpital) fait perdre plusieurs points sans qu'aucun signal sans étiquette ne le voie (`docs/SURVEILLANCE_DERIVE.md`) ; les chiffres obtenus sur PARHAF ne se transportent pas.
- **Calcul** : aucune API payante ni location de GPU sans déclencheur écrit et plafond validé (règles du projet, `CLAUDE.md`).

## 1. Écrire le contrat de la tâche

Un fichier `task_specs/<task_id>.yaml`, validé par `llmft.taskspec` (classes fermées, nommées, définies ; format de sortie fixe ; métriques). Le code ne contient rien de propre à une tâche : tout vient du contrat et de l'adaptateur (`tests/test_transposability.py` vérifie que le noyau ne change pas d'un octet quand on ajoute une tâche). Exemple de la tâche factice, l'orientation d'un message de patient **fictif** vers trois files :

```yaml
# contrat-factice
task_id: orientation_message_factice
title: Orientation d'un message de patient fictif (tâche factice de l'exécution à blanc)
type: multiclass
input:
  unit: document
  max_tokens: 128
  truncation: head
classes:
- id: rendez_vous
  name: Demande de rendez-vous
  definition: Le message demande à prendre, déplacer ou annuler un rendez-vous.
  exclusions:
  - Une question sur un résultat posée à l'occasion d'un rendez-vous relève de resultats.
- id: resultats
  name: Question sur des résultats
  definition: Le message demande un résultat d'examen ou son explication.
  exclusions: []
- id: ordonnance
  name: Demande d'ordonnance
  definition: Le message demande le renouvellement ou la correction d'une ordonnance.
  exclusions: []
output:
  format: "{class_id}"
metrics:
  primary: macro_f1
  secondary: [accuracy, log_loss, ece]
```

## 2. Écrire l'adaptateur : le seul code propre à la tâche

Une classe dont la méthode `load()` rend un tableau à quatre colonnes : `id` (unique), `text`, `label` (un identifiant de classe du contrat) et `author` (qui a écrit le texte : il sert au découpage groupé et au contrôle du raccourci d'auteur). Sur des données réelles, l'adaptateur lit l'extraction préparée dans l'entrepôt du CHU ; ici il génère des messages fictifs :

```python
# adaptateur-factice
import pandas as pd


class OrientationAdapter:
    MOTIFS = {"rendez_vous": ["Je voudrais déplacer mon rendez-vous", "Pouvez-vous me donner un rendez-vous"],
              "resultats": ["Avez-vous reçu mes résultats de prise de sang", "Que signifie le résultat de mon examen"],
              "ordonnance": ["Mon ordonnance arrive à échéance", "Il manque un médicament sur mon ordonnance"]}

    def load(self) -> pd.DataFrame:
        rows = []
        for i in range(90):
            label = list(self.MOTIFS)[i % 3]
            text = f"{self.MOTIFS[label][(i // 3) % 2]}, message fictif numéro {i}."
            rows.append({"id": f"msg{i:03d}", "text": text, "label": label, "author": f"auteur{i % 9}"})
        return pd.DataFrame(rows)
```

## 3. Lancer la chaîne générique

`llmft.pipeline.run_chain` enchaîne le chargement validé par le contrat, le découpage (plis groupés, contrôle d'absence de fuite entre partitions), un entraînement court, les métriques du contrat et l'enregistrement au registre (un fichier JSON par run, jamais réécrit). Sur processeur, le modèle est un sac de mots haché : il sert à vérifier la chaîne, pas à mesurer une qualité. Avec `CONTRAT` le chemin du contrat et `RUNS` le dossier du registre (`results/runs` dans le projet) :

```python
# chaine-factice
from llmft import pipeline, taskspec

spec = taskspec.load_task_spec(CONTRAT)
record = pipeline.run_chain(spec, OrientationAdapter(), backend="cpu", steps=10, runs_dir=RUNS)
print(record["run_id"], record["metrics"])
```

## 4. Passer aux modèles du projet

| Brique | Générique (se réutilise telle quelle) | À adapter |
|---|---|---|
| Contrat, chargeur, découpage, chaîne, registre | `llmft.taskspec`, `llmft.loader`, `llmft.splits`, `llmft.pipeline`, `llmft.registry`, `llmft.mini_registry`, tampon de santé `llmft.machine_health` | rien |
| Références et modèles | `llmft.tfidf`, `llmft.lora_train`, `llmft.multilabel` (tête lue dans le contrat) | `scripts/p1_04_06_tfidf.py` et `scripts/p1_finetune.py` lisent PARHAF par `p1_04_06_tfidf.load` : remplacer ce chargement par l'adaptateur de la tâche |
| Comparaisons et verdicts | `llmft.paired`, `llmft.cluster_bootstrap` (blocs d'auteurs), verdict à trois valeurs (δ de `PROTOCOLE.md`) | δ et question primaire : nouvelle fiche préenregistrée |
| Incertitude | `llmft.calibration`, `llmft.conformal` (marginal, par classe, par famille ; propriétés testées par `tests/test_conformal_proprietes.py`) | familles de classes : définies avec le contrat |
| Service et surveillance | `llmft.serving`, `llmft.http_service`, `llmft.drift_monitor`, `scripts/serve_tfidf.py --reference`, `scripts/reference_prevalence.py` | seuils de dérive à remesurer sur la tâche (`scripts/simulate_drift.py` lit des fichiers de prédictions de PARHAF) |
| Système G et cascade | `llmft.service_g` | `scripts/bench_service_g.py` et `scripts/service_g_cascade.py` chargent les modèles gelés de PARHAF (ADR-016) |

## 5. Protocole : avant le premier chiffre

Dans l'ordre de `CLAUDE.md` : fiche du jeu et contrôle des données personnelles (`dataset-intake`), fiche préenregistrée hachée dans `experiments/INDEX.md` (`experiment-preregistration`), pré-vol de mémoire sur la carte (`vram-preflight`), tests de fuite (`leakage-guard`), test scellé à porte unique, comparaison appariée par blocs d'auteurs (`paired-comparison`), porte des affirmations avant toute sortie (`claim-gate`). Un chiffre sans identifiant de run n'existe pas ; un résultat négatif se publie au même rang qu'un positif.

## 6. Service et surveillance

Le service HTTP n'écoute que sur l'adresse donnée et ne journalise aucun texte ; avec un fichier de référence (`--reference`), il expose `GET /drift` (prévalence des classes prédites sur les 100 dernières prédictions). Les seuils mesurés sur PARHAF ne valent que pour PARHAF : les remesurer par simulation sur la tâche, prévoir un échantillon étiqueté périodique (environ 1 000 cas sur PARHAF pour voir un changement complet d'auteurs) et un retour arrière vers la version précédente identifiée par ses empreintes (`docs/SURVEILLANCE_DERIVE.md`).

## 7. Exécution à blanc du 17/10/2026

Les blocs des étapes 1 à 3 ont été exécutés tels quels sur la tâche factice, sur processeur : contrat validé, 90 messages fictifs, découpage sans fuite, run enregistré avec ses métriques (`tests/test_transposer_guide.py`, rejoué à chaque `make check`). **Limites** : la tâche factice est triviale et synthétique ; l'exécution à blanc prouve que le guide suffit à faire tourner la chaîne générique sur une nouvelle tâche, pas que les modèles du projet transposent leur qualité ; les scripts de la colonne « à adapter » n'ont pas été portés.
