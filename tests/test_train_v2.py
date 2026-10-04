"""Boucle d'entraînement de l'encodeur v2 : poids du curriculum, EMA, équivalence avec la boucle gelée sans option (RM-41, RM-55)."""
import numpy as np
import torch

from llmft import lora_train
from llmft.train_v2 import curriculum_weights, ema_update, train_v2


class _Tiny(torch.nn.Module):
    def __init__(self) -> None:
        super().__init__()
        self.emb = torch.nn.Embedding(8, 4)
        self.head = torch.nn.Linear(4, 2)

    def forward(self, input_ids: torch.Tensor, attention_mask: torch.Tensor) -> object:
        h = (self.emb(input_ids) * attention_mask.unsqueeze(-1)).sum(1) / attention_mask.sum(1, keepdim=True)
        return type("Out", (), {"logits": self.head(h)})()


IDS = [[1, 2], [1, 3], [4, 5], [4, 6]] * 4
Y = [0, 0, 1, 1] * 4


def test_curriculum_weights_are_inverse_frequency_with_unit_mean() -> None:
    w = curriculum_weights([0, 0, 0, 1], 3)
    assert torch.isclose(w[1] / w[0], torch.tensor(3.0)) and abs(float((w[torch.tensor([0, 0, 0, 1])]).mean()) - 1.0) < 1e-6 and float(w[2]) > 0


def test_ema_update_matches_the_hand_computation() -> None:
    shadow = [torch.tensor([1.0, 1.0])]
    ema_update(shadow, [torch.tensor([3.0, 5.0])], 0.9)
    assert torch.allclose(shadow[0], torch.tensor([1.2, 1.4]))


def test_without_options_the_loop_reproduces_the_frozen_training_loop() -> None:
    torch.manual_seed(0)
    a, b = _Tiny(), _Tiny()
    b.load_state_dict(a.state_dict())
    ra = lora_train.train(a, IDS, Y, 0, "cpu", 4, 2, 5, 0.05, 2, 0)
    rb = train_v2(b, IDS, Y, 2, 0, "cpu", 4, 2, 5, 0.05, 2, 0)
    assert np.allclose(ra.loss_history, rb.loss_history, atol=1e-6)
    assert all(torch.allclose(p, q, atol=1e-6) for p, q in zip(a.parameters(), b.parameters(), strict=True))


def test_label_smoothing_ema_and_curriculum_run_and_change_the_result() -> None:
    torch.manual_seed(0)
    base, opt = _Tiny(), _Tiny()
    opt.load_state_dict(base.state_dict())
    train_v2(base, IDS, Y, 2, 0, "cpu", 4, 2, 5, 0.05, 2, 0)
    r = train_v2(opt, IDS, Y, 2, 0, "cpu", 4, 2, 5, 0.05, 2, 0, label_smoothing=0.1, ema_decay=0.9, curriculum_epochs=2)
    assert np.isfinite(r.loss_history).all()
    assert not all(torch.allclose(p, q, atol=1e-6) for p, q in zip(base.parameters(), opt.parameters(), strict=True))


def test_bf16_autocast_runs_on_cpu() -> None:
    torch.manual_seed(0)
    m = _Tiny()
    r = train_v2(m, IDS, Y, 2, 0, "cpu", 4, 2, 2, 0.05, 2, 0, autocast_bf16=True)
    assert np.isfinite(r.loss_history).all()
