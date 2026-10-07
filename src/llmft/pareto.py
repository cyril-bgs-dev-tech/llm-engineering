"""Frontière coût-qualité : un système est dominé si un autre est au moins aussi bon sur la qualité, le coût d'entraînement et la latence de service, et meilleur sur l'un des trois."""
import math
from dataclasses import dataclass, field


@dataclass(frozen=True)
class Point:
    quality: float  # macro-F1, à maximiser
    train_s: float  # secondes d'entraînement, à minimiser
    serve_ms: float  # latence de service par patient, à minimiser


@dataclass
class Verdict:
    dominated_by: list[str] = field(default_factory=list)


def dominates(a: Point, b: Point) -> bool:
    no_worse = a.quality >= b.quality and a.train_s <= b.train_s and a.serve_ms <= b.serve_ms
    better = a.quality > b.quality or a.train_s < b.train_s or a.serve_ms < b.serve_ms
    return no_worse and better


def analyse(points: dict[str, Point]) -> dict[str, Verdict]:
    for name, p in points.items():
        if not all(math.isfinite(v) for v in (p.quality, p.train_s, p.serve_ms)):
            raise ValueError(f"valeur non finie pour {name}")
    return {n: Verdict([m for m, q in points.items() if m != n and dominates(q, p)]) for n, p in points.items()}
