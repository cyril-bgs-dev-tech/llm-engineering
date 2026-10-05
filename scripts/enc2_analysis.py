#!/usr/bin/env python3
"""Analyse de la recette d'encodeur v2 (RM-41 encodeur, RM-55, fiche 2026-10-05-encodeur-recette-v2) : par facteur, moyenne de trois graines par pli, prédictions regroupées, différence avec l'encodeur
non distillé fp32 (mêmes graines) par bootstrap d'auteurs, verdict de la fiche, durée et énergie moyennes par run. Usage : enc2_analysis.py [--register]"""
import glob
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
FACTORS = ("bf16", "ls01", "ema99", "curr2")


def run_metrics(slug: str) -> dict[str, float | None]:
    files = sorted(glob.glob(str(ROOT / f"results/runs/*-{slug}.json")))
    d = json.loads(Path(files[-1]).read_text(encoding="utf-8"))
    m = d.get("metrics", {})
    return {"macro_f1": m.get("macro_f1"), "seconds": m.get("seconds_train"), "wh": (m.get("energie") or {}).get("energie_wh")}


def macro(truth: np.ndarray, scored: list[int], p: np.ndarray) -> float:
    return round(float(_macro_f1(truth[None, :], p.argmax(1)[None, :], scored)[0]), 4)


def main() -> int:
    _, y, _, other, ids_all = p1_04_06_tfidf.load("chapter")
    truth_of = dict(zip(ids_all, y, strict=True))
    meta = pd.read_parquet(p1_04_06_tfidf.PARQUET, columns=["id", "author"])
    author_of = dict(zip(meta["id"].astype(str), meta["author"], strict=True))
    out: dict[str, object] = {}
    for factor in FACTORS:
        ids_f: list[str] = []
        var_p, base_p = [], []
        labels: list[str] = []
        seconds, whs, singles = [], [], []
        for k in range(5):
            names = [f"enc2-{factor}-pli{k}-s{s}" for s in range(3)]
            v = distill_analysis.fold_mean(names)
            b = distill_analysis.fold_mean(distill_analysis.baseline_names(k))
            if v is None or b is None:
                continue
            ids, vp, labels = v
            pos = {i: j for j, i in enumerate(b[0])}
            ids_f += ids
            var_p.append(vp)
            base_p.append(b[1][[pos[i] for i in ids]])
            for n in names:
                rm = run_metrics(n)
                seconds.append(rm["seconds"])
                whs.append(rm["wh"])
                singles.append(rm["macro_f1"])
        if not var_p:
            continue
        var, base = np.vstack(var_p), np.vstack(base_p)
        truth = np.array([labels.index(truth_of[i]) for i in ids_f])
        scored = [labels.index(c) for c in labels if c != other]
        groups = [author_of[i] for i in ids_f]
        d, lo, hi = cluster_interval(truth, var.argmax(1), base.argmax(1), scored, groups)
        if factor == "bf16":
            verdict = "équivalent" if -DELTA <= lo and hi <= DELTA else ("dégradé" if hi < -DELTA else "non résolu")
        else:
            verdict = "gain confirmé" if lo > 0 and d >= DELTA else ("sans gain" if -DELTA <= lo and hi <= DELTA else "non résolu")
        out[factor] = {"plis": len(var_p), "macro_f1_variante": macro(truth, scored, var), "macro_f1_reference": macro(truth, scored, base), "difference_points": [round(d, 2), round(lo, 2), round(hi, 2)], "verdict": verdict,
                       "macro_f1_par_run_moyenne": round(float(np.mean([s for s in singles if s is not None])), 4), "ecart_type_par_run": round(float(np.std([s for s in singles if s is not None], ddof=1)), 4),
                       "secondes_par_run": round(float(np.mean([s for s in seconds if s is not None])), 1), "wh_par_run": round(float(np.mean([w for w in whs if w is not None])), 2) if any(w is not None for w in whs) else None}
        print(factor, out[factor], flush=True)
    (ROOT / "results/measures/enc2_analysis.json").write_text(json.dumps(out, indent=1, ensure_ascii=False), encoding="utf-8")
    if "--register" in sys.argv:
        print(register_run(ROOT / "results/runs", {"kind": "measure", "slug": "encodeur-v2-analyse-cinq-plis", "status": "ok", "summary": "Recette d'encodeur v2 : un tableau par facteur, blocs d'auteurs", "params": {"delta": DELTA}, "metrics": out}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
