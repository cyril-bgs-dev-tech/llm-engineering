#!/usr/bin/env python3
"""Taxonomie d'erreurs sur les prédictions hors pli des cinq plis (3 586 patients, TF-IDF caractères et poids équilibrés), agrégats seulement, développement.

Paires de confusion les plus fréquentes, erreurs confiantes (probabilité de la bonne classe < 0,10 alors que la classe prédite dépasse 0,90 : candidates à un problème d'étiquette,
audit d'étiquettes par apprentissage confiant), exactitude top-1 et top-2 par spécialité et par tercile de longueur. Aucun texte n'est affiché. Usage : error_taxonomy.py [--register]"""
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
    texts, y, _, _other, ids = p1_04_06_tfidf.load("chapter")
    meta = pd.read_parquet(p1_04_06_tfidf.PARQUET, columns=["id", "specialty"])
    spec = dict(zip(meta["id"].astype(str), meta["specialty"].str.lower(), strict=True))
    z = np.load(ROOT / "results/predictions/tfidf-variant-char-balanced.probs.npz", allow_pickle=False)
    labels = [str(c) for c in z["labels"]]
    pos = {str(i): k for k, i in enumerate(z["ids"])}
    p = z["probs"][[pos[i] for i in ids]]
    t = np.array([labels.index(v) for v in y])
    rank = (-p).argsort(1)
    pred = rank[:, 0]
    top2 = (rank[:, :2] == t[:, None]).any(1)
    wrong = pred != t
    pairs = Counter((labels[a], labels[b]) for a, b in zip(t[wrong], pred[wrong], strict=True))
    confident = wrong & (p[np.arange(len(t)), t] < 0.10) & (p.max(1) > 0.90)
    words = np.array([len(x.split()) for x in texts])
    q1, q2 = np.quantile(words, [1 / 3, 2 / 3])
    tercile = np.where(words <= q1, "court", np.where(words <= q2, "moyen", "long"))
    sp = np.array([spec[i] for i in ids])
    out = {"n": len(t), "exactitude_top1": round(float((~wrong).mean()), 4), "exactitude_top2": round(float(top2.mean()), 4), "erreurs": int(wrong.sum()),
           "erreurs_confiantes": int(confident.sum()), "part_des_erreurs_confiantes": round(float(confident.sum() / wrong.sum()), 3),
           "paires_les_plus_frequentes": [{"vrai": a, "predit": b, "n": n} for (a, b), n in pairs.most_common(12)],
           "erreurs_confiantes_par_chapitre": dict(Counter(labels[k] for k in t[confident]).most_common(10)),
           "par_tercile_de_longueur": {g: {"n": int((tercile == g).sum()), "top1": round(float((~wrong)[tercile == g].mean()), 3), "top2": round(float(top2[tercile == g].mean()), 3)} for g in ("court", "moyen", "long")},
           "par_specialite": {s: {"n": int((sp == s).sum()), "top1": round(float((~wrong)[sp == s].mean()), 3), "top2": round(float(top2[sp == s].mean()), 3)} for s in sorted(set(sp)) if (sp == s).sum() >= 40}}
    (ROOT / "results/measures/error_taxonomy.json").write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    print(json.dumps({k: out[k] for k in ("exactitude_top1", "exactitude_top2", "erreurs", "erreurs_confiantes", "part_des_erreurs_confiantes")}), out["paires_les_plus_frequentes"][:6], out["erreurs_confiantes_par_chapitre"])
    if "--register" in sys.argv:
        print(register_run(ROOT / "results/runs", {"kind": "measure", "slug": "error-taxonomy-tfidf-5plis", "status": "ok", "summary": "Taxonomie d'erreurs sur cinq plis (TF-IDF caractères et poids)", "params": {}, "metrics": out}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
