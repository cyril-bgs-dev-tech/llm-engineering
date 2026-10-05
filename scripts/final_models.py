#!/usr/bin/env python3
"""Modèles finaux pour l'ouverture du test scellé (PROTOCOLE_V2.md section 5) : entraînés sur la **totalité des 3 586 patients de développement**, sans aucune évaluation (il n'y a pas de pli tenu à l'écart),
sauvegardés dans `artifacts/final/` avec leur empreinte SHA-256 et enregistrés au registre. Aucune lecture du test scellé ici.
Usage : final_models.py {tfidf|encoder|student|lora} [--seed 1000] [--fiche CHEMIN] [--register]
tfidf : TF-IDF caractères 3 à 5, poids équilibrés, C = 100 (valeur la plus fréquente des plis, non réglée) ; encoder : CamemBERT-bio, recette gelée 10 époques, 1e-4 ;
student : élève distillé de l'ensemble (alpha 0,5, T = 2), professeur = probabilités hors pli de l'ensemble encodeur + TF-IDF des cinq plis ; lora : Qwen3.5-4B, 10 époques, 1e-4, 4 096 tokens."""
import hashlib
import json
import sys
import time
from pathlib import Path
from typing import Any

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent))
import p1_04_06_tfidf
import p1_finetune
from llmft import distill, lora_train, tfidf, train_v2
from llmft.fingerprint import dir_sha256
from llmft.mini_registry import register_run

OUT = ROOT / "artifacts/final"
TEACHER_FILES = {0: "ensemble-encodeur5-tfidf-charbal", 1: "pli1-ensemble-encodeur5-tfidf-charbal", 2: "pli2-ensemble-encodeur5-tfidf-charbal", 3: "pli3-ensemble-encodeur5-tfidf-charbal", 4: "pli4-ensemble-encodeur5-tfidf-charbal"}


def arg(name: str, default: str) -> str:
    return sys.argv[sys.argv.index(name) + 1] if name in sys.argv else default


def main() -> int:
    kind = sys.argv[1]
    seed = int(arg("--seed", "1000"))
    fiche = arg("--fiche", "")
    fiche_sha = hashlib.sha256((ROOT / fiche).read_bytes()).hexdigest() if fiche else None
    texts, y, folds, excluded, ids = p1_04_06_tfidf.load("chapter")
    labels = sorted(set(y))
    idx = np.array([labels.index(v) for v in y])
    OUT.mkdir(parents=True, exist_ok=True)
    t0 = time.time()
    meta: dict[str, Any] = {"n_train": len(texts), "labels": labels, "seed": seed, "fiche_sha256": fiche_sha, "excluded": excluded}
    if kind == "tfidf":
        import joblib

        vec, model = tfidf.fit_model(texts, y, 100.0, (3, 5), "balanced", "char_wb")
        path = OUT / "tfidf.joblib"
        joblib.dump({"vec": vec, "model": model, "labels": labels}, path)
        meta.update({"artifact": str(path.relative_to(ROOT)), "sha256": hashlib.sha256(path.read_bytes()).hexdigest(), "C": 100.0})
        slug = "final-tfidf"
    else:
        import torch
        from transformers import AutoTokenizer

        if kind in ("encoder", "student"):
            name = "almanach/camembert-bio-base"
            tok = AutoTokenizer.from_pretrained(name)
            pad_id = tok.pad_token_id
            x_tr = p1_finetune.build_inputs(tok, texts, 508)
            torch.manual_seed(seed)
            model, _ = p1_finetune.load_model(name, "full", len(labels), pad_id, 16, 32)
            model = model.to("cuda")
            if kind == "encoder":
                res = train_v2.train_v2(model, x_tr, [int(v) for v in idx], len(labels), pad_id, "cuda", 32, 16, 10, 1e-4, 20, seed)
                slug = f"final-encoder-s{seed}"
            else:
                fold_of = {ids[i]: int(folds[i]) for i in range(len(ids))}
                files = {}
                for f, tslug in TEACHER_FILES.items():
                    z = np.load(ROOT / "results/predictions" / f"{tslug}.probs.npz", allow_pickle=False)
                    files[f] = ([str(i) for i in z["ids"]], z["probs"].astype(np.float64))
                teacher = distill.require_teacher(ids, distill.oof_teacher_map(files, fold_of)).astype(np.float32)
                res = distill.train_distilled(model, x_tr, [int(v) for v in idx], teacher, pad_id, "cuda", 32, 16, 10, 1e-4, 20, seed, 0.5, 2.0)
                slug = f"final-student-s{seed}"
                meta["teacher"] = "ensemble encodeur + TF-IDF, probabilités hors pli des cinq plis"
            path = OUT / slug
            model.save_pretrained(path)
            tok.save_pretrained(path)
        elif kind == "lora":
            name = "Qwen/Qwen3.5-4B"
            tok = AutoTokenizer.from_pretrained(name)
            pad_id = tok.pad_token_id if tok.pad_token_id is not None else tok.eos_token_id
            x_tr = p1_finetune.build_inputs(tok, texts, 4096)
            torch.manual_seed(seed)
            model, route = p1_finetune.load_model(name, "lora", len(labels), pad_id, 16, 32)
            model = model.to("cuda")
            res = lora_train.train(model, x_tr, [int(v) for v in idx], pad_id, "cuda", 32, 1, 10, 1e-4, 20, seed)
            slug = f"final-lora-s{seed}"
            path = OUT / slug
            path.mkdir(parents=True, exist_ok=True)
            model.save_pretrained(path)
            meta["route"] = route
        else:
            raise SystemExit("type inconnu")
        meta.update({"artifact": str(path.relative_to(ROOT)), "sha256": dir_sha256(path), "seconds_train": round(res.seconds, 1), "peak_reserved_gib": round(res.peak_reserved_gib or 0, 2), "loss_last": res.loss_history[-1]})
    meta["seconds_total"] = round(time.time() - t0, 1)
    print(json.dumps(meta, ensure_ascii=False, indent=1))
    if "--register" in sys.argv:
        print(register_run(ROOT / "results/runs", {"kind": "train", "slug": slug, "status": "ok", "summary": f"{slug} : modèle final entraîné sur les 3 586 patients de développement, empreinte {str(meta['sha256'])[:12]}", "params": meta, "metrics": {k: meta[k] for k in ("seconds_total", "sha256")}}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
