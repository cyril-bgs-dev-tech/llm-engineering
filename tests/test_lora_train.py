"""Briques d'entraînement du classifieur LoRA : calendrier, troncature tête et fin, lots avec accumulation, boucle (P1-13, RM-16)."""
import itertools
import math

import numpy as np
import pytest

from llmft import lora_train


def test_cosine_lr_echauffement_lineaire_puis_decroissance_vers_zero():
    lrs = [lora_train.cosine_lr(s, total_steps=100, base_lr=1e-4, warmup_steps=10) for s in range(100)]
    assert lrs[0] == pytest.approx(1e-5)  # (0 + 1) / 10 du taux de base
    assert lrs[9] == pytest.approx(1e-4)  # fin de l'échauffement
    assert all(a >= b - 1e-15 for a, b in itertools.pairwise(lrs[9:]))
    assert lrs[-1] < 1e-6 and lrs[-1] >= 0


def test_cosine_lr_echauffement_plus_long_que_l_entrainement_reste_borne():
    assert max(lora_train.cosine_lr(s, 5, 1e-4, 100) for s in range(5)) <= 1e-4


def test_truncate_head_tail_garde_tete_et_fin_avec_marqueur():
    ids = list(range(100))
    out = lora_train.truncate_head_tail(ids, max_len=10, marker=[-1])
    assert out == [0, 1, 2, 3, 4, -1, 95, 96, 97, 98, 99]
    assert lora_train.truncate_head_tail(list(range(10)), max_len=10, marker=[-1]) == list(range(10))  # rien à couper


def test_total_steps_arrondi_au_lot_effectif_par_epoque():
    assert lora_train.total_steps(n=100, effective_batch=32, epochs=2) == 8  # ceil(100/32) = 4 par époque


def test_lots_couvrent_chaque_exemple_une_fois_par_epoque_et_poids_somment_a_un():
    rng = np.random.default_rng(0)
    steps = lora_train.epoch_plan(n=10, effective_batch=4, micro_batch=2, rng=rng)
    flat = [i for step in steps for micro, _ in step for i in micro]
    assert sorted(flat) == list(range(10))
    assert [sum(len(m) for m, _ in step) for step in steps] == [4, 4, 2]
    for step in steps:
        assert all(len(m) <= 2 for m, _ in step)
        assert sum(w for _, w in step) == pytest.approx(1.0)


def test_meme_graine_meme_plan():
    a = lora_train.epoch_plan(10, 4, 2, np.random.default_rng(5))
    b = lora_train.epoch_plan(10, 4, 2, np.random.default_rng(5))
    assert [[m.tolist() for m, _ in s] for s in a] == [[m.tolist() for m, _ in s] for s in b]


def test_boucle_apprend_un_probleme_separable_et_consigne_une_perte_par_pas():
    import torch
    from transformers import LlamaConfig, LlamaForSequenceClassification

    torch.manual_seed(0)
    cfg = LlamaConfig(vocab_size=32, hidden_size=16, intermediate_size=32, num_hidden_layers=2, num_attention_heads=2, num_labels=2, pad_token_id=0)
    model = LlamaForSequenceClassification(cfg)
    ids = [[1, 2, 3, 4] if i % 2 == 0 else [5, 6, 7, 8] for i in range(16)]
    labels = [i % 2 for i in range(16)]
    res = lora_train.train(model, ids, labels, pad_id=0, device="cpu", effective_batch=8, micro_batch=4, epochs=6, base_lr=5e-3, warmup_steps=1, seed=0)
    assert len(res.loss_history) == lora_train.total_steps(16, 8, 6)
    assert all(math.isfinite(x) for x in res.loss_history)
    assert res.loss_history[-1] < res.loss_history[0]


