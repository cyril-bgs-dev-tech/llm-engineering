#!/usr/bin/env python3
"""P0-30 : raccourci d'auteur. Règle et seuil figés dans PROTOCOLE.md section 3 (empreinte dans experiments/INDEX.md).

Modèle « auteur seul » contre modèle « spécialité seule » (même modèle : variables indicatrices + régression logistique,
poids de classe équilibrés, choix d'implémentation fixé avant la mesure), macro-F1 au niveau chapitre sur les plis stratifiés
de développement, prédictions hors pli regroupées. Signalé si la différence atteint 3 points avec une borne basse à 95 %
(bootstrap par patient, 1 000 tirages, appariés) strictement positive.
"""
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import f1_score
from sklearn.preprocessing import OneHotEncoder

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from llmft import cim10, splits

SEED = 20261002
THRESHOLD = 0.03
N_BOOT = 1000


def macro_f1(y: np.ndarray, p: np.ndarray, labels: list[str]) -> float:
    return float(f1_score(y, p, labels=labels, average="macro", zero_division=0))


def oof_predictions(x: np.ndarray, y: np.ndarray, folds: list[np.ndarray]) -> np.ndarray:
    pred = np.empty(len(y), dtype=object)
    for held in folds:
        train = np.setdiff1d(np.arange(len(y)), held)
        model = LogisticRegression(max_iter=2000, class_weight="balanced")
        model.fit(x[train], y[train])
        pred[held] = model.predict(x[held])
    return pred


def main() -> int:
    split = json.loads((ROOT / "data/splits/parhaf_cim10_chapter.json").read_text(encoding="utf-8"))
    df = pd.read_parquet(ROOT / "data/raw/parhaf/data/train-00000-of-00001.parquet", columns=["id", "author", "specialty", "suggested_scenario"])
    h = cim10.load_claml(ROOT / "data/raw/cim10/cim10fr2019.xml")
    df["chapter"] = df["suggested_scenario"].map(lambda s: (h.lookup(s["primary_diagnosis"]["code"][0]) or cim10.Hierarchy("?", "?", (), "?", "")).chapter)
    work = df[df["id"].isin({i for f in split["folds"] for i in f})].copy()
    work["label"] = splits.apply_rare_class_policy(work["chapter"].where(work["chapter"] != "?"))
    labels = sorted(c for c in work["label"].unique() if c != "AUTRE")
    index = {pid: k for k, pid in enumerate(work["id"])}
    y = work["label"].to_numpy()
    strat = [np.array([index[i] for i in f]) for f in split["folds"]]
    control = [np.array([index[i] for i in f]) for f in split["control_folds_by_author"]]

    def design(col: str) -> np.ndarray:
        return OneHotEncoder(handle_unknown="ignore").fit_transform(work[[col]]).toarray()

    x_author, x_spec = design("author"), design("specialty")
    out: dict[str, object] = {"n": len(work), "n_classes_scored": len(labels), "protocol_threshold_points": THRESHOLD * 100}
    rng = np.random.default_rng(SEED)
    for name, folds in [("stratified_folds", strat), ("control_folds_by_author", control)]:
        pa, ps = oof_predictions(x_author, y, folds), oof_predictions(x_spec, y, folds)
        majority = np.full(len(y), pd.Series(y).value_counts().index[0], dtype=object)
        fa, fs, fm = macro_f1(y, pa, labels), macro_f1(y, ps, labels), macro_f1(y, majority, labels)
        diffs = []
        for _ in range(N_BOOT):
            b = rng.integers(0, len(y), len(y))
            diffs.append(macro_f1(y[b], pa[b], labels) - macro_f1(y[b], ps[b], labels))
        lo, hi = np.percentile(diffs, [2.5, 97.5])
        out[name] = {
            "macro_f1_author_only": round(fa, 4), "macro_f1_specialty_only": round(fs, 4), "macro_f1_majority": round(fm, 4),
            "accuracy_author_only": round(float((pa == y).mean()), 4), "accuracy_specialty_only": round(float((ps == y).mean()), 4),
            "diff_author_minus_specialty": round(fa - fs, 4), "diff_ci95": [round(float(lo), 4), round(float(hi), 4)],
        }
    s = out["stratified_folds"]
    assert isinstance(s, dict)
    out["shortcut_flagged"] = bool(s["diff_author_minus_specialty"] >= THRESHOLD and s["diff_ci95"][0] > 0)
    (ROOT / "results/measures/author_shortcut.json").write_text(json.dumps(out, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(json.dumps(out, ensure_ascii=False, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
