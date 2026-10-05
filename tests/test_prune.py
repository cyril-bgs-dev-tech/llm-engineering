import pytest
import torch

from llmft.prune import layers_to_keep, prune_encoder


class _Enc(torch.nn.Module):
    def __init__(self, n: int) -> None:
        super().__init__()
        self.layer = torch.nn.ModuleList([torch.nn.Linear(2, 2) for _ in range(n)])


class _Base(torch.nn.Module):
    def __init__(self, n: int) -> None:
        super().__init__()
        self.encoder = _Enc(n)


class _Cfg:
    num_hidden_layers = 12


class _Model(torch.nn.Module):
    def __init__(self, n: int = 12) -> None:
        super().__init__()
        self.roberta = _Base(n)
        self.config = _Cfg()


def test_layers_to_keep_takes_every_nth_layer() -> None:
    assert layers_to_keep(12, 2) == [0, 2, 4, 6, 8, 10] and layers_to_keep(12, 1) == list(range(12)) and layers_to_keep(3, 5) == [0]
    with pytest.raises(ValueError):
        layers_to_keep(12, 0)


def test_prune_encoder_keeps_the_selected_layers_and_updates_the_config() -> None:
    m = _Model()
    originals = list(m.roberta.encoder.layer)
    keep = prune_encoder(m, 2)
    assert keep == [0, 2, 4, 6, 8, 10] and len(m.roberta.encoder.layer) == 6 and m.config.num_hidden_layers == 6
    assert all(m.roberta.encoder.layer[i] is originals[k] for i, k in enumerate(keep))


def test_prune_encoder_refuses_models_without_a_bert_like_encoder() -> None:
    with pytest.raises(ValueError):
        prune_encoder(torch.nn.Linear(1, 1), 2)
