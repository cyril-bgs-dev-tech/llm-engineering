import numpy as np
import pytest
from sklearn.metrics import f1_score

from llmft.cluster_bootstrap import cluster_interval


def _data(n_groups=12, per=8, seed=4):
    rng = np.random.default_rng(seed)
    truth = rng.integers(0, 3, n_groups * per)
    pa = np.where(rng.random(len(truth)) < 0.75, truth, rng.integers(0, 3, len(truth)))
    pb = np.where(rng.random(len(truth)) < 0.55, truth, rng.integers(0, 3, len(truth)))
    groups = [f"a{i // per:02d}" for i in range(len(truth))]
    return truth, pa, pb, groups


def test_interval_matches_a_naive_replica_with_sklearn():
    truth, pa, pb, groups = _data()
    scored, n_boot, seed, level = [0, 1], 300, 7, 0.95
    uniq = sorted(set(groups))
    members = {g: np.flatnonzero(np.array(groups) == g) for g in uniq}
    rng = np.random.default_rng(seed)
    weights = rng.multinomial(len(uniq), np.full(len(uniq), 1 / len(uniq)), size=n_boot)
    diffs = []
    for w in weights:
        rows = np.concatenate([np.tile(members[g], int(k)) for g, k in zip(uniq, w, strict=True) if k])
        diffs.append(f1_score(truth[rows], pa[rows], labels=scored, average="macro", zero_division=0) - f1_score(truth[rows], pb[rows], labels=scored, average="macro", zero_division=0))
    lo, hi = np.percentile(diffs, [2.5, 97.5])
    d, lo_c, hi_c = cluster_interval(truth, pa, pb, scored, groups, n_boot=n_boot, seed=seed, level=level)
    allrows = np.arange(len(truth))
    obs = f1_score(truth, pa, labels=scored, average="macro", zero_division=0) - f1_score(truth, pb, labels=scored, average="macro", zero_division=0)
    assert d == pytest.approx(100 * obs, abs=1e-9)
    assert (lo_c, hi_c) == pytest.approx((100 * lo, 100 * hi), abs=1e-9)
    assert allrows.size == len(truth)


def test_unscored_class_does_not_move_the_difference():
    truth, pa, pb, groups = _data()
    pa2 = pa.copy()
    pa2[truth == 2] = 0  # ne change que les prédictions sur les patients de la classe exclue
    d1, *_ = cluster_interval(truth, pa, pb, [0, 1], groups, n_boot=50)
    d2, *_ = cluster_interval(truth, pa2, pb, [0, 1], groups, n_boot=50)
    # la classe 2 disparaît du score, mais ses prédictions fausses créent des faux positifs en 0 : on compare à sklearn
    exp = f1_score(truth, pa2, labels=[0, 1], average="macro", zero_division=0) - f1_score(truth, pb, labels=[0, 1], average="macro", zero_division=0)
    assert d2 == pytest.approx(100 * exp, abs=1e-9)
    assert d1 != d2


def test_a_scored_class_absent_from_truth_scores_zero_like_sklearn():
    truth, pa, pb, groups = _data()
    pa = pa.copy()
    pa[::5] = 7  # A prédit la classe 7 (absente du test), B jamais : F1 de la classe 7 = 0 pour A, dénominateur nul pour B
    d, *_ = cluster_interval(truth, pa, pb, [0, 1, 2, 7], groups, n_boot=50)
    exp = f1_score(truth, pa, labels=[0, 1, 2, 7], average="macro", zero_division=0) - f1_score(truth, pb, labels=[0, 1, 2, 7], average="macro", zero_division=0)
    assert d == pytest.approx(100 * exp, abs=1e-9)


def test_swapping_the_systems_negates_the_interval():
    truth, pa, pb, groups = _data()
    d, lo, hi = cluster_interval(truth, pa, pb, [0, 1, 2], groups, n_boot=400)
    d2, lo2, hi2 = cluster_interval(truth, pb, pa, [0, 1, 2], groups, n_boot=400)
    assert d2 == pytest.approx(-d) and lo2 == pytest.approx(-hi) and hi2 == pytest.approx(-lo)


def test_a_single_author_is_refused_instead_of_returning_a_zero_width_interval():
    truth, pa, pb, _ = _data()
    with pytest.raises(ValueError):
        cluster_interval(truth, pa, pb, [0, 1, 2], ["a"] * len(truth), n_boot=50)
