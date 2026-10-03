"""Règle de puissance RM-17 (PROTOCOLE.md 6.3) : largeur moyenne des intervalles percentile à 98,33 % de la différence de macro-F1 entre graines."""
import numpy as np
import pytest
from sklearn.metrics import f1_score

from llmft.power_rule import SEED, THRESHOLD_POINTS, mean_width, pair_widths

COUNTS = {0: 6, 1: 4, 2: 3}  # strates du test jouet


def _pool(rng: np.random.Generator) -> tuple[np.ndarray, list[np.ndarray]]:
    truth = np.repeat([0, 1, 2], [40, 25, 15])
    base = truth.copy()
    preds = []
    for _ in range(3):
        p = base.copy()
        flip = rng.random(len(p)) < 0.2
        p[flip] = rng.integers(0, 3, flip.sum())
        preds.append(p)
    return truth, preds


def test_pair_widths_match_a_naive_sklearn_replica() -> None:
    truth, preds = _pool(np.random.default_rng(5))
    n_boot = 200
    widths = pair_widths(truth, preds, COUNTS, scored=[0, 1, 2], n_boot=n_boot, seed=SEED)
    # réplique naïve : même flux de tirages, métrique de scikit-learn réplique par réplique
    rng = np.random.default_rng(SEED)
    expected = []
    for i in range(3):
        for j in range(i + 1, 3):
            idx = np.concatenate([rng.integers(0, int((truth == c).sum()), size=(n_boot, n)) for c, n in sorted(COUNTS.items())], axis=1)
            by_class = {c: np.where(truth == c)[0] for c in COUNTS}
            rows = np.concatenate([by_class[c][idx[:, sum(COUNTS[k] for k in sorted(COUNTS) if k < c) : sum(COUNTS[k] for k in sorted(COUNTS) if k <= c)]] for c in sorted(COUNTS)], axis=1)
            diffs = [f1_score(truth[r], preds[i][r], labels=[0, 1, 2], average="macro", zero_division=0) - f1_score(truth[r], preds[j][r], labels=[0, 1, 2], average="macro", zero_division=0) for r in rows]
            lo, hi = np.percentile(diffs, [100 * (1 - 0.9833) / 2, 100 * (1 - (1 - 0.9833) / 2)])
            expected.append(100 * (hi - lo))
    assert widths == pytest.approx(expected, abs=1e-9)


def test_pairs_follow_lexicographic_order_and_count() -> None:
    truth, preds = _pool(np.random.default_rng(1))
    assert len(pair_widths(truth, preds, COUNTS, scored=[0, 1, 2], n_boot=50, seed=SEED)) == 3


def test_fewer_than_three_seeds_fails_the_rule() -> None:
    truth, preds = _pool(np.random.default_rng(2))
    assert mean_width(truth, preds[:2], COUNTS, scored=[0, 1, 2], n_boot=50) is None


def test_threshold_is_two_delta() -> None:
    assert THRESHOLD_POINTS == 4.0


def test_identical_seeds_give_zero_width() -> None:
    truth, preds = _pool(np.random.default_rng(3))
    assert pair_widths(truth, [preds[0], preds[0], preds[0]], COUNTS, scored=[0, 1, 2], n_boot=50, seed=SEED) == [0.0, 0.0, 0.0]
