import pytest

from llmft.drift import drift_report, total_variation


def test_total_variation_is_zero_for_identical_distributions_and_one_for_disjoint_ones() -> None:
    assert total_variation(["a", "b"], ["b", "a"]) == 0.0
    assert total_variation(["a", "a"], ["b", "b"]) == 1.0


def test_total_variation_of_partial_overlap() -> None:
    assert total_variation(["a", "a", "b", "b"], ["a", "a", "a", "b"]) == pytest.approx(0.25)


def test_report_flags_only_what_exceeds_the_threshold() -> None:
    ref = {"labels": ["a"] * 50 + ["b"] * 50, "lengths": list(range(100)), "authors": ["x"] * 50 + ["y"] * 50}
    same = drift_report(ref, ref)
    assert not any(same["alertes"].values())
    shifted = drift_report(ref, {"labels": ["a"] * 95 + ["b"] * 5, "lengths": [v + 500 for v in range(100)], "authors": ["z"] * 100})
    assert shifted["alertes"] == {"prevalence": True, "longueur": True, "auteurs": True}


def test_confident_share_counts_rows_whose_maximum_reaches_tau_inclusively() -> None:
    import numpy as np

    from llmft.drift import confident_share

    probs = np.array([[0.6, 0.4], [0.5, 0.5], [0.1, 0.9], [0.59, 0.41]])
    assert confident_share(probs, 0.6) == pytest.approx(0.5)


def test_ks_statistic_is_public_and_matches_the_report() -> None:
    from llmft.drift import ks_statistic

    assert ks_statistic([1, 2, 3], [1, 2, 3]) == 0.0
    assert ks_statistic([0, 0, 0], [5, 5, 5]) == 1.0


def test_draw_lots_samples_without_replacement_and_is_reproducible() -> None:
    import numpy as np

    from llmft.drift import draw_lots

    a = draw_lots(50, 10, 200, seed=7)
    b = draw_lots(50, 10, 200, seed=7)
    assert a.shape == (200, 10)
    assert np.array_equal(a, b)
    assert all(len(set(row)) == 10 for row in a.tolist())


def test_draw_lots_follows_the_weights() -> None:
    import numpy as np

    from llmft.drift import draw_lots

    weights = np.array([0.0] * 10 + [1.0] * 10 + [3.0] * 10)
    lots = draw_lots(30, 5, 2000, seed=1, weights=weights)
    assert not np.isin(lots, np.arange(10)).any()
    heavy = np.isin(lots, np.arange(20, 30)).mean()
    assert heavy > 0.65


def test_lot_signals_are_zero_when_the_lot_is_the_reference() -> None:
    import numpy as np

    from llmft.drift import lot_signals

    probs = np.array([[0.9, 0.1], [0.3, 0.7], [0.55, 0.45], [0.2, 0.8]])
    lengths = np.array([10, 20, 30, 40])
    s = lot_signals(probs, lengths, probs, lengths, tau=0.6)
    assert s == {"s1_baisse_part_e": 0.0, "s2_tv_prevalence_predite": 0.0, "s3_ks_longueur": 0.0}


def test_lot_signals_measure_a_drop_of_confidence_and_a_shift_of_predicted_chapters() -> None:
    import numpy as np

    from llmft.drift import lot_signals

    ref = np.array([[0.9, 0.1], [0.9, 0.1], [0.1, 0.9], [0.1, 0.9]])
    lot = np.array([[0.55, 0.45], [0.55, 0.45], [0.52, 0.48], [0.1, 0.9]])
    s = lot_signals(lot, np.array([1, 2, 3, 4]), ref, np.array([1, 2, 3, 4]), tau=0.6)
    assert s["s1_baisse_part_e"] == pytest.approx(0.75)
    assert s["s2_tv_prevalence_predite"] == pytest.approx(0.25)
    assert s["s3_ks_longueur"] == 0.0


def test_alert_threshold_is_the_upper_quantile_and_detection_is_strict() -> None:
    import numpy as np

    from llmft.drift import alert_threshold, detection_rate

    null = np.arange(1, 101, dtype=float)
    t = alert_threshold(null, 0.99)
    assert t == pytest.approx(np.quantile(null, 0.99))
    assert detection_rate(null, t) == pytest.approx(0.01)
    assert detection_rate(np.array([t, t]), t) == 0.0


def test_low_tail_power_uses_the_lower_quantile_of_the_reference_and_a_strict_comparison() -> None:
    import numpy as np

    from llmft.drift import low_tail_power

    null = np.arange(1, 101, dtype=float)
    threshold, power = low_tail_power(null, np.array([1.0, 5.0, 5.95, 50.0]), 0.05)
    assert threshold == pytest.approx(np.quantile(null, 0.05))
    assert power == pytest.approx(0.5)
    assert low_tail_power(null, null, 0.05)[1] == pytest.approx(0.05)
