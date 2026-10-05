#!/usr/bin/env python3
"""Esquisse de puissance (avant RM-15) : largeur de l'intervalle apparié sur le test scellé, avec des prédictions SIMULÉES.

Aucun modèle, aucune donnée de patient : seuls les effectifs RÉELS du test par classe (`test_class_counts` de `results/measures/splits_summary.json`) servent ; AUCUN n'est lu dans la partition scellée.
Deux « modèles » de même exactitude (écart réel nul) partagent une difficulté latente (corrélation rho) ; les erreurs vont vers
une classe tirée selon la prévalence. Bootstrap stratifié par classe sur les patients seulement (la variance entre graines
s'y ajouterait : la largeur est donc une borne basse). Ce n'est PAS la mesure de RM-15, qui utilisera les prédictions réelles.
"""
import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))
from llmft.mini_registry import register_run

ROOT = Path(__file__).resolve().parents[2]
SEED, REPLICAS, DATASETS = 1, 300, 25
rng = np.random.default_rng(SEED)
classes = {k: v for k, v in json.loads((ROOT / "results/measures/splits_summary.json").read_text(encoding="utf-8"))["test_class_counts"].items() if k != "AUTRE"}
n = np.array(list(classes.values()))
n_classes = len(n)
y = np.repeat(np.arange(n_classes), n)
total = len(y)
prev = n / n.sum()
idx_by_class = [np.where(y == c)[0] for c in range(n_classes)]


def macro_f1(truth: np.ndarray, pred: np.ndarray) -> float:
    scores = []
    for c in range(n_classes):
        tp = ((truth == c) & (pred == c)).sum()
        fp = ((truth != c) & (pred == c)).sum()
        fn = ((truth == c) & (pred != c)).sum()
        denom = 2 * tp + fp + fn
        scores.append(0.0 if denom == 0 else 2 * tp / denom)
    return float(np.mean(scores))


def simulate(acc: float, rho: float) -> tuple[np.ndarray, np.ndarray]:
    shared = rng.random(total)

    def one_model() -> np.ndarray:
        correct = (rho * shared + (1 - rho) * rng.random(total)) < acc
        wrong = rng.choice(n_classes, size=total, p=prev)
        wrong = np.where(wrong == y, (wrong + 1) % n_classes, wrong)
        return np.where(correct, y, wrong)

    return one_model(), one_model()


rows = []
for acc, rho in [(0.6, 0.5), (0.6, 0.8), (0.8, 0.5), (0.8, 0.8)]:
    widths, f1s = [], []
    for _ in range(DATASETS):
        a, b = simulate(acc, rho)
        f1s.append(macro_f1(y, a))
        diffs = []
        for _ in range(REPLICAS):
            ix = np.concatenate([rng.choice(ii, size=len(ii)) for ii in idx_by_class])
            diffs.append(macro_f1(y[ix], a[ix]) - macro_f1(y[ix], b[ix]))
        lo, hi = np.percentile(diffs, [100 * 0.05 / 3 / 2, 100 - 100 * 0.05 / 3 / 2])
        widths.append(float(hi - lo))
    rows.append({"target_accuracy": acc, "correlation": rho, "macro_f1_mean": round(float(np.mean(f1s)), 3),
                 "ci_width_points_mean": round(100 * float(np.mean(widths)), 1),
                 "ci_width_points_min": round(100 * min(widths), 1), "ci_width_points_max": round(100 * max(widths), 1)})
record = {
    "kind": "measure", "slug": "power-sketch-ic-width-v2", "status": "ok",
    "summary": "Esquisse simulée : largeur de l'IC apparié à 98,33 % de la différence de macro-F1 sur le test réel de 629 patients évalués (effectifs réels par classe, AUCUN lu dans la partition : comptes de make_splits ; prédictions simulées, écart réel nul), à comparer à 2 x delta = 4 points ; borne basse, hors variance entre graines ; ne remplace pas RM-15",
    "params": {"seed": SEED, "replicas": REPLICAS, "datasets": DATASETS, "test_size": int(total), "test_counts": n.tolist(), "delta_points": 2.0, "power_rule_max_width_points": 4.0},
    "metrics": {"scenarios": rows},
}
print(json.dumps(record, ensure_ascii=False, indent=1))
if "--register" in sys.argv:
    print(register_run(ROOT / "results/runs", record))
