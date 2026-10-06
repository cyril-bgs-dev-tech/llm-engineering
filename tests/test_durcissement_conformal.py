import numpy as np
import pytest

from llmft import conformal


def test_aps_scores_are_the_inclusive_cumulative_mass_in_descending_order():
    s = conformal._scores_all(np.array([[0.3, 0.6, 0.1]]), "aps")[0]
    assert s == pytest.approx([0.9, 0.6, 1.0])


def test_aps_gives_tied_classes_the_same_larger_score():
    s = conformal._scores_all(np.array([[0.4, 0.4, 0.2]]), "aps")[0]
    assert s == pytest.approx([0.8, 0.8, 1.0])


def test_lac_score_is_one_minus_probability():
    assert conformal._scores_all(np.array([[0.7, 0.3]]), "lac")[0] == pytest.approx([0.3, 0.7])


def test_a_class_whose_score_equals_the_quantile_is_kept():
    p = np.array([[0.9, 0.1]])  # scores LAC : 0.1 et 0.9
    assert conformal.predict_sets(p, 0.9) == [{0, 1}]
    assert conformal.predict_sets(p, 0.5) == [{0}]
    assert conformal.predict_sets_by_class(p, {0: 0.9, 1: 0.9}) == [{0, 1}]
    assert conformal.predict_sets_by_group(p, {0: 0.9}, {0: 0, 1: 0}) == [{0, 1}]


def test_finite_sample_guarantee_holds_exactly_on_every_leave_one_out_split():
    n_total, alpha = 20, 0.1
    values = np.arange(n_total, dtype=float)
    covered = 0
    for j in range(n_total):
        qhat = conformal.conformal_quantile(np.delete(values, j), alpha)
        covered += values[j] <= qhat
    assert covered / n_total >= 1 - alpha
    assert covered / n_total < 1 - alpha + 1 / n_total + 1e-9  # sans ties, pas de sur-couverture au-delà d'un rang


def test_evaluate_reports_n_and_wilson_by_class_from_hits_and_counts():
    r = conformal.evaluate([{0}, {1}, {0}, {0}], np.array([0, 0, 1, 1]))
    assert r["n"] == 4 and r["coverage_by_class"] == {0: 0.5, 1: 0.0}
    assert r["coverage_by_class_wilson"][0] == pytest.approx(conformal.wilson(1, 2))
    assert r["coverage_by_class_wilson"][1] == pytest.approx(conformal.wilson(0, 2))


def test_wilson_stays_inside_zero_and_one_at_the_extremes():
    lo, hi = conformal.wilson(0, 10)
    assert lo == 0.0 and hi == pytest.approx(0.2775, abs=1e-3)
    lo, hi = conformal.wilson(10, 10)
    assert hi == 1.0 and lo == pytest.approx(0.7225, abs=1e-3)


def test_alpha_outside_the_open_unit_interval_is_refused():
    with pytest.raises(ValueError):
        conformal.conformal_quantile(np.arange(1.0, 11.0), 1.5)


def test_nan_probabilities_are_refused():
    p = np.array([[0.5, 0.5], [np.nan, np.nan]])
    with pytest.raises(ValueError):
        conformal.fit(p, np.array([0, 1]), 0.1)
