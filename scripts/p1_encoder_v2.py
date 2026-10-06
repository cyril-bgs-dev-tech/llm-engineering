#!/usr/bin/env python3
"""Encodeur affiné, recette v2 (RM-41, RM-55) : même chargement, mêmes données et même évaluation que `p1_finetune.py` (mode full, importé sans modification), boucle `train_v2`
avec options (lissage d'étiquettes, EMA, curriculum, bf16 par autocast), selon une fiche préenregistrée ; une option à la fois par fiche.
Usage : p1_encoder_v2.py MODELE --lr LR [--fold 0] [--epochs 10] [--seed 1000] [--label-smoothing 0.1] [--ema 0.99] [--curriculum-epochs 2] [--autocast-bf16]
        [--fold-key control_folds_by_author] [--fiche CHEMIN] --slug NOM [--register] [--device cuda] [--max-steps N]"""
import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent))
import p1_04_06_tfidf
import p1_finetune
from llmft import evaluation, failures, lora_train, train_v2
from llmft.energy import PowerSampler
from llmft.mini_registry import register_run


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("model")
    ap.add_argument("--lr", type=float, required=True)
    ap.add_argument("--fold", type=int, default=0)
    ap.add_argument("--fold-key", default="folds", help="clé des plis dans la partition : folds (par patient) ou control_folds_by_author (RM-39)")
    ap.add_argument("--epochs", type=int, default=10)
    ap.add_argument("--max-len", type=int, default=508)
    ap.add_argument("--effective-batch", type=int, default=32)
    ap.add_argument("--micro-batch", type=int, default=16)
    ap.add_argument("--warmup", type=int, default=20)
    ap.add_argument("--seed", type=int, default=1000)
    ap.add_argument("--label-smoothing", type=float, default=0.0)
    ap.add_argument("--ema", type=float, default=0.0)
    ap.add_argument("--curriculum-epochs", type=int, default=0)
    ap.add_argument("--autocast-bf16", action="store_true")
    ap.add_argument("--max-steps", type=int, default=0)
    ap.add_argument("--limit-seconds", type=float, default=0.0)
    ap.add_argument("--device", default="cuda")
    ap.add_argument("--fiche", default="")
    ap.add_argument("--slug", required=True)
    ap.add_argument("--register", action="store_true")
    a = ap.parse_args()

    import torch
    from transformers import AutoTokenizer

    fiche_sha = hashlib.sha256((ROOT / a.fiche).read_bytes()).hexdigest() if a.fiche else None
    texts, y, folds, excluded, ids = p1_04_06_tfidf.load("chapter", a.fold_key)
    labels = sorted(set(y))
    idx = np.array([labels.index(v) for v in y])
    tr, te = np.where(folds != a.fold)[0], np.where(folds == a.fold)[0]
    tok = AutoTokenizer.from_pretrained(a.model)
    pad_id = tok.pad_token_id if tok.pad_token_id is not None else tok.eos_token_id
    x_tr = p1_finetune.build_inputs(tok, [texts[i] for i in tr], a.max_len)
    x_te = p1_finetune.build_inputs(tok, [texts[i] for i in te], a.max_len) if not a.max_steps else []
    if a.max_steps:
        keep = np.random.default_rng(a.seed).permutation(len(x_tr))[: a.max_steps * a.effective_batch]
        x_tr, tr = [x_tr[i] for i in keep], tr[keep]
    torch.manual_seed(a.seed)
    model, route = p1_finetune.load_model(a.model, "full", len(labels), pad_id, 16, 32)
    model = model.to(a.device)
    cfg: dict[str, Any] = {k: v for k, v in vars(a).items() if k != "register"}
    cfg.update({"route": route, "labels": labels, "n_train": len(tr), "n_eval": len(te), "fiche_sha256": fiche_sha})
    record: dict[str, Any] = {"kind": "preflight" if a.max_steps else "train", "slug": a.slug, "params": cfg}
    try:
        with PowerSampler() as power:
            res = train_v2.train_v2(model, x_tr, [int(idx[i]) for i in tr], len(labels), pad_id, a.device, a.effective_batch, a.micro_batch, a.epochs if not a.max_steps else 1, a.lr,
                                    a.warmup, a.seed, a.label_smoothing, a.ema, a.curriculum_epochs, a.autocast_bf16, projected_limit_seconds=a.limit_seconds or None)
    except lora_train.TrainingAborted as exc:
        record.update({"status": "aborted", "summary": f"{a.slug} : arrêt anticipé, durée projetée {exc.projected_seconds:.0f} s", "loss_history": exc.loss_history, "error": str(exc)})
        if a.register:
            print(register_run(ROOT / "results/runs", record))
        return 4
    except lora_train.TrainingDiverged as exc:
        record.update({"summary": f"{a.slug} : perte non finie au pas {len(exc.loss_history)}", "loss_history": exc.loss_history, "error": str(exc)})
        if a.register:
            print(failures.register_failed(ROOT / "results/runs", record))
        return 2
    metrics: dict[str, Any] = {"steps": len(res.loss_history), "seconds_train": round(res.seconds, 1), "loss_first": res.loss_history[0], "loss_last": res.loss_history[-1],
                               "peak_reserved_gib": round(res.peak_reserved_gib or 0, 2), "energie": power.summary()}
    if a.max_steps:
        summary = f"pré-vol {a.slug} : {len(res.loss_history)} pas, {metrics['seconds_train']} s"
    else:
        probs = p1_finetune.predict(model, x_te, pad_id, a.device, a.micro_batch, len(labels))
        rep = evaluation.chapter_report(idx[te], probs, labels, excluded=(excluded,) if excluded else ())
        pred_payload = json.dumps({"ids": [ids[i] for i in te], "pred": [labels[int(k)] for k in probs.argmax(1)], "fold": a.fold}, ensure_ascii=False)
        metrics.update({"macro_f1": round(rep["macro_f1"], 4), "accuracy": round(rep["accuracy"], 4), "log_loss": round(rep["log_loss"], 4), "ece": round(rep["ece"], 4),
                        "predictions_sha256": hashlib.sha256(pred_payload.encode()).hexdigest()})
        summary = f"{a.slug} : macro-F1 {metrics['macro_f1']} sur le pli {a.fold} (17 chapitres), {metrics['seconds_train']} s d'entraînement"
        if a.register:
            out = ROOT / "results/predictions" / f"{a.slug}.json"
            out.write_text(pred_payload, encoding="utf-8")
            np.savez_compressed(out.with_suffix(".probs.npz"), ids=np.array([ids[i] for i in te]), probs=probs.astype(np.float32), labels=np.array(labels))
    record.update({"status": "ok", "summary": summary, "loss_history": res.loss_history, "metrics": metrics})
    print(json.dumps({"summary": summary, "metrics": metrics}, ensure_ascii=False, indent=1))
    if a.register:
        print(register_run(ROOT / "results/runs", record))
    return 0


if __name__ == "__main__":
    sys.exit(main())
