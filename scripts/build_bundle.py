#!/usr/bin/env python3
"""Construit le service d'inférence (TF-IDF caractères et poids équilibrés) sur tout le développement ; température, quantile conforme et seuil d'abstention
sont calculés sur des prédictions hors pli **groupées par auteur** (couverture tenue sous décalage d'auteur). Test scellé jamais lu.
Usage : build_bundle.py [dossier de sortie]   (défaut : artifacts/models/tfidf_chapter_charbal_v1)"""
import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent))
import p1_04_06_tfidf
from llmft import serving


def main() -> int:
    out_dir = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "artifacts/models/tfidf_chapter_charbal_v1"
    texts, y, _, other, ids = p1_04_06_tfidf.load("chapter")
    labels = sorted(set(y))
    z = np.load(ROOT / "results/predictions/tfidf-variant-char-balanced-author.probs.npz", allow_pickle=False)
    assert [str(c) for c in z["labels"]] == labels
    pos = {str(i): k for k, i in enumerate(z["ids"])}
    oof = z["probs"][[pos[i] for i in ids]]
    oof_y = np.array([labels.index(v) for v in y])
    chosen = json.loads(next((ROOT / "results/runs").glob("*-tfidf-variant-char-balanced.json")).read_text(encoding="utf-8"))["metrics"]["chosen"]
    values = [x["C"] for x in chosen]
    c = float(max(set(values), key=values.count))  # C le plus fréquent parmi les plis de la référence
    bundle = serving.train_bundle(texts, y, labels, c=c, ngram=(3, 5), oof_probs=oof, oof_y=oof_y, alpha=0.10, coverage_target=0.70, class_weight="balanced", analyzer="char_wb",
                                  meta={"calibration": "prédictions hors pli groupées par auteur", "n_train": len(texts), "excluded_label": other})
    serving.save_bundle(bundle, out_dir)
    print(json.dumps({"dossier": str(out_dir), "c": c, "temperature": bundle.temperature, "qhat": bundle.qhat, "seuil_abstention": bundle.abstain_threshold}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
