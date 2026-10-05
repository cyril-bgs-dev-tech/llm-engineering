#!/usr/bin/env python3
"""Hypothèse de Cyril (04/10) : l'écart patient contre auteur vient en partie de la discrétisation des petites classes et de plis de validation inégaux.

1) Part de la variance bootstrap de la macro-F1 portée par chaque classe (prédictions hors pli du TF-IDF, plis par patient).
2) Écart patient contre auteur recalculé avec des partitions répétées : StratifiedKFold par patient contre StratifiedGroupKFold par auteur (classes réparties au mieux sous la contrainte de
groupe), trois graines de partition, configuration fixe C = 100, n-grammes (1, 2), TF-IDF, développement seulement, EXPLORE.
Usage : split_discretization_check.py [--register]"""
import json
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.model_selection import StratifiedGroupKFold, StratifiedKFold

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent))
import p1_04_06_tfidf
from llmft import tfidf
from llmft.mini_registry import register_run
from llmft.power_rule import _macro_f1


def main() -> int:
    texts, y, _, other, ids = p1_04_06_tfidf.load("chapter")
    meta = pd.read_parquet(p1_04_06_tfidf.PARQUET, columns=["id", "author"])
    author = dict(zip(meta["id"].astype(str), meta["author"], strict=True))
    groups = np.array([author[i] for i in ids])
    labels = sorted(set(y))
    t = np.array([labels.index(v) for v in y])
    scored = [labels.index(c) for c in labels if c != other]
    # 1) variance par classe de la macro-F1 (bootstrap stratifié sur les prédictions hors pli par patient)
    z = np.load(ROOT / "results/predictions/p1-06-tfidf-chapter.probs.npz", allow_pickle=False)
    pos = {str(i): k for k, i in enumerate(z["ids"])}
    pred = z["probs"][[pos[i] for i in ids]].argmax(1)
    rng = np.random.default_rng(20261004)
    reps = 2000
    f1 = np.zeros((reps, len(labels)))
    by_class = [np.flatnonzero(t == c) for c in range(len(labels))]
    idx = np.concatenate([rng.choice(ix, size=(reps, len(ix))) for ix in by_class], axis=1)
    tt, pp = t[idx], pred[idx]
    for c in range(len(labels)):
        tp = ((tt == c) & (pp == c)).sum(1)
        fp = ((tt != c) & (pp == c)).sum(1)
        fn = ((tt == c) & (pp != c)).sum(1)
        f1[:, c] = np.where(2 * tp + fp + fn > 0, 2 * tp / np.maximum(2 * tp + fp + fn, 1), 0)
    var_share = {labels[c]: float(f1[:, c].var() / sum(f1[:, k].var() for k in scored)) for c in scored}
    out = {"sd_macro_f1_bootstrap_points": round(float(100 * f1[:, scored].mean(1).std()), 2),
           "part_de_variance_par_classe": {k: round(v, 3) for k, v in sorted(var_share.items(), key=lambda kv: -kv[1])},
           "part_des_cinq_plus_petites_classes": round(sum(var_share[c] for c in ("IV", "V", "XII", "XXI", "XXII")), 3)}
    print(json.dumps(out, ensure_ascii=False))
    # 2) partitions répétées
    results = {"patient": [], "auteur": []}
    t0 = time.time()
    for seed in (1, 2, 3):
        for name in ("patient", "auteur"):
            splitter = StratifiedKFold(5, shuffle=True, random_state=seed) if name == "patient" else StratifiedGroupKFold(5, shuffle=True, random_state=seed)
            oof = np.zeros((len(y), len(labels)))
            for tr, te in splitter.split(np.zeros(len(y)), t, groups):
                oof[te] = tfidf.fit_predict_proba([texts[i] for i in tr], [y[i] for i in tr], [texts[i] for i in te], labels, 100.0, (1, 2))
            mf = float(_macro_f1(t[None, :], oof.argmax(1)[None, :], scored)[0])
            results[name].append(round(mf, 4))
            print(seed, name, round(mf, 4), round(time.time() - t0), "s", flush=True)
    gap = [p - a for p, a in zip(results["patient"], results["auteur"], strict=True)]
    out["partitions_repetees"] = {**results, "ecart_patient_moins_auteur_points": [round(100 * g, 2) for g in gap], "ecart_moyen_points": round(100 * float(np.mean(gap)), 2)}
    (ROOT / "results/measures/split_discretization_check.json").write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    print(json.dumps(out["partitions_repetees"]))
    if "--register" in sys.argv:
        print(register_run(ROOT / "results/runs", {"kind": "measure", "slug": "split-discretization-check", "status": "ok", "summary": f"Écart patient moins auteur sur partitions répétées : {out['partitions_repetees']['ecart_moyen_points']} points", "params": {"seeds": [1, 2, 3]}, "metrics": out}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
