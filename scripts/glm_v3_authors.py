#!/usr/bin/env python3
"""Audit GLM v3, C3-A1, A2, A4 : traces d'auteur dans le texte, table auteurs par chapitre, stylométrie. Développement seulement, agrégats seulement.

Usage : glm_v3_authors.py"""
import json
import re
import sys
from collections import Counter
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import StratifiedKFold

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(Path(__file__).resolve().parent))
import p1_04_06_tfidf

OUT = ROOT / "results/measures/glm_v3_authors.json"


def main() -> int:
    texts, y, _, _, ids = p1_04_06_tfidf.load("chapter")
    meta = pd.read_parquet(p1_04_06_tfidf.PARQUET, columns=["id", "author", "reviewer"])
    meta["id"] = meta["id"].astype(str)
    meta = meta.set_index("id").loc[ids]
    author, reviewer = meta["author"].tolist(), meta["reviewer"].tolist()

    def in_text(codes: list[str]) -> int:
        return sum(1 for t, c in zip(texts, codes, strict=True) if c and re.search(r"\b" + re.escape(c) + r"\b", t))

    per_chapter = {c: len({a for a, k in zip(author, y, strict=True) if k == c}) for c in sorted(set(y))}
    support = Counter(y)
    top_share = {}
    for c in sorted(set(y)):
        cnt = Counter(a for a, k in zip(author, y, strict=True) if k == c)
        top_share[c] = round(cnt.most_common(1)[0][1] / support[c], 3)
    # stylométrie : prédire l'auteur à partir du texte (auteurs d'au moins 20 patients), 5 plis stratifiés
    big = {a for a, n in Counter(author).items() if n >= 20}
    idx = [i for i, a in enumerate(author) if a in big]
    xa = [texts[i] for i in idx]
    ya = np.array([author[i] for i in idx])
    pred = np.empty(len(idx), dtype=object)
    for tr, te in StratifiedKFold(5, shuffle=True, random_state=1000).split(xa, ya):
        vec = TfidfVectorizer(sublinear_tf=True, min_df=2, ngram_range=(1, 2), max_features=200000)
        xtr = vec.fit_transform([xa[i] for i in tr])
        clf = LogisticRegression(C=10.0, max_iter=300).fit(xtr, ya[tr])
        pred[te] = clf.predict(vec.transform([xa[i] for i in te]))
    acc = float((pred == ya).mean())
    majority = Counter(ya.tolist()).most_common(1)[0][1] / len(ya)
    res = {"auteur_dans_le_texte": in_text(author), "relecteur_dans_le_texte": in_text(reviewer), "n_patients": len(texts), "n_auteurs": len(set(author)),
           "auteurs_par_chapitre": per_chapter, "part_du_premier_auteur_par_chapitre": top_share,
           "stylometrie": {"auteurs_retenus": len(big), "patients": len(idx), "exactitude_5_plis": round(acc, 4), "classe_majoritaire": round(majority, 4), "hasard_uniforme": round(1 / len(big), 4)}}
    OUT.write_text(json.dumps(res, ensure_ascii=False, indent=1), encoding="utf-8")
    print(json.dumps(res, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
