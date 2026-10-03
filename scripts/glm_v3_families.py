#!/usr/bin/env python3
"""Audit GLM v3, C5-A2 : erreurs lues au niveau de familles de chapitres CIM-10 (regroupement du projet, non normatif), pli 0, développement seulement."""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(Path(__file__).resolve().parent))
import p1_04_06_tfidf

FAMILIES = {"infectieux, tumeurs, sang": ["I", "II", "III"], "endocrinien et mental": ["IV", "V"], "nerveux": ["VI"], "circulatoire et respiratoire": ["IX", "X"], "digestif": ["XI"],
            "peau, muscle, urinaire": ["XII", "XIII", "XIV"], "grossesse": ["XV"], "symptômes, lésions, facteurs": ["XVIII", "XIX", "XXI", "XXII"], "autre": ["AUTRE"]}
PREDS = {"tfidf": "p1-06-tfidf-chapter", "qwen3.5-9b-1e-4": "p1-11-qwen3-5-9b-lr1e-4", "gemma-4-e4b-1e-4": "p1-11-gemma-4-e4b-lr1e-4"}


def main() -> int:
    _, y, folds, _, ids = p1_04_06_tfidf.load("chapter")
    truth = dict(zip(ids, y, strict=True))
    fold0 = {i for i, g in zip(ids, folds, strict=True) if g == 0}
    fam = {c: f for f, cs in FAMILIES.items() for c in cs}
    out = {}
    for name, slug in PREDS.items():
        d = json.loads((ROOT / f"results/predictions/{slug}.json").read_text(encoding="utf-8"))
        errors = [(truth[i], p) for i, p in zip(d["ids"], d["pred"], strict=True) if i in fold0 and truth[i] != p]
        within = sum(1 for t, p in errors if fam[t] == fam[p])
        out[name] = {"erreurs": len(errors), "dans_la_meme_famille": within, "part_meme_famille": round(within / len(errors), 3)}
        print(name, out[name])
    (ROOT / "results/measures/glm_v3_families.json").write_text(json.dumps({"familles": FAMILIES, "resultats": out}, ensure_ascii=False, indent=1), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
