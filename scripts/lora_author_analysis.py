#!/usr/bin/env python3
"""Analyse du LoRA à fin aléatoire en plis groupés par auteur (RM-62, fiche 2026-10-17-lora-fin-aleatoire-plis-auteurs) : prédictions regroupées des cinq plis,
comparaison avec le TF-IDF et l'encodeur sur les mêmes plis (bootstrap par blocs d'auteurs, verdict à trois valeurs, δ = 2,0), perte par rapport aux plis par patient,
réplication de la correction de la fin de texte (diagnostics de robustesse par pli), calibration et couverture conforme étalonnée en croisé sur les plis d'auteurs.
Calcul fait deux fois (`agree_twice`), tampon de santé au registre. Usage : lora_author_analysis.py [--register] | --regle-arret (règle N31 (1) après les plis 0 et 1 : code 10 = arrêt) | --sante K (règle N31 (3) : code 11 = pause) ; tout autre code non nul est une erreur. Développement seulement."""
import glob
import json
import re
import sys
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
from numpy.typing import NDArray

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent))
import glm_v3_families
import p1_04_06_tfidf
from llmft import conformal, evaluation, machine_health
from llmft.cluster_bootstrap import cluster_interval
from llmft.mini_registry import register_run
from llmft.power_rule import _macro_f1
from llmft.resilience import agree_twice

DELTA = 2.0
ALPHA = 0.10
ENCODER_LOSS = 5.23  # run 20261006-213214-encodeur-plis-auteurs-analyse
LORA_PATIENT = 0.7673  # LoRA mûr à cinq plis par patient, sans fin aléatoire (run 20261005-145138-selection-systeme-final-apres-rm56)
TFIDF_AUTHOR_FILE = "tfidf-variant-char-balanced-author"
SLUG = "lora-fin-aleatoire-auteur-pli{k}"
STOP_CODE, PAUSE_CODE = 10, 11  # distincts du code 1 d'une exception Python : une panne du contrôle n'est jamais lue comme une règle


def verdict(lo: float, hi: float) -> str:
    return "gain confirmé" if lo > DELTA else ("absence de gain utile" if hi < DELTA else "non résolu")


def loss_reading(loss: float) -> str:
    return "plus faible" if loss < ENCODER_LOSS - 1.0 else ("comparable" if loss <= ENCODER_LOSS + 1.0 else "plus forte")


def correction_label(clean_and_tail30: Sequence[tuple[float, float]]) -> str:
    """« correction répliquée » si au moins quatre plis perdent au plus 5 points de macro-F1 quand 30 % de la fin du texte est retirée (valeurs en fraction)."""
    kept = sum(1 for clean, tail in clean_and_tail30 if round((clean - tail) * 100, 6) <= 5.0)  # arrondi : 0,78 − 0,73 vaut 5,000000000000004 en flottant
    return "correction répliquée" if kept >= 4 else "non répliquée"


def early_stop(lora_f1: Sequence[float], tfidf_f1: Sequence[float]) -> bool:
    """Règle N31 (1) de la fiche : la recette est déclarée cassée si chacun des plis 0 et 1 est à plus de 10 points de macro-F1 sous le TF-IDF du même pli."""
    return all(round((t - lo) * 100, 6) > 10.0 for lo, t in zip(lora_f1, tfidf_f1, strict=True))


def health_pause(verdicts: Sequence[str]) -> bool:
    """Règle N31 (3) de la fiche : pause du lot si les deux derniers runs n'ont pas un tampon de santé « ok » (« suspect » ou absent)."""
    return len(verdicts) >= 2 and all(v != "ok" for v in verdicts[-2:])


def training_runs(names: Sequence[str], slug: str) -> list[str]:
    """Fichiers de runs dont le slug est exactement `slug` (le diagnostic de robustesse du même pli finit par le même texte)."""
    return sorted(n for n in names if re.fullmatch(rf"\d{{8}}-\d{{6}}-{re.escape(slug)}\.json", n))


def health_check(k: int) -> int:
    """Verdicts de santé des runs d'entraînement des plis 0 à k (dernier run de chaque slug) ; code 11 si la pause s'applique."""
    verdicts = []
    for j in range(k + 1):
        runs = training_runs([Path(f).name for f in glob.glob(str(ROOT / "results/runs/*.json"))], SLUG.format(k=j))
        record = json.loads((ROOT / "results/runs" / runs[-1]).read_text(encoding="utf-8")) if runs else {}
        verdicts.append(str(record.get("machine_health", {}).get("verdict", "absent")))
    pause = health_pause(verdicts)
    print(json.dumps({"verdicts_sante": verdicts, "pause": pause}, ensure_ascii=False))
    return PAUSE_CODE if pause else 0


