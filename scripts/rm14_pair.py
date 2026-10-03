#!/usr/bin/env python3
"""RM-14 : verdict apparié entre les plis par patient (P1-06) et les plis par auteur, selon `experiments/2026-10-03-rm-14-raccourci-tfidf.md`.

Lit les deux fichiers de prédictions hors pli (jamais le test scellé), aligne les patients par identifiant. Usage : rm14_pair.py [--register]"""
import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
import p1_04_06_tfidf  # même dossier de scripts
from llmft import paired
from llmft.mini_registry import register_run

PRED = ROOT / "results/predictions"
THRESHOLD, SEED, N_BOOT, LEVEL = 0.03, 20261003, 2000, 0.95


def decide(lo: float, hi: float, point: float) -> str:
    """Raccourci signalé : écart >= 3 points et borne basse > 0 ; non signalé : borne haute sous 3 points ; sinon non résolu."""
    if point >= THRESHOLD and lo > 0:
        return "signalé"
    if hi < THRESHOLD:
        return "non signalé"
    return "non résolu"


def main() -> int:
    pat = json.loads((PRED / "p1-06-tfidf-chapter.json").read_text(encoding="utf-8"))
    aut = json.loads((PRED / "p1-06-tfidf-chapter-author-folds.json").read_text(encoding="utf-8"))
    common = sorted(set(pat["ids"]) & set(aut["ids"]))
    pa = dict(zip(pat["ids"], pat["pred"], strict=True))
    pb = dict(zip(aut["ids"], aut["pred"], strict=True))
    _, y_all, _, _, ids_all = p1_04_06_tfidf.load("chapter")  # mêmes étiquettes de développement que le run P1-06
    truth_map = dict(zip(ids_all, y_all, strict=True))
    labels = sorted(set(truth_map.values()) | set(pa.values()) | set(pb.values()))
    idx = {lab: i for i, lab in enumerate(labels)}
    scored = [idx[lab] for lab in labels if lab != "AUTRE"]
    t = np.array([idx[truth_map[i]] for i in common])
    a = np.array([[idx[pa[i]] for i in common]])
    b = np.array([[idx[pb[i]] for i in common]])
    res = paired.hierarchical_bootstrap(t, a, b, len(labels), scored, "macro_f1", True, False, N_BOOT, LEVEL, np.random.default_rng(SEED))
    out = {"n_common": len(common), "n_patient_folds": len(pat["ids"]), "n_author_folds": len(aut["ids"]),
           "delta_macro_f1_patient_minus_author": [round(res.estimate, 4), round(res.lo, 4), round(res.hi, 4)], "verdict": decide(res.lo, res.hi, res.estimate), "threshold": THRESHOLD}
    print(json.dumps(out, ensure_ascii=False, indent=1))
    record = {"kind": "measure", "slug": "rm-14-author-shortcut-tfidf", "status": "ok",
              "summary": "RM-14 : écart de macro-F1 entre plis par patient et plis par auteur pour le TF-IDF sur le chapitre, bootstrap apparié ; fiche experiments/2026-10-03-rm-14-raccourci-tfidf.md",
              "params": {"seed": SEED, "n_boot": N_BOOT, "level": LEVEL}, "metrics": out}
    if "--register" in sys.argv:
        print(register_run(ROOT / "results/runs", record))
    return 0


if __name__ == "__main__":
    sys.exit(main())
