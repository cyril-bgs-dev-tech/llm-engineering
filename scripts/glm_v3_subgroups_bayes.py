#!/usr/bin/env python3
"""Audit GLM v3, C8-A3 et C2-A8 : performance par sous-groupe (spécialité, longueur, volume de l'auteur) et lecture bayésienne EXPLORE de l'écart 9B contre TF-IDF.

Pli 0, développement seulement, agrégats seulement. La lecture bayésienne (probabilité que l'écart dépasse δ) est complémentaire, jamais décisionnelle."""
import json
import sys
from collections import Counter
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent))
import p1_04_06_tfidf
from llmft.power_rule import _macro_f1

PREDS = {"tfidf": "p1-06-tfidf-chapter", "qwen3.5-9b-1e-4": "p1-11-qwen3-5-9b-lr1e-4"}
DELTA = 0.02


def main() -> int:
    texts, y, folds, other, ids = p1_04_06_tfidf.load("chapter")
    meta = pd.read_parquet(p1_04_06_tfidf.PARQUET, columns=["id", "specialty", "author"])
    meta["id"] = meta["id"].astype(str)
    meta = meta.set_index("id")
    labels = sorted(set(y))
    pool = [i for i, g in zip(ids, folds, strict=True) if g == 0]
    truth_of = dict(zip(ids, y, strict=True))
    truth = np.array([labels.index(truth_of[i]) for i in pool])
    words = {i: len(t.split()) for i, t in zip(ids, texts, strict=True)}
    author_volume = Counter(meta.loc[ids, "author"])
    vol = {i: author_volume[meta.loc[i, "author"]] for i in pool}
    q1, q2 = np.quantile([words[i] for i in pool], [1 / 3, 2 / 3])
    v1, v2 = np.quantile(list(vol.values()), [1 / 3, 2 / 3])
    groups = {
        "specialite": [str(meta.loc[i, "specialty"]).lower() for i in pool],
        "longueur": ["court" if words[i] <= q1 else ("moyen" if words[i] <= q2 else "long") for i in pool],
        "volume_auteur": ["peu" if vol[i] <= v1 else ("moyen" if vol[i] <= v2 else "beaucoup") for i in pool],
    }
    preds = {}
    for name, slug in PREDS.items():
        d = json.loads((ROOT / f"results/predictions/{slug}.json").read_text(encoding="utf-8"))
        pm = dict(zip(d["ids"], d["pred"], strict=True))
        preds[name] = np.array([labels.index(pm[i]) for i in pool])
    out: dict = {"sous_groupes": {}}
    for gname, g in groups.items():
        ga = np.array(g)
        out["sous_groupes"][gname] = {v: {"n": int((ga == v).sum()), **{m: round(float((preds[m][ga == v] == truth[ga == v]).mean()), 3) for m in PREDS}} for v in sorted(set(g))}
    # lecture bayésienne : bootstrap stratifié, répliques du pli 0 à effectifs de classe conservés
    rng = np.random.default_rng(20261002)
    by_class = [np.flatnonzero(truth == c) for c in range(len(labels))]
    r = 5000
    idx = np.concatenate([rng.choice(ix, size=(r, len(ix))) for ix in by_class if len(ix)], axis=1)
    scored = [labels.index(c) for c in labels if c != other]
    diff = _macro_f1(truth[idx], preds["qwen3.5-9b-1e-4"][idx], scored) - _macro_f1(truth[idx], preds["tfidf"][idx], scored)
    out["bayes_exploratoire"] = {"ecart_moyen_points": round(float(100 * diff.mean()), 2), "p_ecart_superieur_a_0": round(float((diff > 0).mean()), 4), "p_ecart_superieur_a_delta": round(float((diff > DELTA).mean()), 4),
                                 "p_ecart_dans_moins_delta": round(float((np.abs(diff) < DELTA).mean()), 4), "p_9b_inferieur_de_plus_de_delta": round(float((diff < -DELTA).mean()), 4)}
    (ROOT / "results/measures/glm_v3_subgroups_bayes.json").write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    print(json.dumps(out, ensure_ascii=False, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
