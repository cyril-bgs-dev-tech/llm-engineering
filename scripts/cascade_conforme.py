#!/usr/bin/env python3
"""Cascade routée par la taille de l'ensemble conforme du premier modèle (RM-43, fiche 2026-10-05-cascade-conforme), développement seulement.

Pour chaque pli k : quantiles LAC par famille (Mondrian) du premier modèle calibrés sur les autres plis ; le premier répond si son ensemble contient une seule classe, sinon le cas passe au
LoRA, dont les quantiles par famille sont calibrés sur les cas escaladés des autres plis. Rapporte la macro-F1 contre le LoRA seul et contre la cascade à seuil, la couverture par région.
Usage : cascade_conforme.py PREMIER.probs.npz LORA.probs.npz SLUG [--register]"""
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
from llmft.cascade import cascade_probs, choose_threshold, route_by_set_size
from llmft.mini_registry import register_run
from llmft.power_rule import _macro_f1, pooled_interval

ALPHA = 0.10
GRID = (0.5, 0.6, 0.7, 0.8, 0.9, 0.95, 0.99)
TOLERANCE = 0.01
ENCODER_MS, LORA_MS = 5 * 4.3, 61.3  # encodeur bf16 sur GPU (cinq graines), LoRA fusionné bf16 (RESULTATS, reprises de service)


def region_coverage(sets: list[set[int]], y: np.ndarray) -> dict[str, float | list[float] | int]:
    hit = int(sum(int(t) in s for s, t in zip(sets, y, strict=True)))
    lo, hi = conformal.wilson(hit, len(y)) if len(y) else (0.0, 0.0)
    return {"n": len(y), "couverture": round(hit / len(y), 4) if len(y) else 0.0, "wilson95": [round(lo, 4), round(hi, 4)]}


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

    conf_final = np.zeros_like(lora)
    thr_final = np.zeros_like(lora)
    kept = np.zeros(len(ids), dtype=bool)
    thr_kept = np.zeros(len(ids), dtype=bool)
    sets_first: list[set[int]] = [set() for _ in ids]
    sets_lora: list[set[int]] = [set() for _ in ids]
    for k in sorted(set(fold.tolist())):
        cal, ev = np.flatnonzero(fold != k), np.flatnonzero(fold == k)
        q1 = conformal.fit_by_group(first[cal], truth[cal], group_of, ALPHA, "lac")
        s_cal = conformal.predict_sets_by_group(first[cal], q1, group_of, "lac")
        s_ev = conformal.predict_sets_by_group(first[ev], q1, group_of, "lac")
        _, keep_cal = route_by_set_size(s_cal, first[cal], lora[cal])
        esc_cal = cal[~keep_cal]
        q2 = conformal.fit_by_group(lora[esc_cal], truth[esc_cal], group_of, ALPHA, "lac")
        probs, keep = route_by_set_size(s_ev, first[ev], lora[ev])
        conf_final[ev], kept[ev] = probs, keep
        for i, s in zip(ev, s_ev, strict=True):
            sets_first[i] = s
        esc_ev = ev[~keep]
        for i, s in zip(esc_ev, conformal.predict_sets_by_group(lora[esc_ev], q2, group_of, "lac"), strict=True):
            sets_lora[i] = s
        tau = choose_threshold(first[cal], lora[cal], score(truth[cal]), GRID, TOLERANCE)
        thr_final[ev], thr_kept[ev] = cascade_probs(first[ev], lora[ev], tau if tau is not None else 2.0)
    d_lora, lo_l, hi_l = pooled_interval(truth, conf_final.argmax(1), lora.argmax(1), scored)
    d_thr, lo_t, hi_t = pooled_interval(truth, conf_final.argmax(1), thr_final.argmax(1), scored)
    share = float(kept.mean())
    idx_first, idx_lora = np.flatnonzero(kept), np.flatnonzero(~kept)
    final_sets = [sets_first[i] if kept[i] else sets_lora[i] for i in range(len(ids))]
    out = {
        "macro_f1_cascade_conforme": round(score(truth)(conf_final), 4), "macro_f1_lora_seul": round(score(truth)(lora), 4), "macro_f1_cascade_seuil": round(score(truth)(thr_final), 4),
        "cascade_conforme_moins_lora_points": round(d_lora, 2), "ic95_vs_lora": [round(lo_l, 2), round(hi_l, 2)], "non_inferiorite": bool(lo_l > -2.0),
        "part_traitee_par_le_premier": round(share, 3), "part_traitee_par_le_premier_cascade_seuil": round(float(thr_kept.mean()), 3), "economie_50": bool(lo_l > -2.0 and share >= 0.5),
        "cascade_conforme_moins_cascade_seuil_points": round(d_thr, 2), "ic95_vs_seuil": [round(lo_t, 2), round(hi_t, 2)],
        "couverture_region_premier": region_coverage([sets_first[i] for i in idx_first], truth[idx_first]), "couverture_region_lora": region_coverage([sets_lora[i] for i in idx_lora], truth[idx_lora]),
        "couverture_globale": region_coverage(final_sets, truth), "niveau_cible": 1 - ALPHA,
        "latence_moyenne_ms_modelisee": {"cascade_conforme": round(ENCODER_MS + (1 - share) * LORA_MS, 1), "lora_seul": LORA_MS}, "n": len(ids),
    }
    print(json.dumps(out, indent=1))
    if "--register" in sys.argv:
        print(register_run(ROOT / "results/runs", {"kind": "measure", "slug": slug, "status": "ok", "summary": f"{slug} : cascade conforme moins LoRA {out['cascade_conforme_moins_lora_points']} points {out['ic95_vs_lora']}, {share:.0%} des cas sans LoRA",
                                                    "params": {"alpha": ALPHA, "grid": list(GRID), "tolerance": TOLERANCE}, "metrics": out}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
