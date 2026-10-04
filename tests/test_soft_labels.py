import numpy as np
import pytest

from llmft.soft_labels import replicate_soft


def test_alpha_one_gives_the_hard_labels_with_unit_weights() -> None:
    rows, classes, weights = replicate_soft([1, 0], np.array([[0.2, 0.8], [0.5, 0.5]]), alpha=1.0, threshold=0.05)
    assert rows == [0, 1] and classes == [1, 0] and weights == [1.0, 1.0]


def test_mixture_replicates_each_class_above_the_threshold_and_keeps_unit_total_weight() -> None:
    rows, classes, weights = replicate_soft([0], np.array([[0.1, 0.6, 0.3]]), alpha=0.5, threshold=0.05)
    assert rows == [0, 0, 0] and classes == [0, 1, 2]
    assert np.isclose(sum(weights), 1.0) and np.allclose(weights, [0.55, 0.30, 0.15])


def test_small_masses_are_dropped_and_the_rest_renormalised() -> None:
    _, classes, weights = replicate_soft([0], np.array([[0.9, 0.08, 0.02]]), alpha=0.0, threshold=0.05)
    assert classes == [0, 1] and np.isclose(sum(weights), 1.0) and np.isclose(weights[0], 0.9 / 0.98)


def test_invalid_arguments_are_refused() -> None:
    with pytest.raises(ValueError):
        replicate_soft([0], np.array([[1.0, 0.0]]), alpha=2.0, threshold=0.05)
    with pytest.raises(ValueError):
        replicate_soft([0, 1], np.array([[1.0, 0.0]]), alpha=0.5, threshold=0.05)
