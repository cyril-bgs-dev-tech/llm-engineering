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
