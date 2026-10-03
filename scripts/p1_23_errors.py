#!/usr/bin/env python3
"""P1-23 : analyse d'erreurs d'un fichier de prédictions hors pli sur le chapitre (développement seulement).

Par chapitre : précision, rappel, F1, effectif ; confusions les plus fréquentes ; exactitude par spécialité et par tercile de longueur (en mots).
Usage : p1_23_errors.py PRED.json SLUG [--register]"""
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
from llmft.mini_registry import register_run


def main() -> int:
    pred = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
    slug = sys.argv[2]
    texts, y_all, _, _, ids_all = p1_04_06_tfidf.load("chapter")
    truth = dict(zip(ids_all, y_all, strict=True))
    words = dict(zip(ids_all, [len(t.split()) for t in texts], strict=True))
    meta = pd.read_parquet(p1_04_06_tfidf.PARQUET, columns=["id", "specialty"])
    spec = dict(zip(meta["id"].astype(str), meta["specialty"].str.lower(), strict=True))
    ids = [i for i in pred["ids"] if i in truth]
    t = np.array([truth[i] for i in ids])
    p = np.array([dict(zip(pred["ids"], pred["pred"], strict=True))[i] for i in ids])
    per_class = {}
    for c in sorted(set(t)):
        tp, fp, fn = int(((t == c) & (p == c)).sum()), int(((t != c) & (p == c)).sum()), int(((t == c) & (p != c)).sum())
        per_class[c] = {"support": int((t == c).sum()), "precision": round(tp / (tp + fp), 3) if tp + fp else 0.0, "recall": round(tp / (tp + fn), 3) if tp + fn else 0.0,
                        "f1": round(2 * tp / (2 * tp + fp + fn), 3) if tp + fn + fp else 0.0}
    conf = Counter((a, b) for a, b in zip(t, p, strict=True) if a != b)
    by_spec = {}
    for s in sorted({spec[i] for i in ids}):
        m = np.array([spec[i] == s for i in ids])
        by_spec[s] = {"n": int(m.sum()), "accuracy": round(float((t[m] == p[m]).mean()), 3)}
    w = np.array([words[i] for i in ids])
    q = np.quantile(w, [1 / 3, 2 / 3])
    terc = {name: {"n": int(m.sum()), "accuracy": round(float((t[m] == p[m]).mean()), 3)}
            for name, m in (("court", w <= q[0]), ("moyen", (w > q[0]) & (w <= q[1])), ("long", w > q[1]))}
    out = {"n": len(ids), "accuracy": round(float((t == p).mean()), 4), "per_class": per_class,
           "top_confusions": [{"vrai": a, "predit": b, "n": n} for (a, b), n in conf.most_common(10)], "by_specialty": by_spec, "by_length_tercile": terc,
           "tercile_word_bounds": [int(q[0]), int(q[1])]}
    print(json.dumps(out, ensure_ascii=False, indent=1))
    if "--register" in sys.argv:
        print(register_run(ROOT / "results/runs", {"kind": "measure", "slug": slug, "status": "ok",
              "summary": f"Analyse d'erreurs (chapitre) de {Path(sys.argv[1]).name} sur {len(ids)} patients : par classe, confusions, spécialité, longueur", "params": {"pred": Path(sys.argv[1]).name}, "metrics": out}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
