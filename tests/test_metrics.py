"""Métriques de la chaîne : valeurs vérifiées à la main sur de petits cas."""
import numpy as np
import pytest

from llmft import metrics


def test_macro_f1_is_one_for_perfect_predictions_and_zero_for_total_miss():
    assert metrics.macro_f1(["a", "b", "a"], ["a", "b", "a"], ["a", "b"]) == pytest.approx(1.0)
    assert metrics.macro_f1(["a", "a"], ["b", "b"], ["a", "b"]) == pytest.approx(0.0)


def test_macro_f1_hand_computed_case():
    # a : TP=1 FP=0 FN=1 -> F1=2/3 ; b : TP=2 FP=1 FN=0 -> F1=0.8 ; moyenne = 0.7333...
    assert metrics.macro_f1(["a", "a", "b", "b"], ["a", "b", "b", "b"], ["a", "b"]) == pytest.approx((2 / 3 + 0.8) / 2)


def test_accuracy():
    assert metrics.accuracy(["a", "b", "b"], ["a", "b", "a"]) == pytest.approx(2 / 3)


def test_log_loss_matches_the_definition():
    p = np.array([[0.8, 0.2], [0.3, 0.7]])
    assert metrics.log_loss(p, np.array([0, 1])) == pytest.approx(-(np.log(0.8) + np.log(0.7)) / 2)


def test_log_loss_never_returns_infinity_on_zero_probability():
    assert np.isfinite(metrics.log_loss(np.array([[1.0, 0.0]]), np.array([1])))


def test_ece_is_zero_for_a_calibrated_perfect_model_and_large_for_an_overconfident_wrong_one():
    assert metrics.ece(np.array([[1.0, 0.0], [0.0, 1.0]]), np.array([0, 1])) == pytest.approx(0.0)
    assert metrics.ece(np.array([[0.99, 0.01]] * 4), np.array([1, 1, 1, 1])) == pytest.approx(0.99)


def test_compute_returns_the_metrics_a_contract_asks_for():
    p = np.array([[0.9, 0.1], [0.2, 0.8]])
    out = metrics.compute(["macro_f1", "accuracy", "log_loss", "ece"], p, np.array([0, 1]), ["a", "b"])
    assert set(out) == {"macro_f1", "accuracy", "log_loss", "ece"}
    with pytest.raises(KeyError):
        metrics.compute(["spearman"], p, np.array([0, 1]), ["a", "b"])
