#!/usr/bin/env python3
"""P1-03 : bornes sans modèle (classe majoritaire, tirage uniforme, tirage selon la prévalence, prior) sur les trois tâches, par pli de développement.

Un pli est évalué avec les étiquettes des quatre autres : AUCUNE lecture du test scellé (on ne lit que la clé `folds` des partitions).
Chapitre : étiquettes dérivées comme `scripts/make_splits.py` (hiérarchie ClaML, classes rares fusionnées dans `AUTRE`), `AUTRE` exclue de la macro-F1.
Spécialité : colonne `specialty`, au patient. Type de document : au document ; les documents héritent du pli de leur patient.
Usage : p1_03_bounds.py [--register]"""
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from llmft import baselines, cim10, loader, splits
from llmft.mini_registry import register_run

PARQUET = ROOT / "data/raw/parhaf/data/train-00000-of-00001.parquet"
CLAML = ROOT / "data/raw/cim10/cim10fr2019.xml"
PART = ROOT / "data/splits/parhaf_cim10_chapter.json"
SHA = ROOT / "data/splits/parhaf_cim10_chapter.sha256"
N_RANDOM, SEED = 200, 20261003


def main() -> int:
    parts = loader.load_partitions(PART, SHA)
    fold_of = {pid: k for k, ids in enumerate(parts["folds"]) for pid in ids}  # clé `folds` seulement : jamais le test
    df = pd.read_parquet(PARQUET, columns=["id", "specialty", "suggested_scenario", "documents"])
    df = df[df["id"].isin(fold_of)].copy()
    df["fold"] = df["id"].map(fold_of)
    hierarchy = cim10.load_claml(CLAML)
    resolved = df["suggested_scenario"].map(lambda s: hierarchy.lookup(s["primary_diagnosis"]["code"][0]))
    df = df[resolved.notna()].copy()
    df["chapter_raw"] = resolved[resolved.notna()].map(lambda r: r.chapter)
    df["chapter"] = splits.apply_rare_class_policy(df["chapter_raw"])  # fréquences sur le développement seulement : même règle, effectifs du développement
    docs = pd.DataFrame(
        [{"fold": r["fold"], "doctype": str(t).lower()} for r in df.to_dict("records") for t in r["documents"]["type"]]
    )
    tasks = {
        "parhaf_cim10_chapter": (df["chapter"].tolist(), df["fold"].to_numpy(), "AUTRE"),
        "parhaf_specialty": (df["specialty"].str.lower().tolist(), df["fold"].to_numpy(), None),
        "parhaf_doctype": (docs["doctype"].tolist(), docs["fold"].to_numpy(), None),
    }
    rng = np.random.default_rng(SEED)
    results = {}
    for name, (labels_all, folds, excluded) in tasks.items():
        labels = sorted(set(labels_all))
        scored = [lab for lab in labels if lab != excluded]
        per_fold = []
        for k in range(5):
            train = [lab for lab, f in zip(labels_all, folds, strict=True) if f != k]
            test = [lab for lab, f in zip(labels_all, folds, strict=True) if f == k]
            per_fold.append(baselines.fold_bounds(train, test, labels, scored, n_random=N_RANDOM, rng=rng))
        agg = {
            key: {m: [round(float(np.mean([pf[key][m] for pf in per_fold])), 4), round(float(np.std([pf[key][m] for pf in per_fold])), 4)] for m in (("macro_f1", "accuracy") if key != "prior" else ("log_loss", "class_balanced_log_loss"))}
            for key in ("majority", "random_uniform", "random_prior", "prior")
        }
        results[name] = {"classes": len(labels), "scored_classes": len(scored), "n_dev": len(labels_all), "majority_class_by_fold": [pf["majority_class"] for pf in per_fold], "mean_std_over_5_folds": agg}
        print(name, json.dumps(results[name], ensure_ascii=False))
    record = {
        "kind": "measure", "slug": "p1-03-bounds", "status": "ok",
        "summary": "P1-03 : bornes sans modèle sur les trois tâches (classe majoritaire, tirage uniforme, tirage selon la prévalence, prior), moyenne et écart-type sur les 5 plis de développement ; test scellé jamais lu",
        "params": {"seed": SEED, "n_random": N_RANDOM, "partition_sha256_file": str(SHA.relative_to(ROOT))},
        "metrics": results,
    }
    if "--register" in sys.argv:
        print(register_run(ROOT / "results/runs", record))
    return 0


if __name__ == "__main__":
    sys.exit(main())
