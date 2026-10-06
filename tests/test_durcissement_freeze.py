import json
from pathlib import Path

import pytest

from llmft import freeze


def _write(runs: Path, stamp, slug, sha="s", status="ok"):
    (runs / f"{stamp}-{slug}.json").write_text(json.dumps({"run_id": f"{stamp}-{slug}", "status": status, "metrics": {"sha256": sha}}), encoding="utf-8")


def _runs(tmp_path, status="ok"):
    for name in ("tfidf", "encoder-s1", "lora-s1"):
        _write(tmp_path, "20261005-100000", f"final-{name}", status=status if name == "lora-s1" else "ok")
        _write(tmp_path, "20261005-110000", f"temps-a-{name}")
    return tmp_path


def test_a_run_that_did_not_finish_refuses_the_freeze(tmp_path):
    with pytest.raises(ValueError, match="non abouti"):
        freeze.build_frozen(_runs(tmp_path, status="failed"), enc_seeds=(1,), lora_seeds=(1,))


def test_frozen_uncertainty_parameters_and_secondaries_are_pinned(tmp_path):
    f = freeze.build_frozen(_runs(tmp_path), enc_seeds=(1,), lora_seeds=(1,))
    assert f["incertitude"]["niveau_conforme"] == 0.90
    assert f["incertitude"]["abstention_couvertures"] == [1.0, 0.9, 0.8, 0.7, 0.5]
    assert f["secondaires"] == ["E ensemble", "F LoRA"]
    assert f["modeles"]["tfidf"]["sha256_modele"] == "s"


def test_a_freeze_without_encoder_or_lora_seeds_is_refused(tmp_path):
    with pytest.raises(ValueError):
        freeze.build_frozen(_runs(tmp_path), enc_seeds=(), lora_seeds=())
