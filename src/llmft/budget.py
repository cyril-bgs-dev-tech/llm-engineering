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


def _nested_seconds(metrics: dict[str, object]) -> float:
    """Durée d'entraînement rangée un niveau plus bas (`metrics.cout_lora`, `metrics.pre_vol` de RM-61) ; seulement à défaut du premier niveau."""
    return next((s for v in metrics.values() if isinstance(v, dict) and (s := _seconds(v.get("seconds_train")))), 0.0)


def _train_seconds(record: dict[str, object]) -> float:
    metrics = record.get("metrics") or {}
    params = record.get("params") or {}
    assert isinstance(metrics, dict) and isinstance(params, dict)
    return (_seconds(metrics.get("seconds_train")) or _seconds(params.get("seconds_train"))  # runs final-* : durée dans params
            or _nested_seconds(metrics))


def _records(runs_dir: Path) -> list[dict[str, object]]:
    return [json.loads(path.read_text(encoding="utf-8")) for path in sorted(runs_dir.glob("*.json"))]


def consumed_hours(runs_dir: Path) -> float:
    total = 0.0
    for record in _records(runs_dir):
        metrics = record.get("metrics") or {}
        assert isinstance(metrics, dict)
        total += _train_seconds(record) + _seconds(metrics.get("seconds_tokenize"))
    return total / 3600.0


def unread_training_runs(runs_dir: Path) -> list[str]:
    """Runs d'entraînement aboutis dont aucune durée n'est lisible : non comptés, à publier à côté du total (N40)."""
    return [str(r.get("run_id")) for r in _records(runs_dir) if r.get("kind") == "train" and r.get("status") == "ok" and not _train_seconds(r)]


def alert(hours: float) -> bool:
    return hours >= BUDGET_HOURS * ALERT_FRACTION
