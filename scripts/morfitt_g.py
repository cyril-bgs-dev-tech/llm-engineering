#!/usr/bin/env python3
"""G gelé transposé sur MorFITT (RM-61, fiche 2026-10-17-g-gele-morfitt) : LoRA Qwen3.5-4B à tête multi-étiquettes, type et classes lus dans le contrat `task_specs/morfitt_specialities.yaml`,
recette gelée du LoRA de G sans aucun réglage (taux 1e-4, 10 époques, rang 16, alpha 32, lot effectif 32, micro-lot 1, contexte 4 096, échauffement 20, graine 1000) ;
G = moyenne à parts égales du LoRA, des cinq encodeurs de RM-49 (probabilités du test sauvegardées) et du TF-IDF de RM-49 (C de son réglage, recalculé deux fois) ; seuil fixe 0,5 ;
F1 pondéré du papier de référence sur le test public (seconde lecture, déclarée dans la fiche), intervalle bootstrap, verdict contre le meilleur chiffre publié (règle (d)).
Usage : morfitt_g.py [--max-steps N] [--register] ; `--max-steps` : pré-vol sur un sous-ensemble de l'entraînement, **sans lire le test**. GPU libre, sous run_guarded.sh ; lancement réel subordonné à Q26."""
import hashlib
import json
import sys
from pathlib import Path
from typing import Any

import numpy as np
from numpy.typing import NDArray

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent))
import morfitt_run
import p1_finetune
from llmft import machine_health, multilabel, taskspec
from llmft import service_g as sg
from llmft.mini_registry import register_run
from llmft.resilience import agree_twice

BASE, MAX_LEN, LR, EPOCHS, RANK, ALPHA, EFFECTIVE, MICRO, WARMUP, SEED = "Qwen/Qwen3.5-4B", 4096, 1e-4, 10, 16, 32, 32, 1, 20, 1000
PUBLISHED_BEST = ("DrLongformer-CP", 71.95)  # F1 pondéré, test, arXiv 2402.16689 tableau 3 (vérifié à la source le 06/10/2026, RM-49)
FICHE = "experiments/2026-10-17-g-gele-morfitt.md"
CONTRACT = ROOT / "task_specs/morfitt_specialities.yaml"


def published_verdict(lo: float, hi: float, published: float) -> str:
    """Règle (d) de la feuille de route : le chiffre publié n'est dépassé que si la borne basse de l'intervalle à 95 % est au-dessus."""
    return "dépassé" if lo > published else ("en dessous" if hi < published else "dans la bande")


def paired_diff_ci(y: NDArray[np.int_], pred_a: NDArray[np.int_], pred_b: NDArray[np.int_], n_boot: int = 2000, seed: int = 20261017) -> tuple[float, float, float]:
    """Différence de F1 pondéré (points, a moins b) et intervalle à 95 % par bootstrap apparié des résumés (mêmes tirages pour a et b)."""
    def wf1(rows: NDArray[np.int_], p: NDArray[np.int_]) -> float:
        return 100 * multilabel.f1_scores(y[rows], p[rows])["weighted_f1"]

    every = np.arange(len(y))
    rng = np.random.default_rng(seed)
    diffs = []
    for _ in range(n_boot):
        rows = rng.integers(0, len(y), len(y))
        diffs.append(wf1(rows, pred_a) - wf1(rows, pred_b))
    return round(wf1(every, pred_a) - wf1(every, pred_b), 2), round(float(np.percentile(diffs, 2.5)), 2), round(float(np.percentile(diffs, 97.5)), 2)


def sigmoid_probs(model: Any, ids: list[list[int]], pad_id: int, n_labels: int) -> NDArray[np.float64]:
    import torch

    from llmft import lora_train

    probs = np.zeros((len(ids), n_labels))
    model.eval()
    with torch.no_grad():
        order = np.argsort([len(x) for x in ids])
        for s in range(0, len(ids), 8):
            idx = order[s : s + 8]
            x, m = lora_train._pad([ids[i] for i in idx], pad_id, "cuda")
            probs[idx] = torch.sigmoid(model(input_ids=x, attention_mask=m).logits.float()).cpu().numpy()
    return probs


def scores(y: NDArray[np.int_], probs: NDArray[np.floating]) -> dict[str, Any]:
    pred = multilabel.predict_labels(probs)
    s = multilabel.f1_scores(y, pred)
    return {"weighted_f1": round(100 * s["weighted_f1"], 2), "micro_f1": round(100 * s["micro_f1"], 2), "macro_f1": round(100 * s["macro_f1"], 2), "ic95_weighted_f1_bootstrap": morfitt_run.bootstrap_ci(y, pred)}


