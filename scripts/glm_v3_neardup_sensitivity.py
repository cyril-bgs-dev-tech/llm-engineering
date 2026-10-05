#!/usr/bin/env python3
"""Audit GLM v3, C3-A3 : sensibilité du contrôle de quasi-doublons au seuil (0,6 à 0,8), sans toucher au seuil figé 0,8. Agrégats seulement."""
import json
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent))
import p1_04_06_tfidf
from llmft import leakage


def main() -> int:
    df = pd.read_parquet(p1_04_06_tfidf.PARQUET, columns=["id", "author", "documents"])
    texts = {str(r["id"]): "\n".join(r["documents"]["text"]) for r in df.to_dict("records")}
    author = dict(zip(df["id"].astype(str), df["author"], strict=True))
    out = {}
    for th in (0.6, 0.7, 0.8):
        pairs = leakage.near_duplicate_pairs(texts, th)
        out[str(th)] = {"paires": len(pairs), "meme_auteur": sum(author[a] == author[b] for a, b, _ in pairs)}
        print(th, out[str(th)], flush=True)
    (ROOT / "results/measures/glm_v3_neardup_sensitivity.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
