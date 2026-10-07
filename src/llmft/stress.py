"""Synthèse d'un test de charge A/B du TF-IDF (investigation de l'instabilité sporadique) : taux de panne et divergences silencieuses par bras."""
from __future__ import annotations

from collections import Counter
from collections.abc import Sequence
from dataclasses import dataclass, field


@dataclass(frozen=True)
class Trial:
    arm: str
    returncode: int
    digest: str | None
    error: str | None = None


@dataclass
class ArmSummary:
    n: int = 0
    crashes: int = 0
    mismatches: int = 0
    signatures: dict[str, int] = field(default_factory=dict)

    @property
    def crash_rate(self) -> float:
        return self.crashes / self.n if self.n else 0.0


def summarize(trials: Sequence[Trial]) -> dict[str, ArmSummary]:
    """Une panne = code de sortie non nul (signature : l'erreur si connue, sinon le code). Une divergence = succès dont l'empreinte diffère de la plus fréquente parmi tous les succès."""
    for t in trials:
        if t.returncode == 0 and t.digest is None:
            raise ValueError(f"essai réussi sans empreinte dans le bras {t.arm}")
    counts = Counter(t.digest for t in trials if t.returncode == 0)
    reference = counts.most_common(1)[0][0] if counts else None
    out: dict[str, ArmSummary] = {}
    for t in trials:
        s = out.setdefault(t.arm, ArmSummary())
        s.n += 1
        if t.returncode != 0:
            s.crashes += 1
            key = t.error or str(t.returncode)
            s.signatures[key] = s.signatures.get(key, 0) + 1
        elif t.digest != reference:
            s.mismatches += 1
    return out
