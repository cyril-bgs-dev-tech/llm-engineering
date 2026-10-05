#!/usr/bin/env python3
"""Aperçu de la règle de sélection du système final (RM-50, brouillon) sur les prédictions hors pli regroupées : macro-F1 de chaque candidat disponible, borne basse de
(candidat moins meilleur) par bootstrap d'auteurs, admissibilité (delta = 2,0) et système retenu par la règle. N'engage rien : le gel est une décision séparée (RM-37 puis RM-50).
Usage : final_selection_preview.py [--sans-eleves] [--register]
--sans-eleves : écarte C1 et C2 (PROTOCOLE_V2.md section 4, condition de maintien non remplie après RM-56) ; slug du run : selection-systeme-final-apres-rm56."""
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent))
import p1_04_06_tfidf
from llmft import selection
from llmft.cluster_bootstrap import cluster_interval
from llmft.mini_registry import register_run
from llmft.power_rule import _macro_f1

P = ROOT / "results/predictions"
CANDIDATES = [  # (nom, rang de coût, fichier de probabilités regroupées ou liste de fichiers à moyenner)
    ("A TF-IDF caractères équilibré", 0, ["tfidf-variant-char-balanced"]),
    ("B TF-IDF souple (professeur ensemble)", 0, ["tfidf-souple-ens"]),
    ("C1 élève encodeur distillé du LoRA (3 graines)", 1, ["cinq-plis-distill-lora-3graines"]),
    ("C2 élève encodeur distillé de l'ensemble (3 graines)", 1, ["cinq-plis-distill-ens-3graines"]),
    ("D encodeur moyenné (5 graines)", 2, ["cinq-plis-ensemble-encodeur5"]),
    ("E ensemble encodeur + TF-IDF", 3, ["cinq-plis-ensemble-encodeur5-tfidf-charbal"]),
    ("F LoRA 4B", 4, ["cinq-plis-llm-mur"]),
    ("G ensemble LoRA + encodeur + TF-IDF", 5, ["cinq-plis-llm-mur", "cinq-plis-ensemble-encodeur5", "tfidf-variant-char-balanced"]),
]


def load(name: str) -> tuple[list[str], np.ndarray, list[str]]:
    z = np.load(P / f"{name}.probs.npz", allow_pickle=False)
    return [str(i) for i in z["ids"]], z["probs"].astype(np.float64), [str(c) for c in z["labels"]]


def aligned(name: str, ids: list[str]) -> np.ndarray:
    i, p, _ = load(name)
    pos = {x: k for k, x in enumerate(i)}
    return p[[pos[x] for x in ids]]


def main() -> int:
    _, y, _, other, ids_all = p1_04_06_tfidf.load("chapter")
    truth_of = dict(zip(ids_all, y, strict=True))
    meta = pd.read_parquet(p1_04_06_tfidf.PARQUET, columns=["id", "author"])
    author_of = dict(zip(meta["id"].astype(str), meta["author"], strict=True))
    ids, _, labels = load("cinq-plis-ensemble-encodeur5")
    truth = np.array([labels.index(truth_of[i]) for i in ids])
    scored = [labels.index(c) for c in labels if c != other]
    groups = [author_of[i] for i in ids]
    preds: dict[str, tuple[int, np.ndarray]] = {}
    sans_eleves = "--sans-eleves" in sys.argv
    for name, rank, files in CANDIDATES:
        if sans_eleves and name[:2] in ("C1", "C2"):
            continue
        if all((P / f"{f}.probs.npz").exists() for f in files):
            preds[name] = (rank, np.mean([aligned(f, ids) for f in files], axis=0))
    scores = {n: float(_macro_f1(truth[None, :], p.argmax(1)[None, :], scored)[0]) for n, (_, p) in preds.items()}
    best = max(scores, key=lambda n: scores[n])
    cands = []
    rows = {}
    for n, (rank, p) in preds.items():
        if n == best:
            lower = 0.0
        else:
            _, lower, _ = cluster_interval(truth, p.argmax(1), preds[best][1].argmax(1), scored, groups)
        cands.append(selection.Candidate(n, rank, scores[n], lower))
        rows[n] = {"macro_f1": round(scores[n], 4), "borne_basse_contre_meilleur_points": round(lower, 2), "admissible": selection.admissible(cands[-1])}
    chosen = selection.select_final(cands)
    out = {"meilleur": best, "candidats": rows, "retenu_par_la_regle": chosen.name, "delta_points": 2.0, "n": len(ids)}
    print(json.dumps(out, indent=1, ensure_ascii=False))
    if "--register" in sys.argv:
        print(register_run(ROOT / "results/runs", {"kind": "measure", "slug": "selection-systeme-final-apres-rm56" if sans_eleves else "apercu-selection-systeme-final", "status": "ok", "summary": f"Règle de sélection{' sans les élèves (RM-56)' if sans_eleves else ' (aperçu)'} : meilleur {best}, retenu {chosen.name}", "params": {"delta": 2.0}, "metrics": out}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
