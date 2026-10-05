#!/usr/bin/env python3
"""Contexte statistique de l'audit du 03/10/2026 : largeur de l'intervalle apparié selon la taille d'évaluation et la métrique.

SIMULATION (aucun modèle, aucune donnée de patient) : deux modèles de même niveau (écart réel nul) partagent une difficulté latente
(corrélation rho) ; les erreurs vont vers une classe tirée selon la prévalence ; bootstrap stratifié par classe sur les patients
seuls (la variance entre graines s'y ajouterait). Les effectifs viennent de `results/measures/splits_summary.json`
(`classes` et `test_class_counts`) ; AUCUN n'est lu dans la partition scellée. Les largeurs sont des ORDRES DE GRANDEUR : les
corrélations d'erreurs réelles sont inconnues, RM-17 les mesure.
Mesures : largeur de l'IC à 98,33 % de (a) la macro-F1 sur 17 chapitres, (b) l'exactitude, (c) la macro-F1 restreinte aux chapitres
d'au moins 16 patients de test (12 chapitres), pour des évaluations de 629 patients (test), 2 869 (plis 1 à 4, effectifs
proportionnels) et 3 586 (développement entier, effectifs réels).
"""
import json
import sys
from math import erf, sqrt
from pathlib import Path

import numpy as np
from numpy.typing import NDArray

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))
from llmft.mini_registry import register_run

ROOT = Path(__file__).resolve().parents[2]
SEED, REPLICAS, DATASETS = 3, 200, 10
Z = 2.3940  # quantile normal à 98,33 % bilatéral
summary = json.loads((ROOT / "results/measures/splits_summary.json").read_text(encoding="utf-8"))
total = {k: v for k, v in summary["classes"].items() if k != "AUTRE"}
test = {k: v for k, v in summary["test_class_counts"].items() if k != "AUTRE"}
dev = {k: total[k] - test[k] for k in total}
names = list(total)
sizes = {
    "test_629": np.array([test[k] for k in names]),
    "plis_1_a_4_2869": np.array([max(3, round(dev[k] * 2869 / sum(dev.values()))) for k in names]),
    "dev_3586": np.array([dev[k] for k in names]),
}
big = np.array([test[k] >= 16 for k in names])  # chapitres retenus pour la macro-F1 restreinte
rng = np.random.default_rng(SEED)


def macro_f1(truth: NDArray[np.int_], pred: NDArray[np.int_], n_classes: int, keep: NDArray[np.bool_]) -> float:
    scores = []
    for c in range(n_classes):
        if not keep[c]:
            continue
        tp = ((truth == c) & (pred == c)).sum()
        fp = ((truth != c) & (pred == c)).sum()
        fn = ((truth == c) & (pred != c)).sum()
        d = 2 * tp + fp + fn
        scores.append(0.0 if d == 0 else 2 * tp / d)
    return float(np.mean(scores))


def draw_model(y: NDArray[np.int_], prev: NDArray[np.float64], shared: NDArray[np.float64], acc: float, rho: float) -> NDArray[np.int_]:
    """Un modèle simulé : correct si (rho x difficulté partagée + (1 - rho) x bruit propre) < exactitude visée."""
    n_classes = len(prev)
    ok = (rho * shared + (1 - rho) * rng.random(len(y))) < acc
    wrong = rng.choice(n_classes, size=len(y), p=prev)
    wrong = np.where(wrong == y, (wrong + 1) % n_classes, wrong)
    return np.where(ok, y, wrong)


