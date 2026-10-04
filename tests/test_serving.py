import numpy as np
import pytest

from llmft import serving

LABELS = ["a", "b", "c"]
TEXTS = ["alpha tumeur biopsie", "alpha tumeur kyste", "beta fracture femur", "beta fracture tibia", "gamma asthme toux", "gamma asthme dyspnee"] * 8
Y = ["a", "a", "b", "b", "c", "c"] * 8


def _bundle():
    rng = np.random.default_rng(0)
    oof = rng.dirichlet(np.ones(3), size=len(Y))
    oof[np.arange(len(Y)), [LABELS.index(v) for v in Y]] += 1.0
    oof /= oof.sum(1, keepdims=True)
    return serving.train_bundle(TEXTS, Y, LABELS, c=10.0, ngram=(1, 1), oof_probs=oof, oof_y=np.array([LABELS.index(v) for v in Y]), alpha=0.1, coverage_target=0.7)


def test_predictions_contain_label_probability_set_and_abstention_flag() -> None:
    out = serving.predict(_bundle(), ["alpha tumeur kyste", "gamma asthme toux"])
    assert [o["label"] for o in out] == ["a", "c"]
    assert all(0.0 <= o["probability"] <= 1.0 and o["label"] in o["set"] and isinstance(o["abstain"], bool) for o in out)


def test_save_and_load_roundtrip_gives_identical_predictions(tmp_path) -> None:
    b = _bundle()
    serving.save_bundle(b, tmp_path)
    again = serving.load_bundle(tmp_path)
    q = ["beta fracture femur", "alpha asthme"]
    assert serving.predict(b, q) == serving.predict(again, q)


def test_load_refuses_a_modified_model_file(tmp_path) -> None:
    serving.save_bundle(_bundle(), tmp_path)
    with open(tmp_path / "model.joblib", "ab") as handle:
        handle.write(b"x")
    with pytest.raises(ValueError, match="empreinte"):
        serving.load_bundle(tmp_path)


def test_abstention_threshold_reaches_the_target_coverage_on_calibration_data() -> None:
    b = _bundle()
    probs = np.asarray(serving.predict_probs(b, TEXTS))
    kept = (probs.max(1) >= b.abstain_threshold).mean()
    assert kept >= 0.6


def test_family_mode_needs_group_quantiles_and_returns_sets_from_family_thresholds(tmp_path) -> None:
    rng = np.random.default_rng(0)
    oof = rng.dirichlet(np.ones(3), size=len(Y))
    oof[np.arange(len(Y)), [LABELS.index(v) for v in Y]] += 1.0
    oof /= oof.sum(1, keepdims=True)
    groups = {0: 0, 1: 1, 2: 1}
    b = serving.train_bundle(TEXTS, Y, LABELS, c=10.0, ngram=(1, 1), oof_probs=oof, oof_y=np.array([LABELS.index(v) for v in Y]), group_of_class=groups)
    out = serving.predict(b, ["alpha tumeur kyste"], mode="famille")
    assert out[0]["label"] in out[0]["set"]
    serving.save_bundle(b, tmp_path)
    again = serving.load_bundle(tmp_path)
    assert serving.predict(b, ["beta fracture femur"], mode="famille") == serving.predict(again, ["beta fracture femur"], mode="famille")
    with pytest.raises(ValueError, match="famille"):
        serving.predict(_bundle(), ["alpha"], mode="famille")
