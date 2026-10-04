import numpy as np

from llmft.cluster_bootstrap import cluster_interval
from llmft.power_rule import pooled_interval


def _synthetic(correlated: bool) -> tuple[np.ndarray, np.ndarray, np.ndarray, list[str]]:
    rng = np.random.default_rng(1)
    n_groups, per = 40, 25
    truth = rng.integers(0, 3, size=n_groups * per)
    groups = [f"a{i // per}" for i in range(n_groups * per)]
    skill_a = rng.normal(0.8, 0.12 if correlated else 0.0, size=n_groups).clip(0.4, 0.99)
    skill_b = rng.normal(0.6, 0.12 if correlated else 0.0, size=n_groups).clip(0.2, 0.99)
    pa, pb = truth.copy(), truth.copy()
    for g in range(n_groups):
        sl = slice(g * per, (g + 1) * per)
        wrong_a = rng.random(per) > skill_a[g]
        wrong_b = rng.random(per) > skill_b[g]
        pa[sl] = np.where(wrong_a, (truth[sl] + 1) % 3, truth[sl])
        pb[sl] = np.where(wrong_b, (truth[sl] + 2) % 3, truth[sl])
    return truth, pa, pb, groups


def test_observed_difference_matches_the_patient_level_estimate() -> None:
    truth, pa, pb, groups = _synthetic(False)
    d_c, _, _ = cluster_interval(truth, pa, pb, [0, 1, 2], groups, n_boot=300)
    d_p, _, _ = pooled_interval(truth, pa, pb, [0, 1, 2], n_boot=300)
    assert abs(d_c - d_p) < 1e-6


def test_correlated_errors_within_groups_widen_the_interval() -> None:
    truth, pa, pb, groups = _synthetic(True)
    _, lo_c, hi_c = cluster_interval(truth, pa, pb, [0, 1, 2], groups, n_boot=2000)
    _, lo_p, hi_p = pooled_interval(truth, pa, pb, [0, 1, 2], n_boot=2000)
    assert (hi_c - lo_c) > (hi_p - lo_p)


def test_identical_systems_have_a_zero_width_interval() -> None:
    truth, pa, _, groups = _synthetic(False)
    d, lo, hi = cluster_interval(truth, pa, pa, [0, 1, 2], groups, n_boot=200)
    assert d == 0.0 and lo == 0.0 and hi == 0.0
