#!/usr/bin/env python3
"""P0-28, P0-29, P0-33 : jeu de travail PARHAF, classes et découpages (PROTOCOLE.md sections 2 et 3).

Écrit data/splits/parhaf_cim10_chapter.json (identifiants seulement), son SHA-256 et un résumé dans results/measures/.
"""
import json
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from llmft import cim10, leakage, splits

SEED = 20261002
PARQUET = ROOT / "data/raw/parhaf/data/train-00000-of-00001.parquet"
STANDALONE = ROOT / "data/raw/parhaf/standalone/patients.json"
CLAML = ROOT / "data/raw/cim10/cim10fr2019.xml"
OUT = ROOT / "data/splits/parhaf_cim10_chapter.json"


def main() -> int:
    df = pd.read_parquet(PARQUET)
    canonical = {p["id"] for p in json.loads(STANDALONE.read_text(encoding="utf-8"))["data"]}
    n_parquet = len(df)
    df = df[df["id"].isin(canonical)].copy()  # intersection des deux formats (ADR-005) ; texte identique vérifié en P0-21
    n_common = len(df)
    hierarchy = cim10.load_claml(CLAML)
    code = df["suggested_scenario"].map(lambda s: s["primary_diagnosis"]["code"][0])
    resolved = code.map(hierarchy.lookup)
    invalid = df.loc[resolved.isna(), "id"].tolist()
    df = df[resolved.notna()].copy()
    df["label_raw"] = resolved[resolved.notna()].map(lambda r: r.chapter)
    df["label"] = splits.apply_rare_class_policy(df["label_raw"])
    texts = {r.id: "\n".join(r.documents["text"]) for r in df.itertuples()}
    pairs = leakage.near_duplicate_pairs(texts)  # seuil du protocole (section 4)
    groups = leakage.clusters(df["id"], pairs)
    df["cluster"] = df["id"].map(groups)
    label_of = df.set_index("id")["label"]
    author_of = df.set_index("id")["author"]
    s = splits.make_splits(df[["id", "author", "label", "cluster"]], seed=SEED)

    part = {i: "test" for i in s.test} | {i: f"pli{k}" for k, f in enumerate(s.folds) for i in f}
    problems = splits.check_no_overlap(s) + splits.check_tolerance(df[["id", "author", "label"]], s)
    problems += [f"quasi-doublon entre partitions : {a} {b} ({sim})" for a, b, sim in leakage.cross_partition_pairs(pairs, part)]
    (OUT.parent / "near_duplicates.json").write_text(
        json.dumps({"threshold": leakage.NEAR_DUPLICATE_THRESHOLD, "pairs": [[a, b, sim] for a, b, sim in pairs]}, indent=1) + "\n", encoding="utf-8"
    )
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(s.to_json(), encoding="utf-8")
    (OUT.with_suffix(".sha256")).write_text(s.sha256() + "\n", encoding="ascii")

    authors = df.groupby("author")["label"].nunique()
    summary = {
        "seed": SEED, "n_parquet": n_parquet, "n_common_formats": n_common, "invalid_code_patients": invalid,
        "n_working_set": len(df), "n_test": len(s.test), "fold_sizes": [len(f) for f in s.folds],
        "control_fold_sizes": [len(f) for f in s.control_folds],
        "classes": df["label"].value_counts().to_dict(),
        "autre_composition": df.loc[df["label"] == "AUTRE", "label_raw"].value_counts().to_dict(),
        "authors": int(df["author"].nunique()), "authors_single_class": int((authors == 1).sum()),
        "share_patients_of_single_class_authors": round(float(df["author"].isin(authors[authors == 1].index).mean()), 4),
        "near_duplicate_threshold": leakage.NEAR_DUPLICATE_THRESHOLD, "near_duplicate_pairs": len(pairs),
        "near_duplicate_pairs_same_author": sum(author_of[a] == author_of[b] for a, b, _ in pairs),
        "near_duplicate_pairs_same_label": sum(label_of[a] == label_of[b] for a, b, _ in pairs),
        "clusters_with_several_patients": int(df["cluster"].value_counts().gt(1).sum()),
        "test_class_counts": {c: int(label_of[s.test].eq(c).sum()) for c in df["label"].value_counts().index},
        "split_sha256": s.sha256(), "problems": problems,
    }
    (ROOT / "results/measures/splits_summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(json.dumps({k: v for k, v in summary.items() if k != "classes"}, ensure_ascii=False, indent=1))
    print("classes:", summary["classes"])
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
