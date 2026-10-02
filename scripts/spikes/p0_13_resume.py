#!/usr/bin/env python3
"""P0-13 : lancement par `accelerate launch` sur 1 GPU, point de sauvegarde et reprise vérifiés.

Trois usages : sans option (tous les pas), `--stop-at K` (sauvegarde l'état à K pas puis s'arrête), `--resume` (recharge l'état
et poursuit). Les lots sont dérivés de la graine et du numéro de pas : une reprise voit exactement les mêmes lots.
"""
import argparse
import json
import sys
from pathlib import Path

import torch
from accelerate import Accelerator
from accelerate.utils import set_seed
from peft import LoraConfig, get_peft_model
from transformers import AutoModelForCausalLM, AutoTokenizer

MODEL = "Qwen/Qwen3-0.6B"
TEXTS = ["Compte rendu d'hospitalisation : pneumopathie aiguë communautaire chez un patient de soixante ans.",
         "Compte rendu opératoire : cholécystectomie par coelioscopie sans incident peropératoire.",
         "Compte rendu de consultation : suivi d'une hypertension artérielle équilibrée sous traitement.",
         "Compte rendu d'anatomopathologie : adénocarcinome bronchique infiltrant du lobe supérieur."]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--steps", type=int, default=20)
    ap.add_argument("--stop-at", type=int, default=None)
    ap.add_argument("--resume", action="store_true")
    ap.add_argument("--ckpt", default="artifacts/spikes/p0_13_ckpt")
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    set_seed(1234)
    acc = Accelerator(mixed_precision="bf16")
    tok = AutoTokenizer.from_pretrained(MODEL)
    model = AutoModelForCausalLM.from_pretrained(MODEL, torch_dtype=torch.bfloat16)
    model = get_peft_model(model, LoraConfig(r=8, lora_alpha=16, lora_dropout=0.0, target_modules="all-linear", task_type="CAUSAL_LM"))
    opt = torch.optim.AdamW([p for p in model.parameters() if p.requires_grad], lr=1e-3)
    model, opt = acc.prepare(model, opt)

    start = 0
    if args.resume:
        acc.load_state(args.ckpt)
        start = json.loads((Path(args.ckpt) / "step.json").read_text())["step"]

    losses = {}
    model.train()
    for step in range(start, args.stop_at or args.steps):
        g = torch.Generator().manual_seed(1000 + step)
        order = torch.randperm(len(TEXTS), generator=g).tolist()
        batch = tok([TEXTS[i] for i in order[:2]], return_tensors="pt", padding=True).to(acc.device)
        batch["labels"] = batch["input_ids"].clone()
        loss = model(**batch).loss
        acc.backward(loss)
        opt.step()
        opt.zero_grad(set_to_none=True)
        losses[step] = float(loss)
    if args.stop_at:
        acc.save_state(args.ckpt)
        (Path(args.ckpt) / "step.json").write_text(json.dumps({"step": args.stop_at}))
    Path(args.out).write_text(json.dumps({"start": start, "losses": losses}, indent=1), encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
