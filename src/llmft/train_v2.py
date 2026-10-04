"""Boucle d'entraînement de l'encodeur, version 2 (RM-41, RM-55) : lissage d'étiquettes, moyenne exponentielle des poids, curriculum pondéré, bf16 par autocast.

Nouveau module : `lora_train.train` n'est pas modifié (lots en cours). Chaque option est désactivée par défaut ; sans option, la boucle est celle de `lora_train.train`
(même cosinus, même accumulation, mêmes micro-lots, même arrêt sur perte non finie) : la comparaison avec la recette gelée se fait option par option."""
import math
import time
from collections.abc import Sequence
from typing import Any

import numpy as np
import torch

from llmft import lora_train


def curriculum_weights(labels: Sequence[int], n_classes: int) -> torch.Tensor:
    """Poids par classe en 1/n_c (classes absentes : 1), normalisés pour une moyenne de 1 sur les exemples."""
    counts = np.bincount(np.asarray(list(labels), dtype=np.int64), minlength=n_classes).astype(float)
    raw = np.where(counts > 0, 1.0 / np.maximum(counts, 1.0), 1.0)
    scale = float(raw[np.asarray(list(labels), dtype=np.int64)].mean())
    return torch.tensor(raw / scale, dtype=torch.float32)


def ema_update(shadow: list[torch.Tensor], params: Sequence[torch.Tensor], decay: float) -> None:
    """shadow <- decay * shadow + (1 - decay) * params, en place."""
    with torch.no_grad():
        for s, p in zip(shadow, params, strict=True):
            s.mul_(decay).add_(p.detach().float(), alpha=1.0 - decay)


def train_v2(
    model: Any, input_ids: Sequence[Sequence[int]], labels: Sequence[int], n_classes: int, pad_id: int, device: str | torch.device, effective_batch: int, micro_batch: int,
    epochs: int, base_lr: float, warmup_steps: int, seed: int, label_smoothing: float = 0.0, ema_decay: float = 0.0, curriculum_epochs: int = 0, autocast_bf16: bool = False,
    weight_decay: float = 0.0, projected_limit_seconds: float | None = None,
) -> lora_train.TrainResult:
    """Boucle d'entraînement ; avec `ema_decay` > 0 les poids moyennés remplacent les poids du modèle à la fin ; avec `curriculum_epochs` > 0 les premières époques pondèrent
    les exemples à l'inverse de la fréquence de leur classe."""
    params = [p for p in model.parameters() if p.requires_grad]
    opt = torch.optim.AdamW(params, lr=base_lr, weight_decay=weight_decay)
    rng = np.random.default_rng(seed)
    y = torch.tensor(list(labels), dtype=torch.long)
    class_w = curriculum_weights(labels, n_classes) if curriculum_epochs > 0 else None
    shadow = [p.detach().float().clone() for p in params] if ema_decay > 0 else []
    n_total = lora_train.total_steps(len(input_ids), effective_batch, epochs)
    res = lora_train.TrainResult()
    is_cuda = str(device).startswith("cuda")
    if is_cuda:
        torch.cuda.reset_peak_memory_stats()
    t0 = time.time()
    model.train()
    step = 0
    for epoch in range(epochs):
        for micro_batches in lora_train.epoch_plan(len(input_ids), effective_batch, micro_batch, rng):
            for g in opt.param_groups:
                g["lr"] = lora_train.cosine_lr(step, n_total, base_lr, warmup_steps)
            loss_value = 0.0
            for idx, weight in micro_batches:
                ids, mask = lora_train._pad([input_ids[i] for i in idx], pad_id, device)
                with torch.autocast(device_type="cuda" if is_cuda else "cpu", dtype=torch.bfloat16, enabled=autocast_bf16):
                    logits = model(input_ids=ids, attention_mask=mask).logits
                target = y[idx].to(device)
                per_example = torch.nn.functional.cross_entropy(logits.float(), target, reduction="none", label_smoothing=label_smoothing)
                if class_w is not None and epoch < curriculum_epochs:
                    per_example = per_example * class_w.to(device)[target]
                loss = per_example.mean() * weight
                torch.autograd.backward(loss)
                loss_value += float(loss.detach())
            res.loss_history.append(loss_value)
            if not math.isfinite(loss_value):
                raise lora_train.TrainingDiverged(res.loss_history)
            torch.nn.utils.clip_grad_norm_(params, lora_train.MAX_GRAD_NORM)
            opt.step()
            opt.zero_grad(set_to_none=True)
            if shadow:
                ema_update(shadow, params, ema_decay)
            step += 1
            if projected_limit_seconds is not None and step >= max(2, math.ceil(0.1 * n_total)):
                projected = (time.time() - t0) / step * n_total
                if projected > projected_limit_seconds:
                    raise lora_train.TrainingAborted(res.loss_history, projected)
    if shadow:
        with torch.no_grad():
            for s, p in zip(shadow, params, strict=True):
                p.copy_(s.to(p.dtype))
    if is_cuda:
        torch.cuda.synchronize()
        res.peak_alloc_gib = torch.cuda.max_memory_allocated() / 2**30
        res.peak_reserved_gib = torch.cuda.max_memory_reserved() / 2**30
    res.seconds = time.time() - t0
    return res


__all__ = ["curriculum_weights", "ema_update", "train_v2"]
