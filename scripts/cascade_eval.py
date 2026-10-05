#!/usr/bin/env python3
"""Allocation dynamique du calcul à l'inférence (cascade) : un modèle bon marché répond quand sa confiance dépasse un seuil, sinon le cas passe au modèle suivant. Évaluation hors ligne sur des
prédictions hors pli existantes (aucun entraînement), plis 0 et 1, développement seulement, EXPLORE. Latences de référence mesurées : TF-IDF 1,9 ms (CPU), encodeur 191 ms (CPU, par modèle), LoRA 117 ms (GPU).
Usage : cascade_eval.py [--register]"""
import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent))
import p1_04_06_tfidf
from llmft.mini_registry import register_run
from llmft.power_rule import _macro_f1

P = ROOT / "results/predictions"
MS = {"tfidf": 1.9, "encodeur": 191.0, "lora": 117.0}
THRESHOLDS = (0.5, 0.7, 0.8, 0.9, 0.95, 0.99)


def load(name: str) -> tuple[list[str], np.ndarray, list[str]]:
    z = np.load(P / f"{name}.probs.npz", allow_pickle=False)
    return [str(i) for i in z["ids"]], z["probs"].astype(float), [str(c) for c in z["labels"]]


def aligned(name: str, ids: list[str]) -> np.ndarray:
    i, p, _ = load(name)
    pos = {x: k for k, x in enumerate(i)}
    return p[[pos[x] for x in ids]]


def mf(p: np.ndarray, t: np.ndarray, scored: list[int]) -> float:
    return round(float(_macro_f1(t[None, :], p.argmax(1)[None, :], scored)[0]), 4)


def main() -> int:
    _, y, _, other, ids_all = p1_04_06_tfidf.load("chapter")
    truth_of = dict(zip(ids_all, y, strict=True))
    out = {}
    for fold, lora_names in ((0, ["llm-mur2-qwen3-5-4b-ep10-lr1e-4", "llm-mur-s1001-qwen3-5-4b-ep10-lr1e-4"]), (1, ["llm-mur-pli1-qwen3-5-4b-ep10-lr1e-4"])):
        ids, _p, labels = load(lora_names[0])
        lora = np.mean([aligned(n, ids) for n in lora_names], axis=0)
        enc = aligned("ensemble-encodeur5" if fold == 0 else "pli1-ensemble-encodeur5", ids)
        tf = aligned("tfidf-variant-char-balanced", ids)
        t = np.array([labels.index(truth_of[i]) for i in ids])
        scored = [labels.index(c) for c in labels if c != other]
        res = {"tfidf": mf(tf, t, scored), "encodeur": mf(enc, t, scored), "lora": mf(lora, t, scored), "cascades": {}}
        for name, first, second, c1, c2 in (("tfidf_vers_lora", tf, lora, MS["tfidf"], MS["lora"]), ("encodeur_vers_lora", enc, lora, 5 * MS["encodeur"], MS["lora"]), ("tfidf_vers_encodeur", tf, enc, MS["tfidf"], 5 * MS["encodeur"])):
            rows = []
            for tau in THRESHOLDS:
                keep = first.max(1) >= tau
                final = np.where(keep[:, None], first, second)
                rows.append({"seuil": tau, "part_traitee_par_le_premier": round(float(keep.mean()), 3), "macro_f1": mf(final, t, scored), "latence_moyenne_ms": round(float(c1 + (1 - keep.mean()) * c2), 1)})
            res["cascades"][name] = rows
        out[f"pli{fold}"] = res
        print(f"pli {fold}", {k: res[k] for k in ("tfidf", "encodeur", "lora")}, flush=True)
        for name, rows in res["cascades"].items():
            print(" ", name, [(r["seuil"], r["part_traitee_par_le_premier"], r["macro_f1"]) for r in rows])
    (ROOT / "results/measures/cascade_eval.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
    if "--register" in sys.argv:
        print(register_run(ROOT / "results/runs", {"kind": "measure", "slug": "cascade-eval", "status": "ok", "summary": "Cascade TF-IDF, encodeur, LoRA par seuil de confiance (hors ligne, plis 0 et 1)", "params": {"thresholds": list(THRESHOLDS)}, "metrics": out}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
