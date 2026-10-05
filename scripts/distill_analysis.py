#!/usr/bin/env python3
"""Analyse de la distillation vers l'encodeur (RM-32, fiche 2026-10-05-distillation-vers-encodeur) : moyenne des trois graines par pli, prédictions regroupées sur les plis disponibles,
différence avec l'encodeur non distillé (mêmes graines 1000 à 1002) et avec le professeur, bootstrap par blocs d'auteurs ; verdict de la fiche (gain confirmé si borne basse > 0 et différence >= delta).
Usage : distill_analysis.py [--register]"""
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent))
import p1_04_06_tfidf
from llmft.cluster_bootstrap import cluster_interval
from llmft.mini_registry import register_run
from llmft.power_rule import _macro_f1

P = ROOT / "results/predictions"
DELTA = 2.0


def load(name: str) -> tuple[list[str], np.ndarray, list[str]]:
    z = np.load(P / f"{name}.probs.npz", allow_pickle=False)
    return [str(i) for i in z["ids"]], z["probs"].astype(np.float64), [str(c) for c in z["labels"]]


def baseline_names(fold: int) -> list[str]:
    return ["camembert-recette-lr1e-4-ep10", "camembert-graine-ep10-s1", "camembert-graine-ep10-s2"] if fold == 0 else [f"camembert-pli{fold}-ep10-s{s}" for s in range(3)]


def fold_mean(names: list[str]) -> tuple[list[str], np.ndarray, list[str]] | None:
    if not all((P / f"{n}.probs.npz").exists() for n in names):
        return None
    loaded = [load(n) for n in names]
    ids = loaded[0][0]
    pos = [{i: k for k, i in enumerate(x[0])} for x in loaded]
    probs = np.mean([x[1][[p[i] for i in ids]] for x, p in zip(loaded, pos, strict=True)], axis=0)
    return ids, probs, loaded[0][2]


def main() -> int:
    _, y, _, other, ids_all = p1_04_06_tfidf.load("chapter")
    truth_of = dict(zip(ids_all, y, strict=True))
    meta = pd.read_parquet(p1_04_06_tfidf.PARQUET, columns=["id", "author"])
    author_of = dict(zip(meta["id"].astype(str), meta["author"], strict=True))
    out: dict[str, object] = {}
    teachers = {"lora": "cinq-plis-llm-mur", "ens": "cinq-plis-ensemble-encodeur5-tfidf-charbal", "nested": "cinq-plis-ensemble-encodeur5-tfidf-charbal"}  # nested : professeur de référence = ensemble non imbriqué
    kept: dict[str, tuple[list[str], np.ndarray, np.ndarray, list[int], list[str]]] = {}
    for arm in ("lora", "ens", "nested"):
        folds_ok, ids_all_arm, dist_p, base_p = [], [], [], []
        labels: list[str] = []
        for k in range(5):
            d = fold_mean([f"distill-{arm}-pli{k}-s{s}" for s in range(3)])
            b = fold_mean(baseline_names(k))
            if d is None or b is None:
                continue
            ids, dp, labels = d
            pos = {i: j for j, i in enumerate(b[0])}
            ids_all_arm += ids
            dist_p.append(dp)
            base_p.append(b[1][[pos[i] for i in ids]])
            folds_ok.append(k)
        if not folds_ok:
            continue
        dist, base = np.vstack(dist_p), np.vstack(base_p)
        truth = np.array([labels.index(truth_of[i]) for i in ids_all_arm])
        scored = [labels.index(c) for c in labels if c != other]
        groups = [author_of[i] for i in ids_all_arm]
        t_ids, t_probs, _ = load(teachers[arm])
        tpos = {i: j for j, i in enumerate(t_ids)}
        teacher = t_probs[[tpos[i] for i in ids_all_arm]]

        def f1(p: np.ndarray, truth: np.ndarray = truth, scored: list[int] = scored) -> float:
            return round(float(_macro_f1(truth[None, :], p.argmax(1)[None, :], scored)[0]), 4)

        d_b, lo_b, hi_b = cluster_interval(truth, dist.argmax(1), base.argmax(1), scored, groups)
        d_t, lo_t, hi_t = cluster_interval(truth, dist.argmax(1), teacher.argmax(1), scored, groups)
        prior = np.array([sum(1 for v in y if v == c) for c in labels], dtype=float)
        prior = prior / prior.sum()

        def acc(p: np.ndarray, truth: np.ndarray = truth) -> float:
            return round(float((p.argmax(1) == truth).mean()), 4)

        def nll(p: np.ndarray, truth: np.ndarray = truth) -> float:
            return round(float(-np.log(np.clip(p[np.arange(len(truth)), truth], 1e-12, 1)).mean()), 4)

        verdict = "gain confirmé" if lo_b > 0 and d_b >= DELTA else ("sans gain" if -DELTA <= lo_b and hi_b <= DELTA else "non résolu")
        kept[arm] = (ids_all_arm, dist, truth, scored, groups)
        np.savez(P / f"cinq-plis-distill-{arm}-3graines.probs.npz", ids=np.array(ids_all_arm), probs=dist, labels=np.array(labels))
        out[arm] = {"plis": folds_ok, "n": len(ids_all_arm), "macro_f1_distille": f1(dist), "macro_f1_non_distille": f1(base), "macro_f1_professeur": f1(teacher),
                    "distille_moins_non_distille": [round(d_b, 2), round(lo_b, 2), round(hi_b, 2)], "distille_moins_professeur": [round(d_t, 2), round(lo_t, 2), round(hi_t, 2)], "verdict_fiche": verdict,
                    "exactitude": {"distille": acc(dist), "non_distille": acc(base), "professeur": acc(teacher)}, "log_loss": {"distille": nll(dist), "non_distille": nll(base), "professeur": nll(teacher)},
                    "macro_f1_apres_correction_de_priorite": {"distille": f1(dist / prior), "non_distille": f1(base / prior), "professeur": f1(teacher / prior)}}
        print(arm, out[arm], flush=True)
    if "ens" in kept and "nested" in kept and kept["ens"][0] == kept["nested"][0]:
        _, dist_e, truth_e, scored_e, groups_e = kept["ens"]
        d_n, lo_n, hi_n = cluster_interval(truth_e, kept["nested"][1].argmax(1), dist_e.argmax(1), scored_e, groups_e)
        out["nested_moins_ens_non_imbrique_points"] = [round(d_n, 2), round(lo_n, 2), round(hi_n, 2)]
        print("imbriqué moins non imbriqué", out["nested_moins_ens_non_imbrique_points"], flush=True)
    (ROOT / "results/measures/distill_analysis.json").write_text(json.dumps(out, indent=1, ensure_ascii=False), encoding="utf-8")
    if "--register" in sys.argv:
        print(register_run(ROOT / "results/runs", {"kind": "measure", "slug": "distillation-analyse-cinq-plis", "status": "ok", "summary": "Distillation vers l'encodeur : moyenne de trois graines, regroupée, blocs d'auteurs", "params": {"delta": DELTA}, "metrics": out}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
