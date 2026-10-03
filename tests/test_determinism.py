import pytest

from llmft.determinism import compare


def test_identical_runs_are_bit_identical() -> None:
    r = compare([1.0, 0.5, 0.25], [1.0, 0.5, 0.25], ["a", "b"], ["a", "b"])
    assert r["loss_identique"] and r["predictions_identiques"] and r["ecart_perte_max"] == 0.0


def test_small_loss_drift_is_bounded_and_reported() -> None:
    r = compare([1.0, 0.5], [1.0, 0.5004], ["a", "b"], ["a", "b"])
    assert not r["loss_identique"]
    assert r["ecart_perte_max"] == pytest.approx(0.0004)
    assert r["predictions_identiques"]


def test_prediction_disagreements_are_counted() -> None:
    r = compare([1.0], [1.0], ["a", "b", "c"], ["a", "x", "c"])
    assert r["predictions_differentes"] == 1 and not r["predictions_identiques"]


def test_different_number_of_steps_is_an_error() -> None:
    with pytest.raises(ValueError, match="pas"):
        compare([1.0, 2.0], [1.0], ["a"], ["a"])
