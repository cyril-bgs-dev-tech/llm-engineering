import subprocess
import sys
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "scripts/check_exec_bits.py"


def _git(cwd: Path, *args: str) -> None:
    subprocess.run(["git", *args], cwd=cwd, check=True, capture_output=True)


def test_a_shebang_script_without_the_executable_mode_is_reported(tmp_path: Path) -> None:
    box = tmp_path / "repo"
    (box / "scripts").mkdir(parents=True)
    _git(box, "init", "-q")
    (box / "scripts/a.py").write_text("#!/usr/bin/env python3\nprint(1)\n", encoding="utf-8")
    (box / "scripts/b.py").write_text("print(2)\n", encoding="utf-8")
    _git(box, "add", "-A")
    # le script de contrôle se lit depuis son propre dépôt : on le copie dans la boîte
    (box / "scripts/check_exec_bits.py").write_text(SCRIPT.read_text(encoding="utf-8"), encoding="utf-8")
    _git(box, "add", "-A")
    r = subprocess.run([sys.executable, "scripts/check_exec_bits.py"], cwd=box, capture_output=True, text=True, check=False)
    assert r.returncode == 1 and "scripts/a.py" in r.stdout and "scripts/b.py" not in r.stdout
    _git(box, "update-index", "--chmod=+x", "scripts/a.py", "scripts/check_exec_bits.py")
    r2 = subprocess.run([sys.executable, "scripts/check_exec_bits.py"], cwd=box, capture_output=True, text=True, check=False)
    assert r2.returncode == 0
