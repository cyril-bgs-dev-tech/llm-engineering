#!/usr/bin/env python3
"""Puissance au format du test scellé (633 patients) : largeur de l'IC de la différence de macro-F1 entre deux systèmes, bootstrap de patients stratifié par classe avec pour tailles de strate
les effectifs du test scellé (`test_class_counts`, aucun identifiant ni étiquette du test lus), tirage dans le pool hors pli des cinq plis (3 586 prédictions), R = 10 000, graine 20261002,
niveaux 95 % et 98,33 % ; même méthode que la règle de puissance v1 (PROTOCOLE.md 6.3) mais pour des paires de systèmes. Développement seulement. Usage : power_at_test_size.py [--register]"""
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
SYSTEMS = {"TF-IDF": "tfidf-variant-char-balanced", "encodeur": "cinq-plis-ensemble-encodeur5", "ensemble": "cinq-plis-ensemble-encodeur5-tfidf-charbal", "LoRA": "cinq-plis-llm-mur",
           "élève distillé (ensemble)": "cinq-plis-distill-ens-3graines"}
PAIRS = [("ensemble", "TF-IDF"), ("élève distillé (ensemble)", "TF-IDF"), ("LoRA", "TF-IDF"), ("élève distillé (ensemble)", "ensemble"), ("élève distillé (ensemble)", "LoRA")]
R, SEED = 10_000, 20261002


def load(name: str) -> tuple[list[str], np.ndarray, list[str]]:
    z = np.load(P / f"{name}.probs.npz", allow_pickle=False)
    return [str(i) for i in z["ids"]], z["probs"].astype(np.float64), [str(c) for c in z["labels"]]


def main() -> int:
    counts = json.loads((ROOT / "results/measures/splits_summary.json").read_text(encoding="utf-8"))["test_class_counts"]
    _, y, _, other, ids_all = p1_04_06_tfidf.load("chapter")
    truth_of = dict(zip(ids_all, y, strict=True))
    ids, _, labels = load("cinq-plis-ensemble-encodeur5")
    truth = np.array([labels.index(truth_of[i]) for i in ids])
    scored = [labels.index(c) for c in labels if c != other]
    preds = {}
    for n, f in SYSTEMS.items():
        i2, p, _ = load(f)
        pos = {x: k for k, x in enumerate(i2)}
        preds[n] = p[[pos[i] for i in ids]].argmax(1)
    rng = np.random.default_rng(SEED)
    by_class = {labels.index(c): np.flatnonzero(truth == labels.index(c)) for c in counts}
    idx = np.concatenate([by_class[c][rng.integers(0, len(by_class[c]), size=(R, counts[labels[c]]))] for c in sorted(by_class)], axis=1)
    t = truth[idx]
    out = {}
    for a, b in PAIRS:
        diff = _macro_f1(t, preds[a][idx], scored) - _macro_f1(t, preds[b][idx], scored)
        row = {}
        for level, name in ((0.95, "95"), (0.9833, "98_33")):
            lo, hi = np.percentile(diff, [100 * (1 - level) / 2, 100 * (1 + level) / 2])
            row[name] = {"largeur_points": round(100 * float(hi - lo), 2), "ic": [round(100 * float(lo), 2), round(100 * float(hi), 2)]}
        full = _macro_f1(truth[None, :], preds[a][None, :], scored)[0] - _macro_f1(truth[None, :], preds[b][None, :], scored)[0]
        row["difference_observee_developpement_points"] = round(100 * float(full), 2)
        out[f"{a} moins {b}"] = row
        print(a, "moins", b, row, flush=True)
    (ROOT / "results/measures/power_at_test_size.json").write_text(json.dumps(out, indent=1, ensure_ascii=False), encoding="utf-8")
    if "--register" in sys.argv:
        print(register_run(ROOT / "results/runs", {"kind": "measure", "slug": "puissance-au-format-du-test-scelle", "status": "ok", "summary": "Largeur attendue des IC au format du test scellé (633), paires de systèmes", "params": {"R": R, "seed": SEED}, "metrics": out}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
