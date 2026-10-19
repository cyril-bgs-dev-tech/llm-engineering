"""Moniteur de dérive branché au service (P5-08, `docs/SURVEILLANCE_DERIVE.md`) : fenêtre glissante des étiquettes prédites, variation totale contre la prévalence
prédite de référence (signal S2, seuil mesuré par le run 20261017-090325-simulation-derive) et part servie par E seul quand le service donne l'étage (S1, informatif).
Ne garde ni texte ni probabilité individuelle : seulement les étiquettes et les étages des `window` dernières prédictions."""
import threading
from collections import Counter, deque
from collections.abc import Mapping, Sequence
from typing import Any

import numpy as np

S2_THRESHOLD_100 = 0.207  # 99e centile mesuré sur des lots de 100 patients (run 20261017-090325-simulation-derive)


def reference_prevalence(probs: np.ndarray, labels: Sequence[str]) -> dict[str, float]:
    """Prévalence des étiquettes prédites (argmax) sur des prédictions hors pli : la référence du signal S2."""
    counts = np.bincount(probs.argmax(axis=1), minlength=len(labels))
    return {label: float(c / len(probs)) for label, c in zip(labels, counts, strict=True)}


class DriftMonitor:
    def __init__(self, reference: Mapping[str, float], window: int = 100, threshold: float = S2_THRESHOLD_100) -> None:
        if window <= 0:
            raise ValueError("la fenêtre doit compter au moins une prédiction")
        if abs(sum(reference.values()) - 1.0) > 1e-6:
            raise ValueError("la prévalence de référence doit sommer à 1")
        self.reference, self.window, self.threshold = dict(reference), window, threshold
        self._labels: deque[str] = deque(maxlen=window)
        self._stages: deque[str | None] = deque(maxlen=window)
        self._total = 0
        self._lock = threading.Lock()

    def observe(self, prediction: Mapping[str, Any]) -> None:
        with self._lock:
            self._labels.append(str(prediction["label"]))
            self._stages.append(prediction.get("stage"))
            self._total += 1

    def report(self) -> dict[str, Any]:
        with self._lock:
            labels, stages, total = list(self._labels), list(self._stages), self._total
        tv = None
        if len(labels) == self.window:
            counts = Counter(labels)
            keys = set(counts) | set(self.reference)
            tv = 0.5 * sum(abs(counts[k] / len(labels) - self.reference.get(k, 0.0)) for k in keys)
        known = [s for s in stages if s is not None]
        return {"n": len(labels), "fenetre": self.window, "observations_totales": total, "seuil_s2": self.threshold,
                "s2_tv_prevalence_predite": None if tv is None else round(tv, 4), "alerte_s2": tv is not None and tv > self.threshold,
                "part_servie_par_e": round(known.count("E") / len(known), 4) if known else None}
