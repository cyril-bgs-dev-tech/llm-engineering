#!/usr/bin/env python3
"""Taille de l'échantillon étiqueté qui surveille la qualité du service (suite de P5-08, fiche 2026-10-17-taille-echantillon-etiquete, EXPLORE, développement,
processeur seulement) : seuil d'alerte au 5e centile des lots de référence (substitut E′ en plis par patient), puissance contre de nouveaux auteurs (A100 : tout
le lot en plis par auteur ; A40 : 40 % des patients), pour la macro-F1 regroupée et l'exactitude. Calcul fait deux fois, tampon de santé au registre.
Aucun GPU, test scellé jamais lu. Usage : audit_sample_size.py [--register]"""
import json
import sys
from pathlib import Path
from typing import Any

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent))
import p1_04_06_tfidf
import simulate_drift
from llmft import machine_health
from llmft.drift import draw_lots, low_tail_power
from llmft.mini_registry import register_run
from llmft.power_rule import _macro_f1
from llmft.resilience import agree_twice

FICHE = "experiments/2026-10-17-taille-echantillon-etiquete.md"
SIZES, DRAWS, SEED, ALPHA, MIN_POWER, MIX = (100, 200, 500, 1000, 2000), 2000, 20261017, 0.05, 0.80, 0.4
METRICS = ("macro_f1", "exactitude")


def recommend(power: dict[str, dict[str, float]]) -> dict[str, Any]:
    """Critère écrit d'avance : par métrique, plus petite taille dont la puissance pour A100 atteint 0,80 ; métrique recommandée = plus petite taille, macro-F1 en cas d'égalité."""
    by_metric = {m: next((n for n in SIZES if power[m][str(n)] >= MIN_POWER), None) for m in METRICS}
    reachable = [(n, METRICS.index(m), m) for m, n in by_metric.items() if n is not None]
    if not reachable:
        return {"taille_par_metrique": by_metric, "metrique_recommandee": None, "taille_recommandee": None, "lecture": "au-delà de 2 000 patients"}
    n, _, m = min(reachable)
    return {"taille_par_metrique": by_metric, "metrique_recommandee": m, "taille_recommandee": n, "lecture": f"{m} sur {n} patients étiquetés"}


def compute() -> dict[str, Any]:
    _, y, _, other, ids_all = p1_04_06_tfidf.load("chapter")
    z = np.load(simulate_drift.P / f"{simulate_drift.E_FILE}.probs.npz", allow_pickle=False)
    ids, labels = [str(i) for i in z["ids"]], [str(c) for c in z["labels"]]
    y_of = dict(zip(ids_all, y, strict=True))
    truth = np.array([labels.index(y_of[i]) for i in ids])
    scored = [k for k, c in enumerate(labels) if c != other]
    pred = {part: (0.5 * simulate_drift.mean_over_seeds(enc, labels, ids) + 0.5 * simulate_drift.single(tf, labels, ids)).argmax(axis=1)
            for part, (enc, tf) in simulate_drift.PROXY.items()}
    rng = np.random.default_rng(SEED)
    mixed = np.where(rng.random(len(ids)) < MIX, pred["auteur"], pred["patient"])  # A40 : un tirage par patient, fixé pour tous les lots

    def metric(name: str, lots: np.ndarray, p: np.ndarray) -> np.ndarray:
        if name == "macro_f1":
            return _macro_f1(truth[lots], p[lots], scored) * 100
        return np.asarray((truth[lots] == p[lots]).mean(axis=1) * 100, dtype=float)

    out: dict[str, Any] = {"n_patients": len(ids), "lots": DRAWS, "graine": SEED, "alpha": ALPHA, "part_nouveaux_auteurs_a40": MIX,
                           "jeu_entier": {part: {"macro_f1": round(float(metric("macro_f1", np.arange(len(ids))[None, :], p)[0]), 2),
                                                 "exactitude": round(float(metric("exactitude", np.arange(len(ids))[None, :], p)[0]), 2)} for part, p in (("patient", pred["patient"]), ("auteur", pred["auteur"]), ("a40", mixed))},
                           "par_taille": {}, "puissance_a100": {m: {} for m in METRICS}}
    for n in SIZES:
        lots = draw_lots(len(ids), n, DRAWS, SEED + n)
        row: dict[str, Any] = {}
        for m in METRICS:
            ref = metric(m, lots, pred["patient"])
            thr, p100 = low_tail_power(ref, metric(m, lots, pred["auteur"]), ALPHA)
            _, p40 = low_tail_power(ref, metric(m, lots, mixed), ALPHA)
            row[m] = {"seuil": round(thr, 2), "fausse_alerte": round(float(np.mean(ref < thr)), 4), "puissance_a100": round(p100, 4), "puissance_a40": round(p40, 4)}
            out["puissance_a100"][m][str(n)] = round(p100, 4)
        out["par_taille"][str(n)] = row
    rec = recommend(out["puissance_a100"])
    if rec["taille_recommandee"] is not None:
        rec["puissance_a40_a_cette_taille"] = out["par_taille"][str(rec["taille_recommandee"])][rec["metrique_recommandee"]]["puissance_a40"]
    out["decision"] = rec
    return out


def main() -> int:
    start = machine_health.snapshot()
    out = agree_twice(compute, equal=lambda a, b: json.dumps(a, sort_keys=True) == json.dumps(b, sort_keys=True))
    print(json.dumps(out, indent=1, ensure_ascii=False))
    if "--register" in sys.argv:
        (ROOT / "results/measures/taille_echantillon_etiquete.json").write_text(json.dumps(out, indent=1, ensure_ascii=False), encoding="utf-8")
        print(register_run(ROOT / "results/runs", {"kind": "measure", "slug": "taille-echantillon-etiquete", "status": "ok", "summary": f"échantillon étiqueté de surveillance : {out['decision']['lecture']}",
                                                    "params": {"fiche": FICHE, "tailles": list(SIZES), "lots": DRAWS, "graine": SEED, "alpha": ALPHA, "part_a40": MIX},
                                                    "metrics": out, "machine_health": machine_health.stamp(start)}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
