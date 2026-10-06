#!/usr/bin/env python3
"""Analyse de l'encodeur élagué (RM-45, fiche 2026-10-05-encodeur-elague) : moyenne de trois graines par pli, prédictions regroupées sur les cinq plis, différences par bootstrap d'auteurs.

(a) élagué sans distillation moins complet non distillé ; (b) élagué distillé moins complet distillé (même professeur, réserve de second ordre de la fiche : voir RM-56) ;
(c) élagué distillé moins complet non distillé (prédiction de la fiche). Verdicts : « équivalent » si l'IC tient dans ±δ, « dégradé » si la borne haute est sous −δ, sinon « non résolu ».
Usage : prune_analysis.py [--register]. Développement seulement, aucune étiquette du test scellé."""
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent))
import distill_analysis
import p1_04_06_tfidf
from llmft.cluster_bootstrap import cluster_interval
from llmft.mini_registry import register_run
from llmft.power_rule import _macro_f1

DELTA = 2.0
ARMS = {
    "plain": lambda k: [f"prune-plain-pli{k}-s{s}" for s in range(3)],
    "distill": lambda k: [f"prune-distill-pli{k}-s{s}" for s in range(3)],
    "full": distill_analysis.baseline_names,
    "full_distill": lambda k: [f"distill-ens-pli{k}-s{s}" for s in range(3)],
}
COMPARISONS = (("a_elague_contre_complet", "plain", "full"), ("b_elague_distille_contre_complet_distille", "distill", "full_distill"), ("c_elague_distille_contre_complet", "distill", "full"))


def verdict(lo: float, hi: float) -> str:
    return "équivalent" if -DELTA <= lo and hi <= DELTA else ("dégradé" if hi < -DELTA else "non résolu")


def main() -> int:
    _, y, _, other, ids_all = p1_04_06_tfidf.load("chapter")
    truth_of = dict(zip(ids_all, y, strict=True))
    meta = pd.read_parquet(p1_04_06_tfidf.PARQUET, columns=["id", "author"])
    author_of = dict(zip(meta["id"].astype(str), meta["author"], strict=True))
    pooled: dict[str, list[np.ndarray]] = {arm: [] for arm in ARMS}
    ids_f: list[str] = []
    labels: list[str] = []
    for k in range(5):
        folds = {arm: distill_analysis.fold_mean(fn(k)) for arm, fn in ARMS.items()}
        loaded = {arm: v for arm, v in folds.items() if v is not None}
        if len(loaded) != len(ARMS):
            raise SystemExit(f"pli {k} : prédictions manquantes")
        ref_ids, _, labels = loaded["plain"]
        ids_f += ref_ids
        for arm, (ids, p, _) in loaded.items():
            pos = {i: j for j, i in enumerate(ids)}
            pooled[arm].append(p[[pos[i] for i in ref_ids]])
    probs = {arm: np.vstack(parts) for arm, parts in pooled.items()}
    truth = np.array([labels.index(truth_of[i]) for i in ids_f])
    scored = [labels.index(c) for c in labels if c != other]
    groups = [author_of[i] for i in ids_f]
    out: dict[str, object] = {"n_patients": len(ids_f), "macro_f1_regroupee": {arm: round(float(_macro_f1(truth[None, :], p.argmax(1)[None, :], scored)[0]), 4) for arm, p in probs.items()}}
    for name, var, ref in COMPARISONS:
        d, lo, hi = cluster_interval(truth, probs[var].argmax(1), probs[ref].argmax(1), scored, groups)
        out[name] = {"difference_points": [round(d, 2), round(lo, 2), round(hi, 2)], "verdict": verdict(lo, hi)}
        print(name, out[name], flush=True)
    print(out["macro_f1_regroupee"], flush=True)
    (ROOT / "results/measures/prune_analysis.json").write_text(json.dumps(out, indent=1, ensure_ascii=False), encoding="utf-8")
    if "--register" in sys.argv:
        print(register_run(ROOT / "results/runs", {"kind": "measure", "slug": "encodeur-elague-analyse-cinq-plis", "status": "ok", "summary": "Encodeur élagué à six couches : différences par blocs d'auteurs avec l'encodeur complet, cinq plis", "params": {"delta": DELTA, "fiche": "experiments/2026-10-05-encodeur-elague.md"}, "metrics": out}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
