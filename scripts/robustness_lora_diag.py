#!/usr/bin/env python3
"""Diagnostic de l'effondrement du LoRA sans la fin du texte (RM-39 suite, fiche 2026-10-06-diagnostic-effondrement-lora) : inférence seule sur le pli 0.

Texte propre, fin retirée à 10, 20, 30 et 50 % des mots, début retiré à 50 % ; macro-F1, probabilité maximale moyenne, entropie, histogramme des classes prédites ;
probabilités conservées dans `results/predictions/robustesse-lora-<variante>.probs.npz`. Développement seulement. Usage : robustness_lora_diag.py [--register]."""
import json
import os
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

BASE, MAX_LEN, FOLD = "Qwen/Qwen3.5-4B", 4096, 0
ADAPTER = sys.argv[sys.argv.index("--adapter") + 1] if "--adapter" in sys.argv else "llm-mur2-qwen3-5-4b-ep10-lr1e-4"
SUFFIX = "" if "--adapter" not in sys.argv else "-" + ADAPTER


def drop_tail(text: str, fraction: float) -> str:
    words = text.split(" ")
    return " ".join(words[: max(1, round((1 - fraction) * len(words)))])


def drop_head(text: str, fraction: float) -> str:
    words = text.split(" ")
    return " ".join(words[round(fraction * len(words)) :]) if len(words) > 1 else text


def add_newline(text: str) -> str:
    return text if text.endswith("\n") else text + "\n"


VARIANTS_NEWLINE = {"propre_sans_saut_final": lambda t: t.rstrip("\n"), "fin_10_avec_saut": lambda t: add_newline(drop_tail(t, 0.1)), "fin_50_avec_saut": lambda t: add_newline(drop_tail(t, 0.5))}
VARIANTS = {"propre": lambda t: t, "fin_10": lambda t: drop_tail(t, 0.1), "fin_20": lambda t: drop_tail(t, 0.2), "fin_30": lambda t: drop_tail(t, 0.3), "fin_50": lambda t: drop_tail(t, 0.5), "debut_50": lambda t: drop_head(t, 0.5)}


def main() -> int:
    import torch
    from peft import PeftModel
    from transformers import AutoModelForSequenceClassification, AutoTokenizer

    texts, y, folds, excluded, ids_all = p1_04_06_tfidf.load("chapter")
    labels = sorted(set(y))
    idx = np.array([labels.index(v) for v in y])
    te = np.where(folds == FOLD)[0]
    tok = AutoTokenizer.from_pretrained(BASE)
    pad_id = int(tok.pad_token_id if tok.pad_token_id is not None else tok.eos_token_id)
    base = AutoModelForSequenceClassification.from_pretrained(BASE, num_labels=len(labels), torch_dtype=torch.bfloat16)
    base.config.pad_token_id = pad_id
    if getattr(base.config, "text_config", None) is not None:  # Qwen3.5 : la tête lit le jeton de remplissage dans la configuration du texte (sinon, pas de lot supérieur à 1)
        base.config.text_config.pad_token_id = pad_id
    model = PeftModel.from_pretrained(base, ROOT / "artifacts/adapters" / ADAPTER).to("cuda").eval()
    out: dict[str, dict[str, object]] = {}
    series = VARIANTS_NEWLINE if "--serie-saut-de-ligne" in sys.argv else VARIANTS
    for name, fn in series.items():
        x = p1_finetune.build_inputs(tok, [fn(texts[i]) for i in te], MAX_LEN)
        probs = p1_finetune.predict(model, x, pad_id, "cuda", 1, len(labels))
        rep = evaluation.chapter_report(idx[te], probs, labels, excluded=(excluded,))
        counts = np.bincount(probs.argmax(1), minlength=len(labels))
        entropy = float(-(probs * np.log(np.clip(probs, 1e-12, 1))).sum(1).mean())
        top = int(counts.argmax())
        out[name] = {"macro_f1": round(rep["macro_f1"], 4), "accuracy": round(rep["accuracy"], 4), "proba_max_moyenne": round(float(probs.max(1).mean()), 4), "entropie_moyenne": round(entropy, 4),
                     "classe_la_plus_predite": labels[top], "part_classe_la_plus_predite": round(float(counts[top] / counts.sum()), 4), "n_classes_predites": int((counts > 0).sum())}
        print(name, out[name], flush=True)
        if "--register" in sys.argv:
            np.savez_compressed(ROOT / "results/predictions" / f"robustesse-lora-{name}{SUFFIX}.probs.npz", ids=np.array([ids_all[i] for i in te]), probs=probs.astype(np.float32), labels=np.array(labels))
    (ROOT / "results/measures" / (("robustness_lora_saut_de_ligne" if series is VARIANTS_NEWLINE else "robustness_lora_diag") + SUFFIX + ".json")).write_text(json.dumps(out, indent=1, ensure_ascii=False), encoding="utf-8")
    if "--register" in sys.argv:
        print(register_run(ROOT / "results/runs", {"kind": "measure", "slug": ("robustesse-lora-saut-de-ligne" if series is VARIANTS_NEWLINE else "robustesse-lora-diagnostic-fin-retiree") + SUFFIX, "status": "ok", "summary": "Effondrement du LoRA et saut de ligne final (inférence, pli 0)" if series is VARIANTS_NEWLINE else "Diagnostic de l'effondrement du LoRA sans la fin du texte (inférence, pli 0)",
                                                    "params": {"fiche": "experiments/2026-10-06-effondrement-lora-saut-de-ligne.md" if series is VARIANTS_NEWLINE else "experiments/2026-10-06-diagnostic-effondrement-lora.md", "adapter": ADAPTER, "fold": FOLD, "micro_batch": 1}, "metrics": out}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
