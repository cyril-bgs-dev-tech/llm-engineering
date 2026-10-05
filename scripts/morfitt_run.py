#!/usr/bin/env python3
"""Ancrage sur un benchmark public (RM-49, fiche 2026-10-05-ancrage-morfitt) : MorFITT (3 624 résumés d'articles biomédicaux français, 12 spécialités, multi-étiquettes), mêmes outils que PARHAF.

`tune` : grille de taux et d'époques de l'encodeur (une graine) et de C du TF-IDF, sur le **jeu de validation** ; `final` : cinq graines de l'encodeur retenu, TF-IDF et mélange 50/50, évalués **une fois** sur le jeu de test public,
F1 pondéré (métrique du papier de référence), seuil fixe 0,5. Aucun réglage sur le test. Usage : morfitt_run.py {tune|final} [--register] [--fiche CHEMIN]"""
import hashlib
import json
import sys
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent))
import p1_finetune
from llmft import multilabel
from llmft.mini_registry import register_run

DATA = ROOT / "data/raw/morfitt/source"
MODEL = "almanach/camembert-bio-base"
LRS, EPOCHS, SEEDS = (3e-5, 5e-5, 1e-4), (10, 20), (1000, 1001, 1002, 1003, 1004)
TUNING = ROOT / "results/measures/morfitt_tuning.json"
PUBLISHED = {"CamemBERT-bio": 67.53, "DrBERT": 68.70, "DrLongformer-CP": 71.95}  # F1 pondéré, jeu de test, arXiv 2402.16689 tableau 3 (lu par résumé automatique : à vérifier dans le papier)


def load_split(name: str) -> tuple[list[str], np.ndarray]:
    df = pd.read_parquet(DATA / f"{name}-00000-of-00001.parquet")
    return df["abstract"].tolist(), np.stack([np.asarray(v, dtype=np.float32) for v in df["specialities_one_hot"]])


def tfidf_probs(train_x: list[str], train_y: np.ndarray, test_x: list[str], c: float) -> np.ndarray:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.linear_model import LogisticRegression
    from sklearn.multiclass import OneVsRestClassifier

    vec = TfidfVectorizer(sublinear_tf=True, analyzer="char_wb", ngram_range=(3, 5), min_df=2, max_features=200000)
    xtr = vec.fit_transform(train_x)
    clf = OneVsRestClassifier(LogisticRegression(C=c, max_iter=1000, class_weight="balanced")).fit(xtr, train_y.astype(int))
    return clf.predict_proba(vec.transform(test_x))


def train_encoder(tr_ids: list[list[int]], tr_y: np.ndarray, te_ids: list[list[int]], pad_id: int, lr: float, epochs: int, seed: int) -> tuple[np.ndarray, float]:
    import torch

    torch.manual_seed(seed)
    model, _ = p1_finetune.load_model(MODEL, "full", tr_y.shape[1], pad_id, 16, 32)
    model = model.to("cuda")
    res = multilabel.train_multilabel(model, tr_ids, tr_y, pad_id, "cuda", 32, 16, epochs, lr, 20, seed)
    probs = np.zeros((len(te_ids), tr_y.shape[1]))
    model.eval()
    with torch.no_grad():
        from llmft import lora_train

        order = np.argsort([len(x) for x in te_ids])
        for s in range(0, len(te_ids), 16):
            idx = order[s : s + 16]
            x, m = lora_train._pad([te_ids[i] for i in idx], pad_id, "cuda")
            probs[idx] = torch.sigmoid(model(input_ids=x, attention_mask=m).logits.float()).cpu().numpy()
    del model
    torch.cuda.empty_cache()
    return probs, res.seconds


def bootstrap_ci(y: np.ndarray, pred: np.ndarray, n_boot: int = 2000, seed: int = 20261005) -> list[float]:
    rng = np.random.default_rng(seed)
    vals = []
    for _ in range(n_boot):
        idx = rng.integers(0, len(y), len(y))
        vals.append(multilabel.f1_scores(y[idx].astype(int), pred[idx])["weighted_f1"])
    return [round(100 * float(np.percentile(vals, 2.5)), 2), round(100 * float(np.percentile(vals, 97.5)), 2)]


