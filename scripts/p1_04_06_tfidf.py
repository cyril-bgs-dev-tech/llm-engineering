#!/usr/bin/env python3
"""P1-04 (doctype) et P1-06 (chapitre) : TF-IDF + régression logistique hors pli, selon la fiche `experiments/2026-10-03-p1-04-06-tfidf.md`.

Développement seulement (clé `folds`) : le test scellé n'est jamais lu. Pli externe k : validation = pli (k+1) mod 5, réglage sur la grille de
`llmft.tfidf`, ré-entraînement sur les quatre plis, évaluation sur k. Usage : p1_04_06_tfidf.py {doctype|chapter} [--folds author] [--register]
`--folds author` (RM-14) : plis de contrôle groupés par auteur (clé `control_folds_by_author`) au lieu des plis par patient. Les prédictions hors pli
(identifiant, classe prédite) sont écrites dans `results/predictions/<slug>.json`, leur SHA-256 va au registre."""
import hashlib
import json
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from llmft import cim10, evaluation, loader, metrics, splits, tfidf
from llmft.mini_registry import register_run

PARQUET = ROOT / "data/raw/parhaf/data/train-00000-of-00001.parquet"
CLAML = ROOT / "data/raw/cim10/cim10fr2019.xml"
PART = ROOT / "data/splits/parhaf_cim10_chapter.json"
SHA = ROOT / "data/splits/parhaf_cim10_chapter.sha256"
SEED, N_BOOT = 20261003, 2000


def patient_text(docs: dict) -> str:
    return "\n\n".join(f"[{t}]\n{x}" for t, x in zip(docs["type"], docs["text"], strict=True))


def load(task: str, fold_key: str = "folds") -> tuple[list[str], list[str], np.ndarray, str | None, list[str]]:
    parts = loader.load_partitions(PART, SHA)
    fold_of = {pid: k for k, ids in enumerate(parts[fold_key]) for pid in ids}
    df = pd.read_parquet(PARQUET, columns=["id", "suggested_scenario", "documents"])
    df = df[df["id"].isin(fold_of)].copy()
    df["fold"] = df["id"].map(fold_of)
    if task == "doctype":
        rows = [(str(x), str(t).lower(), r["fold"]) for r in df.to_dict("records") for t, x in zip(r["documents"]["type"], r["documents"]["text"], strict=True)]
        return [r[0] for r in rows], [r[1] for r in rows], np.array([r[2] for r in rows]), None, [str(i) for i in range(len(rows))]
    hierarchy = cim10.load_claml(CLAML)
    resolved = df["suggested_scenario"].map(lambda s: hierarchy.lookup(s["primary_diagnosis"]["code"][0]))
    df = df[resolved.notna()].copy()
    df["chapter"] = splits.apply_rare_class_policy(resolved[resolved.notna()].map(lambda r: r.chapter))
    return [patient_text(d) for d in df["documents"]], df["chapter"].tolist(), df["fold"].to_numpy(), "AUTRE", df["id"].astype(str).tolist()


def main() -> int:
    task = sys.argv[1]
    fold_key = "control_folds_by_author" if "--folds" in sys.argv and sys.argv[sys.argv.index("--folds") + 1] == "author" else "folds"
    texts, y, folds, excluded, ids = load(task, fold_key)
    labels = sorted(set(y))
    scored = [lab for lab in labels if lab != excluded]
    idx = np.array([labels.index(v) for v in y])
    oof = np.zeros((len(y), len(labels)))
    per_fold, chosen = [], []
    t0 = time.time()
    for k in range(5):
        tr = np.where(folds != k)[0]
        te = np.where(folds == k)[0]
        cfg = tfidf.select_config([texts[i] for i in tr], [y[i] for i in tr], folds[tr], (k + 1) % 5, labels, scored)
        chosen.append({"fold": k, "C": cfg[0], "ngram": list(cfg[1])})
        oof[te] = tfidf.fit_predict_proba([texts[i] for i in tr], [y[i] for i in tr], [texts[i] for i in te], labels, cfg[0], cfg[1])
        rep = evaluation.chapter_report(idx[te], oof[te], labels, excluded=(excluded,) if excluded else ())
        per_fold.append({"fold": k, "macro_f1": rep["macro_f1"], "accuracy": rep["accuracy"], "log_loss": rep["log_loss"]})
        print(k, chosen[-1], round(rep["macro_f1"], 4), round(time.time() - t0), "s", flush=True)
    pooled = evaluation.chapter_report(idx, oof, labels, excluded=(excluded,) if excluded else ())
    rng = np.random.default_rng(SEED)
    by_class = [np.where(idx == c)[0] for c in range(len(labels))]
    pred = oof.argmax(1)
    boots = []
    for _ in range(N_BOOT):
        ix = np.concatenate([rng.choice(i, size=len(i)) for i in by_class if len(i)])
        boots.append(metrics.macro_f1([y[i] for i in ix], [labels[pred[i]] for i in ix], scored))
    lo, hi = np.percentile(boots, [2.5, 97.5])
    nll = -np.log(np.clip(oof[np.arange(len(y)), idx], 1e-12, 1))
    bal_ll = float(np.mean([nll[idx == c].mean() for c in range(len(labels)) if (idx == c).any()]))
    mf = [p["macro_f1"] for p in per_fold]
    result = {
        "n": len(y), "classes": len(labels), "scored_classes": len(scored), "chosen_config_by_fold": chosen,
        "macro_f1_pooled": [round(pooled["macro_f1"], 4), round(float(lo), 4), round(float(hi), 4)],
        "macro_f1_folds_mean_sd": [round(float(np.mean(mf)), 4), round(float(np.std(mf)), 4)],
        "accuracy": round(pooled["accuracy"], 4), "log_loss": round(pooled["log_loss"], 4), "class_balanced_log_loss": round(bal_ll, 4),
        "ece": round(pooled["ece"], 4), "seconds": round(time.time() - t0),
    }
    print(json.dumps(result, ensure_ascii=False, indent=1))
    slug = f"p1-{'04' if task == 'doctype' else '06'}-tfidf-{task}" + ("-author-folds" if fold_key != "folds" else "")
    payload = json.dumps({"ids": ids, "pred": [labels[int(p)] for p in pred], "fold_key": fold_key}, ensure_ascii=False)
    result["predictions_sha256"] = hashlib.sha256(payload.encode("utf-8")).hexdigest()
    if "--register" in sys.argv:
        pred_path = ROOT / "results/predictions" / f"{slug}.json"
        pred_path.parent.mkdir(parents=True, exist_ok=True)
        pred_path.write_text(payload, encoding="utf-8")
    record = {"kind": "measure", "slug": slug, "status": "ok",
              "summary": f"TF-IDF et régression logistique hors pli sur {task} (développement seulement, 5 plis {fold_key}, réglage C et n-grammes sur le pli suivant) ; fiche experiments/2026-10-03-p1-04-06-tfidf.md",
              "params": {"seed": SEED, "n_boot": N_BOOT, "grid": [[c, list(n)] for c, n in tfidf.GRID], "partition_sha256_file": str(SHA.relative_to(ROOT))},
              "metrics": result}
    if "--register" in sys.argv:
        print(register_run(ROOT / "results/runs", record))
    return 0


if __name__ == "__main__":
    sys.exit(main())
