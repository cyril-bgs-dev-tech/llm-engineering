#!/usr/bin/env python3
"""Différence appariée de macro-F1 (A moins B) entre deux fichiers de prédictions hors pli sur le chapitre, sur les patients communs.

Bootstrap stratifié par chapitre, même tirage pour A et B, IC 95 %, 2 000 tirages, PCG64 graine 20261003 (fiche TF-IDF v1). Verdict en trois valeurs d'ADR-007
avec δ = 0 (« A meilleur » si borne basse > 0, « B meilleur » si borne haute < 0, sinon « non résolu ») : aucun seuil d'utilité ici, comparaison exploratoire.
Usage : pair_preds.py A.json B.json SLUG [--register]   (fichiers de `results/predictions/`, clés `ids` et `pred`)"""
import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent))
import p1_04_06_tfidf
from llmft import paired
from llmft.mini_registry import register_run


def main() -> int:
    pa = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
    pb = json.loads(Path(sys.argv[2]).read_text(encoding="utf-8"))
    slug = sys.argv[3]
    _, y_all, _, _, ids_all = p1_04_06_tfidf.load("chapter")
    truth_map = dict(zip(ids_all, y_all, strict=True))
    da, db = dict(zip(pa["ids"], pa["pred"], strict=True)), dict(zip(pb["ids"], pb["pred"], strict=True))
    common = sorted(set(da) & set(db))
    labels = sorted(set(truth_map.values()) | set(da.values()) | set(db.values()))
    idx = {lab: i for i, lab in enumerate(labels)}
    scored = [idx[lab] for lab in labels if lab != "AUTRE"]
    t = np.array([idx[truth_map[i]] for i in common])
    a = np.array([[idx[da[i]] for i in common]])
    b = np.array([[idx[db[i]] for i in common]])
    res = paired.hierarchical_bootstrap(t, a, b, len(labels), scored, "macro_f1", True, False, 2000, 0.95, np.random.default_rng(20261003))
    verdict = "A meilleur" if res.lo > 0 else "B meilleur" if res.hi < 0 else "non résolu"
    out = {"a": Path(sys.argv[1]).name, "b": Path(sys.argv[2]).name, "n_common": len(common),
           "delta_macro_f1_a_minus_b": [round(res.estimate, 4), round(res.lo, 4), round(res.hi, 4)], "verdict": verdict}
    print(json.dumps(out, ensure_ascii=False, indent=1))
    if "--register" in sys.argv:
        print(register_run(ROOT / "results/runs", {"kind": "measure", "slug": slug, "status": "ok",
              "summary": f"Différence appariée de macro-F1 {out['a']} moins {out['b']} sur {len(common)} patients communs, IC 95 % bootstrap stratifié", "params": {"seed": 20261003, "n_boot": 2000}, "metrics": out}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
