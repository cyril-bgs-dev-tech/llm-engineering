#!/usr/bin/env python3
"""Reprise de la fin de `morfitt_run.py final` (RM-49) : les cinq graines de l'encodeur sont entraînées et enregistrées (`morfitt-final-enc-s1000` à `s1004`, probabilités dans
`results/predictions/morfitt-enc-s*.probs.npz`) mais l'étape TF-IDF a échoué par un TypeError interne de scikit-learn (panne aléatoire, code 1 non relançable dans le lot).
Ce script recharge les probabilités, refait le TF-IDF (trois essais consignés), le mélange 50/50 et le résumé, avec **les mêmes fonctions et le même critère** que `morfitt_run.py`.
Aucun réglage sur le test, aucun réentraînement. Usage : morfitt_finish.py [--register] [--fiche CHEMIN]"""
import hashlib
import json
import sys
from pathlib import Path
from typing import Any

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent))
import morfitt_run as mr
from llmft import multilabel
from llmft.mini_registry import register_run


def main() -> int:
    fiche = sys.argv[sys.argv.index("--fiche") + 1] if "--fiche" in sys.argv else ""
    fiche_sha = hashlib.sha256((ROOT / fiche).read_bytes()).hexdigest() if fiche else None
    tuning = json.loads(mr.TUNING.read_text(encoding="utf-8"))
    best_tf = tuning["tfidf_retenu"]
    tr_x, tr_y = mr.load_split("train")
    te_x, te_y = mr.load_split("test")
    seed_probs = [np.load(ROOT / f"results/predictions/morfitt-enc-s{s}.probs.npz")["probs"].astype(np.float64) for s in mr.SEEDS]
    seed_scores = [100 * multilabel.f1_scores(te_y.astype(int), multilabel.predict_labels(p))["weighted_f1"] for p in seed_probs]
    tf, attempts = None, 0
    for attempts in range(1, 4):
        try:
            tf = mr.tfidf_probs(tr_x, tr_y, te_x, best_tf["C"])
            break
        except TypeError as exc:
            print(f"essai {attempts}/3 : {exc}", flush=True)
    if tf is None:
        raise SystemExit("TF-IDF : trois échecs consécutifs, arrêt (défaut à corriger, pas une panne isolée)")
    enc_mean = np.mean(seed_probs, axis=0)
    mix = 0.5 * enc_mean + 0.5 * tf
    res: dict[str, Any] = {"publie_f1_pondere_test": mr.PUBLISHED, "reglage": tuning["encodeur_retenu"] | {"tfidf_C": best_tf["C"]}, "n_test": len(te_x), "essais_tfidf": attempts}
    res["encodeur_une_graine"] = {"moyenne": round(float(np.mean(seed_scores)), 2), "ecart_type": round(float(np.std(seed_scores, ddof=1)), 2), "par_graine": [round(float(v), 2) for v in seed_scores]}
    for name, probs in (("encodeur_moyenne_5_graines", enc_mean), ("tfidf", tf), ("melange_50_50", mix)):
        pred = multilabel.predict_labels(probs)
        s = multilabel.f1_scores(te_y.astype(int), pred)
        res[name] = {"weighted_f1": round(100 * s["weighted_f1"], 2), "micro_f1": round(100 * s["micro_f1"], 2), "macro_f1": round(100 * s["macro_f1"], 2), "ic95_weighted_f1_bootstrap_patients": mr.bootstrap_ci(te_y, pred)}
        print(name, res[name], flush=True)
    (ROOT / "results/measures/morfitt_final.json").write_text(json.dumps(res, indent=1, ensure_ascii=False), encoding="utf-8")
    if "--register" in sys.argv:
        print(register_run(ROOT / "results/runs", {"kind": "measure", "slug": "morfitt-final-resume", "status": "ok",
                                                    "summary": f"MorFITT test : encodeur {res['encodeur_une_graine']['moyenne']} (5 graines), mélange {res['melange_50_50']['weighted_f1']}, TF-IDF {res['tfidf']['weighted_f1']} (F1 pondéré) ; étape finale reprise après un TypeError de scikit-learn",
                                                    "params": {"fiche_sha256": fiche_sha, "reprise": "scripts/morfitt_finish.py"}, "metrics": res}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
