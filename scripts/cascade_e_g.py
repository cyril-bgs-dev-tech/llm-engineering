#!/usr/bin/env python3
"""Cascade E puis G (RM-60, fiche 2026-10-17-cascade-e-puis-g, EXPLORE, développement) : E répond quand sa probabilité maximale atteint τ, sinon G complet.
τ choisi pour chaque pli sur les quatre autres (`llmft.cascade.choose_threshold_by_agreement`, fidélité à G d'au moins 98 %), cascade regroupée comparée à G et à E
par bootstrap d'auteurs ; calcul fait deux fois (`agree_twice`) ; tampon de santé de la machine au registre (RM-59).
Usage : cascade_e_g.py [--register]"""
import json
import sys
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent))
import p1_04_06_tfidf
from llmft import machine_health
from llmft.cascade import cascade_probs, choose_threshold_by_agreement
from llmft.cluster_bootstrap import cluster_interval
from llmft.mini_registry import register_run
from llmft.power_rule import _macro_f1
from llmft.resilience import agree_twice

P = ROOT / "results/predictions"
FIRST, SECOND = "cinq-plis-ensemble-encodeur5-tfidf-charbal", "cinq-plis-ensemble-g"
GRID = (0.5, 0.6, 0.7, 0.8, 0.9, 0.95, 0.99)
MIN_AGREEMENT = 0.98
DELTA = 2.0
E_MS, LORA_MS, G_MS = 28.8, 61.0, 91.6  # étages mesurés, run 20261007-094117-service-g-bout-en-bout-gpu (premier passage, médianes)


def load(name: str) -> tuple[list[str], np.ndarray, list[str]]:
    z = np.load(P / f"{name}.probs.npz", allow_pickle=False)
    return [str(i) for i in z["ids"]], z["probs"].astype(np.float64), [str(c) for c in z["labels"]]


def compute() -> dict[str, Any]:
    _, y, folds, other, ids_all = p1_04_06_tfidf.load("chapter")
    truth_of = dict(zip(ids_all, y, strict=True))
    fold_of = dict(zip(ids_all, folds.tolist(), strict=True))
    meta = pd.read_parquet(p1_04_06_tfidf.PARQUET, columns=["id", "author"])
    author_of = dict(zip(meta["id"].astype(str), meta["author"], strict=True))
    ids, g, labels = load(SECOND)
    ids_e, e_raw, labels_e = load(FIRST)
    if labels_e != labels:
        raise ValueError("classes de E et de G dans des ordres différents")
    pos = {x: k for k, x in enumerate(ids_e)}
    e = e_raw[[pos[x] for x in ids]]
    truth = np.array([labels.index(truth_of[i]) for i in ids])
    fold = np.array([fold_of[i] for i in ids])
    groups = [author_of[i] for i in ids]
    scored = [labels.index(c) for c in labels if c != other]

    def mf1(p: np.ndarray) -> float:
        return float(_macro_f1(truth[None, :], p.argmax(1)[None, :], scored)[0])

    final = np.zeros_like(g)
    kept = np.zeros(len(ids), dtype=bool)
    taus: dict[str, float | None] = {}
    for k in sorted(set(fold.tolist())):
        cal, ev = fold != k, fold == k
        tau = choose_threshold_by_agreement(e[cal], g[cal], GRID, MIN_AGREEMENT)
        taus[str(k)] = tau
        probs, keep = cascade_probs(e[ev], g[ev], tau if tau is not None else 2.0)  # aucun seuil convenable : tout le pli passe à G
        final[ev], kept[ev] = probs, keep
    d_g, lo_g, hi_g = cluster_interval(truth, final.argmax(1), g.argmax(1), scored, groups)
    d_e, lo_e, hi_e = cluster_interval(truth, final.argmax(1), e.argmax(1), scored, groups)
    share = float(kept.mean())
    if lo_g > -DELTA and share >= 0.5:
        label = "cascade retenue"
    elif lo_g > -DELTA:
        label = "non inférieure mais peu économe"
    else:
        label = "non retenue"
    curve = []
    for tau in GRID:
        p, keep = cascade_probs(e, g, tau)
        curve.append({"tau": tau, "part_sans_lora": round(float(keep.mean()), 4), "macro_f1": round(mf1(p), 4), "fidelite_a_g": round(float((p.argmax(1) == g.argmax(1)).mean()), 4)})
    return {"seuils_par_pli": taus, "part_sans_lora": round(share, 4), "fidelite_a_g": round(float((final.argmax(1) == g.argmax(1)).mean()), 4),
            "macro_f1": {"cascade": round(mf1(final), 4), "g": round(mf1(g), 4), "e": round(mf1(e), 4)},
            "cascade_moins_g_points": round(d_g, 2), "ic95_contre_g": [round(lo_g, 2), round(hi_g, 2)],
            "cascade_moins_e_points": round(d_e, 2), "ic95_contre_e": [round(lo_e, 2), round(hi_e, 2)],
            "latence_moyenne_ms_modelisee": round(E_MS + (1 - share) * LORA_MS, 1), "latence_g_mesuree_ms": G_MS, "verdict": label,
            "courbe_descriptive_sur_tous_les_plis": curve, "n": len(ids), "delta_points": DELTA, "fidelite_minimale": MIN_AGREEMENT}


def main() -> int:
    start = machine_health.snapshot()
    out = agree_twice(compute, equal=lambda a, b: json.dumps(a, sort_keys=True) == json.dumps(b, sort_keys=True))
    print(json.dumps(out, indent=1, ensure_ascii=False))
    if "--register" in sys.argv:
        print(register_run(ROOT / "results/runs", {"kind": "measure", "slug": "cascade-e-puis-g", "status": "ok",
                                                    "summary": f"Cascade E puis G : {out['verdict']}, cascade moins G {out['cascade_moins_g_points']} points {out['ic95_contre_g']}, {out['part_sans_lora']:.0%} sans LoRA",
                                                    "params": {"fiche": "experiments/2026-10-17-cascade-e-puis-g.md", "premier": FIRST, "second": SECOND, "grid": list(GRID), "fidelite_minimale": MIN_AGREEMENT, "calcul_double": True},
                                                    "metrics": out, "machine_health": machine_health.stamp(start)}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
