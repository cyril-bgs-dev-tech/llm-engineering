"""Essai d'avance du correctif : sorties d'un essai mort conservées (à verser dans tests/test_lot_sh.py après le lot RM-62)."""
import os
import shlex
import subprocess
from pathlib import Path

LIB = Path(os.environ["LOT_LIB"])


def _run(tmp_path: Path, body: str) -> tuple[int, str]:
    log = tmp_path / "lot.log"
    script = f'source "{LIB}"; export RUNS_DIR="{tmp_path}/runs"; mkdir -p "$RUNS_DIR"; LOG="{log}"\n{body}\necho "RC=$?"'
    out = subprocess.run(["bash", "-c", script], capture_output=True, text=True, check=False).stdout
    return int(out.strip().split("RC=")[-1]), log.read_text(encoding="utf-8") if log.exists() else ""


def test_the_output_of_a_failed_attempt_is_kept_before_the_next_attempt_overwrites_it(tmp_path) -> None:
    flag, out = shlex.quote(str(tmp_path / "flag")), tmp_path / "a.out"
    step = f"if [ -e {flag} ]; then echo essai2 > {shlex.quote(str(out))}; exit 0; else touch {flag}; echo panne1 > {shlex.quote(str(out))}; exit 139; fi"
    rc, log = _run(tmp_path, f'run_lot "$LOG" a 2 bash -c {shlex.quote(step)}')
    assert rc == 0 and out.read_text() == "essai2\n"
    assert (tmp_path / "a.essai1.out").read_text() == "panne1\n" and "CONSERVE a.out" in log


def test_an_output_older_than_the_attempt_is_not_copied(tmp_path) -> None:
    (tmp_path / "ancien.out").write_text("avant\n")
    rc, _ = _run(tmp_path, 'sleep 0.05; run_lot "$LOG" a 1 bash -c "exit 139"')
    assert rc == 139 and not (tmp_path / "ancien.essai1.out").exists()


def test_a_successful_attempt_copies_nothing_and_leaves_no_marker(tmp_path) -> None:
    step = f"echo ok > {shlex.quote(str(tmp_path / 'a.out'))}"
    rc, _ = _run(tmp_path, f'run_lot "$LOG" a 1 bash -c {shlex.quote(step)}')
    assert rc == 0 and sorted(p.name for p in tmp_path.iterdir()) == ["a.out", "lot.log", "runs"]
