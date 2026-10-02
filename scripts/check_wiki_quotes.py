#!/usr/bin/env python3
"""Vérifie que chaque citation littérale d'une page du wiki figure mot pour mot dans les lignes citées du fichier brut."""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FOOTNOTE = re.compile(r"^\[\^[^\]]+\]:\s*(.*)$")
TARGET = re.compile(r"(raw/[\w.\-]+)")
RANGE = re.compile(r"\bL(\d+)(?:-L?(\d+))?")
QUOTE = re.compile(r"[\"«“]([^\"»”]+)[\"»”]")


def norm(text: str) -> str:
    text = text.replace("’", "'").replace("“", '"').replace("”", '"')
    return re.sub(r"\s+", " ", text).strip().lower()


def check(wiki_root: Path) -> list[str]:
    problems = []
    for page in sorted((wiki_root / "wiki/pages").glob("*.md")):
        for n, line in enumerate(page.read_text(encoding="utf-8").splitlines(), 1):
            m = FOOTNOTE.match(line)
            if not m:
                continue
            body = m.group(1)
            target = TARGET.search(body)
            if not target:
                continue  # citation vers une page source ou une URL : hors périmètre de ce contrôle
            raw = wiki_root / target.group(1)
            where = f"{page.name}:{n}"
            if not raw.exists():
                problems.append(f"{where} : fichier brut introuvable : {target.group(1)}")
                continue
            lines = raw.read_text(encoding="utf-8").splitlines()
            spans = RANGE.findall(body.split("—")[0])
            if not spans:
                problems.append(f"{where} : plage de lignes absente pour {target.group(1)}")
                continue
            chosen, bad_range = [], False
            for start, end in spans:
                a, b = int(start), int(end or start)
                if a < 1 or b > len(lines) or a > b:
                    bad_range = True
                chosen += lines[max(a, 1) - 1 : b]
            if bad_range:
                problems.append(f"{where} : plage de lignes hors du fichier ({len(lines)} lignes)")
                continue
            if "[synthesis]" in body:
                continue
            haystack = norm(" ".join(chosen))
            quotes = QUOTE.findall(body.split("—", 1)[1]) if "—" in body else []
            if not quotes:
                problems.append(f"{where} : ni citation littérale ni balise [synthesis]")
            for q in quotes:
                if norm(q) not in haystack:
                    problems.append(f"{where} : citation absente des lignes citées : « {q[:70]} »")
    return problems


def main() -> int:
    problems = check(ROOT / "knowledge")
    for p in problems:
        print(p, file=sys.stderr)
    print("citations du wiki : " + ("défauts" if problems else "toutes retrouvées dans les lignes citées"))
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