def test_perte_non_finie_arrete_la_boucle_et_garde_l_historique():
    import torch
    from transformers import LlamaConfig, LlamaForSequenceClassification

    cfg = LlamaConfig(vocab_size=32, hidden_size=16, intermediate_size=32, num_hidden_layers=1, num_attention_heads=2, num_labels=2, pad_token_id=0)
    model = LlamaForSequenceClassification(cfg)
    with torch.no_grad():
        model.score.weight.fill_(float("nan"))
    with pytest.raises(lora_train.TrainingDiverged) as err:
        lora_train.train(model, [[1, 2, 3]] * 8, [0, 1] * 4, pad_id=0, device="cpu", effective_batch=4, micro_batch=4, epochs=2, base_lr=1e-3, warmup_steps=1, seed=0)
    assert len(err.value.loss_history) >= 1 and not math.isfinite(err.value.loss_history[-1])


def test_special_affixes_retrouve_prefixe_et_suffixe_d_un_tokenizer_quelconque():
    def encode_bert(text, add_special_tokens):  # [CLS]=101 texte [SEP]=102
        body = [ord(c) for c in text]
        return [101, *body, 102] if add_special_tokens else body

    def encode_qwen(text, add_special_tokens):  # aucun jeton spécial
        return [ord(c) for c in text]

    assert lora_train.special_affixes(encode_bert) == ([101], [102])
    assert lora_train.special_affixes(encode_qwen) == ([], [])


def test_arret_anticipe_si_la_duree_projetee_depasse_la_limite_apres_dix_pour_cent_des_pas():
    from transformers import LlamaConfig, LlamaForSequenceClassification

    cfg = LlamaConfig(vocab_size=32, hidden_size=16, intermediate_size=32, num_hidden_layers=1, num_attention_heads=2, num_labels=2, pad_token_id=0)
    model = LlamaForSequenceClassification(cfg)
    with pytest.raises(lora_train.TrainingAborted) as err:
        lora_train.train(model, [[1, 2, 3]] * 40, [0, 1] * 20, pad_id=0, device="cpu", effective_batch=4, micro_batch=4, epochs=2, base_lr=1e-3, warmup_steps=1, seed=0,
                         projected_limit_seconds=1e-9)
    assert err.value.projected_seconds > 1e-9
    assert 2 <= len(err.value.loss_history) < lora_train.total_steps(40, 4, 2)  # pas avant 10 % (2 pas sur 20), pas jusqu'au bout


def test_sans_limite_la_boucle_va_au_bout():
    from transformers import LlamaConfig, LlamaForSequenceClassification

    cfg = LlamaConfig(vocab_size=32, hidden_size=16, intermediate_size=32, num_hidden_layers=1, num_attention_heads=2, num_labels=2, pad_token_id=0)
    res = lora_train.train(LlamaForSequenceClassification(cfg), [[1, 2, 3]] * 8, [0, 1] * 4, pad_id=0, device="cpu", effective_batch=4, micro_batch=4, epochs=1, base_lr=1e-3, warmup_steps=1, seed=0)
    assert len(res.loss_history) == 2


def test_perte_ponderee_par_classe_reproduit_le_calcul_a_la_main_meme_en_micro_lot_de_un():
    import torch

    class Toy(torch.nn.Module):
        def __init__(self) -> None:
            super().__init__()
            self.w = torch.nn.Parameter(torch.zeros(1, 2))

        def forward(self, input_ids, attention_mask):
            del attention_mask
            return type("Out", (), {"logits": self.w.expand(input_ids.shape[0], 2)})()

    ids = [[1], [2], [3], [4]]
    labels = [0, 0, 0, 1]
    weights = torch.tensor([0.5, 2.0])
    res = lora_train.train(Toy(), ids, labels, pad_id=0, device="cpu", effective_batch=4, micro_batch=1, epochs=1, base_lr=0.0, warmup_steps=1, seed=0, class_weights=weights)
    expected = math.log(2) * (0.5 * 3 + 2.0 * 1) / 4  # logits nuls : entropie croisée ln 2 par exemple
    assert res.loss_history[0] == pytest.approx(expected)


def test_poids_en_inverse_racine_des_effectifs_ont_une_moyenne_de_un_sur_les_exemples():
    w = lora_train.inverse_sqrt_class_weights([0, 0, 0, 0, 1, 1, 2], 3)
    assert float(np.mean([float(w[c]) for c in [0, 0, 0, 0, 1, 1, 2]])) == pytest.approx(1.0)
    assert float(w[2]) > float(w[1]) > float(w[0])
