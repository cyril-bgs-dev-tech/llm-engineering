"""Perte de distillation sur cas analytiques, cible stricte hors pli, boucle sur un jouet (RM-32, P3-01)."""
import math

import numpy as np
import pytest
import torch

from llmft import distill


def _logits() -> torch.Tensor:
    return torch.tensor([[2.0, 0.5, -1.0], [0.0, 1.0, 0.0]])


def test_alpha_one_is_cross_entropy() -> None:
    target = torch.tensor([0, 1])
    teacher = torch.full((2, 3), 1 / 3)
    loss = distill.distillation_loss(_logits(), teacher, target, alpha=1.0, temperature=3.0)
    assert torch.isclose(loss, torch.nn.functional.cross_entropy(_logits(), target))


def test_alpha_zero_with_teacher_equal_to_student_is_zero() -> None:
    teacher = torch.softmax(_logits(), dim=-1)
    loss = distill.distillation_loss(_logits(), teacher, torch.tensor([0, 1]), alpha=0.0, temperature=1.0)
    assert abs(float(loss)) < 1e-6


def test_kl_matches_closed_form_and_scales_with_temperature_squared() -> None:
    teacher = torch.tensor([[0.7, 0.2, 0.1], [0.1, 0.8, 0.1]])
    t = 2.0
    pt = torch.softmax(torch.log(teacher) / t, dim=-1)
    ps = torch.softmax(_logits() / t, dim=-1)
    expected = float((pt * (pt.log() - ps.log())).sum(dim=-1).mean()) * t**2
    loss = distill.distillation_loss(_logits(), teacher, torch.tensor([0, 1]), alpha=0.0, temperature=t)
    assert math.isclose(float(loss), expected, rel_tol=1e-5)


def test_invalid_hyperparameters_are_refused() -> None:
    with pytest.raises(ValueError):
        distill.distillation_loss(_logits(), torch.full((2, 3), 1 / 3), torch.tensor([0, 1]), alpha=1.5, temperature=1.0)
    with pytest.raises(ValueError):
        distill.distillation_loss(_logits(), torch.full((2, 3), 1 / 3), torch.tensor([0, 1]), alpha=0.5, temperature=0.0)


def test_oof_map_refuses_a_patient_outside_its_fold_and_duplicates() -> None:
    fold_of = {"a": 0, "b": 0, "c": 1}
    ok = {0: (["a", "b"], np.array([[1.0, 0.0], [0.0, 1.0]])), 1: (["c"], np.array([[0.5, 0.5]]))}
    assert set(distill.oof_teacher_map(ok, fold_of)) == {"a", "b", "c"}
    with pytest.raises(ValueError, match="fuite"):
        distill.oof_teacher_map({0: (["a", "c"], np.zeros((2, 2)))}, fold_of)
    with pytest.raises(ValueError, match="doublon"):
        distill.oof_teacher_map({0: (["a", "a"], np.zeros((2, 2)))}, fold_of)


def test_require_teacher_refuses_missing_examples_and_aligns_rows() -> None:
    teacher = {"a": np.array([1.0, 0.0]), "b": np.array([0.0, 1.0])}
    assert np.allclose(distill.require_teacher(["b", "a"], teacher), [[0.0, 1.0], [1.0, 0.0]])
    with pytest.raises(ValueError, match="sans probabilité"):
        distill.require_teacher(["a", "z"], teacher)


class _Tiny(torch.nn.Module):
    def __init__(self) -> None:
        super().__init__()
        self.emb = torch.nn.Embedding(8, 4)
        self.head = torch.nn.Linear(4, 2)

    def forward(self, input_ids: torch.Tensor, attention_mask: torch.Tensor) -> object:
        h = (self.emb(input_ids) * attention_mask.unsqueeze(-1)).sum(1) / attention_mask.sum(1, keepdim=True)
        return type("Out", (), {"logits": self.head(h)})()


def test_distilled_student_moves_toward_the_teacher_on_a_toy_problem() -> None:
    torch.manual_seed(0)
    ids = [[1, 2], [1, 3], [4, 5], [4, 6]] * 4
    labels = [0, 0, 1, 1] * 4
    teacher = np.array([[0.9, 0.1], [0.9, 0.1], [0.1, 0.9], [0.1, 0.9]] * 4, dtype=np.float32)
    model = _Tiny()
    res = distill.train_distilled(model, ids, labels, teacher, 0, "cpu", 4, 2, 30, 0.05, 0, 0, alpha=0.3, temperature=2.0)
    assert res.loss_history[-1] < res.loss_history[0]
    probs = torch.softmax(model(torch.tensor(ids[:4]), torch.ones(4, 2)).logits, dim=-1).detach().numpy()
    assert probs[:2, 0].min() > 0.5 and probs[2:, 1].min() > 0.5
