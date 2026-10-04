import pytest

from llmft.selection import Candidate, admissible, select_final


def test_the_cheapest_admissible_candidate_is_chosen() -> None:
    cands = [Candidate("tfidf", 0, 0.72, -5.0), Candidate("ensemble", 3, 0.77, 0.0), Candidate("encodeur", 2, 0.75, -1.5), Candidate("lora", 4, 0.775, 0.0)]
    assert select_final(cands).name == "encodeur"


def test_ties_on_cost_go_to_the_higher_macro_f1() -> None:
    cands = [Candidate("a", 1, 0.70, -1.0), Candidate("b", 1, 0.74, -0.5)]
    assert select_final(cands).name == "b"


def test_the_best_candidate_is_always_admissible_and_wins_if_nothing_else_is() -> None:
    cands = [Candidate("x", 0, 0.60, -9.0), Candidate("best", 5, 0.80, 0.0)]
    assert admissible(cands[1]) and select_final(cands).name == "best"


def test_the_bound_must_be_strictly_above_minus_delta() -> None:
    assert not admissible(Candidate("c", 0, 0.7, -2.0))
    assert admissible(Candidate("c", 0, 0.7, -1.99))


def test_empty_list_is_refused() -> None:
    with pytest.raises(ValueError):
        select_final([])
