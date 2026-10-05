#!/usr/bin/env python3
"""Analyse de l'encodeur élagué (RM-45, fiche 2026-10-05-encodeur-elague) : (A) élagué seul contre encodeur complet non distillé ; (B) élagué distillé contre encodeur complet distillé (bras ensemble) ;
moyenne de trois graines par pli, prédictions regroupées, bootstrap d'auteurs ; verdict de la fiche (équivalent / dégradé / non résolu) ; latence lue dans results/measures/bench_pruned_latency.json.
Usage : prune_analysis.py [--register]"""
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
ARMS = {"A_elague_seul": ("prune-plain", lambda k: distill_analysis.baseline_names(k)), "B_elague_distille": ("prune-distill", lambda k: [f"distill-ens-pli{k}-s{s}" for s in range(3)])}


def macro(truth: np.ndarray, scored: list[int], p: np.ndarray) -> float:
    return round(float(_macro_f1(truth[None, :], p.argmax(1)[None, :], scored)[0]), 4)


def main() -> int:
    _, y, _, other, ids_all = p1_04_06_tfidf.load("chapter")
    truth_of = dict(zip(ids_all, y, strict=True))
    meta = pd.read_parquet(p1_04_06_tfidf.PARQUET, columns=["id", "author"])
    author_of = dict(zip(meta["id"].astype(str), meta["author"], strict=True))
    out: dict[str, object] = {}
    for arm, (prefix, base_names) in ARMS.items():
        ids_a: list[str] = []
        var_p, base_p = [], []
        labels: list[str] = []
        for k in range(5):
            v = distill_analysis.fold_mean([f"{prefix}-pli{k}-s{s}" for s in range(3)])
            b = distill_analysis.fold_mean(base_names(k))
            if v is None or b is None:
                continue
            ids, vp, labels = v
            pos = {i: j for j, i in enumerate(b[0])}
            ids_a += ids
            var_p.append(vp)
            base_p.append(b[1][[pos[i] for i in ids]])
        if not var_p:
            continue
        var, base = np.vstack(var_p), np.vstack(base_p)
        truth = np.array([labels.index(truth_of[i]) for i in ids_a])
        scored = [labels.index(c) for c in labels if c != other]
        groups = [author_of[i] for i in ids_a]
        d, lo, hi = cluster_interval(truth, var.argmax(1), base.argmax(1), scored, groups)
        verdict = "équivalent" if -DELTA <= lo and hi <= DELTA else ("dégradé" if hi < -DELTA else "non résolu")
        out[arm] = {"plis": len(var_p), "macro_f1_elague": macro(truth, scored, var), "macro_f1_reference_complet": macro(truth, scored, base), "difference_points": [round(d, 2), round(lo, 2), round(hi, 2)], "verdict": verdict}
        print(arm, out[arm], flush=True)
    lat = ROOT / "results/measures/bench_pruned_latency.json"
    if lat.exists():
        data = json.loads(lat.read_text(encoding="utf-8"))
        out["latence_ms_p50"] = {k: v["p50_ms"] for k, v in data.items()}
        out["acceleration"] = {tag: round(data[f"12 couches {tag}"]["p50_ms"] / data[f"6 couches {tag}"]["p50_ms"], 2) for tag in ("gpu_fp32", "gpu_bf16", "cpu_fp32") if f"6 couches {tag}" in data}
        print("latence", out["latence_ms_p50"], out["acceleration"], flush=True)
    (ROOT / "results/measures/prune_analysis.json").write_text(json.dumps(out, indent=1, ensure_ascii=False), encoding="utf-8")
    if "--register" in sys.argv:
        print(register_run(ROOT / "results/runs", {"kind": "measure", "slug": "encodeur-elague-analyse-cinq-plis", "status": "ok", "summary": "Encodeur élagué : équivalence et latence", "params": {"delta": DELTA}, "metrics": out}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
