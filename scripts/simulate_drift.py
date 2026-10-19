#!/usr/bin/env python3
"""Simulation de dérive (P5-08, fiche 2026-10-17-simulation-derive, EXPLORE, développement, processeur seulement) : seuils d'alerte des signaux sans étiquette
(S1 baisse de la part servie par E seul, S2 prévalence des chapitres prédits, S3 longueurs) mesurés sur des lots tirés de la référence hors pli, puis taux de détection
et impact sur la macro-F1 de trois scénarios (A nouveaux auteurs sur le substitut E′, B prévalence, C textes courts). Calcul fait deux fois (`agree_twice`),
tampon de santé au registre. Aucun GPU, test scellé jamais lu. Usage : simulate_drift.py [--register]"""
import json
import sys
from pathlib import Path
from typing import Any

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent))
import p1_04_06_tfidf
from llmft import machine_health
from llmft.drift import KS_ALERT, TV_ALERT, alert_threshold, detection_rate, draw_lots, lot_signals
from llmft.mini_registry import register_run
from llmft.power_rule import _macro_f1
from llmft.resilience import agree_twice

P = ROOT / "results/predictions"
FICHE = "experiments/2026-10-17-simulation-derive.md"
E_FILE = "cinq-plis-ensemble-encodeur5-tfidf-charbal"
PROXY = {"patient": ("enc2-bf16", "tfidf-variant-char-balanced"), "auteur": ("enc-auteur", "tfidf-variant-char-balanced-author")}
TAU, Q, DRAWS, SEED, SIZES, WEIGHT = 0.6, 0.99, 2000, 20261017, (100, 200, 500), 3.0
DELTA, MIN_DETECTION, DECISION_SIZE = 2.0, 0.80, 200
SIGNALS = ("s1_baisse_part_e", "s2_tv_prevalence_predite", "s3_ks_longueur")


def _rows(path: Path, labels: list[str]) -> dict[str, list[np.ndarray]]:
    z = np.load(path, allow_pickle=False)
    if [str(c) for c in z["labels"]] != labels:
        raise ValueError(f"classes de {path.name} dans un autre ordre que E")
    return {str(i): [r] for i, r in zip(z["ids"], z["probs"].astype(np.float64), strict=True)}


def mean_over_seeds(prefix: str, labels: list[str], ids: list[str]) -> np.ndarray:
    rows: dict[str, list[np.ndarray]] = {}
    for f in sorted(P.glob(f"{prefix}-pli[0-4]-s[0-9].probs.npz")):
        for i, r in _rows(f, labels).items():
            rows.setdefault(i, []).extend(r)
    if {len(v) for v in rows.values()} != {3} or set(rows) != set(ids):
        raise ValueError(f"{prefix} : trois graines attendues pour chacun des {len(ids)} patients")
    return np.stack([np.mean(rows[i], axis=0) for i in ids])


def single(name: str, labels: list[str], ids: list[str]) -> np.ndarray:
    rows = _rows(P / f"{name}.probs.npz", labels)
    return np.stack([rows[i][0] for i in ids])


def signals_of(lots: np.ndarray, probs: np.ndarray, lengths: np.ndarray, ref_probs: np.ndarray, ref_lengths: np.ndarray) -> dict[str, np.ndarray]:
    per_lot = [lot_signals(probs[lot], lengths[lot], ref_probs, ref_lengths, TAU) for lot in lots]
    return {s: np.array([d[s] for d in per_lot]) for s in SIGNALS}


def f1_of(lots: np.ndarray, probs: np.ndarray, truth: np.ndarray, scored: list[int]) -> np.ndarray:
    return _macro_f1(truth[lots], probs.argmax(axis=1)[lots], scored) * 100


