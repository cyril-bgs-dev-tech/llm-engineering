import pytest

from llmft import pareto


def point(quality: float, train_s: float, serve_ms: float) -> pareto.Point:
    return pareto.Point(quality=quality, train_s=train_s, serve_ms=serve_ms)


def test_un_point_domine_s_il_est_au_moins_aussi_bon_partout_et_meilleur_quelque_part():
    assert pareto.dominates(point(0.78, 100, 10), point(0.77, 200, 10))
    assert not pareto.dominates(point(0.78, 100, 10), point(0.78, 100, 10))
    assert not pareto.dominates(point(0.78, 300, 10), point(0.77, 200, 10))


def test_la_frontiere_garde_les_points_non_domines_et_nomme_le_dominant():
    pts = {"A": point(0.72, 50, 2), "B": point(0.78, 18000, 85), "C": point(0.70, 60, 3), "D": point(0.77, 3000, 28)}
    out = pareto.analyse(pts)
    assert out["C"].dominated_by == ["A"]
    assert out["A"].dominated_by == [] and out["B"].dominated_by == [] and out["D"].dominated_by == []


def test_un_point_a_valeur_non_finie_est_refuse():
    with pytest.raises(ValueError, match="finie"):
        pareto.analyse({"X": point(float("nan"), 1, 1)})
