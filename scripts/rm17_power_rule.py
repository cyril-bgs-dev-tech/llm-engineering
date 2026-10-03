#!/usr/bin/env python3
"""RM-17 : règle de puissance (PROTOCOLE.md 6.3), à lancer une seule fois après P1-19 et P1-20, jamais avec une autre graine de bootstrap.

Lit les prédictions du pli 0 des runs `p1-19-s<k>` (k = 0 à 4). `--rehearsal` : répétition de la machinerie sur des fichiers de prédiction donnés
(pas des graines : aucun résultat, rien n'est enregistré). Usage : rm17_power_rule.py [--register] | --rehearsal FICHIER.json FICHIER.json FICHIER.json"""
import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent))
import p1_04_06_tfidf
from llmft import power_rule
from llmft.mini_registry import register_run


def main() -> int:
    rehearsal = "--rehearsal" in sys.argv
    files = [Path(a) for a in sys.argv[2:]] if rehearsal else [p for k in range(5) if (p := ROOT / f"results/predictions/p1-19-s{k}.json").exists()]
    _, y, folds, other, ids = p1_04_06_tfidf.load("chapter")
    labels = sorted(set(y))
    pool = [i for i, g in zip(ids, folds, strict=True) if g == 0]
    truth_of = dict(zip(ids, (labels.index(v) for v in y), strict=True))
    truth = np.array([truth_of[i] for i in pool])
    preds = []
    for f in files:
        d = json.loads(f.read_text(encoding="utf-8"))
        pm = dict(zip(d["ids"], d["pred"], strict=True))
        preds.append(np.array([labels.index(pm[i]) for i in pool]))
    summary = json.loads((ROOT / "results/measures/splits_summary.json").read_text(encoding="utf-8"))["test_class_counts"]
    counts = {labels.index(c): n for c, n in summary.items()}
    scored = [labels.index(c) for c in labels if c != other]
    widths = power_rule.pair_widths(truth, preds, counts, scored) if len(preds) >= 3 else []
    mean = float(np.mean(widths)) if widths else None
    passed = mean is not None and mean <= power_rule.THRESHOLD_POINTS
    out = {"graines": len(preds), "largeurs_par_paire": [round(w, 4) for w in widths], "largeur_moyenne": mean, "seuil": power_rule.THRESHOLD_POINTS, "regle": "réussite" if passed else "échec", "repetition": rehearsal}
    print(json.dumps(out, ensure_ascii=False, indent=1))
    if "--register" in sys.argv and not rehearsal:
        print(register_run(ROOT / "results/runs", {"kind": "measure", "slug": "rm-17-power-rule", "status": "ok", "summary": f"Règle de puissance RM-17 : largeur moyenne {mean}, règle {out['regle']}", "params": {"seed": power_rule.SEED, "n_boot": power_rule.N_BOOT}, "metrics": out}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
