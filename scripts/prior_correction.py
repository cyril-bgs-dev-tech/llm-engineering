#!/usr/bin/env python3
"""Audit GLM v4, A-c1 : correction de priorité à l'inférence, p' ∝ p / q^tau (q = prévalence d'entraînement des plis ≠ 0), pli 0, développement seulement.

tau est choisi sur une moitié stratifiée du pli 0 (macro-F1 maximale), évalué sur l'autre moitié, puis les deux rôles sont échangés. EXPLORE.
Usage : prior_correction.py PROBS.npz [PROBS.npz ...] [--register]"""
import json
import sys
from pathlib import Path

import numpy as np
from sklearn.model_selection import StratifiedKFold

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent))
import p1_04_06_tfidf
from llmft.mini_registry import register_run
from llmft.power_rule import _macro_f1

TAUS = (0.0, 0.25, 0.5, 0.75, 1.0)


def score(p: np.ndarray, tt: np.ndarray, tau: float, q: np.ndarray, scored: list[int]) -> float:
    adj = p / q**tau
    return float(_macro_f1(tt[None, :], adj.argmax(1)[None, :], scored)[0])


def main() -> int:
    files = [a for a in sys.argv[1:] if not a.startswith("--")]
    _, y, folds, other, ids = p1_04_06_tfidf.load("chapter")
    truth = dict(zip(ids, y, strict=True))
    out = {}
    for f in files:
        z = np.load(f, allow_pickle=False)
        labels = [str(c) for c in z["labels"]]
        pid = [str(i) for i in z["ids"]]
        probs = z["probs"].astype(np.float64)
        t = np.array([labels.index(truth[i]) for i in pid])
        train_counts = np.bincount([labels.index(v) for v, g in zip(y, folds, strict=True) if g != 0], minlength=len(labels)).astype(float)
        q = np.clip(train_counts / train_counts.sum(), 1e-6, 1)
        scored = [labels.index(c) for c in labels if c != other]

        by_tau = {tau: [] for tau in TAUS}
        chosen = []
        for a, b in StratifiedKFold(2, shuffle=True, random_state=1000).split(probs, t):
            for sel, ev in ((a, b), (b, a)):
                best = max(TAUS, key=lambda tau, s=sel: (score(probs[s], t[s], tau, q, scored), -tau))
                chosen.append(best)
                for tau in TAUS:
                    by_tau[tau].append(score(probs[ev], t[ev], tau, q, scored))
        res = {"n": len(pid), "tau_choisi_par_moitie": chosen, "macro_f1_evaluee_par_tau": {str(k): round(float(np.mean(v)), 4) for k, v in by_tau.items()},
               "macro_f1_avec_tau_choisi": round(float(np.mean([by_tau[c][i] for i, c in enumerate(chosen)])), 4)}
        out[Path(f).name] = res
        print(Path(f).name, res)
    (ROOT / "results/measures/prior_correction.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
    if "--register" in sys.argv:
        print(register_run(ROOT / "results/runs", {"kind": "measure", "slug": "prior-correction-fold0", "status": "ok", "summary": "Correction de priorité à l'inférence (tau choisi sur une moitié du pli 0)", "params": {"taus": list(TAUS)}, "metrics": out}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
