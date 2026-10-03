import numpy as np
import pytest
from scipy import stats
from statsmodels.stats.contingency_tables import mcnemar as sm_mcnemar
from statsmodels.stats.multitest import multipletests

from llmft import paired


def test_mcnemar_exact_matches_statsmodels_and_scipy_on_several_tables():
    for b, c in [(0, 0), (3, 3), (10, 2), (1, 9), (25, 40), (7, 0)]:
        a_ok = np.array([True] * b + [False] * c + [True] * 5)
        b_ok = np.array([False] * b + [True] * c + [True] * 5)
        res = paired.mcnemar_exact(a_ok, b_ok)
        assert (res.only_a, res.only_b) == (b, c)
        if b + c:
            table = [[5, b], [c, 0]]
            assert res.p_value == pytest.approx(sm_mcnemar(table, exact=True).pvalue, abs=1e-12)
            assert res.p_value == pytest.approx(stats.binomtest(min(b, c), b + c, 0.5).pvalue, abs=1e-12)
        else:
            assert res.p_value == 1.0


def test_holm_adjusted_p_values_match_statsmodels():
    p = np.array([0.01, 0.04, 0.03, 0.2, 0.0005])
    ours = paired.holm_adjust(p)
    ref = multipletests(p, method="holm")[1]
    assert ours == pytest.approx(ref, abs=1e-12)


def test_holm_never_exceeds_one_and_keeps_the_input_order():
    adj = paired.holm_adjust(np.array([0.5, 0.9, 0.001]))
    assert adj.max() <= 1.0 and adj[2] == pytest.approx(0.003)


def test_exact_paired_permutation_matches_scipy_permutation_test():
    d = np.array([0.5, -0.2, 0.9, 0.4, 1.1, -0.1, 0.3, 0.8, 0.6, 0.25, -0.35, 0.7])
    ours = paired.paired_permutation_pvalue(d, n_perm=None)
    ref = stats.permutation_test((d,), lambda x: x.mean(), permutation_type="samples", n_resamples=np.inf, alternative="two-sided")
    assert ours == pytest.approx(ref.pvalue, abs=1e-12)


def test_monte_carlo_permutation_is_close_to_the_exact_value():
    d = np.array([0.5, -0.2, 0.9, 0.4, 1.1, -0.1, 0.3, 0.8, 0.6, 0.25, -0.35, 0.7])
    exact = paired.paired_permutation_pvalue(d, n_perm=None)
    approx = paired.paired_permutation_pvalue(d, n_perm=20000, rng=np.random.default_rng(1))
    assert approx == pytest.approx(exact, abs=0.01)


def test_unstratified_bootstrap_on_accuracy_matches_the_scipy_percentile_interval():
    rng = np.random.default_rng(7)
    truth = rng.integers(0, 3, size=300)
    a = np.where(rng.random(300) < 0.70, truth, (truth + 1) % 3)
    b = np.where(rng.random(300) < 0.62, truth, (truth + 1) % 3)
    ours = paired.hierarchical_bootstrap(truth, a[None, :], b[None, :], 3, scored=[0, 1, 2], metric="accuracy", stratify=False, n_boot=10000, level=0.95, rng=np.random.default_rng(2))
    ref = stats.bootstrap(((a == truth).astype(float), (b == truth).astype(float)), lambda x, y: x.mean() - y.mean(), paired=True, vectorized=False, n_resamples=10000, confidence_level=0.95, method="percentile", random_state=3)
    assert ours.estimate == pytest.approx((a == truth).mean() - (b == truth).mean())
    assert ours.lo == pytest.approx(ref.confidence_interval.low, abs=0.012)
    assert ours.hi == pytest.approx(ref.confidence_interval.high, abs=0.012)


def test_macro_f1_point_estimate_equals_the_direct_computation_and_excludes_the_unscored_class():
    from llmft import metrics

    truth = np.array([0, 0, 1, 1, 2, 2, 3, 3])
    a = np.array([0, 0, 1, 3, 2, 2, 3, 0])
    b = np.array([0, 1, 1, 1, 2, 3, 3, 3])
    res = paired.hierarchical_bootstrap(truth, a[None, :], b[None, :], 4, scored=[0, 1, 2], metric="macro_f1", n_boot=200, level=0.95, rng=np.random.default_rng(0))
    labs = ["a", "b", "c", "d"]
    direct = metrics.macro_f1([labs[i] for i in truth], [labs[i] for i in a], labs[:3]) - metrics.macro_f1([labs[i] for i in truth], [labs[i] for i in b], labs[:3])
    assert res.estimate == pytest.approx(direct)


