import json

from llmft.budget import ALERT_FRACTION, BUDGET_HOURS, alert, consumed_hours, unread_training_runs


def test_consumed_hours_sums_train_and_tokenize_seconds(tmp_path) -> None:
    (tmp_path / "a.json").write_text(json.dumps({"metrics": {"seconds_train": 3600.0, "seconds_tokenize": 1800.0}}))
    (tmp_path / "b.json").write_text(json.dumps({"metrics": {"seconds_train": 1800.0}}))
    (tmp_path / "c.json").write_text(json.dumps({"metrics": {"accuracy": 0.5}}))
    assert consumed_hours(tmp_path) == 2.0


def test_alert_fires_at_eighty_percent_of_budget() -> None:
    assert not alert(BUDGET_HOURS * ALERT_FRACTION - 0.01)
    assert alert(BUDGET_HOURS * ALERT_FRACTION)


def test_consumed_hours_ignores_non_numeric_fields(tmp_path) -> None:
    (tmp_path / "a.json").write_text(json.dumps({"metrics": {"seconds_train": "n/a"}}))
    assert consumed_hours(tmp_path) == 0.0


def test_consumed_hours_falls_back_to_params_for_final_model_runs(tmp_path) -> None:
    """Les runs `final-*` rangent la durée d'entraînement dans `params` (leurs métriques n'ont que `seconds_total`) : elle compte quand même."""
    (tmp_path / "final.json").write_text(json.dumps({"params": {"seconds_train": 7200.0, "seconds_total": 7300.0}, "metrics": {"seconds_total": 7300.0}}))
    (tmp_path / "both.json").write_text(json.dumps({"params": {"seconds_train": 99999.0}, "metrics": {"seconds_train": 3600.0}}))
    assert consumed_hours(tmp_path) == 3.0  # 2 h (repli sur params) + 1 h (les métriques priment, params ignorés)


def test_consumed_hours_reads_a_training_time_nested_one_level_down_in_metrics(tmp_path) -> None:
    """Régression du 17/10 : RM-61 (`morfitt_g.py`) range sa durée dans `metrics.cout_lora` et son pré-vol dans `metrics.pre_vol` ; le compteur les oubliait."""
    (tmp_path / "rm61.json").write_text(json.dumps({"metrics": {"cout_lora": {"seconds_train": 3600.0, "steps": 480}, "g": {"weighted_f1": 72.3}}}))
    (tmp_path / "preflight.json").write_text(json.dumps({"metrics": {"pre_vol": {"seconds_train": 1800.0}}}))
    (tmp_path / "top.json").write_text(json.dumps({"metrics": {"seconds_train": 3600.0, "detail": {"seconds_train": 99999.0}}}))
    assert consumed_hours(tmp_path) == 2.5  # 1 h + 0,5 h + 1 h (la durée du premier niveau prime, jamais comptée deux fois)


def test_the_counter_lists_the_successful_training_runs_whose_duration_it_could_not_read(tmp_path) -> None:
    """N40 : un compteur publie ce qu'il n'a pas pu compter (RM-61 oublié en silence le 17/10)."""
    (tmp_path / "20261017-000000-lu.json").write_text(json.dumps({"kind": "train", "status": "ok", "run_id": "lu", "metrics": {"seconds_train": 60.0}}))
    (tmp_path / "20261017-000001-muet.json").write_text(json.dumps({"kind": "train", "status": "ok", "run_id": "muet", "metrics": {"seconds": 60.0}}))
    (tmp_path / "20261017-000002-abandon.json").write_text(json.dumps({"kind": "train", "status": "aborted", "run_id": "abandon", "metrics": {}}))
    (tmp_path / "20261017-000003-mesure.json").write_text(json.dumps({"kind": "measure", "status": "ok", "run_id": "mesure", "metrics": {}}))
    assert unread_training_runs(tmp_path) == ["muet"]
