#!/usr/bin/env python3
"""Variance comparée de trois métriques candidates avec un modèle de PROBABILITÉS simulé (aucune donnée de patient).

Question : la log loss moyennée par chapitre (chaque chapitre pèse pareil) a-t-elle un intervalle apparié plus étroit que la
macro-F1 sur le test réel (effectifs réels, 629 patients évalués) ? Le MCC multiclasse sert de point de repère (non équilibré
par classe). Deux modèles de même niveau (écart réel nul) partagent une difficulté latente (corrélation rho) ; chacun produit
des probabilités par softmax de logits = marge sur la bonne classe + bruit propre ; bootstrap stratifié par classe sur les patients
seuls (la variance entre graines s'y ajouterait). ORDRE DE GRANDEUR : les corrélations réelles sont inconnues.
Les trois métriques n'ont pas la même unité : on compare donc la largeur de l'intervalle à 98,33 % de la différence RAPPORTÉE à l'effet
que produit un vrai changement de compétence (de 2,0 à 2,5 unités de marge). Plus ce rapport est petit, plus la métrique sépare
un vrai écart du bruit d'échantillonnage.
"""
import json
import sys
from pathlib import Path
from typing import Any

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))
from llmft.mini_registry import register_run

ROOT = Path(__file__).resolve().parents[2]
SEED, REPLICAS, DATASETS = 5, 200, 10
test = {k: v for k, v in json.loads((ROOT / "results/measures/splits_summary.json").read_text(encoding="utf-8"))["test_class_counts"].items() if k != "AUTRE"}
counts = np.array(list(test.values()))
K = len(counts)
y = np.repeat(np.arange(K), counts)
idx = [np.where(y == c)[0] for c in range(K)]
rng = np.random.default_rng(SEED)


def probs(skill: float, rho: float, shared: np.ndarray) -> np.ndarray:
    """Softmax de logits : bonne classe relevée de `skill`, bruit partagé (rho) et propre (1 - rho) ; classes voisines non modélisées."""
    noise = np.sqrt(rho) * shared + np.sqrt(1 - rho) * rng.normal(size=(len(y), K))
    logits = noise.copy()
    logits[np.arange(len(y)), y] += skill
    e = np.exp(logits - logits.max(1, keepdims=True))
    return np.asarray(e / e.sum(1, keepdims=True))


def macro_f1(yt: np.ndarray, pred: np.ndarray) -> float:
    s = []
    for c in range(K):
        tp = ((yt == c) & (pred == c)).sum(); fp = ((yt != c) & (pred == c)).sum(); fn = ((yt == c) & (pred != c)).sum()
        d = 2 * tp + fp + fn
        s.append(0.0 if d == 0 else 2 * tp / d)
    return float(np.mean(s))


def class_balanced_logloss(yt: np.ndarray, p: np.ndarray) -> float:
    nll = -np.log(np.clip(p[np.arange(len(yt)), yt], 1e-12, 1.0))
    return float(np.mean([nll[yt == c].mean() for c in range(K) if (yt == c).any()]))


def mcc(yt: np.ndarray, pred: np.ndarray) -> float:
    cm = np.zeros((K, K))
    np.add.at(cm, (yt, pred), 1)
    t, p, c, s = cm.sum(1), cm.sum(0), np.trace(cm), cm.sum()
    den = np.sqrt((s**2 - (p**2).sum()) * (s**2 - (t**2).sum()))
    return float((c * s - (t * p).sum()) / den) if den > 0 else 0.0


def metrics(yt: np.ndarray, p: np.ndarray) -> dict[str, float]:
    pred = p.argmax(1)
    return {"macro_f1": 100 * macro_f1(yt, pred), "class_balanced_logloss": class_balanced_logloss(yt, p), "mcc": 100 * mcc(yt, pred)}


rows: list[dict[str, Any]] = []
for skill, rho in [(1.5, 0.5), (1.5, 0.8), (2.5, 0.5), (2.5, 0.8)]:
    widths: dict[str, list[float]] = {"macro_f1": [], "class_balanced_logloss": [], "mcc": []}
    levels = []
    for _ in range(DATASETS):
        shared = rng.normal(size=(len(y), K))
        a, b = probs(skill, rho, shared), probs(skill, rho, shared)
        levels.append(metrics(y, a))
        diffs: dict[str, list[float]] = {k: [] for k in widths}
        for _ in range(REPLICAS):
            ix = np.concatenate([rng.choice(i, size=len(i)) for i in idx])
            ma, mb = metrics(y[ix], a[ix]), metrics(y[ix], b[ix])
            for k, bucket in diffs.items():
                bucket.append(ma[k] - mb[k])
        for k, d in diffs.items():
            lo, hi = np.percentile(d, [0.8333, 99.1667])
            widths[k].append(float(hi - lo))
    ref = {k: float(np.mean([lv[k] for lv in levels])) for k in widths}
    # étendue de référence d'une métrique : écart entre ce niveau de compétence et un niveau inférieur d'une unité de marge (pour rendre les largeurs comparables)
    rows.append({"skill": skill, "rho": rho, "level": {k: round(v, 3) for k, v in ref.items()}, "width_98_33": {k: round(float(np.mean(w)), 3) for k, w in widths.items()}})
# échelle : sensibilité de chaque métrique à un changement de compétence de 0,5 (Δ attendu entre deux modèles réellement différents)
sens = {}
for skill in (1.5, 2.0, 2.5):
    shared = rng.normal(size=(len(y), K))
    sens[skill] = metrics(y, probs(skill, 0.5, shared))
delta = {k: round(sens[2.5][k] - sens[2.0][k], 3) for k in sens[2.5]}
for r in rows:
    r["width_over_effect_of_half_skill_unit"] = {k: round(r["width_98_33"][k] / abs(delta[k]), 3) for k in delta}
record = {"kind": "measure", "slug": "metric-widths-candidates", "status": "ok",
          "summary": "Largeur de l'intervalle apparié de la macro-F1, de la log loss moyennée par chapitre et du MCC, probabilités simulées, effectifs réels du test, rapportée à l'effet d'un changement de compétence de 0,5 ; ordre de grandeur, corrélations inventées",
          "params": {"seed": SEED, "replicas": REPLICAS, "datasets": DATASETS, "test_size": len(y)},
          "metrics": {"rows": rows, "effect_of_half_skill_unit": delta}}
print(json.dumps(record, ensure_ascii=False, indent=1))
if "--register" in sys.argv:
    print(register_run(ROOT / "results/runs", record))
