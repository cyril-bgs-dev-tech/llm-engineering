import numpy as np
import pytest
from sklearn.metrics import f1_score

from llmft import paired


def test_holm_caps_adjusted_values_at_one():
    assert paired.holm_adjust(np.array([0.5, 0.7, 0.9])).tolist() == [1.0, 1.0, 1.0]


def test_holm_with_ties_and_a_single_value():
    assert paired.holm_adjust(np.array([0.02, 0.02, 0.02])).tolist() == pytest.approx([0.06, 0.06, 0.06])
    assert paired.holm_adjust(np.array([0.3])).tolist() == [0.3]


def test_exact_permutation_refuses_more_than_twenty_patients():
    with pytest.raises(ValueError, match="20"):
        paired.paired_permutation_pvalue(np.ones(21), n_perm=None)


def test_monte_carlo_permutation_p_value_is_never_zero():
    p = paired.paired_permutation_pvalue(np.ones(30), n_perm=50, rng=np.random.default_rng(0))
    assert p >= 1 / 51


def test_exact_permutation_of_all_equal_gaps_is_two_over_two_to_the_n():
    assert paired.paired_permutation_pvalue(np.ones(5)) == pytest.approx(2 / 32)


def test_empty_input_is_refused_instead_of_returning_p_zero():
    with pytest.raises(ValueError):
        paired.paired_permutation_pvalue(np.array([]))


def test_verdict_is_non_resolved_when_the_upper_bound_equals_delta():
    assert paired.verdict(-4.0, 2.0, delta=2.0) == "non résolu"


def test_stratified_weights_really_resample_every_class():
    truth = np.array([0] * 40 + [1] * 30 + [2] * 20)
    w = paired.stratified_weights(truth, 2000, np.random.default_rng(1))
    for c in range(3):
        cols = w[:, truth == c]
        assert cols.var() > 0.8  # binomiale (m, 1/m) : variance ~ 1 - 1/m
        assert cols.mean() == pytest.approx(1.0)


@pytest.mark.parametrize("metric", ["macro_f1", "accuracy"])
def test_weighted_metric_equals_the_metric_on_the_expanded_sample(metric):
    rng = np.random.default_rng(3)
    truth = rng.integers(0, 4, 40)
    pred = np.where(rng.random(40) < 0.6, truth, rng.integers(0, 4, 40))
    w = rng.integers(0, 4, size=(6, 40))
    w[:, 0] += 1
    got = paired._metric_per_replicate(w, truth, pred, 4, [0, 1, 2], metric)
    for r in range(6):
        t, p = np.repeat(truth, w[r]), np.repeat(pred, w[r])
        exp = (t == p).mean() if metric == "accuracy" else f1_score(t, p, labels=[0, 1, 2], average="macro", zero_division=0)
        assert got[r] == pytest.approx(exp, abs=1e-12)


def test_percentile_interval_matches_the_normal_approximation_at_the_requested_level():
    rng = np.random.default_rng(0)
    n = 2000
    truth = np.zeros(n, dtype=int)
    a_ok, b_ok = rng.random(n) < 0.6, rng.random(n) < 0.5
    a, b = np.where(a_ok, 0, 1), np.where(b_ok, 0, 1)
    gaps = a_ok.astype(float) - b_ok.astype(float)
    se = gaps.std() / np.sqrt(n)
    res = paired.hierarchical_bootstrap(truth, a[None], b[None], 2, [0], metric="accuracy", stratify=False, resample_seeds=False, n_boot=20000, level=0.95, rng=np.random.default_rng(1))
    assert res.lo == pytest.approx(gaps.mean() - 1.96 * se, abs=0.07 * se)
    assert res.hi == pytest.approx(gaps.mean() + 1.96 * se, abs=0.07 * se)


def test_seed_resampling_is_applied_to_both_recipes_symmetrically():
    rng = np.random.default_rng(5)
    truth = rng.integers(0, 3, 150)
    base = np.where(rng.random(150) < 0.7, truth, rng.integers(0, 3, 150))
    varied = np.stack([np.where(rng.random(150) < 0.8, base, rng.integers(0, 3, 150)) for _ in range(6)])
    const = np.stack([base] * 6)
    kw = {"k_classes": 3, "scored": [0, 1, 2], "n_boot": 2000, "level": 0.95}
    only_patients = paired.hierarchical_bootstrap(truth, varied, const, resample_seeds=False, rng=np.random.default_rng(2), **kw).width
    a_var = paired.hierarchical_bootstrap(truth, varied, const, rng=np.random.default_rng(2), **kw).width
    b_var = paired.hierarchical_bootstrap(truth, const, varied, rng=np.random.default_rng(2), **kw).width
    assert a_var > only_patients * 1.02 and b_var > only_patients * 1.02


@pytest.mark.parametrize("side", ["a", "b"])
def test_interval_is_centred_on_the_seed_averaged_estimate_whichever_recipe_has_the_varying_seeds(side):
    rng = np.random.default_rng(6)
    truth = rng.integers(0, 3, 300)
    good = truth.copy()  # exactitude 1
    noisy = [np.where(rng.random(300) < 0.5, truth, rng.integers(0, 3, 300)) for _ in range(5)]
    varied = np.stack([good, *noisy])  # la graine 0 est bien meilleure que la moyenne
    const = np.stack([np.where(rng.random(300) < 0.6, truth, rng.integers(0, 3, 300))] * 6)
    a, b = (varied, const) if side == "a" else (const, varied)
    r = paired.hierarchical_bootstrap(truth, a, b, 3, [0, 1, 2], metric="accuracy", n_boot=4000, level=0.95, rng=np.random.default_rng(0))
    assert abs((r.lo + r.hi) / 2 - r.estimate) < 0.2 * r.width