def main() -> int:
    mode = sys.argv[1]
    register = "--register" in sys.argv
    fiche = sys.argv[sys.argv.index("--fiche") + 1] if "--fiche" in sys.argv else ""
    fiche_sha = hashlib.sha256((ROOT / fiche).read_bytes()).hexdigest() if fiche else None
    from transformers import AutoTokenizer

    tok = AutoTokenizer.from_pretrained(MODEL)
    pad_id = tok.pad_token_id
    tr_x, tr_y = load_split("train")
    va_x, va_y = load_split("validation")
    te_x, te_y = load_split("test")
    enc = {n: p1_finetune.build_inputs(tok, x, 508) for n, x in (("train", tr_x), ("validation", va_x), ("public_test", te_x))}
    if mode == "tune":
        rows: list[dict[str, Any]] = []
        for lr in LRS:
            for ep in EPOCHS:
                probs, secs = train_encoder(enc["train"], tr_y, enc["validation"], pad_id, lr, ep, 1000)
                s = multilabel.f1_scores(va_y.astype(int), multilabel.predict_labels(probs))
                rows.append({"type": "encodeur", "lr": lr, "epochs": ep, "validation_weighted_f1": round(100 * s["weighted_f1"], 2), "seconds": round(secs, 1)})
                print(rows[-1], flush=True)
        for c in (10.0, 100.0, 1000.0):
            s = multilabel.f1_scores(va_y.astype(int), multilabel.predict_labels(tfidf_probs(tr_x, tr_y, va_x, c)))
            rows.append({"type": "tfidf", "C": c, "validation_weighted_f1": round(100 * s["weighted_f1"], 2)})
            print(rows[-1], flush=True)
        best_enc = max((r for r in rows if r["type"] == "encodeur"), key=lambda r: r["validation_weighted_f1"])
        best_tf = max((r for r in rows if r["type"] == "tfidf"), key=lambda r: r["validation_weighted_f1"])
        out = {"grille": rows, "encodeur_retenu": best_enc, "tfidf_retenu": best_tf, "fiche_sha256": fiche_sha}
        TUNING.write_text(json.dumps(out, indent=1), encoding="utf-8")
        if register:
            print(register_run(ROOT / "results/runs", {"kind": "measure", "slug": "morfitt-reglage-validation", "status": "ok", "summary": f"MorFITT, réglage sur validation : encodeur lr {best_enc['lr']}, {best_enc['epochs']} époques ; TF-IDF C = {best_tf['C']}", "params": {"fiche_sha256": fiche_sha}, "metrics": out}))
        return 0
    tuning = json.loads(TUNING.read_text(encoding="utf-8"))
    best_enc, best_tf = tuning["encodeur_retenu"], tuning["tfidf_retenu"]
    seed_probs, seed_scores = [], []
    for seed in SEEDS:
        probs, secs = train_encoder(enc["train"], tr_y, enc["public_test"], pad_id, best_enc["lr"], best_enc["epochs"], seed)
        pred = multilabel.predict_labels(probs)
        s = multilabel.f1_scores(te_y.astype(int), pred)
        seed_probs.append(probs)
        seed_scores.append(100 * s["weighted_f1"])
        np.savez_compressed(ROOT / f"results/predictions/morfitt-enc-s{seed}.probs.npz", probs=probs.astype(np.float32))
        print("graine", seed, round(100 * s["weighted_f1"], 2), flush=True)
        if register:
            print(register_run(ROOT / "results/runs", {"kind": "train", "slug": f"morfitt-final-enc-s{seed}", "status": "ok", "summary": f"MorFITT test : F1 pondéré {100 * s['weighted_f1']:.2f} (encodeur, graine {seed})",
                                                        "params": {"lr": best_enc["lr"], "epochs": best_enc["epochs"], "seed": seed, "fiche_sha256": fiche_sha}, "metrics": {"weighted_f1": round(100 * s["weighted_f1"], 2), "micro_f1": round(100 * s["micro_f1"], 2), "macro_f1": round(100 * s["macro_f1"], 2), "seconds_train": round(secs, 1)}}))
    enc_mean = np.mean(seed_probs, axis=0)
    tf = tfidf_probs(tr_x, tr_y, te_x, best_tf["C"])
    mix = 0.5 * enc_mean + 0.5 * tf
    res: dict[str, Any] = {"publie_f1_pondere_test": PUBLISHED, "reglage": tuning["encodeur_retenu"] | {"tfidf_C": best_tf["C"]}, "n_test": len(te_x)}
    res["encodeur_une_graine"] = {"moyenne": round(float(np.mean(seed_scores)), 2), "ecart_type": round(float(np.std(seed_scores, ddof=1)), 2), "par_graine": [round(float(v), 2) for v in seed_scores]}
    for name, probs in (("encodeur_moyenne_5_graines", enc_mean), ("tfidf", tf), ("melange_50_50", mix)):
        pred = multilabel.predict_labels(probs)
        s = multilabel.f1_scores(te_y.astype(int), pred)
        res[name] = {"weighted_f1": round(100 * s["weighted_f1"], 2), "micro_f1": round(100 * s["micro_f1"], 2), "macro_f1": round(100 * s["macro_f1"], 2), "ic95_weighted_f1_bootstrap_patients": bootstrap_ci(te_y, pred)}
        print(name, res[name], flush=True)
    (ROOT / "results/measures/morfitt_final.json").write_text(json.dumps(res, indent=1, ensure_ascii=False), encoding="utf-8")
    if register:
        print(register_run(ROOT / "results/runs", {"kind": "measure", "slug": "morfitt-final-resume", "status": "ok", "summary": f"MorFITT test : encodeur {res['encodeur_une_graine']['moyenne']}, mélange {res['melange_50_50']['weighted_f1']} (F1 pondéré)", "params": {"fiche_sha256": fiche_sha}, "metrics": res}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
