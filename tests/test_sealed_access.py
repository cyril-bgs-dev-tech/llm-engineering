"""Le test scellé n'est lisible que par un seul module, et une seule fois (P0-34, RM-20)."""
import re
from pathlib import Path

import pytest

from llmft import sealed

ROOT = Path(__file__).resolve().parents[1]
ALLOWED = {
    ROOT / "src/llmft/sealed.py",  # la porte
    ROOT / "src/llmft/splits.py",  # fabrique les partitions
    ROOT / "scripts/make_splits.py",  # les écrit
}
READS_TEST_PARTITION = re.compile(r"""\[\s*["']test["']\s*\]|\.test\b|sealed""")


def python_sources():
    for base in ("src", "scripts", "data/scripts"):
        yield from (ROOT / base).rglob("*.py")


def test_no_other_module_reads_the_sealed_partition():
    offenders = [
        f"{p.relative_to(ROOT)}:{n}"
        for p in python_sources() if p not in ALLOWED
        for n, line in enumerate(p.read_text(encoding="utf-8").splitlines(), 1)
        if READS_TEST_PARTITION.search(line) and not line.lstrip().startswith("#")
    ]
    assert offenders == [], f"lecture de la partition scellée hors de la porte : {offenders}"


def test_the_detector_would_catch_a_leaky_module(tmp_path):
    leaky = tmp_path / "leaky.py"
    leaky.write_text('ids = json.load(f)["test"]\n', encoding="utf-8")
    assert READS_TEST_PARTITION.search(leaky.read_text(encoding="utf-8"))


def test_opening_requires_an_explicit_reason_and_happens_once(tmp_path):
    marker = tmp_path / "opened.json"
    ids = sealed.open_sealed_test({"test": ["P1", "P2"]}, marker=marker, reason="évaluation finale du protocole")
    assert ids == ["P1", "P2"] and marker.exists()
    with pytest.raises(sealed.AlreadyOpenedError):
        sealed.open_sealed_test({"test": ["P1", "P2"]}, marker=marker, reason="encore une fois")


def test_empty_reason_is_refused(tmp_path):
    with pytest.raises(ValueError, match="reason"):
        sealed.open_sealed_test({"test": ["P1"]}, marker=tmp_path / "o.json", reason=" ")
    assert not (tmp_path / "o.json").exists()
