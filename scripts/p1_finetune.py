#!/usr/bin/env python3
"""Affinage d'un classifieur de chapitre CIM-10 sur le pli de développement k (P1-07 encodeur, P1-11 / P1-13 LoRA), selon une fiche préenregistrée.

Entraînement sur les quatre autres plis (clé `folds`), évaluation sur le pli k : le test scellé n'est jamais lu. Entrée : documents du patient concaténés
avec balise de type, troncature tête et fin au niveau des tokens (PROTOCOLE.md section 1).
Usage : p1_finetune.py MODELE --mode {lora|full} --lr LR [--fold 0] [--epochs 2] [--max-len 4096] [--rank 16] [--alpha 32] [--effective-batch 32]
        [--micro-batch 4] [--seed 1000] [--max-steps N] [--fiche CHEMIN] [--slug NOM] [--register]
`--max-steps N` : pré-vol (vram-preflight) : N pas d'optimiseur, pas d'évaluation, enregistré comme `preflight` seulement avec --register ;
`--order random` mesure le débit moyen (RM-16) au lieu du pire cas.
Lancer avec HF_HOME=$PWD/artifacts/hf_cache."""
import argparse
import hashlib
import json
import os
import sys
import time
from pathlib import Path
from typing import Any

# Le tokenizer Rust de HF a fait des erreurs de segmentation (signal 11) avec un parallélisme sur 32 threads (3 runs de P1-11 sur 6, 03/10/2026)
os.environ.setdefault("TOKENIZERS_PARALLELISM", "false")
os.environ.setdefault("RAYON_NUM_THREADS", "2")

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent))
import p1_04_06_tfidf  # chargement des étiquettes de développement, même fonction que les références TF-IDF
from llmft import evaluation, failures, last_token, lora_train
from llmft.fingerprint import dir_sha256
from llmft.mini_registry import register_run


def build_inputs(tok: Any, texts: list[str], max_len: int) -> list[list[int]]:
    """Tokens avec jetons spéciaux du modèle ; au-delà de `max_len` tokens de texte : `max_len`/2 de tête et de fin avec le marqueur `[...]` (la séquence dépasse donc `max_len` du marqueur et des jetons spéciaux ; pour un encodeur à 512 positions, passer 508)."""
    marker = tok.encode("[...]", add_special_tokens=False)
    prefix, suffix = lora_train.special_affixes(tok.encode)
    out = []
    for t in texts:
        ids = tok.encode(t, add_special_tokens=False)
        ids = lora_train.truncate_head_tail(ids, max_len, marker)  # max_len/2 tokens de tête et de fin, comme PROTOCOLE.md section 1
        out.append([*prefix, *ids, *suffix])
    return out


def load_model(name: str, mode: str, n_labels: int, pad_id: int, rank: int, alpha: int) -> tuple[Any, str]:
    """Voie A : classe de classification de transformers ; voie B (Gemma 4) : modèle causal et tête sur le dernier token. Renvoie (modèle, voie)."""
    import torch
    from transformers import AutoConfig, AutoModelForCausalLM, AutoModelForSequenceClassification

    dtype = torch.bfloat16 if mode == "lora" else torch.float32
    try:
        model = AutoModelForSequenceClassification.from_pretrained(name, num_labels=n_labels, torch_dtype=dtype)
        route = "A"
    except ValueError:  # « Unrecognized configuration class » : pas de classe de classification pour cette architecture
        base = AutoModelForCausalLM.from_pretrained(name, torch_dtype=dtype)
        cfg = AutoConfig.from_pretrained(name)
        hidden = getattr(cfg, "hidden_size", None) or cfg.text_config.hidden_size
        base.gradient_checkpointing_enable(gradient_checkpointing_kwargs={"use_reentrant": False})
        base.enable_input_require_grads()
        from peft import LoraConfig, get_peft_model

        base = get_peft_model(base, LoraConfig(task_type="CAUSAL_LM", r=rank, lora_alpha=alpha, lora_dropout=0.05, target_modules="all-linear"))
        return last_token.LastTokenClassifier(base, hidden, n_labels), "B"
    model.config.pad_token_id = pad_id
    if hasattr(model.config, "text_config"):
        model.config.text_config.pad_token_id = pad_id
    if mode == "lora":
        from peft import LoraConfig, get_peft_model

        model.gradient_checkpointing_enable(gradient_checkpointing_kwargs={"use_reentrant": False})
        model.enable_input_require_grads()
        model = get_peft_model(model, LoraConfig(task_type="SEQ_CLS", r=rank, lora_alpha=alpha, lora_dropout=0.05, target_modules="all-linear"))
    return model, route