def test_identical_recipes_give_a_zero_width_interval_because_the_patient_draw_is_shared():
    rng = np.random.default_rng(5)
    truth = rng.integers(0, 4, size=120)
    pred = np.where(rng.random(120) < 0.6, truth, rng.integers(0, 4, size=120))
    seeds = np.stack([pred, pred, pred])
    res = paired.hierarchical_bootstrap(truth, seeds, seeds.copy(), 4, scored=[0, 1, 2, 3], n_boot=300, level=0.95, rng=np.random.default_rng(1))
    assert res.estimate == 0.0 and res.width == pytest.approx(0.0)


def test_stratified_bootstrap_keeps_every_class_present_in_every_replicate():
    truth = np.array([0] * 30 + [1] * 5 + [2] * 3)
    weights = paired.stratified_weights(truth, n_boot=400, rng=np.random.default_rng(0))
    assert weights.shape == (400, 38)
    for c in range(3):
        assert (weights[:, truth == c].sum(axis=1) == (truth == c).sum()).all()


def test_the_hierarchical_interval_is_wider_than_the_patient_only_interval_when_seeds_differ():
    rng = np.random.default_rng(11)
    truth = rng.integers(0, 4, size=200)
    base = np.where(rng.random(200) < 0.65, truth, rng.integers(0, 4, size=200))
    seeds_a = np.stack([np.where(rng.random(200) < 0.9, base, rng.integers(0, 4, size=200)) for _ in range(5)])
    seeds_b = np.stack([np.where(rng.random(200) < 0.9, base, rng.integers(0, 4, size=200)) for _ in range(5)])
    hier = paired.hierarchical_bootstrap(truth, seeds_a, seeds_b, 4, scored=[0, 1, 2, 3], n_boot=2000, level=0.95, rng=np.random.default_rng(3))
    patients_only = paired.hierarchical_bootstrap(truth, seeds_a, seeds_b, 4, scored=[0, 1, 2, 3], n_boot=2000, level=0.95, rng=np.random.default_rng(3), resample_seeds=False)
    assert hier.width > patients_only.width


def test_verdict_has_exactly_three_values_following_adr_007():
    assert paired.verdict(3.0, 7.0, delta=2.0) == "gain confirmé"
    assert paired.verdict(-4.0, 1.5, delta=2.0) == "absence de gain utile"
    assert paired.verdict(-1.0, 5.0, delta=2.0) == "non résolu"
    assert paired.verdict(2.0, 5.0, delta=2.0) == "non résolu"  # borne basse égale à δ : pas strictement au-dessus


def test_bonferroni_level_for_three_comparisons_is_98_33_percent():
    assert paired.bonferroni_level(3, alpha=0.05) == pytest.approx(1 - 0.05 / 3)


def test_false_alarm_rate_of_mcnemar_stays_below_five_percent_without_effect():
    rng = np.random.default_rng(0)
    hits = 0
    for _ in range(600):
        shared = rng.random(300)
        a = (0.6 * shared + 0.4 * rng.random(300)) < 0.7
        b = (0.6 * shared + 0.4 * rng.random(300)) < 0.7
        hits += paired.mcnemar_exact(a, b).p_value < 0.05
    assert hits / 600 <= 0.06


def test_mcnemar_detects_an_injected_effect():
    rng = np.random.default_rng(1)
    hits = 0
    for _ in range(200):
        shared = rng.random(600)
        a = (0.6 * shared + 0.4 * rng.random(600)) < 0.6
        b = (0.6 * shared + 0.4 * rng.random(600)) < 0.72
        hits += paired.mcnemar_exact(b, a).p_value < 0.05
    assert hits / 200 >= 0.9


def _noisy(truth: np.ndarray, shared: np.ndarray, rng: np.random.Generator, acc: float) -> np.ndarray:
    return np.where((0.6 * shared + 0.4 * rng.random(len(truth))) < acc, truth, (truth + 1) % 4)


def test_bootstrap_false_alarm_rate_without_effect_is_close_to_nominal_and_detects_an_injected_effect():
    rng = np.random.default_rng(2)
    null_hits, effect_hits, n = 0, 0, 120
    for _ in range(n):
        truth = np.repeat(np.arange(4), [60, 60, 40, 40])
        shared = rng.random(200)
        a, b, c = _noisy(truth, shared, rng, 0.65), _noisy(truth, shared, rng, 0.65), _noisy(truth, shared, rng, 0.85)
        r0 = paired.hierarchical_bootstrap(truth, a[None, :], b[None, :], 4, scored=[0, 1, 2, 3], n_boot=300, level=0.95, rng=rng)
        r1 = paired.hierarchical_bootstrap(truth, c[None, :], a[None, :], 4, scored=[0, 1, 2, 3], n_boot=300, level=0.95, rng=rng)
        null_hits += (r0.lo > 0) or (r0.hi < 0)
        effect_hits += r1.lo > 0
    assert null_hits / n <= 0.12
    assert effect_hits / n >= 0.9
