"""Distillation d'un professeur vers un élève (RM-32, P3-01) : perte, cible stricte hors pli, boucle d'entraînement.

Perte : `alpha * CE(élève, étiquette) + (1 - alpha) * T^2 * KL(professeur_T || élève_T)` (Hinton et al.), les logits du professeur étant reconstruits depuis ses probabilités
hors pli (`log p / T` renormalisé), donc sans accès au modèle professeur.

Cible stricte hors pli : la probabilité du professeur utilisée pour l'exemple `i` doit venir d'un professeur qui n'a pas vu `i` (leakage-guard, contrôle 3) ; `oof_teacher_map` lève
une erreur si un patient apparaît deux fois, hors de son pli, ou manque. Réserve connue (deuxième ordre) : le professeur du pli `j` a vu le pli `k` de validation de l'élève ; l'évaluation
de l'élève sur le pli `k` reste donc légèrement optimiste ; le test scellé, jamais vu par aucun professeur, est la seule mesure exempte de cet effet.
"""
import math
import time
from collections.abc import Mapping, Sequence
from typing import Any

import numpy as np
import torch
from numpy.typing import NDArray

from llmft import lora_train


def distillation_loss(student_logits: torch.Tensor, teacher_probs: torch.Tensor, target: torch.Tensor, alpha: float, temperature: float) -> torch.Tensor:
    """Perte moyenne sur le lot ; alpha = 1 : entropie croisée seule ; alpha = 0 : divergence de KL seule (échelle T^2)."""
    if not 0.0 <= alpha <= 1.0 or temperature <= 0.0:
        raise ValueError("alpha dans [0, 1] et température > 0")
    ce = torch.nn.functional.cross_entropy(student_logits, target)
    if alpha == 1.0:
        return ce
    log_t = torch.log(teacher_probs.clamp_min(1e-12)) / temperature
    teacher_t = torch.softmax(log_t, dim=-1)
    log_s = torch.log_softmax(student_logits / temperature, dim=-1)
    kl = torch.nn.functional.kl_div(log_s, teacher_t, reduction="batchmean")
    return alpha * ce + (1.0 - alpha) * temperature**2 * kl


def oof_teacher_map(files: Mapping[int, tuple[Sequence[str], NDArray[np.floating[Any]]]], fold_of: Mapping[str, int]) -> dict[str, NDArray[np.floating[Any]]]:
    """Carte patient vers probabilités du professeur, avec contrôle strict : le fichier du pli `k` ne contient que des patients du pli `k` (hors pli pour ce professeur), chacun une fois."""
    out: dict[str, NDArray[np.floating[Any]]] = {}
    for fold, (ids, probs) in files.items():
        if len(ids) != len(probs):
            raise ValueError(f"pli {fold} : identifiants et probabilités de tailles différentes")
        for pid, p in zip(ids, probs, strict=True):
            if fold_of.get(pid) != fold:
                raise ValueError(f"fuite : {pid} est dans le fichier du pli {fold} mais appartient au pli {fold_of.get(pid)}")
            if pid in out:
                raise ValueError(f"doublon : {pid}")
            out[pid] = np.asarray(p, dtype=np.float64)
    return out


def require_teacher(train_ids: Sequence[str], teacher: Mapping[str, NDArray[np.floating[Any]]]) -> NDArray[np.float32]:
    """Matrice des probabilités du professeur alignée sur les exemples d'entraînement ; refuse tout exemple sans cible hors pli."""
    missing = [i for i in train_ids if i not in teacher]
    if missing:
        raise ValueError(f"{len(missing)} exemples sans probabilité de professeur hors pli (premier : {missing[0]})")
    return np.stack([teacher[i] for i in train_ids]).astype(np.float32)


def train_distilled(
    model: Any, input_ids: Sequence[Sequence[int]], labels: Sequence[int], teacher_probs: NDArray[np.float32], pad_id: int, device: str | torch.device, effective_batch: int,
    micro_batch: int, epochs: int, base_lr: float, warmup_steps: int, seed: int, alpha: float, temperature: float, weight_decay: float = 0.0,
    projected_limit_seconds: float | None = None,
) -> lora_train.TrainResult:
    """Même boucle que `lora_train.train` (cosinus, accumulation, arrêt sur perte non finie), avec la perte de distillation."""
    params = [p for p in model.parameters() if p.requires_grad]
    opt = torch.optim.AdamW(params, lr=base_lr, weight_decay=weight_decay)
    rng = np.random.default_rng(seed)
    y = torch.tensor(list(labels), dtype=torch.long)
    tp = torch.from_numpy(teacher_probs)
    n_total = lora_train.total_steps(len(input_ids), effective_batch, epochs)
    res = lora_train.TrainResult()
    is_cuda = str(device).startswith("cuda")
    if is_cuda:
        torch.cuda.reset_peak_memory_stats()
    t0 = time.time()
    model.train()
    step = 0
    for _ in range(epochs):
        for micro_batches in lora_train.epoch_plan(len(input_ids), effective_batch, micro_batch, rng):
            for g in opt.param_groups:
                g["lr"] = lora_train.cosine_lr(step, n_total, base_lr, warmup_steps)
            loss_value = 0.0
            for idx, weight in micro_batches:
                ids, mask = lora_train._pad([input_ids[i] for i in idx], pad_id, device)
                logits = model(input_ids=ids, attention_mask=mask).logits.float()
                loss = distillation_loss(logits, tp[idx].to(device), y[idx].to(device), alpha, temperature) * weight
                torch.autograd.backward(loss)
                loss_value += float(loss.detach())
            res.loss_history.append(loss_value)
            if not math.isfinite(loss_value):
                raise lora_train.TrainingDiverged(res.loss_history)
            torch.nn.utils.clip_grad_norm_(params, lora_train.MAX_GRAD_NORM)
            opt.step()
            opt.zero_grad(set_to_none=True)
            step += 1
            if projected_limit_seconds is not None and step >= max(2, math.ceil(0.1 * n_total)):
                projected = (time.time() - t0) / step * n_total
                if projected > projected_limit_seconds:
                    raise lora_train.TrainingAborted(res.loss_history, projected)
    if is_cuda:
        torch.cuda.synchronize()
        res.peak_alloc_gib = torch.cuda.max_memory_allocated() / 2**30
        res.peak_reserved_gib = torch.cuda.max_memory_reserved() / 2**30
    res.seconds = time.time() - t0
    return res
