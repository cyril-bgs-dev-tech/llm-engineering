#!/usr/bin/env python3
"""Encodeur élagué (RM-45, fiche 2026-10-05-encodeur-elague) : CamemBERT-bio dont on garde une couche sur `--every` (6 couches sur 12 par défaut), affiné à la recette gelée,
avec ou sans distillation (`--teacher` : mêmes professeurs hors pli que `p3_distill.py`). Importe `p1_finetune` sans le modifier.
Usage : p1_encoder_pruned.py MODELE --lr LR [--every 2] [--teacher "0=slug0,..."] [--alpha-kd 0.5 --temperature 2] [--fold 0] [--epochs 10] [--seed 1000] [--fiche CHEMIN] --slug NOM [--register]"""
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
import p3_distill
from llmft import distill, evaluation, failures, lora_train, prune, train_v2
from llmft.energy import PowerSampler
from llmft.mini_registry import register_run


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("model")
    ap.add_argument("--lr", type=float, required=True)
    ap.add_argument("--every", type=int, default=2)
    ap.add_argument("--teacher", default="")
    ap.add_argument("--alpha-kd", type=float, default=0.5)
    ap.add_argument("--temperature", type=float, default=2.0)
    ap.add_argument("--fold", type=int, default=0)
    ap.add_argument("--epochs", type=int, default=10)
    ap.add_argument("--max-len", type=int, default=508)
    ap.add_argument("--effective-batch", type=int, default=32)
    ap.add_argument("--micro-batch", type=int, default=16)
    ap.add_argument("--warmup", type=int, default=20)
    ap.add_argument("--seed", type=int, default=1000)
    ap.add_argument("--device", default="cuda")
    ap.add_argument("--fiche", default="")
    ap.add_argument("--slug", required=True)
    ap.add_argument("--register", action="store_true")
    a = ap.parse_args()

    import torch
    from transformers import AutoTokenizer

    fiche_sha = hashlib.sha256((ROOT / a.fiche).read_bytes()).hexdigest() if a.fiche else None
    texts, y, folds, excluded, ids = p1_04_06_tfidf.load("chapter")
    labels = sorted(set(y))
    idx = np.array([labels.index(v) for v in y])
    tr, te = np.where(folds != a.fold)[0], np.where(folds == a.fold)[0]
    teacher_probs = None
    teacher_sha: dict[str, str] = {}
    if a.teacher:
        fold_of = {ids[i]: int(folds[i]) for i in range(len(ids))}
        files: dict[int, tuple[list[str], np.ndarray]] = {}
        for f, slug in p3_distill.parse_teacher(a.teacher).items():
            if f == a.fold:
                continue
            path = ROOT / "results/predictions" / f"{slug}.probs.npz"
            z = np.load(path, allow_pickle=False)
            files[f] = ([str(i) for i in z["ids"]], z["probs"].astype(np.float64))
            teacher_sha[slug] = hashlib.sha256(path.read_bytes()).hexdigest()
        teacher_probs = distill.require_teacher([ids[i] for i in tr], distill.oof_teacher_map(files, fold_of)).astype(np.float32)
    tok = AutoTokenizer.from_pretrained(a.model)
    pad_id = tok.pad_token_id if tok.pad_token_id is not None else tok.eos_token_id
    x_tr = p1_finetune.build_inputs(tok, [texts[i] for i in tr], a.max_len)
    x_te = p1_finetune.build_inputs(tok, [texts[i] for i in te], a.max_len)
    torch.manual_seed(a.seed)
    model, route = p1_finetune.load_model(a.model, "full", len(labels), pad_id, 16, 32)
    kept = prune.prune_encoder(model, a.every)
    model = model.to(a.device)
    cfg: dict[str, Any] = {k: v for k, v in vars(a).items() if k != "register"}
    cfg.update({"route": route, "labels": labels, "n_train": len(tr), "n_eval": len(te), "fiche_sha256": fiche_sha, "couches_gardees": kept, "teacher_files_sha256": teacher_sha,
                "parametres_millions": round(sum(p.numel() for p in model.parameters()) / 1e6, 1)})
    record: dict[str, Any] = {"kind": "train", "slug": a.slug, "params": cfg}
    y_tr = [int(idx[i]) for i in tr]
    try:
        with PowerSampler() as power:
            if teacher_probs is not None:
                res = distill.train_distilled(model, x_tr, y_tr, teacher_probs, pad_id, a.device, a.effective_batch, a.micro_batch, a.epochs, a.lr, a.warmup, a.seed, a.alpha_kd, a.temperature)
            else:
                res = train_v2.train_v2(model, x_tr, y_tr, len(labels), pad_id, a.device, a.effective_batch, a.micro_batch, a.epochs, a.lr, a.warmup, a.seed)
    except lora_train.TrainingDiverged as exc:
        record.update({"summary": f"{a.slug} : perte non finie au pas {len(exc.loss_history)}", "loss_history": exc.loss_history, "error": str(exc)})
        if a.register:
            print(failures.register_failed(ROOT / "results/runs", record))
        return 2
    probs = p1_finetune.predict(model, x_te, pad_id, a.device, a.micro_batch, len(labels))
    rep = evaluation.chapter_report(idx[te], probs, labels, excluded=(excluded,) if excluded else ())
    pred_payload = json.dumps({"ids": [ids[i] for i in te], "pred": [labels[int(k)] for k in probs.argmax(1)], "fold": a.fold}, ensure_ascii=False)
    metrics: dict[str, Any] = {"steps": len(res.loss_history), "seconds_train": round(res.seconds, 1), "peak_reserved_gib": round(res.peak_reserved_gib or 0, 2), "energie": power.summary(),
                               "macro_f1": round(rep["macro_f1"], 4), "accuracy": round(rep["accuracy"], 4), "log_loss": round(rep["log_loss"], 4), "ece": round(rep["ece"], 4),
                               "predictions_sha256": hashlib.sha256(pred_payload.encode()).hexdigest()}
    summary = f"{a.slug} : macro-F1 {metrics['macro_f1']} sur le pli {a.fold} (encodeur à {len(kept)} couches), {metrics['seconds_train']} s d'entraînement"
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
