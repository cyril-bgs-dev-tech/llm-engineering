"""Encodeur par fenêtres : un patient plus long que la fenêtre de l'encodeur est découpé en fenêtres de `window` tokens (chacune entourée des jetons spéciaux),
les logits des fenêtres sont moyennés. Entrée : séquences complètes avec jeton de début et de fin déjà posés, remplissage à droite (même interface que le modèle de base)."""
from __future__ import annotations

from types import SimpleNamespace
from typing import Any

import torch


class WindowedClassifier(torch.nn.Module):
    def __init__(self, base: Any, cls_id: int, sep_id: int, pad_id: int, window: int = 510, max_windows: int = 8) -> None:
        super().__init__()
        self.base = base
        self.cls_id, self.sep_id, self.pad_id, self.window, self.max_windows = cls_id, sep_id, pad_id, window, max_windows

    def _windows(self, ids: torch.Tensor, mask: torch.Tensor) -> tuple[torch.Tensor, torch.Tensor, list[int]]:
        rows: list[torch.Tensor] = []
        owners: list[int] = []
        for b in range(ids.size(0)):
            n = int(mask[b].sum())
            body = ids[b, 1 : n - 1]  # sans jeton de début ni de fin
            starts = list(range(0, max(len(body), 1), self.window))[: self.max_windows]
            for s in starts:
                chunk = body[s : s + self.window]
                rows.append(torch.cat([ids.new_tensor([self.cls_id]), chunk, ids.new_tensor([self.sep_id])]))
                owners.append(b)
        width = max(len(r) for r in rows)
        out = ids.new_full((len(rows), width), self.pad_id)
        attn = torch.zeros((len(rows), width), dtype=mask.dtype, device=ids.device)
        for i, r in enumerate(rows):
            out[i, : len(r)] = r
            attn[i, : len(r)] = 1
        return out, attn, owners

    def forward(self, input_ids: torch.Tensor, attention_mask: torch.Tensor) -> SimpleNamespace:
        w_ids, w_mask, owners = self._windows(input_ids, attention_mask)
        logits = self.base(input_ids=w_ids, attention_mask=w_mask).logits
        owner = torch.tensor(owners, device=logits.device)
        summed = torch.zeros((input_ids.size(0), logits.size(1)), dtype=logits.dtype, device=logits.device).index_add(0, owner, logits)
        counts = torch.zeros(input_ids.size(0), dtype=logits.dtype, device=logits.device).index_add(0, owner, torch.ones_like(owner, dtype=logits.dtype))
        return SimpleNamespace(logits=summed / counts.unsqueeze(1))
