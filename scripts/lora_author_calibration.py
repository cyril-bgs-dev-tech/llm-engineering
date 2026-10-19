#!/usr/bin/env python3
"""Étalonnage par température du LoRA à fin aléatoire en plis d'auteurs (fiche 2026-10-17-etalonnage-nouveaux-auteurs, suite de RM-62, EXPLORE, développement,
processeur seulement) : température apprise sur les quatre autres plis (autres auteurs) contre température apprise dans le même pli (deux moitiés stratifiées
de patients, mêmes auteurs). Calcul fait deux fois, tampon de santé au registre. Aucun GPU, test scellé jamais lu. À lancer après le lot RM-62.
Usage : lora_author_calibration.py [--register]"""
import json
import sys
from collections.abc import Sequence
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
from numpy.typing import NDArray
from sklearn.model_selection import StratifiedKFold

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent))
import p1_04_06_tfidf
from llmft import machine_health, metrics
from llmft.calibration import apply_temperature, fit_temperature
from llmft.mini_registry import register_run
from llmft.resilience import agree_twice

FICHE = "experiments/2026-10-17-etalonnage-nouveaux-auteurs.md"
SLUG = "lora-fin-aleatoire-auteur-pli{k}"
TRANSPORTABLE, NOT_TRANSPORTABLE, AUTHOR_GAP = 0.05, 0.08, 0.02
DRAWS, SEED, HALVES_SEED = 2000, 20261017, 1000
DECISION_CONSTANTS = (TRANSPORTABLE, NOT_TRANSPORTABLE, AUTHOR_GAP, DRAWS, SEED, HALVES_SEED)  # N41 : confrontées au texte de la fiche (scripts/check_fiches.py)


def verdict(ece_transported: float) -> str:
    """Critère écrit d'avance, sur le point estimé."""
    e = round(ece_transported, 6)
    return "étalonnage transportable" if e <= TRANSPORTABLE else "non transportable" if e >= NOT_TRANSPORTABLE else "partiel"


def author_reading(ece_transported: float, ece_within: float) -> str:
    return "dépend des auteurs" if round(ece_transported - ece_within, 6) > AUTHOR_GAP else "ne dépend pas des auteurs"


def transported(probs: NDArray[np.float64], y: NDArray[np.int_], fold: NDArray[np.int_]) -> tuple[NDArray[np.float64], list[float]]:
    """Pli k étalonné par la température apprise sur tous les autres plis : ses étiquettes ne sont jamais lues pour lui."""
    out, temps = np.empty_like(probs), []
    for k in sorted(set(fold.tolist())):
        t = fit_temperature(probs[fold != k], y[fold != k])
        out[fold == k] = apply_temperature(probs[fold == k], t)
        temps.append(t)
    return out, temps


def within_fold(probs: NDArray[np.float64], y: NDArray[np.int_], fold: NDArray[np.int_], seed: int = HALVES_SEED) -> NDArray[np.float64]:
    """Dans chaque pli, deux moitiés stratifiées de patients : chaque moitié étalonnée par la température apprise sur l'autre (méthode de q5_uncertainty)."""
    out = np.empty_like(probs)
    for k in sorted(set(fold.tolist())):
        idx = np.flatnonzero(fold == k)
        for fit_idx, apply_idx in StratifiedKFold(2, shuffle=True, random_state=seed).split(probs[idx], y[idx]):
            out[idx[apply_idx]] = apply_temperature(probs[idx[apply_idx]], fit_temperature(probs[idx[fit_idx]], y[idx[fit_idx]]))
    return out


def author_block_interval(probs: NDArray[np.float64], y: NDArray[np.int_], groups: Sequence[str], draws: int = DRAWS, seed: int = SEED) -> tuple[float, float]:
    """Intervalle à 95 % de l'ECE par bootstrap des auteurs (tous les patients d'un auteur tirés ensemble)."""
    members: dict[str, list[int]] = {}
    for i, g in enumerate(groups):
        members.setdefault(g, []).append(i)
    blocks = [np.array(v) for v in members.values()]
    rng = np.random.default_rng(seed)
    values = []
    for _ in range(draws):
        rows = np.concatenate([blocks[j] for j in rng.integers(0, len(blocks), len(blocks))])
        values.append(metrics.ece(probs[rows], y[rows]))
    return float(np.percentile(values, 2.5)), float(np.percentile(values, 97.5))