def conformal_cross_fit(probs: NDArray[np.float64], t: NDArray[np.int_], split: NDArray[np.int_], group_of: Mapping[int, int], alpha: float) -> dict[str, Any]:
    """Couverture conforme (LAC) marginale et conditionnelle par famille, chaque pli étalonné sur les autres plis seulement ; couverture par famille avec Wilson."""
    folds = sorted(set(split.tolist()))
    if len(folds) < 2:
        raise ValueError("au moins deux plis sont nécessaires pour étalonner hors du pli évalué")
    fam_true = np.array([group_of[int(c)] for c in t])
    res: dict[str, Any] = {}
    for mode in ("marginal", "famille"):
        covered, size = np.zeros(len(t), bool), np.zeros(len(t))
        for k in folds:
            cal, te = np.flatnonzero(split != k), np.flatnonzero(split == k)
            if mode == "marginal":
                sets = conformal.predict_sets(probs[te], conformal.fit(probs[cal], t[cal], alpha, "lac"), "lac")
            else:
                sets = conformal.predict_sets_by_group(probs[te], conformal.fit_by_group(probs[cal], t[cal], group_of, alpha, "lac"), group_of, "lac")
            for i, s in zip(te, sets, strict=True):
                covered[i], size[i] = t[i] in s, len(s)
        by_family: dict[int, dict[str, Any]] = {}
        for g in sorted(set(fam_true.tolist())):
            sel = fam_true == g
            lo, hi = conformal.wilson(int(covered[sel].sum()), int(sel.sum()))
            by_family[g] = {"n": int(sel.sum()), "couverture": round(float(covered[sel].mean()), 3), "wilson95": [round(lo, 3), round(hi, 3)]}
        res[mode] = {"couverture": round(float(covered.mean()), 3), "taille_moyenne": round(float(size.mean()), 2), "par_famille": by_family,
                     "couverture_minimale_famille": round(min(v["couverture"] for v in by_family.values()), 3)}
    return res


def _pooled(paths_by_fold: Sequence[Sequence[Path]]) -> tuple[list[str], NDArray[np.float64]]:
    """Probabilités regroupées des cinq plis ; dans un pli, moyenne des fichiers (graines) alignés sur les identifiants du premier."""
    ids_pooled: list[str] = []
    parts = []
    for paths in paths_by_fold:
        mats, ref = [], None
        for p in paths:
            z = np.load(p, allow_pickle=False)
            ids = [str(i) for i in z["ids"]]
            ref = ref or ids
            pos = {i: j for j, i in enumerate(ids)}
            mats.append(z["probs"].astype(np.float64)[[pos[i] for i in ref]])
        ids_pooled += ref or []
        parts.append(np.mean(mats, axis=0))
    return ids_pooled, np.vstack(parts)


def compute() -> dict[str, Any]:
    _, y, folds, other, ids_all = p1_04_06_tfidf.load("chapter", "control_folds_by_author")
    labels = sorted(set(y))
    idx = {i: labels.index(v) for i, v in zip(ids_all, y, strict=True)}
    fold_of = dict(zip(ids_all, folds.tolist(), strict=True))
    meta = pd.read_parquet(p1_04_06_tfidf.PARQUET, columns=["id", "author"])
    author_of = dict(zip(meta["id"].astype(str), meta["author"], strict=True))
    pred = ROOT / "results/predictions"
    ids, lora = _pooled([[pred / f"{SLUG.format(k=k)}.probs.npz"] for k in range(5)])
    enc_ids, enc = _pooled([sorted(map(Path, glob.glob(str(pred / f"enc-auteur-pli{k}-s*.probs.npz")))) for k in range(5)])
    enc = enc[[{i: j for j, i in enumerate(enc_ids)}[i] for i in ids]]
    z = np.load(pred / f"{TFIDF_AUTHOR_FILE}.probs.npz", allow_pickle=False)
    pos = {str(i): j for j, i in enumerate(z["ids"])}
    tf = z["probs"].astype(np.float64)[[pos[i] for i in ids]]
    truth = np.array([idx[i] for i in ids])
    scored = [labels.index(c) for c in labels if c != other]
    groups = [author_of[i] for i in ids]

    def mf1(p: NDArray[np.float64]) -> float:
        return float(_macro_f1(truth[None, :], p.argmax(1)[None, :], scored)[0])

    d_tf, lo_tf, hi_tf = cluster_interval(truth, lora.argmax(1), tf.argmax(1), scored, groups)
    d_en, lo_en, hi_en = cluster_interval(truth, lora.argmax(1), enc.argmax(1), scored, groups)
    loss = (LORA_PATIENT - mf1(lora)) * 100
    per_fold = []
    for k in range(5):
        diag = json.loads((ROOT / f"results/measures/robustness_lora_diag-{SLUG.format(k=k)}.json").read_text(encoding="utf-8"))
        per_fold.append((float(diag["propre"]["macro_f1"]), float(diag["fin_30"]["macro_f1"])))
    rep = evaluation.chapter_report(truth, lora, labels, excluded=(other,) if other else ())
    fam_names = list(glm_v3_families.FAMILIES)
    fam_of_label = {c: fam_names.index(n) for n, cs in glm_v3_families.FAMILIES.items() for c in cs}
    split = np.array([fold_of[i] for i in ids])
    cover = conformal_cross_fit(lora, truth, split, {j: fam_of_label[c] for j, c in enumerate(labels)}, ALPHA)
    return {"n_patients": len(ids), "macro_f1": {"lora": round(mf1(lora), 4), "encodeur": round(mf1(enc), 4), "tfidf": round(mf1(tf), 4)},
            "a_lora_moins_tfidf_points": [round(d_tf, 2), round(lo_tf, 2), round(hi_tf, 2)], "a_verdict": verdict(lo_tf, hi_tf),
            "a2_lora_moins_encodeur_points": [round(d_en, 2), round(lo_en, 2), round(hi_en, 2)], "a2_verdict": verdict(lo_en, hi_en),
            "b_perte_points": round(loss, 2), "b_lecture": loss_reading(loss),
            "c_par_pli_propre_et_fin_30": [[round(a, 4), round(b, 4)] for a, b in per_fold], "c_verdict": correction_label(per_fold),
            "d_ece": round(rep["ece"], 4), "d_log_loss": round(rep["log_loss"], 4), "d_exactitude": round(rep["accuracy"], 4), "d_conforme": cover, "alpha": ALPHA, "delta_points": DELTA}


