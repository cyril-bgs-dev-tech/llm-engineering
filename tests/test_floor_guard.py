"""Garde-fou du plancher de CONSTRAINTS.md : chaque mouvement qui abaisse la barre est détecté sur un dépôt piégé."""
import subprocess
import sys
from pathlib import Path

import pytest

GUARD = Path(__file__).resolve().parents[1] / "scripts/floor_guard.py"


def git(repo, *args):
    subprocess.run(["git", "-C", str(repo), "-c", "user.email=t@t", "-c", "user.name=t", *args], check=True, capture_output=True)


@pytest.fixture
def repo(tmp_path):
    git(tmp_path, "init", "-q", "-b", "main")
    (tmp_path / "src").mkdir()
    (tmp_path / "tests").mkdir()
    (tmp_path / "src/mod.py").write_text("def f():\n    return 1\n", encoding="utf-8")
    (tmp_path / "tests/test_mod.py").write_text("from src.mod import f\n\n\ndef test_f():\n    assert f() == 1\n", encoding="utf-8")
    (tmp_path / "CONSTRAINTS.md").write_text(
        "# Constraints\n\n## Floor\n\n- No new suppression comments: x\n\n## Enforced with numbers\n\n"
        "| Dimension | Rule | Checked by |\n|---|---|---|\n| Coverage | Changed lines >= 80% covered | pytest |\n| Typage | Zero error | mypy |\n",
        encoding="utf-8",
    )
    git(tmp_path, "add", "-A")
    git(tmp_path, "commit", "-q", "-m", "base")
    return tmp_path


def run(repo, *extra):
    return subprocess.run([sys.executable, str(GUARD), "--root", str(repo), *extra], capture_output=True, text=True, check=False)


def test_clean_tree_passes(repo):
    assert run(repo).returncode == 0


@pytest.mark.parametrize(
    "path, content, rule",
    [
        ("src/mod.py", "def f():\n    return 1  # type: ignore\n", "silenced-checker"),
        ("src/mod.py", "def f():\n    return 1  # noqa: E501\n", "silenced-checker"),
        ("src/mod.py", "def f():\n    try:\n        return 1\n    except Exception:\n        pass\n", "unfinished-work"),
        ("src/mod.py", "def f():\n    raise NotImplementedError('à faire')\n", "unfinished-work"),
        ("tests/test_mod.py", "import pytest\n\n\n@pytest.mark.skip\ndef test_f():\n    assert True\n", "test-made-easier"),
        ("tests/test_mod.py", "from src.mod import f\n\n\ndef test_f():\n    f()\n", "assertion-removed"),
    ],
)
def test_each_lowering_move_is_detected(repo, path, content, rule):
    (repo / path).write_text(content, encoding="utf-8")
    result = run(repo)
    assert result.returncode == 1 and rule in result.stderr


def test_a_deleted_test_file_is_detected(repo):
    (repo / "tests/test_mod.py").unlink()
    result = run(repo)
    assert result.returncode == 1 and "test-deleted" in result.stderr


def test_a_loosened_threshold_is_detected_but_a_tightened_one_is_silent(repo):
    c = repo / "CONSTRAINTS.md"
    c.write_text(c.read_text(encoding="utf-8").replace(">= 80%", ">= 60%"), encoding="utf-8")
    assert run(repo).returncode == 1 and "threshold-loosened" in run(repo).stderr
    c.write_text(c.read_text(encoding="utf-8").replace(">= 60%", ">= 90%"), encoding="utf-8")
    assert run(repo).returncode == 0


def test_a_removed_rule_is_detected(repo):
    c = repo / "CONSTRAINTS.md"
    c.write_text("\n".join(x for x in c.read_text(encoding="utf-8").splitlines() if "Typage" not in x) + "\n", encoding="utf-8")
    result = run(repo)
    assert result.returncode == 1 and "rule-removed" in result.stderr


def test_untracked_new_files_are_inspected_too(repo):
    (repo / "src/new.py").write_text("x = 1  # type: ignore\n", encoding="utf-8")
    assert run(repo).returncode == 1


def test_guard_that_cannot_run_exits_two_never_zero(tmp_path):
    assert run(tmp_path).returncode == 2  # pas un dépôt Git