def run_scenario(counts: NDArray[np.int_], acc: float, rho: float) -> list[float]:
    n_classes = len(counts)
    y = np.repeat(np.arange(n_classes), counts)
    prev = counts / counts.sum()
    idx = [np.where(y == c)[0] for c in range(n_classes)]
    keep_all = np.ones(n_classes, bool)
    w_macro: list[float] = []
    w_acc: list[float] = []
    w_big: list[float] = []
    for _ in range(DATASETS):
        shared = rng.random(len(y))
        a = draw_model(y, prev, shared, acc, rho)
        b = draw_model(y, prev, shared, acc, rho)
        d_macro: list[float] = []
        d_acc: list[float] = []
        d_big: list[float] = []
        for _ in range(REPLICAS):
            ix = np.concatenate([rng.choice(i, size=len(i)) for i in idx])
            yt, pa, pb = y[ix], a[ix], b[ix]
            d_macro.append(macro_f1(yt, pa, n_classes, keep_all) - macro_f1(yt, pb, n_classes, keep_all))
            d_acc.append(float((pa == yt).mean() - (pb == yt).mean()))
            d_big.append(macro_f1(yt, pa, n_classes, big) - macro_f1(yt, pb, n_classes, big))
        for store, d in ((w_macro, d_macro), (w_acc, d_acc), (w_big, d_big)):
            lo, hi = np.percentile(d, [0.8333, 99.1667])
            store.append(float(hi - lo))
    return [round(100 * float(np.mean(w)), 1) for w in (w_macro, w_acc, w_big)]


def cdf(x: float) -> float:
    return 0.5 * (1 + erf(x / sqrt(2)))


rows: list[dict[str, float | int | str]] = []
for size_name, counts in sizes.items():
    for acc, rho in [(0.6, 0.5), (0.6, 0.8), (0.8, 0.5), (0.8, 0.8)]:
        wm, wa, wb = run_scenario(counts, acc, rho)
        rows.append({"evaluation": size_name, "patients": int(counts.sum()), "target_accuracy": acc, "correlation": rho,
                     "width_macro_f1_17_points": wm, "width_accuracy_points": wa, "width_macro_f1_12_big_classes_points": wb})
# probabilité d'un verdict résolu : normale, sigma = largeur / (2 Z), règle d'ADR-007 (gain confirmé si L > delta, absence si U < delta)
prob = []
for width in (4.0, 6.0, 8.0, 10.0):
    sigma = width / (2 * Z)
    for gain in (0.0, 2.0, 3.0, 4.0, 5.0, 6.0):
        p_confirm = 1 - cdf((2.0 + width / 2 - gain) / sigma)
        p_absence = cdf((2.0 - width / 2 - gain) / sigma)
        prob.append({"ci_width_points": width, "true_gain_points": gain, "p_gain_confirmed": round(p_confirm, 3),
                     "p_no_useful_gain": round(p_absence, 3), "p_unresolved": round(1 - p_confirm - p_absence, 3)})
# taille nécessaire pour atteindre une largeur de 4 points si la largeur varie en 1/racine(n), depuis chaque scénario du test
need = [{"width_at_629": float(r["width_macro_f1_17_points"]), "patients_for_width_4": int(629 * (float(r["width_macro_f1_17_points"]) / 4) ** 2)}
        for r in rows if r["evaluation"] == "test_629"]
record = {
    "kind": "measure", "slug": "power-curves-audit", "status": "ok",
    "summary": "Simulation de contexte pour l'audit du 03/10/2026 : largeur de l'IC apparie a 98,33 % selon la taille d'evaluation (629, 2869, 3586) et la metrique (macro-F1 17, exactitude, macro-F1 12 grands chapitres) ; probabilite de verdict resolu ; taille necessaire pour 4 points ; ordres de grandeur, correlations inventees",
    "params": {"seed": SEED, "replicas": REPLICAS, "datasets": DATASETS, "z": Z, "sizes": {k: int(v.sum()) for k, v in sizes.items()}, "big_chapters": [n for n, b in zip(names, big, strict=True) if b]},
    "metrics": {"widths": rows, "verdict_probabilities": prob, "patients_needed_for_width_4_from_629": need},
}
print(json.dumps(record, ensure_ascii=False, indent=1))
if "--register" in sys.argv:
    print(register_run(ROOT / "results/runs", record))
