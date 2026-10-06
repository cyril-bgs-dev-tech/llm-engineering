import numpy as np
import pytest
from sklearn.metrics import f1_score

from llmft.power_rule import LEVEL, SEED, mean_width, pair_widths, pooled_interval


def _pool(n_seeds, rng):
    truth = np.repeat([0, 1, 2], [40, 25, 15])
    return truth, [np.where(rng.random(80) < 0.8, truth, rng.integers(0, 3, 80)) for _ in range(n_seeds)]


@pytest.mark.parametrize("n_seeds", [3, 4])
def test_mean_width_is_the_arithmetic_mean_of_the_pair_widths(n_seeds):
    truth, preds = _pool(n_seeds, np.random.default_rng(8))
    counts = {0: 6, 1: 4, 2: 3}
    widths = pair_widths(truth, preds, counts, [0, 1, 2], n_boot=100)
    assert len(widths) == n_seeds * (n_seeds - 1) // 2 and len(set(np.round(widths, 6))) > 1
    got = mean_width(truth, preds, counts, [0, 1, 2], n_boot=100)
    assert got == pytest.approx(float(np.mean(widths)))
    assert min(widths) < got < max(widths)


def test_pooled_interval_matches_a_naive_replica_at_the_default_level():
    truth, (a, b) = _pool(2, np.random.default_rng(9))
    n_boot = 150
    rng = np.random.default_rng(SEED)
    by_class = [np.flatnonzero(truth == c) for c in np.unique(truth)]
    rows = np.concatenate([ix[rng.integers(0, len(ix), size=(n_boot, len(ix)))] for ix in by_class], axis=1)
    diffs = [f1_score(truth[r], a[r], labels=[0, 1, 2], average="macro", zero_division=0) - f1_score(truth[r], b[r], labels=[0, 1, 2], average="macro", zero_division=0) for r in rows]
    alpha = (1 - LEVEL) / 2
    lo, hi = np.percentile(diffs, [100 * alpha, 100 * (1 - alpha)])
    d, lo_p, hi_p = pooled_interval(truth, a, b, [0, 1, 2], n_boot=n_boot)
    assert (lo_p, hi_p) == pytest.approx((100 * lo, 100 * hi), abs=1e-9)
    full = np.arange(80)
    assert d == pytest.approx(100 * (f1_score(truth[full], a[full], labels=[0, 1, 2], average="macro", zero_division=0) - f1_score(truth[full], b[full], labels=[0, 1, 2], average="macro", zero_division=0)), abs=1e-9)
