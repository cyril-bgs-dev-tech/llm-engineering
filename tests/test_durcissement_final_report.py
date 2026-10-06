import numpy as np
import pytest
from sklearn.metrics import f1_score

from llmft import final_report as fr
from llmft.power_rule import pooled_interval


def _onehot(pred, k=3):
    return np.eye(k)[np.asarray(pred)] * 0.9 + 0.05


def test_verdict_boundaries_are_strict_on_both_sides():
    assert fr.verdict(2.0, 9.0, 2.0) == "non résolu"
    assert fr.verdict(-3.0, 2.0, 2.0) == "non résolu"


def test_system_metrics_on_a_hand_computed_example():
    truth = np.array([0, 0, 1, 1, 2, 2])
    probs = _onehot([0, 1, 1, 1, 2, 0])
    m = fr.system_metrics(truth, probs, [0, 1, 2], ["a", "b", "c"])
    assert m["accuracy"] == 0.6667  # 4 justes sur 6, arrondi à 4 décimales
    assert m["f1_par_chapitre"] == {"a": {"n": 2, "f1": 0.5}, "b": {"n": 2, "f1": 0.8}, "c": {"n": 2, "f1": 0.6667}}
    assert m["macro_f1"] == round(f1_score(truth, probs.argmax(1), labels=[0, 1, 2], average="macro"), 4) == 0.6556
    only_ab = fr.system_metrics(truth, probs, [0, 1], ["a", "b", "c"])
    assert only_ab["macro_f1"] == 0.65 and "c" not in only_ab["f1_par_chapitre"]


def test_compare_gives_the_pooled_interval_at_95_percent_and_keeps_a_minus_b_orientation():
    rng = np.random.default_rng(0)
    truth = rng.integers(0, 3, 300)
    good, bad = _onehot(truth), _onehot(rng.integers(0, 3, 300))
    groups = [f"a{i % 15}" for i in range(300)]
    r = fr.compare(truth, good, bad, [0, 1, 2], groups, n_boot=200)
    _, lo, hi = pooled_interval(truth, good.argmax(1), bad.argmax(1), [0, 1, 2], n_boot=200, level=0.95)
    assert r["ic95_patients"] == [round(lo, 2), round(hi, 2)] and r["difference_points"] > 0
    assert fr.compare(truth, bad, good, [0, 1, 2], groups, n_boot=200)["difference_points"] == -r["difference_points"]


def test_conformal_report_is_calibrated_on_the_calibration_set_only():
    k = 3
    cal_y = np.repeat(np.arange(k), 40)
    cal_p = _onehot(cal_y) * 0 + np.eye(k)[cal_y] * 0.97 + 0.01  # calibration très sûre : seuil LAC bas
    test_y = np.repeat(np.arange(k), 40)
    test_p = np.full((120, k), 0.3) + np.eye(k)[(test_y + 1) % k] * 0.1  # test difficile : la vraie classe a p = 0.3
    test_p /= test_p.sum(1, keepdims=True)
    r = fr.conformal_report(cal_p, cal_y, test_p, test_y, {0: 0, 1: 0, 2: 1}, alpha=0.1)
    assert r["niveau_vise"] == pytest.approx(0.9)
    assert r["marginal"]["couverture"] < 0.5  # le seuil appris sur le développement ne couvre pas un test plus dur
    assert r["par_famille"]["couverture"] < 0.5


def test_conformal_report_minimum_is_the_smallest_family_coverage():
    rng = np.random.default_rng(1)
    y = rng.integers(0, 4, 800)
    p = np.where(np.isin(y, [2, 3])[:, None], 0.25 + 0.1 * rng.random((800, 4)), np.eye(4)[y] * 0.9 + 0.025)
    p /= p.sum(1, keepdims=True)
    r = fr.conformal_report(p[:400], y[:400], p[400:], y[400:], {0: 0, 1: 0, 2: 1, 3: 1})
    cov = [v["couverture"] for v in r["par_famille"]["details"].values()]
    assert len(set(cov)) > 1  # le scénario sépare bien les familles
    assert r["par_famille"]["couverture_minimale"] == min(cov)


