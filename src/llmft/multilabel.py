"""Classification multi-étiquettes (RM-49, MorFITT) : métrique F1 pondérée du papier de référence, perte binaire croisée, boucle d'entraînement (même cosinus, même accumulation que `lora_train`)."""
import math
import time
from collections.abc import Sequence
from typing import Any

import numpy as np
import torch
from numpy.typing import NDArray
from sklearn.metrics import f1_score

from llmft import lora_train


def f1_scores(y_true: NDArray[np.int_], y_pred: NDArray[np.int_]) -> dict[str, float]:
    """F1 pondéré par le support de chaque étiquette (métrique du papier de référence), micro et macro, sur des matrices (n, k) de 0 et 1."""
    return {
        "weighted_f1": float(f1_score(y_true, y_pred, average="weighted", zero_division=0)),
        "micro_f1": float(f1_score(y_true, y_pred, average="micro", zero_division=0)),
        "macro_f1": float(f1_score(y_true, y_pred, average="macro", zero_division=0)),
    }


def predict_labels(probs: NDArray[np.floating], threshold: float = 0.5) -> NDArray[np.int_]:
    """Étiquettes prédites par seuil fixe ; au moins une étiquette par exemple (la plus probable) si aucune ne passe le seuil."""
    pred = (probs >= threshold).astype(int)
    empty = pred.sum(axis=1) == 0
    pred[empty, probs[empty].argmax(axis=1)] = 1
    return pred


def train_multilabel(
    model: Any, input_ids: Sequence[Sequence[int]], targets: NDArray[np.floating], pad_id: int, device: str | torch.device, effective_batch: int, micro_batch: int, epochs: int,
    base_lr: float, warmup_steps: int, seed: int, weight_decay: float = 0.0,
) -> lora_train.TrainResult:
    """AdamW, cosinus, accumulation, perte binaire croisée moyenne par exemple et par étiquette, arrêt sur perte non finie."""
    params = [p for p in model.parameters() if p.requires_grad]
    opt = torch.optim.AdamW(params, lr=base_lr, weight_decay=weight_decay)
    rng = np.random.default_rng(seed)
    y = torch.tensor(np.asarray(targets), dtype=torch.float32)
    n_total = lora_train.total_steps(len(input_ids), effective_batch, epochs)
    res = lora_train.TrainResult()
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
                loss = torch.nn.functional.binary_cross_entropy_with_logits(logits, y[idx].to(device)) * weight
                torch.autograd.backward(loss)
                loss_value += float(loss.detach())
            res.loss_history.append(loss_value)
            if not math.isfinite(loss_value):
                raise lora_train.TrainingDiverged(res.loss_history)
            torch.nn.utils.clip_grad_norm_(params, lora_train.MAX_GRAD_NORM)
            opt.step()
            opt.zero_grad(set_to_none=True)
            step += 1
    res.seconds = time.time() - t0
    return res