def predict(model: Any, ids: list[list[int]], pad_id: int, device: str, micro_batch: int, n_labels: int) -> np.ndarray:
    import torch

    model.eval()
    order = np.argsort([len(x) for x in ids])
    probs = np.zeros((len(ids), n_labels))
    with torch.no_grad():
        for s in range(0, len(ids), micro_batch):
            idx = order[s : s + micro_batch]
            x, m = lora_train._pad([ids[i] for i in idx], pad_id, device)
            probs[idx] = torch.softmax(model(input_ids=x, attention_mask=m).logits.float(), dim=-1).cpu().numpy()
    return probs


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("model")
    ap.add_argument("--mode", choices=["lora", "full"], required=True)
    ap.add_argument("--lr", type=float, required=True)
    ap.add_argument("--fold", type=int, default=0)
    ap.add_argument("--epochs", type=int, default=2)
    ap.add_argument("--max-len", type=int, default=4096)
    ap.add_argument("--rank", type=int, default=16)
    ap.add_argument("--alpha", type=int, default=32)
    ap.add_argument("--effective-batch", type=int, default=32)
    ap.add_argument("--micro-batch", type=int, default=4)
    ap.add_argument("--warmup", type=int, default=20)
    ap.add_argument("--seed", type=int, default=1000)
    ap.add_argument("--max-steps", type=int, default=0)
    ap.add_argument("--order", choices=["longest", "random"], default="longest", help="pré-vol : exemples les plus longs d'abord (pire cas mémoire) ou tirage au hasard (débit moyen)")
    ap.add_argument("--limit-seconds", type=float, default=0.0, help="arrêt anticipé : limite de durée projetée (1,5 fois l'estimation de la fiche) ; 0 = aucune")
    ap.add_argument("--class-weights", choices=["none", "inv-sqrt"], default="none", help="perte pondérée par classe en 1/√n (exploration Q19, fiche à part) ; none = référence")
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
    tok = AutoTokenizer.from_pretrained(a.model)
    pad_id = tok.pad_token_id if tok.pad_token_id is not None else tok.eos_token_id
    t_tok = time.time()
    x_tr = build_inputs(tok, [texts[i] for i in tr], a.max_len)
    x_te = build_inputs(tok, [texts[i] for i in te], a.max_len) if not a.max_steps else []
    tok_seconds = time.time() - t_tok
    if a.max_steps:  # pré-vol : le plus long exemple d'abord, le pire cas mémoire
        order = (np.argsort([-len(x) for x in x_tr]) if a.order == "longest" else np.random.default_rng(a.seed).permutation(len(x_tr)))[: a.max_steps * a.effective_batch]
        x_tr = [x_tr[i] for i in order]
        tr = tr[order]
    torch.manual_seed(a.seed)
    model, route = load_model(a.model, a.mode, len(labels), pad_id, a.rank, a.alpha)
    model = model.to("cuda")
    cfg: dict[str, Any] = {k: v for k, v in vars(a).items() if k not in ("register",)}
    cfg.update({"route": route, "labels": labels, "n_train": len(tr), "n_eval": len(te), "fiche_sha256": fiche_sha, "train_token_length_max": max(len(x) for x in x_tr)})
    record: dict[str, Any] = {"kind": "preflight" if a.max_steps else "train", "slug": a.slug, "params": cfg}
    try:
        res = lora_train.train(model, x_tr, [int(idx[i]) for i in tr], pad_id, "cuda", a.effective_batch, a.micro_batch, a.epochs if not a.max_steps else 1,
                               a.lr, a.warmup, a.seed, projected_limit_seconds=a.limit_seconds or None,
                               class_weights=lora_train.inverse_sqrt_class_weights([int(idx[i]) for i in tr], len(labels)) if a.class_weights == "inv-sqrt" else None)
    except lora_train.TrainingAborted as exc:
        record.update({"status": "aborted", "summary": f"{a.slug} : arrêt anticipé, durée projetée {exc.projected_seconds:.0f} s", "loss_history": exc.loss_history, "error": str(exc)})
        print(json.dumps({k: record[k] for k in ("slug", "summary")}, ensure_ascii=False))
        if a.register:
            print(register_run(ROOT / "results/runs", record))
        return 4
    except lora_train.TrainingDiverged as exc:
        record.update({"summary": f"{a.slug} : perte non finie au pas {len(exc.loss_history)}", "loss_history": exc.loss_history, "error": str(exc)})
        print(json.dumps({k: record[k] for k in ("slug", "summary")}))
        if a.register:
            print(failures.register_failed(ROOT / "results/runs", record))
        return 2
    except torch.cuda.OutOfMemoryError as exc:
        record.update({"summary": f"{a.slug} : mémoire insuffisante", "loss_history": [], "error": str(exc)[:300]})
        print(json.dumps({k: record[k] for k in ("slug", "summary")}))
        if a.register:
            print(failures.register_failed(ROOT / "results/runs", record))
        return 3
    metrics: dict[str, Any] = {"steps": len(res.loss_history), "seconds_train": round(res.seconds, 1), "seconds_tokenize": round(tok_seconds, 1),
                               "peak_alloc_gib": round(res.peak_alloc_gib or 0, 2), "peak_reserved_gib": round(res.peak_reserved_gib or 0, 2),
                               "loss_first": res.loss_history[0], "loss_last": res.loss_history[-1]}
    if a.max_steps:
        summary = f"pré-vol {a.slug} : {len(res.loss_history)} pas, pic réservé {metrics['peak_reserved_gib']} Gio, {metrics['seconds_train']} s"
    else:
        probs = predict(model, x_te, pad_id, "cuda", a.micro_batch, len(labels))
        rep = evaluation.chapter_report(idx[te], probs, labels, excluded=(excluded,) if excluded else ())
        nll = -np.log(np.clip(probs[np.arange(len(te)), idx[te]], 1e-12, 1))
        bal = float(np.mean([nll[idx[te] == c].mean() for c in range(len(labels)) if (idx[te] == c).any()]))
        pred_payload = json.dumps({"ids": [ids[i] for i in te], "pred": [labels[int(k)] for k in probs.argmax(1)], "fold": a.fold}, ensure_ascii=False)
        metrics.update({"macro_f1": round(rep["macro_f1"], 4), "accuracy": round(rep["accuracy"], 4), "log_loss": round(rep["log_loss"], 4),
                        "class_balanced_log_loss": round(bal, 4), "ece": round(rep["ece"], 4), "predictions_sha256": hashlib.sha256(pred_payload.encode()).hexdigest()})
        summary = f"{a.slug} : macro-F1 {metrics['macro_f1']} sur le pli {a.fold} (17 chapitres), {metrics['seconds_train']} s d'entraînement"
        if a.register:
            out = ROOT / "results/predictions" / f"{a.slug}.json"
            out.parent.mkdir(parents=True, exist_ok=True)
            out.write_text(pred_payload, encoding="utf-8")
            np.savez_compressed(out.with_suffix(".probs.npz"), ids=np.array([ids[i] for i in te]), probs=probs.astype(np.float32), labels=np.array(labels))  # pour calibration et prédiction conforme
    if a.register and a.mode == "lora" and not a.max_steps:  # point de sauvegarde pour robustesse, hors-distribution et service (Q4, Q9)
        try:  # un échec de sauvegarde ne doit jamais faire perdre le résultat du run
            adapter_dir = ROOT / "artifacts/adapters" / a.slug
            adapter_dir.mkdir(parents=True, exist_ok=True)
            if route == "A":
                model.save_pretrained(adapter_dir)
            else:
                model.base.save_pretrained(adapter_dir)
                torch.save(model.head.state_dict(), adapter_dir / "head.pt")
            metrics["adapter_dir"] = str(adapter_dir.relative_to(ROOT))
            metrics["adapter_sha256"] = dir_sha256(adapter_dir)
        except (OSError, RuntimeError, ValueError, AttributeError) as exc:
            metrics["adapter_save_error"] = f"{type(exc).__name__}: {str(exc)[:200]}"
    record.update({"status": "ok", "summary": summary, "loss_history": res.loss_history, "metrics": metrics})
    print(json.dumps({"summary": summary, "metrics": metrics}, ensure_ascii=False, indent=1))
    if a.register:
        print(register_run(ROOT / "results/runs", record))
    return 0


if __name__ == "__main__":
    sys.exit(main())
