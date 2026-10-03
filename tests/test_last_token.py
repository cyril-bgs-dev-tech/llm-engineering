"""Voie B : tête linéaire sur l'état caché du dernier token réel (remplissage à droite)."""
import torch
from transformers import LlamaConfig, LlamaForCausalLM

from llmft import last_token


def _model():
    torch.manual_seed(0)
    cfg = LlamaConfig(vocab_size=32, hidden_size=16, intermediate_size=32, num_hidden_layers=2, num_attention_heads=2, pad_token_id=0)
    return last_token.LastTokenClassifier(LlamaForCausalLM(cfg), hidden=16, n_labels=3)


def test_sortie_logits_une_ligne_par_exemple():
    m = _model().eval()
    ids = torch.tensor([[1, 2, 3, 0], [4, 5, 6, 7]])
    out = m(input_ids=ids, attention_mask=(ids != 0).long())
    assert out.logits.shape == (2, 3)


def test_le_remplissage_a_droite_ne_change_pas_la_prediction():
    m = _model().eval()
    short = torch.tensor([[1, 2, 3]])
    padded = torch.tensor([[1, 2, 3, 0, 0]])
    a = m(input_ids=short, attention_mask=torch.ones_like(short)).logits
    b = m(input_ids=padded, attention_mask=(padded != 0).long()).logits
    assert torch.allclose(a, b, atol=1e-5)


def test_le_dernier_token_reel_change_la_prediction():
    m = _model().eval()
    x = torch.tensor([[1, 2, 3, 0]])
    y = torch.tensor([[1, 2, 5, 0]])
    la = m(input_ids=x, attention_mask=(x != 0).long()).logits
    lb = m(input_ids=y, attention_mask=(y != 0).long()).logits
    assert not torch.allclose(la, lb, atol=1e-5)


def test_la_tete_est_entrainable_et_en_float32():
    m = _model()
    assert all(p.requires_grad for p in m.head.parameters())
    assert m.head.weight.dtype == torch.float32
