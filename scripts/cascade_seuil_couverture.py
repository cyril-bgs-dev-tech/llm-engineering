#!/usr/bin/env python3
"""Couverture conforme par région de la cascade à seuil de probabilité (RM-43 suite, fiche 2026-10-05-cascade-seuil-couverture), développement seulement.

Pour chaque pli k : seuil choisi sur les autres plis ; quantiles LAC par famille calibrés région par région sur les autres plis ; couverture sur le pli k.
Usage : cascade_seuil_couverture.py PREMIER.probs.npz LORA.probs.npz SLUG [--register]"""
import json
import sys
from collections.abc import Callable
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent))
import glm_v3_families
import p1_04_06_tfidf
from llmft import conformal
from llmft.cascade import cascade_probs, choose_threshold
from llmft.mini_registry import register_run
from llmft.power_rule import _macro_f1

ALPHA = 0.10
GRID = (0.5, 0.6, 0.7, 0.8, 0.9, 0.95, 0.99)
TOLERANCE = 0.01


def region(sets: list[set[int]], y: np.ndarray) -> dict[str, float | list[float] | int]:
    hit = int(sum(int(t) in s for s, t in zip(sets, y, strict=True)))
    lo, hi = conformal.wilson(hit, len(y)) if len(y) else (0.0, 0.0)
    return {"n": len(y), "couverture": round(hit / len(y), 4) if len(y) else 0.0, "wilson95": [round(lo, 4), round(hi, 4)],
            "taille_moyenne": round(float(np.mean([len(s) for s in sets])), 3) if sets else 0.0}


def main() -> int:
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    path_first, path_lora, slug = args
    _, y_all, folds_all, other, ids_all = p1_04_06_tfidf.load("chapter")
    truth_of = dict(zip(ids_all, y_all, strict=True))
    fold_of = dict(zip(ids_all, folds_all.tolist(), strict=True))
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
    fam_names = list(glm_v3_families.FAMILIES)
    fam_of_label = {c: fam_names.index(n) for n, cs in glm_v3_families.FAMILIES.items() for c in cs}
    group_of = {k: fam_of_label[labels[k]] for k in range(len(labels))}

    def score(t: np.ndarray) -> Callable[[np.ndarray], float]:
        return lambda p: float(_macro_f1(t[None, :], p.argmax(1)[None, :], scored)[0])

    kept = np.zeros(len(ids), dtype=bool)
    sets: list[set[int]] = [set() for _ in ids]
    taus: dict[str, float | None] = {}
    for k in sorted(set(fold.tolist())):
        cal, ev = np.flatnonzero(fold != k), np.flatnonzero(fold == k)
        tau = choose_threshold(first[cal], lora[cal], score(truth[cal]), GRID, TOLERANCE)
        taus[str(k)] = tau
        t = tau if tau is not None else 2.0
        _, keep_cal = cascade_probs(first[cal], lora[cal], t)
        _, keep_ev = cascade_probs(first[ev], lora[ev], t)
        kept[ev] = keep_ev
        for model, region_cal, region_ev in ((first, cal[keep_cal], ev[keep_ev]), (lora, cal[~keep_cal], ev[~keep_ev])):
            q = conformal.fit_by_group(model[region_cal], truth[region_cal], group_of, ALPHA, "lac")
            for i, s in zip(region_ev, conformal.predict_sets_by_group(model[region_ev], q, group_of, "lac"), strict=True):
                sets[i] = s
    idx_first, idx_lora = np.flatnonzero(kept), np.flatnonzero(~kept)
    out = {"seuils_par_pli": taus, "part_traitee_par_le_premier": round(float(kept.mean()), 3), "region_encodeur": region([sets[i] for i in idx_first], truth[idx_first]),
           "region_lora": region([sets[i] for i in idx_lora], truth[idx_lora]), "globale": region(sets, truth), "niveau_cible": 1 - ALPHA, "n": len(ids)}
    print(json.dumps(out, indent=1))
    if "--register" in sys.argv:
        print(register_run(ROOT / "results/runs", {"kind": "measure", "slug": slug, "status": "ok", "summary": f"{slug} : couverture {out['globale']['couverture']} globale, région LoRA {out['region_lora']['couverture']}",
                                                    "params": {"alpha": ALPHA, "grid": list(GRID), "tolerance": TOLERANCE}, "metrics": out}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
