#!/usr/bin/env python3
"""Robustesse d'un LoRA sauvegardé aux perturbations de texte (audit GLM v4, C5-A5) : inférence seule sur le pli d'évaluation, texte propre contre accents retirés, fautes de frappe, casse.

Charge le modèle de base et l'adaptateur de `artifacts/adapters/<slug>` (voie A). Développement seulement, EXPLORE.
Usage : robustesse_llm.py MODELE_DE_BASE SLUG_ADAPTATEUR [--fold 0] [--register]   (à lancer quand le GPU est libre)"""
import json
import os
import random
import sys
from pathlib import Path

os.environ.setdefault("TOKENIZERS_PARALLELISM", "false")
os.environ.setdefault("RAYON_NUM_THREADS", "2")

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent))
import p1_04_06_tfidf
import p1_finetune
from llmft import evaluation
from llmft.mini_registry import register_run
from llmft.perturb import ABLATIONS, PERTURBATIONS


def main() -> int:
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    base_name, slug = args[0], args[1]
    fold = int(sys.argv[sys.argv.index("--fold") + 1]) if "--fold" in sys.argv else 0
    import torch
    from peft import PeftModel
    from transformers import AutoModelForSequenceClassification, AutoTokenizer

    texts, y, folds, excluded, _ = p1_04_06_tfidf.load("chapter")
    labels = sorted(set(y))
    idx = np.array([labels.index(v) for v in y])
    te = np.where(folds == fold)[0]
    tok = AutoTokenizer.from_pretrained(base_name)
    pad_id = tok.pad_token_id if tok.pad_token_id is not None else tok.eos_token_id
    base = AutoModelForSequenceClassification.from_pretrained(base_name, num_labels=len(labels), torch_dtype=torch.bfloat16)
    base.config.pad_token_id = pad_id
    model = PeftModel.from_pretrained(base, ROOT / "artifacts/adapters" / slug).to("cuda").eval()
    variants = {"propre": [texts[i] for i in te]}
    for name, fn in {**PERTURBATIONS, **ABLATIONS}.items():
        rng = random.Random(1000)
        variants[name] = [fn(texts[i], rng) for i in te]
    out = {}
    for name, tx in variants.items():
        x = p1_finetune.build_inputs(tok, tx, 4096)
        probs = p1_finetune.predict(model, x, pad_id, "cuda", 1, len(labels))
        rep = evaluation.chapter_report(idx[te], probs, labels, excluded=(excluded,))
        out[name] = {"macro_f1": round(rep["macro_f1"], 4), "accuracy": round(rep["accuracy"], 4)}
        print(name, out[name], flush=True)
    (ROOT / "results/measures" / f"robustness_{slug}.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
    if "--register" in sys.argv:
        print(register_run(ROOT / "results/runs", {"kind": "measure", "slug": f"robustness-{slug}", "status": "ok", "summary": f"Robustesse aux perturbations de {slug} (inférence, pli {fold})", "params": {"fold": fold, "base": base_name}, "metrics": out}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
