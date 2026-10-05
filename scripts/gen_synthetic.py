#!/usr/bin/env python3
"""Génération de comptes rendus synthétiques ciblés (fiche 2026-10-04-synthetique-cible-chapitres-rares), à lancer **après** le Qwen3.5-4B à 10 époques.

Sources : patients des plis d'entraînement (plis ≠ --fold) des chapitres ciblés uniquement ; chaque texte généré porte l'identifiant de sa source ; contrôles : lignée
(`augment.validated_synthetic`), qualité (`synthetic_gen.acceptable`), copies de la validation (`augment.copies_of_validation`). Écrit `results/synthetic/<slug>.jsonl`.
`--dry` : compte les sources et affiche une invite, sans charger de modèle.
Usage : gen_synthetic.py MODELE --fold 0 --targets IV,V,XII,XXI,XXII --per-source 2 --slug NOM [--dry]"""
import argparse
import json
import os
import sys
from pathlib import Path

os.environ.setdefault("TOKENIZERS_PARALLELISM", "false")
os.environ.setdefault("RAYON_NUM_THREADS", "2")

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent))
import p1_04_06_tfidf
from llmft import augment, synthetic_gen


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("model")
    ap.add_argument("--fold", type=int, default=0)
    ap.add_argument("--targets", default="IV,V,XII,XXI,XXII")
    ap.add_argument("--per-source", type=int, default=2)
    ap.add_argument("--max-new-tokens", type=int, default=1500)
    ap.add_argument("--slug", required=True)
    ap.add_argument("--dry", action="store_true")
    a = ap.parse_args()
    texts, y, folds, _, ids = p1_04_06_tfidf.load("chapter")
    targets = set(a.targets.split(","))
    train = [k for k, g in enumerate(folds) if g != a.fold]
    sources = [k for k in train if y[k] in targets]
    print(f"{len(sources)} sources d'entraînement dans les classes {sorted(targets)} ; {len(sources) * a.per_source} textes à générer")
    if a.dry:
        print(synthetic_gen.build_prompt(texts[sources[0]][:300] + " [...]", "court")[:900])
        return 0
    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer

    tok = AutoTokenizer.from_pretrained(a.model)
    tok.padding_side = "left"
    if tok.pad_token_id is None:
        tok.pad_token = tok.eos_token
    model = AutoModelForCausalLM.from_pretrained(a.model, torch_dtype=torch.bfloat16).to("cuda").eval()
    records, rejected = [], 0
    out_dir = ROOT / "results/synthetic"
    out_dir.mkdir(parents=True, exist_ok=True)
    for n, k in enumerate(sources):
        prompt = synthetic_gen.build_prompt(texts[k])
        text_in = tok.apply_chat_template([{"role": "user", "content": prompt}], tokenize=False, add_generation_prompt=True) if tok.chat_template else prompt
        batch = tok([text_in] * a.per_source, return_tensors="pt", padding=True).to("cuda")
        with torch.no_grad():
            gen = model.generate(**batch, max_new_tokens=a.max_new_tokens, do_sample=True, temperature=0.8, top_p=0.95)
        for j in range(a.per_source):
            text = tok.decode(gen[j, batch["input_ids"].shape[1] :], skip_special_tokens=True).strip()
            if synthetic_gen.acceptable(text, texts[k]):
                records.append(synthetic_gen.make_record(ids[k], y[k], text, j))
            else:
                rejected += 1
        print(n + 1, "/", len(sources), "acceptés", len(records), "rejetés", rejected, flush=True)
    label_of = dict(zip(ids, y, strict=True))
    augment.validated_synthetic(records, {ids[k] for k in train}, targets, label_of)
    validation = {ids[k]: texts[k] for k, g in enumerate(folds) if g == a.fold}
    copies = augment.copies_of_validation({r["id"]: r["text"] for r in records}, validation)
    kept = [r for r in records if r["id"] not in set(copies)]
    path = out_dir / f"{a.slug}.jsonl"
    path.write_text("\n".join(json.dumps(r, ensure_ascii=False) for r in kept) + "\n", encoding="utf-8")
    print(json.dumps({"slug": a.slug, "acceptes": len(records), "rejetes": rejected, "copies_de_la_validation": len(copies), "ecrits": len(kept), "fichier": str(path.relative_to(ROOT))}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
