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


MIN_TRIALS_AFTER = 100  # sous ce nombre d'essais après la mise à jour, aucune conclusion (règle de trois : 0/100 borne le taux à 3 %)


@dataclass(frozen=True)
class BiosVerdict:
    label: str  # "toujours instable", "stabilisée", "aucune panne après, effet non démontré", "non concluant"
    crashes_before: int
    n_before: int
    crashes_after: int
    divergent_after: int
    n_after: int
    p_value: float


def bios_verdict(before: Sequence[Trial], after: Sequence[Trial], *, reference_digest: str, alpha: float = 0.05) -> BiosVerdict:
    """Verdict de RM-64 (fiche `2026-10-17-verification-machine-apres-bios`). Après la mise à jour, une seule panne ou une seule empreinte différente
    de la référence d'avant suffit à dire « toujours instable » (ce calcul déterministe ne peut ni planter ni changer sur une machine correcte) ;
    « stabilisée » exige au moins MIN_TRIALS_AFTER essais sans panne ni divergence et un taux de panne d'avant plus élevé (Fisher unilatéral, p < alpha)."""
    from scipy.stats import fisher_exact

    crashes_before = sum(t.returncode != 0 for t in before)
    crashes_after = sum(t.returncode != 0 for t in after)
    divergent_after = sum(t.returncode == 0 and t.digest != reference_digest for t in after)
    table = [[crashes_before, len(before) - crashes_before], [crashes_after, len(after) - crashes_after]]
    p = float(fisher_exact(table, alternative="greater")[1]) if before and after else 1.0
    if crashes_after or divergent_after:
        label = "toujours instable"
    elif len(after) < MIN_TRIALS_AFTER:
        label = "non concluant"
    elif p < alpha:
        label = "stabilisée"
    else:
        label = "aucune panne après, effet non démontré"
    return BiosVerdict(label, crashes_before, len(before), crashes_after, divergent_after, len(after), p)