def stop_rule() -> int:
    """Macro-F1 du LoRA et du TF-IDF en plis d'auteurs sur les plis 0 et 1, mêmes patients ; code 10 si la règle d'arrêt s'applique."""
    _, y, _, other, ids_all = p1_04_06_tfidf.load("chapter", "control_folds_by_author")
    labels = sorted(set(y))
    idx = {i: labels.index(v) for i, v in zip(ids_all, y, strict=True)}
    scored = [labels.index(c) for c in labels if c != other]
    z = np.load(ROOT / f"results/predictions/{TFIDF_AUTHOR_FILE}.probs.npz", allow_pickle=False)
    pos = {str(i): j for j, i in enumerate(z["ids"])}
    tf_all = z["probs"].astype(np.float64)
    lora_f1, tfidf_f1 = [], []
    for k in (0, 1):
        zk = np.load(ROOT / f"results/predictions/{SLUG.format(k=k)}.probs.npz", allow_pickle=False)
        ids = [str(i) for i in zk["ids"]]
        truth = np.array([idx[i] for i in ids])
        lora_f1.append(float(_macro_f1(truth[None, :], zk["probs"].argmax(1)[None, :], scored)[0]))
        tfidf_f1.append(float(_macro_f1(truth[None, :], tf_all[[pos[i] for i in ids]].argmax(1)[None, :], scored)[0]))
    stop = early_stop(lora_f1, tfidf_f1)
    print(json.dumps({"regle_arret_n31": stop, "lora_plis_0_1": [round(v, 4) for v in lora_f1], "tfidf_plis_0_1": [round(v, 4) for v in tfidf_f1]}, ensure_ascii=False))
    return STOP_CODE if stop else 0


def main() -> int:
    start = machine_health.snapshot()
    out = agree_twice(compute, equal=lambda a, b: json.dumps(a, sort_keys=True) == json.dumps(b, sort_keys=True))
    print(json.dumps(out, indent=1, ensure_ascii=False))
    if "--register" in sys.argv:
        (ROOT / "results/measures/lora_author_analysis.json").write_text(json.dumps(out, indent=1, ensure_ascii=False), encoding="utf-8")
        print(register_run(ROOT / "results/runs", {"kind": "measure", "slug": "lora-fin-aleatoire-plis-auteurs-analyse", "status": "ok",
                                                    "summary": f"LoRA à fin aléatoire en plis d'auteurs : contre TF-IDF {out['a_verdict']}, contre encodeur {out['a2_verdict']}, perte {out['b_perte_points']} points ({out['b_lecture']}), {out['c_verdict']}",
                                                    "params": {"fiche": "experiments/2026-10-17-lora-fin-aleatoire-plis-auteurs.md", "delta": DELTA, "alpha": ALPHA, "calcul_double": True},
                                                    "metrics": out, "machine_health": machine_health.stamp(start)}))
    return 0


if __name__ == "__main__":
    if "--sante" in sys.argv:
        sys.exit(health_check(int(sys.argv[sys.argv.index("--sante") + 1])))
    sys.exit(stop_rule() if "--regle-arret" in sys.argv else main())
