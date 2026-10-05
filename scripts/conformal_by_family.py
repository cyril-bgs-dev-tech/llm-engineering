#!/usr/bin/env python3
"""Étalonnage conforme conditionnel par famille de chapitres (Mondrian, sans étiquette de test) contre marginal, couverture par famille avec Wilson, développement seulement.

Pour chaque jeu de probabilités : étalonnage croisé par moitiés stratifiées (jeux d'un seul pli) ou par plis (TF-IDF, cinq plis). Une classe candidate est dans l'ensemble si son score
est sous le quantile de **sa** famille (`conformal.predict_sets_by_group`). Usage : conformal_by_family.py NOM=PROBS.npz [NOM=PROBS.npz ...] [--register]"""
import json
import sys
from pathlib import Path

import numpy as np
from sklearn.model_selection import StratifiedKFold

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent))
import glm_v3_families
import p1_04_06_tfidf
from llmft import conformal
from llmft.mini_registry import register_run

ALPHA = 0.10


def main() -> int:
    _, y_all, folds_all, _, ids_all = p1_04_06_tfidf.load("chapter")
    truth = dict(zip(ids_all, y_all, strict=True))
    fold_of = dict(zip(ids_all, folds_all.tolist(), strict=True))
    fam_names = list(glm_v3_families.FAMILIES)
    fam_of_label = {c: fam_names.index(n) for n, cs in glm_v3_families.FAMILIES.items() for c in cs}
    out = {}
    for arg in [a for a in sys.argv[1:] if not a.startswith("--")]:
        name, path = arg.split("=", 1)
        z = np.load(path, allow_pickle=False)
        labels = [str(c) for c in z["labels"]]
        ids = [str(i) for i in z["ids"]]
        probs = z["probs"].astype(np.float64)
        t = np.array([labels.index(truth[i]) for i in ids])
        group_of = {k: fam_of_label[labels[k]] for k in range(len(labels))}
        f = np.array([fold_of[i] for i in ids])
        split = f if len(set(f.tolist())) >= 3 else np.zeros(len(t), int)
        if len(set(split.tolist())) == 1:
            for h, (_, te) in enumerate(StratifiedKFold(2, shuffle=True, random_state=1000).split(probs, t)):
                split[te] = h
        res = {}
        for mode in ("marginal", "famille"):
            covered = np.zeros(len(t), bool)
            size = np.zeros(len(t))
            for k in sorted(set(split.tolist())):
                cal, te = np.flatnonzero(split != k), np.flatnonzero(split == k)
                if mode == "marginal":
                    sets = conformal.predict_sets(probs[te], conformal.fit(probs[cal], t[cal], ALPHA, "lac"), "lac")
                else:
                    sets = conformal.predict_sets_by_group(probs[te], conformal.fit_by_group(probs[cal], t[cal], group_of, ALPHA, "lac"), group_of, "lac")
                for i, s in zip(te, sets, strict=True):
                    covered[i], size[i] = t[i] in s, len(s)
            fam_true = np.array([group_of[int(c)] for c in t])
            by_family = {}
            for g, nm in enumerate(fam_names):
                sel = fam_true == g
                if sel.sum() >= 15 and nm != "autre":
                    lo, hi = conformal.wilson(int(covered[sel].sum()), int(sel.sum()))
                    by_family[nm] = {"n": int(sel.sum()), "couverture": round(float(covered[sel].mean()), 3), "wilson95": [round(lo, 3), round(hi, 3)]}
            res[mode] = {"couverture": round(float(covered.mean()), 3), "taille_moyenne": round(float(size.mean()), 2), "par_famille": by_family,
                         "couverture_minimale_famille": round(min(v["couverture"] for v in by_family.values()), 3)}
        out[name] = res
        print(name, {m: (r["couverture"], r["taille_moyenne"], r["couverture_minimale_famille"]) for m, r in res.items()}, flush=True)
    (ROOT / "results/measures/conformal_by_family.json").write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    if "--register" in sys.argv:
        print(register_run(ROOT / "results/runs", {"kind": "measure", "slug": "conformal-by-family", "status": "ok", "summary": "Conforme marginal contre conditionnel par famille (sans étiquette de test)", "params": {"alpha": ALPHA}, "metrics": out}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