def compute() -> dict[str, Any]:
    texts, y, _, other, ids_all = p1_04_06_tfidf.load("chapter")
    z = np.load(P / f"{E_FILE}.probs.npz", allow_pickle=False)
    ids, e, labels = [str(i) for i in z["ids"]], z["probs"].astype(np.float64), [str(c) for c in z["labels"]]
    text_of, y_of = dict(zip(ids_all, texts, strict=True)), dict(zip(ids_all, y, strict=True))
    truth = np.array([labels.index(y_of[i]) for i in ids])
    lengths = np.array([len(text_of[i]) for i in ids], dtype=float)
    scored = [k for k, c in enumerate(labels) if c != other]
    proxy = {part: 0.5 * mean_over_seeds(enc, labels, ids) + 0.5 * single(tf, labels, ids) for part, (enc, tf) in PROXY.items()}
    frequent = max(scored, key=lambda c: int((truth == c).sum()))
    weights = {"b_prevalence": np.where(truth == frequent, WEIGHT, 1.0), "c_textes_courts": np.where(lengths <= np.quantile(lengths, 0.25), WEIGHT, 1.0)}
    n_items = len(ids)
    out: dict[str, Any] = {"n_patients": n_items, "tau": TAU, "q": Q, "lots": DRAWS, "graine": SEED, "chapitre_frequent": labels[frequent],
                           "part_e_reference": round(float(np.mean(e.max(axis=1) >= TAU)), 4),
                           "part_e_substitut": {p: round(float(np.mean(v.max(axis=1) >= TAU)), 4) for p, v in proxy.items()},
                           "macro_f1_reference": round(float(f1_of(np.arange(n_items)[None, :], e, truth, scored)[0]), 2),
                           "macro_f1_substitut": {p: round(float(f1_of(np.arange(n_items)[None, :], v, truth, scored)[0]), 2) for p, v in proxy.items()},
                           "seuils": {}, "scenarios": {}}
    for n in SIZES:
        null_lots = draw_lots(n_items, n, DRAWS, SEED + n)
        thresholds, f1_null = {}, {}
        for ref_name, ref in (("e", e), ("substitut", proxy["patient"])):
            stats = signals_of(null_lots, ref, lengths, ref, lengths)
            thr = {s: alert_threshold(stats[s], Q) for s in SIGNALS}
            union = float(np.mean(np.any([stats[s] > thr[s] for s in SIGNALS], axis=0)))
            thresholds[ref_name] = thr
            f1_null[ref_name] = f1_of(null_lots, ref, truth, scored)
            out["seuils"].setdefault(ref_name, {})[str(n)] = {**{s: round(v, 4) for s, v in thr.items()}, "fausse_alerte_union": round(union, 4),
                                                              "fausse_alerte_seuils_actuels": {"s2_tv_0_15": round(detection_rate(stats["s2_tv_prevalence_predite"], TV_ALERT), 4),
                                                                                               "s3_ks_0_2": round(detection_rate(stats["s3_ks_longueur"], KS_ALERT), 4)}}
        lots_a = draw_lots(n_items, n, DRAWS, SEED + 10_000 + n)
        stats_a = signals_of(lots_a, proxy["auteur"], lengths, proxy["patient"], lengths)
        impact_a = f1_of(lots_a, proxy["auteur"], truth, scored) - f1_of(lots_a, proxy["patient"], truth, scored)
        scen = {"a_nouveaux_auteurs": (stats_a, thresholds["substitut"], impact_a)}
        for k, (name, w) in enumerate(weights.items()):
            lots = draw_lots(n_items, n, DRAWS, SEED + 20_000 * (k + 1) + n, weights=w)
            scen[name] = (signals_of(lots, e, lengths, e, lengths), thresholds["e"], f1_of(lots, e, truth, scored) - float(np.mean(f1_null["e"])))
        for name, (stats, thr, impact) in scen.items():
            out["scenarios"].setdefault(name, {})[str(n)] = {"detection": {s: round(detection_rate(stats[s], thr[s]), 4) for s in SIGNALS},
                                                              "impact_macro_f1_points": round(float(np.mean(impact)), 2),
                                                              "impact_centiles_5_95": [round(float(np.quantile(impact, 0.05)), 2), round(float(np.quantile(impact, 0.95)), 2)]}
    out["decision"] = decide(out["scenarios"])
    return out


def decide(scenarios: dict[str, Any]) -> dict[str, Any]:
    """Critère écrit d'avance : nuisible si impact moyen ≤ −δ (à n = 200, taille de décision) ; signal retenu si détection ≥ 0,80 à n = 200 ; règle = union des signaux
    **retenus** pour un scénario nuisible, à la plus petite taille où chacun atteint 0,80 ; scénario nuisible sans signal à 0,80 pour n = 500 : « non surveillable sans étiquettes ».
    `signaux_a_500` : signaux qui n'atteignent 0,80 qu'à n = 500 au plus, rapportés à part (seconde lecture de la fiche, écart déclaré dans experiments/INDEX.md)."""
    out: dict[str, Any] = {"scenarios": {}, "regle_alerte": {}}
    for name, by_n in scenarios.items():
        at = by_n[str(DECISION_SIZE)]
        harmful = round(at["impact_macro_f1_points"], 6) <= -DELTA
        kept = [s for s in SIGNALS if at["detection"][s] >= MIN_DETECTION and not (name == "a_nouveaux_auteurs" and s == "s3_ks_longueur")]
        reachable = [s for s in SIGNALS if by_n[str(max(SIZES))]["detection"][s] >= MIN_DETECTION and not (name == "a_nouveaux_auteurs" and s == "s3_ks_longueur")]
        out["scenarios"][name] = {"nuisible": harmful, "signaux_retenus": kept, "signaux_a_500": reachable, "non_surveillable_sans_etiquettes": harmful and not reachable}
        if harmful:
            for s in kept:
                n_min = min(n for n in SIZES if by_n[str(n)]["detection"][s] >= MIN_DETECTION)
                out["regle_alerte"][s] = min(out["regle_alerte"].get(s, n_min), n_min)
    return out


def main() -> int:
    start = machine_health.snapshot()
    out = agree_twice(compute, equal=lambda a, b: json.dumps(a, sort_keys=True) == json.dumps(b, sort_keys=True))
    print(json.dumps(out, indent=1, ensure_ascii=False))
    if "--register" in sys.argv:
        (ROOT / "results/measures/simulation_derive.json").write_text(json.dumps(out, indent=1, ensure_ascii=False), encoding="utf-8")
        d = out["decision"]
        summary = "simulation de dérive : " + " ; ".join(f"{k} {'nuisible' if v['nuisible'] else 'non nuisible'}, retenus {v['signaux_retenus'] or 'aucun'}" for k, v in d["scenarios"].items())
        print(register_run(ROOT / "results/runs", {"kind": "measure", "slug": "simulation-derive", "status": "ok", "summary": summary,
                                                    "params": {"fiche": FICHE, "tau": TAU, "q": Q, "lots": DRAWS, "graine": SEED, "tailles": list(SIZES), "poids": WEIGHT},
                                                    "metrics": out, "machine_health": machine_health.stamp(start)}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
