import numpy as np

from llmft.final_report import abstention_table, compare, conformal_report, full_report, verdict


def test_verdict_has_three_values() -> None:
    assert verdict(2.1, 9.0, 2.0) == "gain confirmé"
    assert verdict(-3.0, 1.9, 2.0) == "absence de gain utile"
    assert verdict(0.5, 7.0, 2.0) == "non résolu"


def _toy(n: int = 400, k: int = 4, seed: int = 0) -> tuple[np.ndarray, np.ndarray, np.ndarray, list[str]]:
    rng = np.random.default_rng(seed)
    truth = rng.integers(0, k, size=n)
    good = np.eye(k)[truth] * 0.7 + rng.dirichlet(np.ones(k), size=n) * 0.3
    bad = np.eye(k)[rng.integers(0, k, size=n)] * 0.4 + rng.dirichlet(np.ones(k), size=n) * 0.6
    groups = [f"a{i % 20}" for i in range(n)]
    return truth, good, bad, groups


def test_compare_reports_a_positive_difference_with_both_interval_kinds() -> None:
    truth, good, bad, groups = _toy()
    r = compare(truth, good, bad, list(range(4)), groups, n_boot=300)
    assert r["difference_points"] > 0 and r["ic95_blocs_auteurs"][0] < r["difference_points"] < r["ic95_blocs_auteurs"][1] and len(r["ic95_patients"]) == 2


def test_conformal_and_abstention_are_consistent_on_the_toy_problem() -> None:
    truth, good, _, _ = _toy(800)
    fam = {0: 0, 1: 0, 2: 1, 3: 1}
    r = conformal_report(good[:400], truth[:400], good[400:], truth[400:], fam, 0.10)
    assert r["marginal"]["couverture"] >= 0.85 and r["par_famille"]["couverture_minimale"] >= 0.8
    a = abstention_table(good, truth)
    assert a["0.5"]["exactitude"] >= a["1.0"]["exactitude"]


def test_full_report_answers_the_primary_question_and_lists_secondaries_without_verdict() -> None:
    truth, good, bad, groups = _toy(600)
    labels = ["I", "II", "XVIII", "AUTRE"]
    rep = full_report(truth, {"final": good, "tfidf": bad, "ens": good * 0.9 + bad * 0.1}, labels, "AUTRE", groups, "final", "tfidf", ["ens"], 2.0, {0: 0, 1: 0, 2: 1, 3: 1}, {"final": (good, truth)}, n_boot=200)
    assert rep["question_primaire"]["verdict"] in ("gain confirmé", "absence de gain utile", "non résolu")
    assert list(rep["secondaires_sans_verdict"]) == ["final moins ens"] and "verdict" not in rep["secondaires_sans_verdict"]["final moins ens"]
    assert set(rep["sensibilite"]) == {"sans XVIII", "sans XVIII ni XXI"}
