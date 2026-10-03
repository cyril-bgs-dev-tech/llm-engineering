import pytest

from llmft.quant import load_kwargs


def test_no_quantization_adds_no_loading_arguments() -> None:
    assert load_kwargs("none") == {}


def test_nf4_requests_four_bit_loading_on_the_first_gpu() -> None:
    kw = load_kwargs("nf4")
    cfg = kw["quantization_config"]
    assert cfg.load_in_4bit is True and cfg.bnb_4bit_quant_type == "nf4" and cfg.bnb_4bit_use_double_quant is True
    assert kw["device_map"] == {"": 0}


def test_unknown_quantization_is_rejected() -> None:
    with pytest.raises(ValueError, match="int3"):
        load_kwargs("int3")
