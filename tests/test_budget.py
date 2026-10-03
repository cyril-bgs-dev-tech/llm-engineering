import json

from llmft.budget import ALERT_FRACTION, BUDGET_HOURS, alert, consumed_hours


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
