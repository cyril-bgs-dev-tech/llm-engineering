"""Budget de GPU (protocole, section 5) : somme des durées des runs du registre et alerte à 80 % de B."""
import json
import math
from pathlib import Path

BUDGET_HOURS = 90.0
ALERT_FRACTION = 0.8


def _seconds(value: object) -> float:
    if not isinstance(value, int | float) or isinstance(value, bool):
        return 0.0
    number = float(value)
    return number if math.isfinite(number) and number > 0.0 else 0.0  # une durée NaN, infinie ou négative ne fausse pas le total


def consumed_hours(runs_dir: Path) -> float:
    total = 0.0
    for path in sorted(runs_dir.glob("*.json")):
        record = json.loads(path.read_text(encoding="utf-8"))
        metrics = record.get("metrics", {})
        train = _seconds(metrics.get("seconds_train")) or _seconds(record.get("params", {}).get("seconds_train"))  # runs final-* : durée dans params
        total += train + _seconds(metrics.get("seconds_tokenize"))
    return total / 3600.0


def alert(hours: float) -> bool:
    return hours >= BUDGET_HOURS * ALERT_FRACTION
