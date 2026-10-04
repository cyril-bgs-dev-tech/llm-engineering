import pytest

torch = pytest.importorskip("torch")
from transformers import BertConfig, BertForSequenceClassification

from llmft.windowed import WindowedClassifier

CLS, SEP, PAD = 1, 2, 0


def _base() -> BertForSequenceClassification:
    torch.manual_seed(0)
    cfg = BertConfig(vocab_size=64, hidden_size=16, num_hidden_layers=1, num_attention_heads=2, intermediate_size=32, max_position_embeddings=64, num_labels=3, pad_token_id=PAD)
    return BertForSequenceClassification(cfg).eval()


def _batch(seqs: list[list[int]]) -> tuple[torch.Tensor, torch.Tensor]:
    n = max(len(s) for s in seqs)
    ids = torch.full((len(seqs), n), PAD)
    mask = torch.zeros((len(seqs), n), dtype=torch.long)
    for i, s in enumerate(seqs):
        ids[i, : len(s)] = torch.tensor(s)
        mask[i, : len(s)] = 1
    return ids, mask


def test_single_window_sequence_equals_the_base_model() -> None:
    base = _base()
    model = WindowedClassifier(base, CLS, SEP, PAD, window=8)
    seq = [CLS, 5, 6, 7, 8, SEP]
    ids, mask = _batch([seq])
    with torch.no_grad():
        assert torch.allclose(model(input_ids=ids, attention_mask=mask).logits, base(input_ids=ids, attention_mask=mask).logits, atol=1e-5)


def test_long_sequence_is_the_mean_of_the_logits_of_its_windows() -> None:
    base = _base()
    model = WindowedClassifier(base, CLS, SEP, PAD, window=4)
    body = list(range(10, 20))  # 10 tokens de texte : fenêtres de 4, 4, 2
    ids, mask = _batch([[CLS, *body, SEP]])
    parts = [body[0:4], body[4:8], body[8:10]]
    with torch.no_grad():
        expected = torch.stack([base(input_ids=_batch([[CLS, *p, SEP]])[0], attention_mask=_batch([[CLS, *p, SEP]])[1]).logits[0] for p in parts]).mean(0)
        got = model(input_ids=ids, attention_mask=mask).logits[0]
    assert torch.allclose(got, expected, atol=1e-5)


def test_padding_of_a_short_sequence_in_a_batch_does_not_change_its_logits() -> None:
    base = _base()
    model = WindowedClassifier(base, CLS, SEP, PAD, window=4)
    short = [CLS, 5, 6, SEP]
    long_ = [CLS, *range(10, 22), SEP]
    with torch.no_grad():
        alone = model(input_ids=_batch([short])[0], attention_mask=_batch([short])[1]).logits[0]
        ids, mask = _batch([short, long_])
        together = model(input_ids=ids, attention_mask=mask).logits[0]
    assert torch.allclose(alone, together, atol=1e-5)


def test_gradients_reach_the_base_parameters() -> None:
    base = _base().train()
    model = WindowedClassifier(base, CLS, SEP, PAD, window=4)
    ids, mask = _batch([[CLS, *range(10, 20), SEP]])
    model(input_ids=ids, attention_mask=mask).logits.sum().backward()
    assert any(p.grad is not None and float(p.grad.abs().sum()) > 0 for p in base.parameters())
