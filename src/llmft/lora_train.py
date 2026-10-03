"""Briques d'entraînement du classifieur à tête de classification (LoRA ou non) : calendrier, troncature, lots, boucle.

Rien ici ne dépend d'une tâche ni d'un modèle : le modèle, les identifiants de tokens et les étiquettes arrivent en arguments (PROTOCOLE.md section 1 pour la troncature)."""
from __future__ import annotations

import math
import time
from collections.abc import Sequence
from dataclasses import dataclass, field
from typing import Any

import numpy as np
import torch
from numpy.typing import NDArray

MAX_GRAD_NORM = 1.0


class TrainingDiverged(RuntimeError):
    """Une perte n'est pas finie : le run s'arrête, l'historique sert au classement du registre (`llmft.failures`)."""

    def __init__(self, loss_history: list[float]) -> None:
        super().__init__(f"perte non finie au pas {len(loss_history)}")
        self.loss_history = loss_history


@dataclass
class TrainResult:
    loss_history: list[float] = field(default_factory=list)
    seconds: float = 0.0
    peak_alloc_gib: float | None = None
    peak_reserved_gib: float | None = None


def cosine_lr(step: int, total_steps: int, base_lr: float, warmup_steps: int) -> float:
    """Échauffement linéaire (le pas `warmup_steps - 1` atteint `base_lr`) puis cosinus jusqu'à zéro."""
    if step < warmup_steps:
        return base_lr * (step + 1) / warmup_steps
    progress = (step - warmup_steps) / max(1, total_steps - warmup_steps)
    return base_lr * 0.5 * (1 + math.cos(math.pi * min(progress, 1.0)))


def truncate_head_tail(ids: Sequence[int], max_len: int, marker: Sequence[int]) -> list[int]:
    """Au-delà de `max_len`, garde la moitié de tête et la moitié de fin avec `marker` entre les deux (PROTOCOLE.md section 1)."""
    if len(ids) <= max_len:
        return list(ids)
    half = max_len // 2
    return [*ids[:half], *marker, *ids[len(ids) - half :]]


def total_steps(n: int, effective_batch: int, epochs: int) -> int:
    return math.ceil(n / effective_batch) * epochs


def epoch_plan(n: int, effective_batch: int, micro_batch: int, rng: np.random.Generator) -> list[list[tuple[NDArray[np.int_], float]]]:
    """Un pas d'optimiseur = liste de micro-lots `(indices, poids)` ; les poids somment à un (perte moyenne sur le lot effectif)."""
    order = rng.permutation(n)
    steps: list[list[tuple[NDArray[np.int_], float]]] = []
    for start in range(0, n, effective_batch):
        batch = order[start : start + effective_batch]
        steps.append([(batch[i : i + micro_batch], len(batch[i : i + micro_batch]) / len(batch)) for i in range(0, len(batch), micro_batch)])
    return steps


def _pad(rows: Sequence[Sequence[int]], pad_id: int, device: str | torch.device) -> tuple[torch.Tensor, torch.Tensor]:
    width = max(len(r) for r in rows)
    ids = torch.full((len(rows), width), pad_id, dtype=torch.long)
    mask = torch.zeros((len(rows), width), dtype=torch.long)
    for i, r in enumerate(rows):
        ids[i, : len(r)] = torch.tensor(list(r), dtype=torch.long)  # remplissage à droite
        mask[i, : len(r)] = 1
    return ids.to(device), mask.to(device)


def train(
    model: Any, input_ids: Sequence[Sequence[int]], labels: Sequence[int], pad_id: int, device: str | torch.device, effective_batch: int, micro_batch: int,
    epochs: int, base_lr: float, warmup_steps: int, seed: int, weight_decay: float = 0.0,
) -> TrainResult:
    """Boucle d'entraînement : AdamW sur les paramètres entraînables, cosinus, accumulation, perte moyenne par lot effectif, arrêt sur perte non finie."""
    params = [p for p in model.parameters() if p.requires_grad]
    opt = torch.optim.AdamW(params, lr=base_lr, weight_decay=weight_decay)
    rng = np.random.default_rng(seed)
    y = torch.tensor(list(labels), dtype=torch.long)
    n_total = total_steps(len(input_ids), effective_batch, epochs)
    res = TrainResult()
    is_cuda = str(device).startswith("cuda")
    if is_cuda:
        torch.cuda.reset_peak_memory_stats()
    t0 = time.time()
    model.train()
    step = 0
    for _ in range(epochs):
        for micro_batches in epoch_plan(len(input_ids), effective_batch, micro_batch, rng):
            for g in opt.param_groups:
                g["lr"] = cosine_lr(step, n_total, base_lr, warmup_steps)
            loss_value = 0.0
            for idx, weight in micro_batches:
                ids, mask = _pad([input_ids[i] for i in idx], pad_id, device)
                logits = model(input_ids=ids, attention_mask=mask).logits.float()
                loss = torch.nn.functional.cross_entropy(logits, y[idx].to(device)) * weight
                torch.autograd.backward(loss)
                loss_value += float(loss.detach())
            res.loss_history.append(loss_value)
            if not math.isfinite(loss_value):
                raise TrainingDiverged(res.loss_history)
            torch.nn.utils.clip_grad_norm_(params, MAX_GRAD_NORM)
            opt.step()
            opt.zero_grad(set_to_none=True)
            step += 1
    if is_cuda:
        torch.cuda.synchronize()
        res.peak_alloc_gib = torch.cuda.max_memory_allocated() / 2**30
        res.peak_reserved_gib = torch.cuda.max_memory_reserved() / 2**30
    res.seconds = time.time() - t0
    return res
