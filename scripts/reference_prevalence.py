#!/usr/bin/env python3
"""Fichier de référence du moniteur de dérive (P5-08, `docs/SURVEILLANCE_DERIVE.md`) : prévalence des chapitres prédits par le système servi sur ses prédictions
hors pli, seuil S2 et fenêtre mesurés par le run 20261017-090325-simulation-derive. Usage : reference_prevalence.py tfidf|g-cascade --out FICHIER.json"""
import argparse
import json
import sys
from pathlib import Path
from typing import Any

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from llmft.cascade import cascade_probs
from llmft.drift_monitor import S2_THRESHOLD_100, reference_prevalence

P = ROOT / "results/predictions"
SOURCES = {"tfidf": "tfidf-variant-char-balanced-author", "e": "cinq-plis-ensemble-encodeur5-tfidf-charbal", "g": "cinq-plis-ensemble-g"}
TAU, WINDOW, RUN = 0.6, 100, "20261017-090325-simulation-derive"


def payload(system: str, probs: np.ndarray, labels: list[str], source: str) -> dict[str, Any]:
    return {"systeme": system, "source": source, "prevalence": reference_prevalence(probs, labels), "seuil_s2": S2_THRESHOLD_100, "fenetre": WINDOW, "run_seuil": RUN}


def cascade_argmax_probs(e: np.ndarray, g: np.ndarray, tau: float) -> np.ndarray:
    return np.asarray(cascade_probs(e, g, tau)[0])


def _load(name: str) -> tuple[list[str], np.ndarray, list[str]]:
    z = np.load(P / f"{name}.probs.npz", allow_pickle=False)
    return [str(i) for i in z["ids"]], z["probs"].astype(np.float64), [str(c) for c in z["labels"]]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("system", choices=["tfidf", "g-cascade"])
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    if a.system == "tfidf":
        _, probs, labels = _load(SOURCES["tfidf"])
        out = payload("tfidf", probs, labels, f"results/predictions/{SOURCES['tfidf']}.probs.npz")
    else:
        ids_e, e, labels = _load(SOURCES["e"])
        ids_g, g, labels_g = _load(SOURCES["g"])
        if labels_g != labels:
            raise ValueError("classes de E et de G dans des ordres différents")
        pos = {x: k for k, x in enumerate(ids_g)}
        out = payload("g-cascade", cascade_argmax_probs(e, g[[pos[x] for x in ids_e]], TAU), labels, f"cascade τ = {TAU} de {SOURCES['e']} et {SOURCES['g']}")
    Path(a.out).write_text(json.dumps(out, indent=1, ensure_ascii=False), encoding="utf-8")
    print(f"référence écrite : {a.out} ({len(out['prevalence'])} classes)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
