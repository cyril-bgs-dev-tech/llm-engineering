#!/usr/bin/env python3
"""Couverture des lignes modifiées de src/ : lit le rapport JSON de pytest-cov et le diff Git, sans relancer la suite.

Seuil : 80 % (CONSTRAINTS.md). Sans commit, toutes les lignes de src/ comptent comme modifiées.
En CI l'arbre est propre : la variable CHANGED_COVERAGE_BASE (ex. origin/main) donne la base du diff, sinon la porte passerait à vide.
"""
import json
import os
import re
import subprocess
import sys
from pathlib import Path

THRESHOLD = 0.80
EMPTY_TREE = "4b825dc642cb6eb9a060e54bf8d69288fbee4904"
ROOT = Path(__file__).resolve().parents[1]


def diff_base(base_ref: str | None, has_head: bool) -> str:
    """Cible du diff : le dépôt sans commit compare à l'arbre vide ; une base explicite (CI) se compare à HEAD."""
    if not has_head or base_ref == EMPTY_TREE:
        return EMPTY_TREE
    return f"{base_ref}...HEAD" if base_ref else "HEAD"


def added_lines(diff: str) -> dict[str, set[int]]:
    out: dict[str, set[int]] = {}
    current: str | None = None
    for line in diff.splitlines():
        if line.startswith("+++ "):
            name = re.sub(r"^b/", "", line[4:])
            current = name if name.startswith("src/") and name.endswith(".py") else None
        elif line.startswith("@@") and current:
            m = re.search(r"\+(\d+)(?:,(\d+))?", line)
            if m:
                start, count = int(m.group(1)), int(m.group(2) or 1)
                out.setdefault(current, set()).update(range(start, start + count))
    return out


def changed_coverage(changed: dict[str, set[int]], report: dict) -> tuple[int, int]:
    covered = total = 0
    for path, lines in changed.items():
        entry = report["files"].get(path)
        if not entry:
            continue
        executable = set(entry["executed_lines"]) | set(entry["missing_lines"])
        relevant = lines & executable
        total += len(relevant)
        covered += len(relevant & set(entry["executed_lines"]))
    return covered, total


def git(*args: str, ok: tuple[int, ...] = (0,)) -> str:
    r = subprocess.run(["git", "-C", str(ROOT), *args], capture_output=True, text=True, check=False)
    return r.stdout if r.returncode in ok else ""


def main() -> int:
    report_path = ROOT / "artifacts/coverage.json"
    if not report_path.exists():
        print("couverture : artifacts/coverage.json absent, lancer d'abord pytest --cov", file=sys.stderr)
        return 2
    report = json.loads(report_path.read_text(encoding="utf-8"))
    has_head = bool(git("rev-parse", "--verify", "HEAD").strip())
    diff = git("diff", "--unified=0", diff_base(os.environ.get("CHANGED_COVERAGE_BASE"), has_head), "--", "src")
    for f in filter(None, git("ls-files", "--others", "--exclude-standard", "src").splitlines()):
        diff += "\n" + git("diff", "--no-index", "--unified=0", "/dev/null", f, ok=(0, 1))
    covered, total = changed_coverage(added_lines(diff), report)
    if total == 0:
        print("couverture des lignes modifiées : rien à vérifier")
        return 0
    ratio = covered / total
    print(f"couverture des lignes modifiées : {ratio:.1%} ({covered}/{total}), seuil {THRESHOLD:.0%}")
    return 0 if ratio >= THRESHOLD else 1


if __name__ == "__main__":
    sys.exit(main())
