#!/usr/bin/env python3
"""P1-02 / ADR-007 point 7 : caractéristiques opératoires SIMULÉES de l'intervalle hiérarchique de `llmft.paired` sur les effectifs réels du test.

Aucun modèle, aucune donnée de patient : deux recettes simulées (K = 5 graines chacune, modèles indépendants entre graines, difficulté latente partagée
de corrélation rho) ; la VRAIE différence de macro-F1 est calée à 0, δ = 2 et 4 points par un grand échantillon (effectifs x 30, 30 modèles par recette).
Pour chaque vraie différence : sur N jeux de la taille du test, couverture de l'intervalle à 98,33 %, largeur moyenne, et fréquence de chacun des trois
verdicts d'ADR-007 (donc la fausse confirmation à Δ = δ et la puissance réelle, sans approximation normale). Ordre de grandeur : corrélations inventées."""
import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))
from llmft import paired
from llmft.mini_registry import register_run

ROOT = Path(__file__).resolve().parents[2]
SEED, N_SETS, R, K_SEEDS, RHO, ACC_A, DELTA = 7, 300, 2000, 5, 0.5, 0.70, 2.0
test = {k: v for k, v in json.loads((ROOT / "results/measures/splits_summary.json").read_text(encoding="utf-8"))["test_class_counts"].items() if k != "AUTRE"}
counts = np.array(list(test.values()))
K = len(counts)
rng = np.random.default_rng(SEED)


def model(y: np.ndarray, prev: np.ndarray, shared: np.ndarray, acc: float) -> np.ndarray:
    ok = (RHO * shared + (1 - RHO) * rng.random(len(y))) < acc
    wrong = rng.choice(K, size=len(y), p=prev)
    wrong = np.where(wrong == y, (wrong + 1) % K, wrong)
    return np.where(ok, y, wrong)


def macro_f1(y: np.ndarray, p: np.ndarray) -> float:
    cm = np.bincount(y * K + p, minlength=K * K).reshape(K, K)
    tp = np.diag(cm).astype(float)
    denom = 2 * tp + (cm.sum(0) - tp) + (cm.sum(1) - tp)
    return float(np.mean(np.where(denom > 0, 2 * tp / np.maximum(denom, 1), 0.0)))


def population_gap(acc_b: float) -> float:
    big = counts * 30
    y = np.repeat(np.arange(K), big)
    prev = counts / counts.sum()
    shared = rng.random(len(y))
    fa = np.mean([macro_f1(y, model(y, prev, shared, ACC_A)) for _ in range(30)])
    fb = np.mean([macro_f1(y, model(y, prev, shared, acc_b)) for _ in range(30)])
    return 100 * float(fa - fb)


def calibrate(target: float) -> float:
    if target == 0.0:
        return ACC_A
    lo, hi = ACC_A - 0.3, ACC_A
    for _ in range(14):
        mid = (lo + hi) / 2
        if population_gap(mid) > target:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2


y = np.repeat(np.arange(K), counts)
prev = counts / counts.sum()
level = paired.bonferroni_level(3)
rows = []
for target in (0.0, DELTA, 4.0):
    acc_b = calibrate(target)
    true_gap = float(np.mean([population_gap(acc_b) for _ in range(3)]))
    cover, verdicts, widths = 0, {"gain confirmé": 0, "absence de gain utile": 0, "non résolu": 0}, []
    for _ in range(N_SETS):
        shared = rng.random(len(y))
        a = np.stack([model(y, prev, shared, ACC_A) for _ in range(K_SEEDS)])
        b = np.stack([model(y, prev, shared, acc_b) for _ in range(K_SEEDS)])
        r = paired.hierarchical_bootstrap(y, a, b, K, scored=list(range(K)), n_boot=R, level=level, rng=rng)
        lo, hi = 100 * r.lo, 100 * r.hi
        cover += lo <= true_gap <= hi
        verdicts[paired.verdict(lo, hi, DELTA)] += 1
        widths.append(hi - lo)
    rows.append({"target_gap_points": target, "calibrated_acc_b": round(acc_b, 4), "true_gap_points": round(true_gap, 2), "coverage": round(cover / N_SETS, 3),
                 "mean_width_points": round(float(np.mean(widths)), 2), "verdict_frequencies": {k: round(v / N_SETS, 3) for k, v in verdicts.items()}})
    print(rows[-1], flush=True)
record = {"kind": "measure", "slug": "coverage-hierarchical-interval", "status": "ok",
          "summary": "Caractéristiques opératoires simulées de l'intervalle hiérarchique (llmft.paired) à 98,33 % sur les effectifs réels du test : couverture, largeur et fréquences des trois verdicts pour une vraie différence de 0, 2 et 4 points ; corrélations inventées, ordre de grandeur",
          "params": {"seed": SEED, "n_sets": N_SETS, "n_boot": R, "seeds_per_recipe": K_SEEDS, "rho": RHO, "acc_a": ACC_A, "delta": DELTA, "level": level, "test_size": int(counts.sum())},
          "metrics": {"rows": rows}}
if "--register" in sys.argv:
    print(register_run(ROOT / "results/runs", record))
print(json.dumps(record, ensure_ascii=False, indent=1))