def main() -> int:
    import torch
    from transformers import AutoTokenizer

    start = machine_health.snapshot()
    max_steps = int(sys.argv[sys.argv.index("--max-steps") + 1]) if "--max-steps" in sys.argv else 0
    spec = taskspec.load_task_spec(CONTRACT)
    if spec.type != "multilabel":
        raise SystemExit(f"le contrat {CONTRACT.name} n'est pas multi-étiquettes")
    tr_x, tr_y = morfitt_run.load_split("train")
    if tr_y.shape[1] != len(spec.classes):
        raise SystemExit(f"{tr_y.shape[1]} étiquettes dans les données contre {len(spec.classes)} classes au contrat")
    tok = AutoTokenizer.from_pretrained(BASE)
    pad_id = int(tok.pad_token_id if tok.pad_token_id is not None else tok.eos_token_id)
    x_tr = p1_finetune.build_inputs(tok, tr_x, MAX_LEN)
    y_tr = tr_y
    if max_steps:  # pré-vol : les plus longs résumés d'abord (pire cas mémoire), une époque, le test n'est pas lu
        order = np.argsort([-len(x) for x in x_tr])[: max_steps * EFFECTIVE]
        x_tr, y_tr = [x_tr[i] for i in order], tr_y[order]
    torch.manual_seed(SEED)
    model, route = p1_finetune.load_model(BASE, "lora", len(spec.classes), pad_id, RANK, ALPHA)
    model = model.to("cuda")
    res = multilabel.train_multilabel(model, x_tr, y_tr, pad_id, "cuda", EFFECTIVE, MICRO, 1 if max_steps else EPOCHS, LR, WARMUP, SEED)
    cost = {"steps": len(res.loss_history), "seconds_train": round(res.seconds, 1), "peak_alloc_gib": round(torch.cuda.max_memory_allocated() / 2**30, 2),
            "peak_reserved_gib": round(torch.cuda.max_memory_reserved() / 2**30, 2), "loss_first": res.loss_history[0], "loss_last": res.loss_history[-1]}
    params = {"fiche": FICHE, "fiche_sha256": hashlib.sha256((ROOT / FICHE).read_bytes()).hexdigest() if (ROOT / FICHE).exists() else None, "route": route,
              "base": BASE, "lr": LR, "epochs": EPOCHS, "rank": RANK, "alpha": ALPHA, "effective_batch": EFFECTIVE, "micro_batch": MICRO, "max_len": MAX_LEN, "seed": SEED, "max_steps": max_steps}
    if max_steps:
        out: dict[str, Any] = {"pre_vol": cost}
        print(json.dumps(out, indent=1, ensure_ascii=False))
        if "--register" in sys.argv:
            print(register_run(ROOT / "results/runs", {"kind": "preflight", "slug": "preflight-morfitt-g-lora", "status": "ok", "summary": f"pré-vol du LoRA multi-étiquettes MorFITT : {cost['steps']} pas, pic réservé {cost['peak_reserved_gib']} Gio",
                                                        "params": params, "metrics": out, "machine_health": machine_health.stamp(start)}))
        return 0
    te_x, te_y = morfitt_run.load_split("test")  # seconde lecture du test public (la première : RM-49), déclarée dans la fiche
    lora = sigmoid_probs(model, p1_finetune.build_inputs(tok, te_x, MAX_LEN), pad_id, len(spec.classes))
    np.savez_compressed(ROOT / "results/predictions/morfitt-lora-s1000.probs.npz", probs=lora.astype(np.float32))
    encoders = [np.load(ROOT / f"results/predictions/morfitt-enc-s{s}.probs.npz")["probs"].astype(np.float64) for s in morfitt_run.SEEDS]
    c = float(json.loads(morfitt_run.TUNING.read_text(encoding="utf-8"))["tfidf_retenu"]["C"])
    tf = agree_twice(lambda: morfitt_run.tfidf_probs(tr_x, tr_y, te_x, c), equal=lambda a, b: bool(np.array_equal(a, b)))
    g = sg.combine_g(lora, encoders, tf)
    mix = 0.5 * np.mean(encoders, axis=0) + 0.5 * tf  # le mélange de RM-49 (encodeurs et TF-IDF), pendant de E
    y = te_y.astype(int)
    out = {"n_test": len(te_x), "cout_lora": cost, "lora": scores(y, lora), "melange_rm49": scores(y, mix), "g": scores(y, g), "tfidf_C": c}
    d, lo, hi = paired_diff_ci(y, multilabel.predict_labels(g), multilabel.predict_labels(mix))
    out["g_moins_melange_points"] = [d, lo, hi]
    name, published = PUBLISHED_BEST
    out["publie_meilleur"] = {"systeme": name, "weighted_f1": published}
    g_lo, g_hi = out["g"]["ic95_weighted_f1_bootstrap"]
    out["verdict_regle_d"] = published_verdict(g_lo, g_hi, published)
    print(json.dumps(out, indent=1, ensure_ascii=False))
    if "--register" in sys.argv:
        (ROOT / "results/measures/morfitt_g.json").write_text(json.dumps(out, indent=1, ensure_ascii=False), encoding="utf-8")
        print(register_run(ROOT / "results/runs", {"kind": "train", "slug": "morfitt-g-gele", "status": "ok",
                                                    "summary": f"G gelé sur MorFITT : F1 pondéré {out['g']['weighted_f1']} {out['g']['ic95_weighted_f1_bootstrap']} contre {published} publié ({out['verdict_regle_d']})",
                                                    "params": params, "metrics": out, "machine_health": machine_health.stamp(start)}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
