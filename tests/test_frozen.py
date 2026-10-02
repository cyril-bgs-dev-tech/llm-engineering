import hashlib
from pathlib import Path

from llmft import frozen


def _index(tmp_path: Path, path: str, sha: str) -> str:
    return (
        "| Date | Objet | Fichier | SHA-256 | Avant quelle mesure |\n|---|---|---|---|---|\n"
        f"| 2026-10-03 | gel | `{path}` | `{sha}` | P1-03 |\n"
        "| 2026-10-02 | ancien, sans instantané | `PROTOCOLE.md` (état entier) | `" + "a" * 64 + "` | P0-28 |\n"
    )


def _snapshot(tmp_path: Path, text: str = "règle gelée\n") -> tuple[Path, str]:
    target = tmp_path / "experiments/frozen/PROTOCOLE-2026-10-03.md"
    target.parent.mkdir(parents=True)
    target.write_text(text, encoding="utf-8")
    return target, hashlib.sha256(text.encode("utf-8")).hexdigest()


def test_matching_snapshot_has_no_problem(tmp_path):
    _, sha = _snapshot(tmp_path)
    assert frozen.check_index(_index(tmp_path, "experiments/frozen/PROTOCOLE-2026-10-03.md", sha), tmp_path) == []


def test_modified_snapshot_is_reported(tmp_path):
    target, sha = _snapshot(tmp_path)
    target.write_text("règle changée\n", encoding="utf-8")
    problems = frozen.check_index(_index(tmp_path, "experiments/frozen/PROTOCOLE-2026-10-03.md", sha), tmp_path)
    assert len(problems) == 1 and "empreinte" in problems[0]


def test_missing_snapshot_is_reported(tmp_path):
    problems = frozen.check_index(_index(tmp_path, "experiments/frozen/absent.md", "b" * 64), tmp_path)
    assert len(problems) == 1 and "absent" in problems[0]


def test_rows_without_snapshot_are_ignored(tmp_path):
    only_old = "| Date | Objet | Fichier | SHA-256 | Avant |\n|---|---|---|---|---|\n| 2026-10-02 | x | `PROTOCOLE.md` | `" + "a" * 64 + "` | P0-28 |\n"
    assert frozen.check_index(only_old, tmp_path) == []
