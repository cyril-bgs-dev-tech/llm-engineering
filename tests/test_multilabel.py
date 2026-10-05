import numpy as np
import torch

from llmft.multilabel import f1_scores, predict_labels, train_multilabel


def test_weighted_f1_matches_the_hand_computation() -> None:
    y = np.array([[1, 0], [1, 0], [0, 1], [1, 1]])
    p = np.array([[1, 0], [0, 0], [0, 1], [1, 0]])
    s = f1_scores(y, p)
    # étiquette 0 : tp=2 fp=0 fn=1 -> F1 0,8 (support 3) ; étiquette 1 : tp=1 fp=0 fn=1 -> F1 2/3 (support 2)
    assert abs(s["weighted_f1"] - (0.8 * 3 + (2 / 3) * 2) / 5) < 1e-9
    assert abs(s["macro_f1"] - (0.8 + 2 / 3) / 2) < 1e-9


def test_predict_labels_always_returns_at_least_one_label() -> None:
    probs = np.array([[0.2, 0.3, 0.1], [0.9, 0.6, 0.1]])
    assert predict_labels(probs).tolist() == [[0, 1, 0], [1, 1, 0]]


class _Tiny(torch.nn.Module):
    def __init__(self) -> None:
        super().__init__()
        self.emb = torch.nn.Embedding(8, 4)
        self.head = torch.nn.Linear(4, 3)

    def forward(self, input_ids: torch.Tensor, attention_mask: torch.Tensor) -> object:
        h = (self.emb(input_ids) * attention_mask.unsqueeze(-1)).sum(1) / attention_mask.sum(1, keepdim=True)
        return type("Out", (), {"logits": self.head(h)})()


def test_multilabel_training_learns_a_separable_toy_problem() -> None:
    torch.manual_seed(0)
    ids = [[1, 2], [1, 3], [4, 5], [4, 6], [1, 4], [2, 5]] * 4
    targets = np.array([[1, 0, 0], [1, 0, 0], [0, 1, 0], [0, 1, 0], [1, 1, 0], [0, 0, 1]] * 4, dtype=np.float32)
    m = _Tiny()
    r = train_multilabel(m, ids, targets, 0, "cpu", 8, 4, 60, 0.05, 2, 0)
    assert r.loss_history[-1] < r.loss_history[0]
    probs = torch.sigmoid(m(torch.tensor(ids[:2]), torch.ones(2, 2, dtype=torch.long)).logits).detach().numpy()
    assert probs[:, 0].min() > 0.5 and probs[:, 2].max() < 0.5
