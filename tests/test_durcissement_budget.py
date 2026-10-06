import json
import math

from llmft import budget


def test_protocol_constants_are_pinned_to_their_literal_values():
    assert budget.BUDGET_HOURS == 90.0 and budget.ALERT_FRACTION == 0.8


def test_alert_threshold_in_literal_hours():
    assert not budget.alert(71.99) and budget.alert(72.0)


def test_an_empty_registry_has_consumed_nothing(tmp_path):
    assert budget.consumed_hours(tmp_path) == 0.0


def test_a_nan_duration_does_not_silence_the_alert(tmp_path):
    (tmp_path / "a.json").write_text('{"metrics": {"seconds_train": NaN}}')
    hours = budget.consumed_hours(tmp_path)
    assert math.isfinite(hours)  # un total NaN ferait taire l'alerte


def test_negative_durations_never_reduce_the_total(tmp_path):
    (tmp_path / "a.json").write_text(json.dumps({"metrics": {"seconds_train": 7200}}))
    (tmp_path / "b.json").write_text(json.dumps({"metrics": {"seconds_train": -3600}}))
    assert budget.consumed_hours(tmp_path) >= 2.0
