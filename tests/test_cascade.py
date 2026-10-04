import numpy as np

from llmft.cascade import cascade_probs, choose_threshold


def test_cascade_keeps_confident_first_answers_and_escalates_the_rest() -> None:
    first = np.array([[0.9, 0.1], [0.55, 0.45]])
    second = np.array([[0.2, 0.8], [0.1, 0.9]])
    probs, keep = cascade_probs(first, second, 0.8)
    assert keep.tolist() == [True, False] and np.allclose(probs, [[0.9, 0.1], [0.1, 0.9]])


def test_threshold_is_the_smallest_one_within_tolerance_of_the_second_model() -> None:
    truth = np.array([0, 0, 1, 1])
    first = np.array([[0.95, 0.05], [0.6, 0.4], [0.9, 0.1], [0.3, 0.7]])  # faux sur le 3e cas, confiant
    second = np.array([[0.9, 0.1], [0.8, 0.2], [0.1, 0.9], [0.2, 0.8]])  # parfait

    def accuracy(p: np.ndarray) -> float:
        return float((p.argmax(1) == truth).mean())

    assert choose_threshold(first, second, accuracy, [0.5, 0.7, 0.99], tolerance=0.0) == 0.99
    assert choose_threshold(first, second, accuracy, [0.5, 0.7], tolerance=0.0) is None
    assert choose_threshold(first, second, accuracy, [0.5, 0.7], tolerance=0.3) == 0.5
