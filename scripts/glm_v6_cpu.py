#!/usr/bin/env python3
"""Quatre mesures sans GPU issues de l'audit GLM v6 (fiche 2026-10-05-audit-glm-v6-mesures-cpu) : A blocs d'auteurs, B empilement, C variance, D sous-ensembles d'usage.
Usage : glm_v6_cpu.py [--register]   (développement seulement ; un thread, priorité basse)"""
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent))
import p1_04_06_tfidf
from llmft.cluster_bootstrap import cluster_interval
from llmft.conformal import wilson
from llmft.mini_registry import register_run
from llmft.power_rule import _macro_f1, pooled_interval

P = ROOT / "results/predictions"
EPS = 1e-6


def load(name: str) -> tuple[list[str], np.ndarray, list[str]]:
    z = np.load(P / f"{name}.probs.npz", allow_pickle=False)
    return [str(i) for i in z["ids"]], z["probs"].astype(np.float64), [str(c) for c in z["labels"]]


def main() -> int:
    _, y, folds, other, ids_all = p1_04_06_tfidf.load("chapter")
    truth_of = dict(zip(ids_all, y, strict=True))
    fold_of = dict(zip(ids_all, folds.tolist(), strict=True))
    meta = pd.read_parquet(p1_04_06_tfidf.PARQUET, columns=["id", "author", "pool"])
    author_of = dict(zip(meta["id"].astype(str), meta["author"], strict=True))
    pool_of = dict(zip(meta["id"].astype(str), meta["pool"], strict=True))
    ids_e, enc, labels = load("cinq-plis-ensemble-encodeur5")
    pos_t = {i: k for k, i in enumerate(load("tfidf-variant-char-balanced")[0])}
    tf_all = load("tfidf-variant-char-balanced")[1]
    tf = tf_all[[pos_t[i] for i in ids_e]]
    truth = np.array([labels.index(truth_of[i]) for i in ids_e])
    scored = [labels.index(c) for c in labels if c != other]
    fold = np.array([fold_of[i] for i in ids_e])
    groups = [author_of[i] for i in ids_e]
    mix = 0.5 * enc + 0.5 * tf
    out: dict[str, object] = {"n": len(ids_e), "n_auteurs": len(set(groups))}

    # A. blocs d'auteurs
    a: dict[str, object] = {}
    for name, pa in (("ensemble_moins_tfidf", mix), ("encodeur_moins_tfidf", enc)):
        d, lo, hi = cluster_interval(truth, pa.argmax(1), tf.argmax(1), scored, groups)
        _, lop, hip = pooled_interval(truth, pa.argmax(1), tf.argmax(1), scored, level=0.95)
        _, lo2, hi2 = cluster_interval(truth, pa.argmax(1), tf.argmax(1), scored, groups, level=0.9833)
        _, lop2, hip2 = pooled_interval(truth, pa.argmax(1), tf.argmax(1), scored, level=0.9833)
        a[name] = {"difference": round(d, 2), "blocs_auteurs": [round(lo, 2), round(hi, 2), round(hi - lo, 2)], "patients": [round(lop, 2), round(hip, 2), round(hip - lop, 2)],
                   "blocs_auteurs_98_33": [round(lo2, 2), round(hi2, 2), round(hi2 - lo2, 2)], "patients_98_33": [round(lop2, 2), round(hip2, 2), round(hip2 - lop2, 2)]}
        print("A", name, a[name], flush=True)
    out["A_blocs_auteurs"] = a

    if "--only-a" in sys.argv:
        if "--register" in sys.argv:
            print(register_run(ROOT / "results/runs", {"kind": "measure", "slug": "glm-v6-blocs-auteurs-niveaux", "status": "ok", "summary": "Audit GLM v6, blocs d'auteurs aux niveaux 95 % et 98,33 %", "params": {"fiche": "2026-10-05-audit-glm-v6-mesures-cpu"}, "metrics": a}))
        return 0

    # B. empilement et décision, validation croisée par pli
    def macro(p: np.ndarray, t: np.ndarray) -> float:
        return float(_macro_f1(t[None, :], p.argmax(1)[None, :], scored)[0])

    pred = {"S0_50_50": np.zeros_like(mix), "S1_poids_global": np.zeros_like(mix), "S2_regression_logistique": np.zeros_like(mix), "S4_biais_par_classe": np.zeros_like(mix)}
    weights_chosen = {}
    for k in range(5):
        tr, te = fold != k, fold == k
        pred["S0_50_50"][te] = mix[te]
        grid = np.linspace(0, 1, 11)
        best_w = max(grid, key=lambda w: macro(w * enc[tr] + (1 - w) * tf[tr], truth[tr]))
        weights_chosen[str(k)] = round(float(best_w), 1)
        pred["S1_poids_global"][te] = best_w * enc[te] + (1 - best_w) * tf[te]
        x = np.hstack([np.log(enc + EPS), np.log(tf + EPS)])
        lr = LogisticRegression(C=0.1, max_iter=500, class_weight="balanced").fit(x[tr], truth[tr])
        probs = np.zeros((te.sum(), len(labels)))
        probs[:, lr.classes_] = lr.predict_proba(x[te])
        pred["S2_regression_logistique"][te] = probs
        logm = np.log(mix + EPS)
        bias = np.zeros(len(labels))
        for _ in range(3):
            for c in range(len(labels)):
                best_b, best_s = bias[c], macro(logm[tr] + bias, truth[tr])
                for b in (-1.0, -0.5, -0.25, 0.25, 0.5, 1.0):
                    trial = bias.copy()
                    trial[c] = bias[c] + b
                    s = macro(logm[tr] + trial, truth[tr])
                    if s > best_s + 1e-9:
                        best_b, best_s = trial[c], s
                bias[c] = best_b
        pred["S4_biais_par_classe"][te] = np.exp(logm[te] + bias)
        print("B pli", k, "poids", weights_chosen[str(k)], flush=True)
    b: dict[str, object] = {"poids_choisis_par_pli": weights_chosen}
    for name, p in pred.items():
        row: dict[str, object] = {"macro_f1": round(macro(p, truth), 4)}
        if name != "S0_50_50":
            d, lo, hi = cluster_interval(truth, p.argmax(1), pred["S0_50_50"].argmax(1), scored, groups)
            row["contre_S0_points"] = [round(d, 2), round(lo, 2), round(hi, 2)]
        b[name] = row
        print("B", name, row, flush=True)
    out["B_empilement"] = b

    # C. variance
    seeds = {0: ["camembert-recette-lr1e-4-ep10", *[f"camembert-graine-ep10-s{s}" for s in range(1, 5)]], **{k: [f"camembert-pli{k}-ep10-s{s}" for s in range(5)] for k in range(1, 5)}}
    m = np.zeros((5, 5))
    for k in range(5):
        for s, name in enumerate(seeds[k]):
            ids_s, ps, lab = load(name)
            t = np.array([lab.index(truth_of[i]) for i in ids_s])
            sc = [lab.index(c) for c in lab if c != other]
            m[k, s] = float(_macro_f1(t[None, :], ps.argmax(1)[None, :], sc)[0])
    grand = m.mean()
    ss_fold = 5 * ((m.mean(1) - grand) ** 2).sum()
    ss_seed = 5 * ((m.mean(0) - grand) ** 2).sum()
    ss_res = ((m - m.mean(1, keepdims=True) - m.mean(0, keepdims=True) + grand) ** 2).sum()
    ms_fold, ms_seed, ms_res = ss_fold / 4, ss_seed / 4, ss_res / 16
    comp = {"pli": max((ms_fold - ms_res) / 5, 0.0) ** 0.5, "graine": max((ms_seed - ms_res) / 5, 0.0) ** 0.5, "reste_interaction_et_noyau": ms_res**0.5}
    sd_points = {k: round(100 * v, 2) for k, v in comp.items()}
    out["C_variance"] = {"macro_f1_par_pli_et_graine": np.round(m, 4).tolist(), "ecarts_types_points": sd_points,
                         "ecart_type_entre_graines_par_pli_points": [round(100 * float(m[k].std(ddof=1)), 2) for k in range(5)]}
    print("C", sd_points, flush=True)

    # D. sous-ensembles d'usage
    d_out: dict[str, object] = {}
    pools = np.array([pool_of[i] for i in ids_e])
    for pname in sorted(set(pools), key=lambda s: -(pools == s).sum()):
        sel = pools == pname
        row = {"n": int(sel.sum())}
        for sysname, p in (("ensemble", mix), ("encodeur", enc), ("tfidf", tf)):
            hits = int((p[sel].argmax(1) == truth[sel]).sum())
            lo, hi = wilson(hits, int(sel.sum()))
            row[sysname] = {"exactitude": round(hits / sel.sum(), 3), "wilson95": [round(lo, 3), round(hi, 3)], "macro_f1": round(macro(p[sel], truth[sel]), 3)}
        d_out[str(pname)] = row
        print("D", pname, row["n"], row["ensemble"], flush=True)
    out["D_sous_ensembles"] = d_out
    (ROOT / "results/measures/glm_v6_cpu.json").write_text(json.dumps(out, indent=1, ensure_ascii=False), encoding="utf-8")
    if "--register" in sys.argv:
        for key, slug in (("A_blocs_auteurs", "glm-v6-blocs-auteurs"), ("B_empilement", "glm-v6-empilement"), ("C_variance", "glm-v6-variance"), ("D_sous_ensembles", "glm-v6-par-pool")):
            print(register_run(ROOT / "results/runs", {"kind": "measure", "slug": slug, "status": "ok", "summary": f"Audit GLM v6, mesure {key}", "params": {"fiche": "2026-10-05-audit-glm-v6-mesures-cpu"}, "metrics": out[key]}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
