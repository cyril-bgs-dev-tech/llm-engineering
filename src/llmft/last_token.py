"""Voie B (modèles sans classe de classification, ex. Gemma 4) : tête linéaire sur l'état caché du dernier token réel d'un modèle causal.

Le remplissage est à droite ; `logits_to_keep=1` évite de calculer les logits sur tout le vocabulaire à chaque position (saturation de VRAM constatée
le 02/10/2026 sur Gemma-4-E4B, voir `compatibilite-modeles-p0-06`)."""
from __future__ import annotations

from types import SimpleNamespace
from typing import Any

import torch


class LastTokenClassifier(torch.nn.Module):
    def __init__(self, base: Any, hidden: int, n_labels: int) -> None:
        super().__init__()
        self.base = base
        self.head = torch.nn.Linear(hidden, n_labels)

    def forward(self, input_ids: torch.Tensor, attention_mask: torch.Tensor) -> SimpleNamespace:
        h = self.base(input_ids=input_ids, attention_mask=attention_mask, output_hidden_states=True, logits_to_keep=1).hidden_states[-1]
        last = attention_mask.sum(dim=1) - 1
        return SimpleNamespace(logits=self.head(h[torch.arange(h.size(0)), last].float()))