def test_abstention_keeps_the_most_confident_and_rounds_the_count():
    conf = np.array([0.9, 0.8, 0.7, 0.6, 0.5])  # 5 patients
    probs = np.stack([conf, 1 - conf], axis=1)
    truth = np.array([0, 0, 1, 0, 1])  # prédiction 0 partout : justes aux rangs 1, 2, 4
    out = fr.abstention_table(probs, truth, coverages=(1.0, 0.7, 0.6, 0.5))
    assert out["0.7"]["n_traites"] == 4  # round(3.5) = 4 (et non int(3.5) = 3)
    assert out["1.0"]["n_traites"] == 5 and out["1.0"]["exactitude"] == 0.6
    assert out["0.6"]["n_traites"] == 3 and out["0.6"]["exactitude"] == pytest.approx(0.667, abs=1e-3)
    assert out["0.5"]["n_traites"] == 2  # round(2.5) = 2 : arrondi bancaire, à connaître


def test_full_report_primary_question_orientation_delta_and_sensitivity():
    rng = np.random.default_rng(2)
    truth = rng.integers(0, 4, 400)
    labels = ["I", "XVIII", "XXI", "AUTRE"]
    good, bad = _onehot(truth, 4), _onehot(rng.integers(0, 4, 400), 4)
    groups = [f"a{i % 20}" for i in range(400)]
    kw = {"labels": labels, "other": "AUTRE", "groups": groups, "secondary": [], "delta": 2.0, "family_of_class": {0: 0, 1: 0, 2: 1, 3: 1}, "n_boot": 200}
    up = fr.full_report(truth, {"f": good, "r": bad}, final="f", reference="r", calibration={"f": (good, truth)}, **kw)
    down = fr.full_report(truth, {"f": bad, "r": good}, final="f", reference="r", calibration={"f": (bad, truth)}, **kw)
    assert up["question_primaire"]["verdict"] == "gain confirmé" and up["question_primaire"]["delta"] == 2.0
    assert down["question_primaire"]["verdict"] == "absence de gain utile"
    assert up["sensibilite"]["sans XVIII"]["f"] == pytest.approx(fr.macro_f1(truth, good.argmax(1), [0, 2]), abs=1e-4)
    assert up["sensibilite"]["sans XVIII ni XXI"]["r"] == pytest.approx(fr.macro_f1(truth, bad.argmax(1), [0]), abs=1e-4)
    assert up["systemes"]["f"]["macro_f1"] == pytest.approx(fr.macro_f1(truth, good.argmax(1), [0, 1, 2]), abs=1e-4)


def test_full_report_verdict_is_read_from_the_blocks_of_authors_interval(monkeypatch):
    fake = {"difference_points": 1.0, "ic95_blocs_auteurs": [-1.0, 5.0], "ic95_patients": [0.0, 2.0]}
    monkeypatch.setattr(fr, "compare", lambda *a, **k: fake)
    rng = np.random.default_rng(0)
    truth = rng.integers(0, 3, 60)
    p = _onehot(truth)
    rep = fr.full_report(truth, {"f": p, "r": p}, ["I", "II", "AUTRE"], "AUTRE", ["a"] * 60, "f", "r", [], 2.0, {0: 0, 1: 0, 2: 1}, {"f": (p, truth)}, n_boot=10)
    assert rep["question_primaire"]["verdict"] == "non résolu"  # [-1 ; 5] contient delta = 2


def test_the_two_verdict_implementations_agree_on_a_grid():
    from llmft import paired

    grid = [-5.0, 0.0, 1.9, 2.0, 2.1, 7.0]
    for lo in grid:
        for hi in grid:
            if lo <= hi:
                assert fr.verdict(lo, hi, 2.0) == paired.verdict(lo, hi, 2.0)
