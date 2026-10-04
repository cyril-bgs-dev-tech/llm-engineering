import numpy as np
import pytest

from llmft.ensemble import average_probs


def test_average_aligns_on_ids_not_on_row_order() -> None:
    a = (["x", "y"], np.array([[1.0, 0.0], [0.0, 1.0]]))
    b = (["y", "x"], np.array([[1.0, 0.0], [1.0, 0.0]]))
    ids, p = average_probs([a, b])
    assert ids == ["x", "y"]
    assert np.allclose(p, [[1.0, 0.0], [0.5, 0.5]])


def test_weights_are_normalised() -> None:
    a = (["x"], np.array([[1.0, 0.0]]))
    b = (["x"], np.array([[0.0, 1.0]]))
    _, p = average_probs([a, b], weights=[3, 1])
    assert np.allclose(p, [[0.75, 0.25]])


def test_rejects_different_patients_and_bad_weights() -> None:
    a = (["x"], np.array([[1.0, 0.0]]))
    with pytest.raises(ValueError):
        average_probs([a, (["z"], np.array([[1.0, 0.0]]))])
    with pytest.raises(ValueError):
        average_probs([a], weights=[0])
