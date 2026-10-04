"""Fonction de lancement partagée des lots (scripts/lib/lot.sh, règle N25)."""
import subprocess
from pathlib import Path

LIB = Path(__file__).resolve().parents[1] / "scripts/lib/lot.sh"


def _run(tmp_path: Path, body: str) -> tuple[int, str]:
    log = tmp_path / "lot.log"
    script = f'source "{LIB}"; export RUNS_DIR="{tmp_path}/runs"; mkdir -p "$RUNS_DIR"; LOG="{log}"\n{body}\necho "RC=$?"'
    out = subprocess.run(["bash", "-c", script], capture_output=True, text=True, check=False).stdout
    return int(out.strip().split("RC=")[-1]), log.read_text(encoding="utf-8") if log.exists() else ""


def test_exit_code_is_captured_before_logging(tmp_path) -> None:
    rc, log = _run(tmp_path, 'run_lot "$LOG" a 1 bash -c "exit 3"')
    assert rc == 3 and "code=3" in log


def test_retries_a_retryable_code_then_succeeds_and_logs_each_attempt(tmp_path) -> None:
    flag = tmp_path / "flag"
    rc, log = _run(tmp_path, f'run_lot "$LOG" a 4 bash -c "if [ -e {flag} ]; then exit 0; else touch {flag}; exit 139; fi"')
    assert rc == 0 and log.count("DEBUT") == 2 and "code=139" in log and "code=0" in log


def test_non_retryable_code_stops_immediately(tmp_path) -> None:
    rc, log = _run(tmp_path, 'run_lot "$LOG" a 4 bash -c "exit 7"')
    assert rc == 7 and log.count("DEBUT") == 1 and "ARRET" in log


def test_attempts_are_capped_and_the_failure_is_declared(tmp_path) -> None:
    rc, log = _run(tmp_path, 'run_lot "$LOG" a 3 bash -c "exit 139"')
    assert rc == 139 and log.count("DEBUT") == 3 and "ECHEC" in log


def test_run_already_in_the_registry_is_skipped(tmp_path) -> None:
    rc, log = _run(tmp_path, 'touch "$RUNS_DIR/20260101-000000-a.json"; run_lot "$LOG" a 3 bash -c "exit 1"')
    assert rc == 0 and "DEJA" in log and "DEBUT" not in log


def test_a_registered_run_with_a_longer_slug_does_not_hide_a_shorter_one(tmp_path) -> None:
    rc, log = _run(tmp_path, 'touch "$RUNS_DIR/20260101-000000-camembert-pli2.json"; run_lot "$LOG" pli2 1 bash -c "exit 0"')
    assert rc == 0 and "DEBUT" in log and "DEJA" not in log