def compute() -> dict[str, Any]:
    _, y_all, folds_all, _, ids_all = p1_04_06_tfidf.load("chapter", "control_folds_by_author")
    y_of, fold_of = dict(zip(ids_all, y_all, strict=True)), dict(zip(ids_all, folds_all.tolist(), strict=True))
    ids: list[str] = []
    parts, labels = [], None
    for k in range(5):
        z = np.load(ROOT / "results/predictions" / f"{SLUG.format(k=k)}.probs.npz", allow_pickle=False)
        file_labels = [str(c) for c in z["labels"]]
        assert labels is None or file_labels == labels, "classes différentes d'un pli à l'autre"
        labels = file_labels
        fold_ids = [str(i) for i in z["ids"]]
        assert all(fold_of[i] == k for i in fold_ids), f"pli {k} : patients hors du pli d'auteurs attendu"
        ids += fold_ids
        parts.append(z["probs"].astype(np.float64))
    assert labels is not None and len(ids) == len(set(ids)) == len(ids_all), "les cinq plis doivent couvrir chaque patient une fois"
    probs = np.concatenate(parts)
    y = np.array([labels.index(y_of[i]) for i in ids])
    fold = np.array([fold_of[i] for i in ids])
    meta = pd.read_parquet(p1_04_06_tfidf.PARQUET, columns=["id", "author"])
    author_of = dict(zip(meta["id"].astype(str), meta["author"], strict=True))
    groups = [str(author_of[i]) for i in ids]
    cal_t, temps = transported(probs, y, fold)
    cal_w = within_fold(probs, y, fold)
    e_raw, e_t, e_w = metrics.ece(probs, y), metrics.ece(cal_t, y), metrics.ece(cal_w, y)
    lo, hi = author_block_interval(cal_t, y, groups)
    return {"n_patients": len(ids), "n_auteurs": len(set(groups)),
            "ece_brute": round(e_raw, 4), "ece_transportee": round(e_t, 4), "ece_transportee_ic95_blocs_auteurs": [round(lo, 4), round(hi, 4)],
            "ece_meme_pli": round(e_w, 4), "temperatures_transportees": [round(t, 3) for t in temps],
            "log_loss": {"brute": round(metrics.log_loss(probs, y), 4), "transportee": round(metrics.log_loss(cal_t, y), 4), "meme_pli": round(metrics.log_loss(cal_w, y), 4)},
            "exactitude": {"brute": round(float((probs.argmax(1) == y).mean()), 4), "transportee": round(float((cal_t.argmax(1) == y).mean()), 4)},
            "verdict": verdict(e_t), "lecture_auteurs": author_reading(e_t, e_w),
            "reference_par_patient": {"run": "20261004-071613-q5-uncertainty-llm-mur2-fold0", "ece_brute": 0.110, "ece_apres_temperature": 0.028}}


def main() -> int:
    start = machine_health.snapshot()
    out = agree_twice(compute, equal=lambda a, b: json.dumps(a, sort_keys=True) == json.dumps(b, sort_keys=True))
    print(json.dumps(out, indent=1, ensure_ascii=False))
    if "--register" in sys.argv:
        (ROOT / "results/measures/etalonnage_nouveaux_auteurs.json").write_text(json.dumps(out, indent=1, ensure_ascii=False), encoding="utf-8")
        print(register_run(ROOT / "results/runs", {"kind": "measure", "slug": "etalonnage-nouveaux-auteurs", "status": "ok",
                                                    "summary": f"étalonnage du LoRA en plis d'auteurs : ECE {out['ece_brute']} brute, {out['ece_transportee']} après température transportée ({out['verdict']})",
                                                    "params": {"fiche": FICHE, "tirages": DRAWS, "graine": SEED, "graine_moities": HALVES_SEED},
                                                    "metrics": out, "machine_health": machine_health.stamp(start)}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
