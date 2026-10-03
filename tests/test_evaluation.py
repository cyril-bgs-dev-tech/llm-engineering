import numpy as np
import pytest

from llmft import evaluation, metrics

LABELS = ["a", "b", "c", "autre"]


def onehot(pred: list[int], k: int = 4) -> np.ndarray:
    out = np.full((len(pred), k), 0.01)
    out[np.arange(len(pred)), pred] = 0.97
    return out


def test_perfect_predictions_score_one_on_the_three_scored_classes_and_exclude_autre_from_the_mean():
    y = np.array([0, 1, 2, 3, 0, 1])
    r = evaluation.chapter_report(y, onehot(list(y)), LABELS)
    assert r["macro_f1"] == pytest.approx(1.0)
    assert r["scored_classes"] == ["a", "b", "c"]
    assert r["accuracy"] == pytest.approx(1.0)


def test_a_patient_of_a_scored_class_predicted_autre_is_a_false_negative_of_that_class():
    y = np.array([0, 0, 1, 2])
    pred = [3, 0, 1, 2]  # un patient de « a » prédit « autre »
    r = evaluation.chapter_report(y, onehot(pred), LABELS)
    # a : tp 1, fn 1, fp 0 -> f1 2/3 ; b et c parfaits ; moyenne sur 3 classes seulement
    assert r["macro_f1"] == pytest.approx((2 / 3 + 1 + 1) / 3)
    assert r["per_class"]["a"]["recall"] == pytest.approx(0.5)


def test_a_patient_of_autre_predicted_as_a_scored_class_is_a_false_positive_of_that_class():
    y = np.array([0, 1, 2, 3])
    pred = [0, 1, 2, 0]  # le patient « autre » est prédit « a »
    r = evaluation.chapter_report(y, onehot(pred), LABELS)
    # a : tp 1, fp 1, fn 0 -> f1 2/3
    assert r["per_class"]["a"]["precision"] == pytest.approx(0.5)
    assert r["macro_f1"] == pytest.approx((2 / 3 + 1 + 1) / 3)


def test_autre_is_reported_apart_with_its_own_precision_recall_and_support():
    y = np.array([0, 3, 3, 1])
    pred = [0, 3, 1, 1]  # un « autre » retrouvé, un « autre » perdu vers « b »
    r = evaluation.chapter_report(y, onehot(pred), LABELS)
    assert r["excluded"]["autre"] == {"precision": 1.0, "recall": pytest.approx(0.5), "support": 2}
    assert "autre" not in r["per_class"]


def test_accuracy_log_loss_and_ece_count_autre_as_an_ordinary_class():
    y = np.array([0, 3, 1, 3, 2])
    probs = onehot([0, 3, 1, 0, 2])
    r = evaluation.chapter_report(y, probs, LABELS)
    idx = y.astype(np.int64)
    assert r["accuracy"] == pytest.approx(metrics.accuracy([LABELS[i] for i in y], [LABELS[i] for i in probs.argmax(1)]))
    assert r["log_loss"] == pytest.approx(metrics.log_loss(probs, idx))
    assert r["ece"] == pytest.approx(metrics.ece(probs, idx))


def test_classes_with_fewer_than_ten_patients_are_flagged_very_low_support():
    y = np.array([0] * 12 + [1] * 3 + [2] * 10 + [3])
    r = evaluation.chapter_report(y, onehot(list(y)), LABELS)
    assert r["per_class"]["a"]["very_low_support"] is False
    assert r["per_class"]["b"]["very_low_support"] is True
    assert r["per_class"]["c"]["very_low_support"] is False  # 10 patients : seuil strict (moins de 10)


def test_an_excluded_label_missing_from_the_class_list_is_refused():
    with pytest.raises(ValueError, match="autre"):
        evaluation.chapter_report(np.array([0]), onehot([0], 3), ["a", "b", "c"])
