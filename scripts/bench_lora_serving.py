#!/usr/bin/env python3
"""Service d'un LoRA sauvegardé (RM-34) : adaptateur fusionné au modèle de base en bf16 ; latence par patient (lot de 1), débit par lots triés par longueur, mémoire de pointe,
énergie par patient (puissance du GPU échantillonnée pendant la mesure). Développement seulement (pli 0), jamais le test scellé. À lancer GPU libre.
Usage : bench_lora_serving.py MODELE_DE_BASE SLUG_ADAPTATEUR [--n 200] [--batch 8] [--price-eur-kwh 0.25] [--register]
Le prix du kWh est un paramètre de lecture du coût, jamais une valeur mesurée."""
import json
import os
import sys
import time
from pathlib import Path

os.environ.setdefault("TOKENIZERS_PARALLELISM", "false")
os.environ.setdefault("RAYON_NUM_THREADS", "2")

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent))
import p1_04_06_tfidf
import p1_finetune
from llmft import servicecost
from llmft.energy import PowerSampler
from llmft.mini_registry import register_run


def arg(name: str, default: str) -> str:
    return sys.argv[sys.argv.index(name) + 1] if name in sys.argv else default


def main() -> int:
    args = [a for a in sys.argv[1:] if not a.startswith("--") and a not in (arg("--n", ""), arg("--batch", ""), arg("--price-eur-kwh", ""))]
    base_name, slug = args[0], args[1]
    n, batch, price = int(arg("--n", "200")), int(arg("--batch", "8")), float(arg("--price-eur-kwh", "0.25"))
    import torch
    from peft import PeftModel
    from transformers import AutoModelForSequenceClassification, AutoTokenizer

    texts, _, folds, _, _ = p1_04_06_tfidf.load("chapter")
    labels = sorted(set(p1_04_06_tfidf.load("chapter")[1]))
    sample = [t for t, g in zip(texts, folds, strict=True) if g == 0][:n]
    tok = AutoTokenizer.from_pretrained(base_name)
    pad_id = tok.pad_token_id if tok.pad_token_id is not None else tok.eos_token_id
    t0 = time.perf_counter()
    base = AutoModelForSequenceClassification.from_pretrained(base_name, num_labels=len(labels), torch_dtype=torch.bfloat16)
    base.config.pad_token_id = pad_id
    model = PeftModel.from_pretrained(base, ROOT / "artifacts/adapters" / slug).merge_and_unload().to("cuda").eval()
    load_s = time.perf_counter() - t0
    x = p1_finetune.build_inputs(tok, sample, 4096)
    p1_finetune.predict(model, x[:4], pad_id, "cuda", 1, len(labels))  # échauffement
    torch.cuda.reset_peak_memory_stats()
    single: list[float] = []
    with PowerSampler() as ps_single:
        for xi in x:
            s = time.perf_counter()
            p1_finetune.predict(model, [xi], pad_id, "cuda", 1, len(labels))
            torch.cuda.synchronize()
            single.append(1000 * (time.perf_counter() - s))
    e_single = servicecost.energy_wh(np.array(ps_single.samples), 1.0)
    with PowerSampler() as ps_batch:
        s = time.perf_counter()
        p1_finetune.predict(model, x, pad_id, "cuda", batch, len(labels))
        torch.cuda.synchronize()
        batch_s = time.perf_counter() - s
    e_batch = servicecost.energy_wh(np.array(ps_batch.samples), 1.0)
    out = {"adaptateur": slug, "fusionne_bf16": True, "n_patients": len(x), "chargement_s": round(load_s, 1), **servicecost.latency_summary(single),
           "debit_lot_patients_par_s": round(len(x) / batch_s, 2), "taille_lot": batch, "memoire_pic_gib": round(torch.cuda.max_memory_allocated() / 2**30, 2),
           "puissance_moyenne_w": round(float(np.mean(ps_batch.samples)), 1) if ps_batch.samples else None,
           "energie_lot": servicecost.per_1000(e_batch, len(x), price), "energie_lot_de_1": servicecost.per_1000(e_single, len(x), price), "prix_eur_kwh_parametre": price}
    print(json.dumps(out, indent=1, ensure_ascii=False))
    (ROOT / "results/measures" / f"bench_lora_serving_{slug}.json").write_text(json.dumps(out, indent=1, ensure_ascii=False), encoding="utf-8")
    if "--register" in sys.argv:
        print(register_run(ROOT / "results/runs", {"kind": "measure", "slug": f"bench-lora-serving-{slug}", "status": "ok", "summary": f"Service LoRA fusionné bf16 : p50 {out['p50_ms']} ms, {out['debit_lot_patients_par_s']} patients/s en lot de {batch}", "params": {"n": n, "batch": batch}, "metrics": out}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
