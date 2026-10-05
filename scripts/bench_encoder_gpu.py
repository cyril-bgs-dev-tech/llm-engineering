#!/usr/bin/env python3
"""Service de l'encodeur sauvegardé sur GPU (RM-34) : latence par patient (lot de 1), débit par lots, mémoire de pointe, énergie par 1 000 patients, fp32 et bf16.
Développement seulement (pli 0). À lancer GPU libre. Usage : bench_encoder_gpu.py SLUG_DU_MODELE_SAUVEGARDE [--n 200] [--batch 16] [--price-eur-kwh 0.25] [--register]"""
import json
import sys
import time
from functools import partial
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent))
import bench_lora_serving
import p1_04_06_tfidf
import p1_finetune
from llmft import energy, servicecost
from llmft.mini_registry import register_run

arg = bench_lora_serving.arg


def batch_pass(model: object, pad_id: int, x: list[list[int]], batch: int, n_labels: int) -> int:
    import torch

    p1_finetune.predict(model, x, pad_id, "cuda", batch, n_labels)
    torch.cuda.synchronize()
    return len(x)


def single_pass(model: object, pad_id: int, x: list[list[int]], n_labels: int) -> int:
    import torch

    for xi in x[:50]:
        p1_finetune.predict(model, [xi], pad_id, "cuda", 1, n_labels)
    torch.cuda.synchronize()
    return min(50, len(x))


def main() -> int:
    slug = sys.argv[1]
    n, batch, price = int(arg("--n", "200")), int(arg("--batch", "16")), float(arg("--price-eur-kwh", "0.25"))
    import torch
    from transformers import AutoModelForSequenceClassification, AutoTokenizer

    model_dir = ROOT / "artifacts/models" / slug
    texts, y, folds, _, _ = p1_04_06_tfidf.load("chapter")
    labels = sorted(set(y))
    sample = [t for t, g in zip(texts, folds, strict=True) if g == 0][:n]
    tok = AutoTokenizer.from_pretrained(model_dir)
    x = p1_finetune.build_inputs(tok, sample, 508)
    out: dict[str, object] = {"modele": slug, "n_patients": len(x), "taille_lot": batch, "prix_eur_kwh_parametre": price}
    for name, dtype in (("fp32", torch.float32), ("bf16", torch.bfloat16)):
        model = AutoModelForSequenceClassification.from_pretrained(model_dir, torch_dtype=dtype).to("cuda").eval()
        p1_finetune.predict(model, x[:4], tok.pad_token_id, "cuda", 1, len(labels))
        torch.cuda.reset_peak_memory_stats()
        single: list[float] = []
        for xi in x:
            s = time.perf_counter()
            p1_finetune.predict(model, [xi], tok.pad_token_id, "cuda", 1, len(labels))
            torch.cuda.synchronize()
            single.append(1000 * (time.perf_counter() - s))
        batch_s_probe = time.perf_counter()
        p1_finetune.predict(model, x, tok.pad_token_id, "cuda", batch, len(labels))
        torch.cuda.synchronize()
        batch_probe = time.perf_counter() - batch_s_probe

        e_batch = energy.measure_repeated(partial(batch_pass, model, tok.pad_token_id, x, batch, len(labels)), 15.0)
        e_single = energy.measure_repeated(partial(single_pass, model, tok.pad_token_id, x, len(labels)), 15.0)
        out[name] = {**servicecost.latency_summary(single), "debit_lot_patients_par_s": round(len(x) / batch_probe, 1), "memoire_pic_gib": round(torch.cuda.max_memory_allocated() / 2**30, 2),
                     "energie_lot_15s": e_batch, "energie_lot_de_1_15s": e_single}
        print(name, out[name], flush=True)
        del model
        torch.cuda.empty_cache()
    (ROOT / "results/measures" / f"bench_encoder_gpu_{slug}{arg('--tag', '')}.json").write_text(json.dumps(out, indent=1, ensure_ascii=False), encoding="utf-8")
    if "--register" in sys.argv:
        print(register_run(ROOT / "results/runs", {"kind": "measure", "slug": f"bench-encoder-gpu-{slug}{arg('--tag', '')}", "status": "ok", "summary": f"Service de l'encodeur {slug} sur GPU, fp32 et bf16", "params": {"n": n, "batch": batch}, "metrics": out}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
