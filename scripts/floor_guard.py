#!/usr/bin/env python3
"""Garde-fou du plancher de CONSTRAINTS.md : détecte, dans le diff, les mouvements qui abaissent la barre.

Adapté de la référence du skill constraint-driven-development. Sortie 0 propre, 1 violation, 2 impossible à exécuter.
Sans commit (dépôt neuf), la base est l'arbre vide : tout fichier est alors « ajouté ».
Rapporte la règle et l'emplacement, jamais une valeur de secret.
"""
import argparse
import re
import subprocess
import sys
from pathlib import Path

SUPPRESSIONS = re.compile(r"#\s*noqa|#\s*type:\s*ignore|#\s*pragma:\s*no cover|nosemgrep|gitleaks:allow|#\s*pylint:\s*disable|ruff:\s*noqa")
STUBS = re.compile(r"raise NotImplementedError|except[^:\n]*:\s*pass\b|^\s*pass\s*#\s*stub|\bTODO\b|\bFIXME\b")
SKIPS = re.compile(r"@pytest\.mark\.(skip|xfail)\b|pytest\.skip\(|@unittest\.skip")
ASSERT = re.compile(r"\b(assert|raises|approx|check_)\b")
EMPTY_TREE = "4b825dc642cb6eb9a060e54bf8d69288fbee4904"  # arbre vide de Git (git hash-object -t tree /dev/null)
MIN_BEFORE = re.compile(r"(>=|>|≥|at least|minimum|\bmin\b|not fall|ne doit pas baisser)\s*$")
MAX_BEFORE = re.compile(r"(<=|<|≤|at most|maximum|\bmax\b|under|below|not grow|ne doit pas croître)\s*$")


def git(root: Path, *args: str, ok: tuple[int, ...] = (0,)) -> str | None:
    r = subprocess.run(["git", "-C", str(root), *args], capture_output=True, text=True, check=False)
    return r.stdout if r.returncode in ok else None


def is_test(path: str) -> bool:
    return bool(re.search(r"(^|/)(test_[^/]*|[^/]*_test)\.py$", path))


def rule_key(text: str) -> str | None:
    s = text.strip()
    if s.startswith("|"):
        cells = [c.strip() for c in s.split("|") if c.strip()]
        return cells[0] if cells and not set(cells[0]) <= {"-", ":"} else None
    if re.match(r"^[-*] ", s):
        return s[2:].split(":")[0].strip()
    return None


def thresholds(text: str) -> list[tuple[float, str | None]]:
    out = []
    for m in re.finditer(r"\d+(?:\.\d+)?", text):
        before = text[max(0, m.start() - 24) : m.start()].lower()
        direction = "min" if MIN_BEFORE.search(before) else "max" if MAX_BEFORE.search(before) else None
        out.append((float(m.group()), direction))
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=".")
    ap.add_argument("--base", default=None)
    args = ap.parse_args()
    root = Path(args.root)
    if git(root, "rev-parse", "--git-dir") is None:
        print("floor-guard : pas un dépôt Git", file=sys.stderr)
        return 2
    base = args.base or ("HEAD" if git(root, "rev-parse", "--verify", "HEAD") else EMPTY_TREE)
    tracked = git(root, "diff", "--unified=0", base, "--")
    untracked_list = git(root, "ls-files", "--others", "--exclude-standard")
    if tracked is None or untracked_list is None:
        print("floor-guard : diff impossible", file=sys.stderr)
        return 2
    diff = tracked
    for f in filter(None, untracked_list.splitlines()):
        d = git(root, "diff", "--no-index", "--unified=0", "/dev/null", f, ok=(0, 1))
        diff += "\n" + (d or "")

    added, removed, deleted = [], [], []
    old = cur = ""
    for line in diff.splitlines():
        if line.startswith("--- "):
            old = re.sub(r"^[ab]/", "", line[4:])
        elif line.startswith("+++ "):
            new = re.sub(r"^[ab]/", "", line[4:])
            cur = old if new == "/dev/null" else new
            if new == "/dev/null":
                deleted.append(cur)
        elif line.startswith("+") and not line.startswith("+++"):
            added.append((cur, line[1:]))
        elif line.startswith("-") and not line.startswith("---"):
            removed.append((cur, line[1:]))

    findings: list[tuple[str, str, str]] = []

    def flag(rule: str, f: str, text: str) -> None:
        findings.append((rule, f, text.strip()[:120]))

    for f, text in added:
        if f.endswith(("floor_guard.py", "test_floor_guard.py")):
            continue  # le garde-fou et ses cas piégés contiennent par nature les motifs qu'il détecte
        if f.endswith((".py", ".sh")):
            if SUPPRESSIONS.search(text):
                flag("silenced-checker", f, text)
            if STUBS.search(text):
                flag("unfinished-work", f, text)
            if SKIPS.search(text):
                flag("test-made-easier", f, text)
    for k in range(len(added) - 1):  # `except ...:` suivi d'un `pass` sur la ligne ajoutée suivante : erreur avalée
        (f1, a), (f2, b) = added[k], added[k + 1]
        if f1 == f2 and f1.endswith(".py") and not f1.endswith("test_floor_guard.py") and re.match(r"^\s*except\b.*:\s*$", a) and re.match(r"^\s*pass\s*$", b):
            flag("unfinished-work", f1, a + " / pass")
    for f in deleted:
        if is_test(f):
            flag("test-deleted", f, "fichier supprimé")
    for f, text in removed:
        if is_test(f) and f not in deleted and ASSERT.search(text):
            flag("assertion-removed", f, text)

    gone = [(f, t) for f, t in removed if f.endswith("CONSTRAINTS.md") and rule_key(t)]
    new_rules = [(f, t) for f, t in added if f.endswith("CONSTRAINTS.md") and rule_key(t)]
    for f, text in gone:
        match = next((t for g, t in new_rules if rule_key(t) == rule_key(text)), None)
        if match is None:
            flag("rule-removed", f, text)
            continue
        before, after = thresholds(text), thresholds(match)
        for direction in ("min", "max"):
            was = [n for n, d in before if d == direction]
            now = [n for n, d in after if d == direction]
            for i, b in enumerate(was):
                if i >= len(now):
                    flag("threshold-removed", f, text)
                elif (direction == "min" and now[i] < b) or (direction == "max" and now[i] > b):
                    flag("threshold-loosened", f, f"{text.strip()}  ->  {match.strip()}")

    if not findings:
        print("floor-guard : propre")
        return 0
    print(f"floor-guard : {len(findings)} violation(s) du plancher :", file=sys.stderr)
    for rule, f, text in findings:
        print(f"  [{rule}] {f} : {text}", file=sys.stderr)
    print("Chacune abaisse la barre : corriger le code, ou passer par une exception tracée.", file=sys.stderr)
    return 1


if __name__ == "__main__":
    sys.exit(main())
