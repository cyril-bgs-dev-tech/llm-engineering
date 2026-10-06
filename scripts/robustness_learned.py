#!/usr/bin/env python3
"""Robustesse de l'encodeur et du LoRA aux perturbations et ablations de texte (RM-39 partie inférence, fiche 2026-10-06-robustesse-modeles-appris).

Inférence seule sur le pli 0 (717 patients tenus à l'écart de l'entraînement), texte propre contre accents retirés, fautes, casse, fin retirée, début retiré ;
différence de macro-F1 avec le texte propre par bootstrap d'auteurs, verdict de la fiche (±δ = 2,0). Développement seulement, aucune étiquette du test scellé.
Usage : robustness_learned.py {encoder|lora} [--register]. Lancer avec HF_HOME=$PWD/artifacts/hf_cache quand le GPU est libre."""
import json
import os
import random
import sys
from pathlib import Path

os.environ.setdefault("TOKENIZERS_PARALLELISM", "false")
os.environ.setdefault("RAYON_NUM_THREADS", "2")

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent))
import p1_04_06_tfidf
import p1_finetune
from llmft import evaluation
from llmft.cluster_bootstrap import cluster_interval
from llmft.mini_registry import register_run
from llmft.perturb import ABLATIONS, PERTURBATIONS

DELTA = 2.0
FOLD = 0
ENCODER = ("camembert-deploy-ep10-lr1e-4", 508)
LORA = ("Qwen/Qwen3.5-4B", "llm-mur2-qwen3-5-4b-ep10-lr1e-4", 4096)


def verdict(lo: float, hi: float) -> str:
    return "robuste" if -DELTA <= lo and hi <= DELTA else ("dégradé" if hi < -DELTA else "non résolu")


def load_model(kind: str, n_labels: int) -> tuple[object, object, int, int]:
    import torch
    from transformers import AutoModelForSequenceClassification, AutoTokenizer

    if kind == "encoder":
        model_dir = ROOT / "artifacts/models" / ENCODER[0]
        tok = AutoTokenizer.from_pretrained(model_dir)
        model = AutoModelForSequenceClassification.from_pretrained(model_dir, torch_dtype=torch.float32).to("cuda").eval()
        return model, tok, int(tok.pad_token_id), ENCODER[1]
    from peft import PeftModel

    tok = AutoTokenizer.from_pretrained(LORA[0])
    pad_id = int(tok.pad_token_id if tok.pad_token_id is not None else tok.eos_token_id)
    base = AutoModelForSequenceClassification.from_pretrained(LORA[0], num_labels=n_labels, torch_dtype=torch.bfloat16)
    base.config.pad_token_id = pad_id
    return PeftModel.from_pretrained(base, ROOT / "artifacts/adapters" / LORA[1]).to("cuda").eval(), tok, pad_id, LORA[2]


def main() -> int:
    kind = sys.argv[1]
    texts, y, folds, excluded, ids_all = p1_04_06_tfidf.load("chapter")
    labels = sorted(set(y))
    idx = np.array([labels.index(v) for v in y])
    te = np.where(folds == FOLD)[0]
    meta = pd.read_parquet(p1_04_06_tfidf.PARQUET, columns=["id", "author"])
    author_of = dict(zip(meta["id"].astype(str), meta["author"], strict=True))
    groups = [author_of[ids_all[i]] for i in te]
    scored = [labels.index(c) for c in labels if c != excluded]
    model, tok, pad_id, max_len = load_model(kind, len(labels))
    variants = {"propre": [texts[i] for i in te]}
    for name, fn in {**PERTURBATIONS, **ABLATIONS}.items():
        rng = random.Random(1000)
        variants[name] = [fn(texts[i], rng) for i in te]
    preds: dict[str, np.ndarray] = {}
    out: dict[str, dict[str, object]] = {}
    for name, tx in variants.items():
        x = p1_finetune.build_inputs(tok, tx, max_len)
        probs = p1_finetune.predict(model, x, pad_id, "cuda", 16 if kind == "encoder" else 1, len(labels))
        preds[name] = probs.argmax(1)
        rep = evaluation.chapter_report(idx[te], probs, labels, excluded=(excluded,))
        out[name] = {"macro_f1": round(rep["macro_f1"], 4), "accuracy": round(rep["accuracy"], 4)}
        if name != "propre":
            d, lo, hi = cluster_interval(idx[te], preds[name], preds["propre"], scored, groups)
            out[name].update({"difference_points": [round(d, 2), round(lo, 2), round(hi, 2)], "verdict": verdict(lo, hi)})
        print(name, out[name], flush=True)
    (ROOT / "results/measures" / f"robustness_learned_{kind}.json").write_text(json.dumps(out, indent=1, ensure_ascii=False), encoding="utf-8")
    if "--register" in sys.argv:
        print(register_run(ROOT / "results/runs", {"kind": "measure", "slug": f"robustesse-modeles-appris-{kind}", "status": "ok", "summary": f"Robustesse de {kind} aux perturbations et ablations de texte (inférence, pli {FOLD})",
                                                    "params": {"fiche": "experiments/2026-10-06-robustesse-modeles-appris.md", "delta": DELTA, "fold": FOLD, "n_patients": len(te)}, "metrics": out}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
