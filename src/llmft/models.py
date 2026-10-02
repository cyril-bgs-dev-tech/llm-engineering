"""Classifieurs de texte interchangeables derrière une même interface : `fit(texts, label_idx, steps)` et `predict_proba(texts)`.

`cpu` : sac de mots hachés, pour la CI sans GPU. `gpu` : petit modèle de langage avec tête de classification et LoRA.
Aucune des deux ne connaît les tâches : le nombre de classes vient du contrat.
"""
from __future__ import annotations

import re
import zlib
from collections.abc import Sequence
from typing import Protocol

import numpy as np
import torch
from numpy.typing import NDArray

HF_MODEL = "Qwen/Qwen3-0.6B"
_WORD = re.compile(r"\w+")


class Classifier(Protocol):
    def fit(self, texts: Sequence[str], label_idx: Sequence[int], steps: int) -> None: ...
    def predict_proba(self, texts: Sequence[str]) -> NDArray[np.float64]: ...


class HashedBowClassifier:
    """Sac de mots hachés (EmbeddingBag) et couche linéaire ; déterministe pour une graine donnée."""

    def __init__(self, num_labels: int, buckets: int = 1 << 14, dim: int = 32, seed: int = 0, lr: float = 0.05) -> None:
        torch.manual_seed(seed)
        self.buckets = buckets
        self.embed = torch.nn.EmbeddingBag(buckets, dim, mode="mean")
        self.head = torch.nn.Linear(dim, num_labels)
        self.lr = lr

    def _ids(self, texts: Sequence[str]) -> tuple[torch.Tensor, torch.Tensor]:
        flat: list[int] = []
        offsets = [0]
        for t in texts:
            ids = [zlib.crc32(w.encode()) % self.buckets for w in _WORD.findall(t.lower())] or [0]
            flat.extend(ids)
            offsets.append(offsets[-1] + len(ids))
        return torch.tensor(flat), torch.tensor(offsets[:-1])

    def _logits(self, texts: Sequence[str]) -> torch.Tensor:
        flat, offsets = self._ids(texts)
        return self.head(self.embed(flat, offsets))

    def fit(self, texts: Sequence[str], label_idx: Sequence[int], steps: int) -> None:
        opt = torch.optim.Adam([*self.embed.parameters(), *self.head.parameters()], lr=self.lr)
        y = torch.tensor(list(label_idx))
        for _ in range(steps):
            opt.zero_grad()
            torch.nn.functional.cross_entropy(self._logits(texts), y).backward()
            opt.step()

    def predict_proba(self, texts: Sequence[str]) -> NDArray[np.float64]:
        with torch.no_grad():
            return torch.softmax(self._logits(texts), dim=-1).numpy().astype(np.float64)


class HFLoraClassifier:
    """Modèle de langage avec tête de classification (`AutoModelForSequenceClassification`) entraîné par LoRA."""

    def __init__(self, num_labels: int, max_tokens: int, seed: int = 0, lr: float = 5e-4, batch_size: int = 8, model_name: str = HF_MODEL) -> None:
        from peft import LoraConfig, get_peft_model
        from transformers import AutoModelForSequenceClassification, AutoTokenizer

        torch.manual_seed(seed)
        self.device = torch.device("cuda")
        self.tok = AutoTokenizer.from_pretrained(model_name)
        base = AutoModelForSequenceClassification.from_pretrained(model_name, num_labels=num_labels, torch_dtype=torch.bfloat16)
        base.config.pad_token_id = self.tok.pad_token_id
        if hasattr(base.config, "text_config"):  # modèles multimodaux (Qwen3.5, Gemma 4) : la tête lit la configuration du texte
            base.config.text_config.pad_token_id = self.tok.pad_token_id
        self.model = get_peft_model(base, LoraConfig(task_type="SEQ_CLS", r=8, lora_alpha=16, lora_dropout=0.0, target_modules="all-linear")).to(self.device)
        self.max_tokens, self.lr, self.batch_size = max_tokens, lr, batch_size

    def _batch(self, texts: Sequence[str]) -> dict[str, torch.Tensor]:
        enc = self.tok(list(texts), return_tensors="pt", padding=True, truncation=True, max_length=self.max_tokens)
        return {k: v.to(self.device) for k, v in enc.items()}

    def fit(self, texts: Sequence[str], label_idx: Sequence[int], steps: int) -> None:
        opt = torch.optim.AdamW([p for p in self.model.parameters() if p.requires_grad], lr=self.lr)
        y_all = torch.tensor(list(label_idx))
        rng = np.random.default_rng(0)
        self.model.train()
        for _ in range(steps):
            pick = rng.choice(len(texts), size=min(self.batch_size, len(texts)), replace=False)
            logits = self.model(**self._batch([texts[i] for i in pick])).logits.float()
            loss = torch.nn.functional.cross_entropy(logits, y_all[pick].to(self.device))
            loss.backward()
            opt.step()
            opt.zero_grad(set_to_none=True)

    def predict_proba(self, texts: Sequence[str]) -> NDArray[np.float64]:
        self.model.eval()
        out = []
        with torch.no_grad():
            for i in range(0, len(texts), 16):
                logits = self.model(**self._batch(texts[i : i + 16])).logits.float()
                out.append(torch.softmax(logits, dim=-1).cpu().numpy())
        return np.concatenate(out).astype(np.float64)


def build_classifier(backend: str, num_labels: int, max_tokens: int, seed: int = 0) -> Classifier:
    if backend == "cpu":
        return HashedBowClassifier(num_labels, seed=seed)
    if backend == "gpu":
        return HFLoraClassifier(num_labels, max_tokens=max_tokens, seed=seed)
    raise ValueError(f"backend inconnu : {backend!r} (cpu ou gpu)")
