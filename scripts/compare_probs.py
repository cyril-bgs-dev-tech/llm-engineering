#!/usr/bin/env python3
"""Différence appariée de macro-F1 de plusieurs fichiers de probabilités (.probs.npz) contre une référence, sur les patients communs.

Bootstrap stratifié par chapitre, même tirage pour tous, 5 000 répliques, PCG64 graine 20261004 ; IC 95 % non ajusté et p bootstrap ajustées par Holm.
Usage : compare_probs.py REF.npz VARIANTE.npz [VARIANTE.npz ...] SLUG [--register]"""
import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent))
import p1_04_06_tfidf
from llmft.mini_registry import register_run
from llmft.paired import holm_adjust
from llmft.power_rule import _macro_f1


def main() -> int:
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    ref, variants, slug = args[0], args[1:-1], args[-1]
    _, y, _, other, ids = p1_04_06_tfidf.load("chapter")
    truth = dict(zip(ids, y, strict=True))
    z = np.load(ref, allow_pickle=False)
    labels = [str(c) for c in z["labels"]]
    order = [str(i) for i in z["ids"]]
    probs = {Path(ref).name: z["probs"]}
    for v in variants:
        zv = np.load(v, allow_pickle=False)
        pos = {str(i): k for k, i in enumerate(zv["ids"])}
        order = [i for i in order if i in pos]
        probs[Path(v).name] = (zv, pos)
    pos_ref = {str(i): k for k, i in enumerate(z["ids"])}
    t = np.array([labels.index(truth[i]) for i in order])
    base = z["probs"][[pos_ref[i] for i in order]].argmax(1)
    scored = [labels.index(c) for c in labels if c != other]
    rng = np.random.default_rng(20261004)
    idx = np.concatenate([rng.choice(ix, size=(5000, len(ix))) for ix in (np.flatnonzero(t == c) for c in range(len(labels))) if len(ix)], axis=1)
    f_base = _macro_f1(t[idx], base[idx], scored)
    rows, pvals = [], []
    for v in variants:
        zv, pos = probs[Path(v).name]
        pred = zv["probs"][[pos[i] for i in order]].argmax(1)
        d = _macro_f1(t[idx], pred[idx], scored) - f_base
        p = float(min(1.0, 2 * min((d <= 0).mean(), (d >= 0).mean())))
        pvals.append(p)
        rows.append({"variante": Path(v).name, "macro_f1": round(float(_macro_f1(t[None, :], pred[None, :], scored)[0]), 4), "delta_points": round(float(100 * d.mean()), 2),
                     "ic95_points": [round(float(100 * np.percentile(d, 2.5)), 2), round(float(100 * np.percentile(d, 97.5)), 2)], "p_bootstrap": round(p, 4)})
    for r, adj in zip(rows, holm_adjust(np.array(pvals)), strict=True):
        r["p_holm"] = round(float(adj), 4)
    out = {"reference": Path(ref).name, "macro_f1_reference": round(float(_macro_f1(t[None, :], base[None, :], scored)[0]), 4), "n": len(order), "comparaisons": rows}
    print(json.dumps(out, ensure_ascii=False, indent=1))
    if "--register" in sys.argv:
        print(register_run(ROOT / "results/runs", {"kind": "measure", "slug": slug, "status": "ok", "summary": f"Comparaison appariée de {len(variants)} variantes contre {Path(ref).name}", "params": {"ref": Path(ref).name}, "metrics": out}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
