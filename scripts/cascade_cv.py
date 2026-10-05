#!/usr/bin/env python3
"""Cascade par seuil de confiance, seuil choisi hors du pli évalué (RM-40, fiche 2026-10-04-cascade-cinq-plis).

Entrées : probabilités hors pli regroupées (cinq plis) du premier modèle, du LoRA et du TF-IDF. Pour chaque pli k : τ choisi sur les autres plis (`llmft.cascade.choose_threshold`, tolérance 1,0 point),
appliqué au pli k ; prédictions regroupées de la cascade comparées au LoRA seul.
Usage : cascade_cv.py PREMIER.probs.npz LORA.probs.npz SLUG [--register]   (développement seulement)"""
import json
import sys
from collections.abc import Callable
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent))
import p1_04_06_tfidf
from llmft.cascade import cascade_probs, choose_threshold
from llmft.mini_registry import register_run
from llmft.power_rule import _macro_f1, pooled_interval

GRID = (0.5, 0.6, 0.7, 0.8, 0.9, 0.95, 0.99)
TOLERANCE = 0.01
MS = {"tfidf": 1.9, "encodeur": 5 * 191.0, "lora": 117.0}


def main() -> int:
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    path_first, path_lora, slug = args
    _, y, folds, other, ids_all = p1_04_06_tfidf.load("chapter")
    truth_of = dict(zip(ids_all, y, strict=True))
    fold_of = dict(zip(ids_all, folds.tolist(), strict=True))
    zl = np.load(path_lora, allow_pickle=False)
    ids = [str(i) for i in zl["ids"]]
    labels = [str(c) for c in zl["labels"]]
    lora = zl["probs"].astype(np.float64)
    zf = np.load(path_first, allow_pickle=False)
    pos = {str(i): k for k, i in enumerate(zf["ids"])}
    first = zf["probs"].astype(np.float64)[[pos[i] for i in ids]]
    truth = np.array([labels.index(truth_of[i]) for i in ids])
    fold = np.array([fold_of[i] for i in ids])
    scored = [labels.index(c) for c in labels if c != other]

    def make_score(t: np.ndarray) -> Callable[[np.ndarray], float]:
        return lambda p: float(_macro_f1(t[None, :], p.argmax(1)[None, :], scored)[0])

    final = np.zeros_like(lora)
    kept = np.zeros(len(ids), dtype=bool)
    taus: dict[str, float | None] = {}
    for k in sorted(set(fold.tolist())):
        cal, ev = fold != k, fold == k
        tau = choose_threshold(first[cal], lora[cal], make_score(truth[cal]), GRID, TOLERANCE)
        taus[str(k)] = tau
        probs, keep = cascade_probs(first[ev], lora[ev], tau if tau is not None else 2.0)  # aucun seuil convenable : tout passe au LoRA
        final[ev], kept[ev] = probs, keep
    d, lo, hi = pooled_interval(truth, final.argmax(1), lora.argmax(1), scored)
    share = float(kept.mean())
    out = {"seuils_par_pli": taus, "part_traitee_par_le_premier": round(share, 3), "macro_f1_cascade": round(make_score(truth)(final), 4), "macro_f1_lora_seul": round(make_score(truth)(lora), 4),
           "cascade_moins_lora_points": round(d, 2), "ic95_points": [round(lo, 2), round(hi, 2)], "non_inferiorite": bool(lo > -2.0), "economie_50": bool(lo > -2.0 and share >= 0.5),
           "latence_moyenne_ms_modelisee": {"encodeur_puis_lora": round(MS["encodeur"] + (1 - share) * MS["lora"], 1), "lora_seul": MS["lora"]}, "n": len(ids)}
    print(json.dumps(out, indent=1))
    if "--register" in sys.argv:
        print(register_run(ROOT / "results/runs", {"kind": "measure", "slug": slug, "status": "ok", "summary": f"{slug} : cascade moins LoRA {out['cascade_moins_lora_points']} points {out['ic95_points']}, {share:.0%} des cas sans LoRA",
                                                    "params": {"grid": list(GRID), "tolerance": TOLERANCE}, "metrics": out}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
