"""Gardes des fiches préenregistrées : empreinte inchangée depuis le hachage (N29), aucune heure postérieure au moment de l'écriture (N37),
constantes de décision du code présentes dans le texte de la fiche (N41)."""
import hashlib
import re
from collections.abc import Sequence
from datetime import UTC, datetime
from pathlib import Path

_ROW = re.compile(r"^\|[^|]*\|[^|]*\|\s*`(experiments/[^`/]+\.md)`[^|]*\|\s*`([0-9a-f]{64})`")
_FR = re.compile(r"\b(\d{2})/(\d{2})/(\d{4}) (?:vers |à |a )?(\d{2}):(\d{2})(?::(\d{2}))?Z")
_ISO = re.compile(r"\b(\d{4})-(\d{2})-(\d{2})T(\d{2}):(\d{2})(?::(\d{2}))?Z")
_SEP = "[   ]?"


def check_fiche_hashes(index_text: str, root: Path) -> tuple[list[str], int]:
    """Chaque fiche `experiments/*.md` citée par l'index garde l'une de ses empreintes consignées ; toute fiche datée du dossier est citée."""
    hashes: dict[str, set[str]] = {}
    for line in index_text.splitlines():
        if m := _ROW.match(line):
            hashes.setdefault(m[1], set()).add(m[2])
    problems = []
    for rel, expected in sorted(hashes.items()):
        path = root / rel
        if not path.is_file():
            problems.append(f"fiche citée absente : {rel}")
        elif hashlib.sha256(path.read_bytes()).hexdigest() not in expected:
            problems.append(f"fiche modifiée après son hachage : {rel}")
    for path in sorted((root / "experiments").glob("20*.md")):
        rel = path.relative_to(root).as_posix()
        if rel not in hashes:
            problems.append(f"fiche sans empreinte dans l'index : {rel}")
    return problems, len(hashes)


def future_times(text: str, now: datetime) -> list[str]:
    """Heures datées (« le 17/10/2026 vers 20:10Z », « 2026-10-17T20:10:00Z ») postérieures à `now` : tapées ou estimées, pas lues sur l'horloge."""
    found = []
    for m in _FR.finditer(text):
        d, mo, y, h, mi, s = m.groups()
        if datetime(int(y), int(mo), int(d), int(h), int(mi), int(s or 0), tzinfo=UTC) > now:
            found.append(f"{d}/{mo}/{y} {h}:{mi}Z")
    for m in _ISO.finditer(text):
        y, mo, d, h, mi, s = m.groups()
        if datetime(int(y), int(mo), int(d), int(h), int(mi), int(s or 0), tzinfo=UTC) > now:
            found.append(m[0])
    return found


def _pattern(value: float) -> str:
    if isinstance(value, int):
        digits = str(value)
        head, rest = digits[: len(digits) % 3 or 3], digits[len(digits) % 3 or 3 :]
        body = re.escape(head) + "".join(_SEP + rest[i : i + 3] for i in range(0, len(rest), 3))
        return rf"(?<![\d,]){body}(?![\d]|,\d)"
    return rf"(?<![\d,]){re.escape(f'{value:g}'.replace('.', ','))}0*(?!\d)"


def missing_constants(fiche_text: str, constants: Sequence[float]) -> list[float]:
    """Constantes de décision du code introuvables dans la fiche, écrites à la française (virgule décimale, espace des milliers facultative)."""
    return [c for c in constants if not re.search(_pattern(c), fiche_text)]
