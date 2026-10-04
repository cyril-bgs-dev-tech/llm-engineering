#!/usr/bin/env python3
"""Ancrage externe (RM-30, P1-09 sur un pli) : un LLM ouvert local, sans affinage, classe les patients d'un pli de développement en zéro-shot par lettres.

Invite construite depuis le contrat `task_specs/parhaf_cim10_chapter.yaml` (nom et définition de chaque chapitre), document tronqué tête et fin en tokens, probabilités lues sur les lettres de réponse.
Aucune étiquette ni exemple n'entre dans l'invite ; développement seulement (jamais le test scellé). À lancer GPU libre, selon une fiche préenregistrée.
Usage : zero_shot.py MODELE --slug NOM [--fold 0] [--max-doc-tokens 3500] [--limit N] [--device cuda] [--fiche CHEMIN] [--register]"""
import hashlib
import json
import os
import sys
import time
from pathlib import Path

os.environ.setdefault("TOKENIZERS_PARALLELISM", "false")
os.environ.setdefault("RAYON_NUM_THREADS", "2")

import numpy as np
import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent))
import p1_04_06_tfidf
from llmft import evaluation, lora_train, zeroshot
from llmft.mini_registry import register_run


def arg(name: str, default: str) -> str:
    return sys.argv[sys.argv.index(name) + 1] if name in sys.argv else default


def main() -> int:
    model_name = sys.argv[1]
    slug, fold, max_doc = arg("--slug", ""), int(arg("--fold", "0")), int(arg("--max-doc-tokens", "3500"))
    limit, device, fiche = int(arg("--limit", "0")), arg("--device", "cuda"), arg("--fiche", "")
    if not slug:
        raise SystemExit("--slug requis")
    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer

    spec = yaml.safe_load((ROOT / "task_specs/parhaf_cim10_chapter.yaml").read_text(encoding="utf-8"))
    classes = [{"name": c["name"], "definition": c["definition"]} for c in spec["classes"]]
    class_to_label = {c["id"]: ("AUTRE" if c["id"] == "autre" else c["id"].removeprefix("ch_").upper()) for c in spec["classes"]}
    order = [class_to_label[c["id"]] for c in spec["classes"]]
    texts, y, folds, excluded, ids = p1_04_06_tfidf.load("chapter")
    labels = sorted(set(y))
    te = np.where(folds == fold)[0][: limit or None]
    tok = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForCausalLM.from_pretrained(model_name, torch_dtype=torch.bfloat16).to(device).eval()
    letters = zeroshot.class_letters(len(classes))
    letter_ids = [tok.encode(lt, add_special_tokens=False)[0] for lt in letters]
    marker = tok.encode("[...]", add_special_tokens=False)
    probs_order = np.zeros((len(te), len(classes)))
    t0 = time.time()
    for k, i in enumerate(te):
        doc_ids = lora_train.truncate_head_tail(tok.encode(texts[i], add_special_tokens=False), max_doc, marker)
        prompt = zeroshot.build_prompt(classes, tok.decode(doc_ids))
        try:
            chat = tok.apply_chat_template([{"role": "user", "content": prompt}], tokenize=False, add_generation_prompt=True, enable_thinking=False)
        except TypeError:
            chat = tok.apply_chat_template([{"role": "user", "content": prompt}], tokenize=False, add_generation_prompt=True)
        x = tok(chat, return_tensors="pt", add_special_tokens=False).to(device)
        with torch.no_grad():
            logits = model(**x).logits[:, -1, :].float().cpu().numpy()
        probs_order[k] = zeroshot.letter_probs(logits, letter_ids)[0]
    seconds = time.time() - t0
    probs = np.zeros((len(te), len(labels)))
    for j, name in enumerate(order):  # colonnes de l'invite vers l'ordre alphabétique des classes de la tâche
        probs[:, labels.index(name)] = probs_order[:, j]
    idx = np.array([labels.index(v) for v in y])
    rep = evaluation.chapter_report(idx[te], probs, labels, excluded=(excluded,) if excluded else ())
    metrics = {"macro_f1": round(rep["macro_f1"], 4), "accuracy": round(rep["accuracy"], 4), "log_loss": round(rep["log_loss"], 4), "seconds_inference": round(seconds, 1), "n_eval": len(te),
               "prompt_sha256": hashlib.sha256(zeroshot.build_prompt(classes, "").encode()).hexdigest(), "fiche_sha256": hashlib.sha256((ROOT / fiche).read_bytes()).hexdigest() if fiche else None}
    summary = f"{slug} : macro-F1 {metrics['macro_f1']} en zéro-shot sur le pli {fold} ({len(te)} patients, aucun affinage)"
    print(json.dumps({"summary": summary, "metrics": metrics}, ensure_ascii=False, indent=1))
    if "--register" in sys.argv:
        out = ROOT / "results/predictions" / f"{slug}.json"
        out.write_text(json.dumps({"ids": [ids[i] for i in te], "pred": [labels[int(k)] for k in probs.argmax(1)], "fold": fold}, ensure_ascii=False), encoding="utf-8")
        np.savez_compressed(out.with_suffix(".probs.npz"), ids=np.array([ids[i] for i in te]), probs=probs.astype(np.float32), labels=np.array(labels))
        print(register_run(ROOT / "results/runs", {"kind": "train", "slug": slug, "status": "ok", "summary": summary, "params": {"model": model_name, "fold": fold, "max_doc_tokens": max_doc, "mode": "zero-shot par lettres"}, "metrics": metrics}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
