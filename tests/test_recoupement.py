import numpy as np
import pytest

from llmft import recoupement


def test_identical_arrays_are_flagged_identical_with_same_digest():
    a = np.array([[0.2, 0.8], [0.6, 0.4]])
    out = recoupement.compare_probs(a, a.copy())
    assert out["verdict"] == "concorde"
    assert out["max_abs_diff"] == 0.0
    assert out["n_class_changes"] == 0
    assert out["digest_reference"] == out["digest_recomputed"]


def test_tiny_float_gap_without_class_change_is_concordant_up_to_floats():
    a = np.array([[0.2, 0.8], [0.6, 0.4]])
    out = recoupement.compare_probs(a, a + 1e-12)
    assert out["verdict"] == "concorde aux flottants près"
    assert out["n_class_changes"] == 0


def test_class_change_diverges_even_with_small_gap():
    a = np.array([[0.5000001, 0.4999999]])
    b = np.array([[0.4999999, 0.5000001]])
    out = recoupement.compare_probs(a, b)
    assert out["verdict"] == "diverge"
    assert out["n_class_changes"] == 1


def test_large_gap_diverges():
    a = np.array([[0.2, 0.8]])
    assert recoupement.compare_probs(a, np.array([[0.25, 0.75]]))["verdict"] == "diverge"


def test_gap_just_above_tolerance_diverges():
    a = np.array([[0.2, 0.8]])
    assert recoupement.compare_probs(a, a + 2e-9)["verdict"] == "diverge"


def test_shape_mismatch_is_refused():
    with pytest.raises(ValueError):
        recoupement.compare_probs(np.zeros((2, 3)), np.zeros((3, 3)))


def test_per_fold_gap_is_reported():
    a = np.array([[0.2, 0.8], [0.6, 0.4], [0.3, 0.7]])
    b = a.copy()
    b[2] += 0.01
    out = recoupement.compare_probs(a, b, folds=np.array([0, 1, 1]))
    assert out["max_abs_diff_by_fold"] == {"0": 0.0, "1": pytest.approx(0.01)}
