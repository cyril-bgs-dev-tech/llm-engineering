import numpy as np
import pytest

from llmft import baselines


def test_majority_baseline_hand_computed_case():
    r = baselines.fold_bounds(["a", "a", "b"], ["a", "b"], ["a", "b"], ["a", "b"], n_random=10, rng=np.random.default_rng(0))
    # prédit « a » partout : F1(a) = 2/(2+1) = 2/3, F1(b) = 0, exactitude 1/2
    assert r["majority"]["macro_f1"] == pytest.approx(1 / 3)
    assert r["majority"]["accuracy"] == pytest.approx(0.5)
    assert r["majority_class"] == "a"


def test_prior_log_loss_matches_the_definition_and_the_class_balanced_variant_weights_classes_equally():
    r = baselines.fold_bounds(["a", "a", "b"], ["a", "a", "a", "b"], ["a", "b"], ["a", "b"], n_random=5, rng=np.random.default_rng(0))
    p_a, p_b = 2 / 3, 1 / 3
    assert r["prior"]["log_loss"] == pytest.approx(-(3 * np.log(p_a) + np.log(p_b)) / 4)
    assert r["prior"]["class_balanced_log_loss"] == pytest.approx(-(np.log(p_a) + np.log(p_b)) / 2)


def test_a_class_scored_but_absent_from_the_test_counts_zero_in_the_macro_f1():
    r = baselines.fold_bounds(["a", "b", "c"], ["a", "a"], ["a", "b", "c"], ["a", "b", "c"], n_random=5, rng=np.random.default_rng(0))
    assert r["majority"]["macro_f1"] <= 1 / 3 + 1e-12


def test_excluded_class_is_not_averaged_but_still_predictable():
    r = baselines.fold_bounds(["a", "autre", "autre"], ["a", "b", "autre"], ["a", "b", "autre"], ["a", "b"], n_random=5, rng=np.random.default_rng(0))
    assert r["majority_class"] == "autre"
    assert r["majority"]["macro_f1"] == 0.0  # « autre » prédit partout : aucun patient noté retrouvé


def test_random_draws_are_reproducible_with_the_same_seed_and_uniform_beats_nothing_on_a_balanced_task():
    y = ["a"] * 50 + ["b"] * 50
    r1 = baselines.fold_bounds(y, y, ["a", "b"], ["a", "b"], n_random=300, rng=np.random.default_rng(3))
    r2 = baselines.fold_bounds(y, y, ["a", "b"], ["a", "b"], n_random=300, rng=np.random.default_rng(3))
    assert r1 == r2
    assert r1["random_uniform"]["accuracy"] == pytest.approx(0.5, abs=0.03)
    assert r1["random_prior"]["accuracy"] == pytest.approx(0.5, abs=0.03)
