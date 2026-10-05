"""Mesure d'énergie d'un bloc de calcul GPU (RM-42) : puissance du GPU échantillonnée une fois par seconde dans un fil, énergie en Wh, coût avec un prix du kWh passé en paramètre."""
import subprocess
import threading
from collections.abc import Callable
from typing import Self

import numpy as np

from llmft import servicecost


def read_gpu_power_w(index: int = 0) -> float | None:
    """Puissance instantanée du GPU `index` en watts, ou None si `nvidia-smi` ne répond pas."""
    out = subprocess.run(["nvidia-smi", "--query-gpu=power.draw", "--format=csv,noheader,nounits", "-i", str(index)], capture_output=True, text=True, check=False).stdout.strip()
    try:
        return float(out.splitlines()[0]) if out else None
    except ValueError:
        return None


class PowerSampler:
    """Échantillonneur de puissance, utilisable comme gestionnaire de contexte ; `reader` est injectable pour les tests."""

    def __init__(self, interval_s: float = 1.0, reader: Callable[[], float | None] = read_gpu_power_w) -> None:
        self.interval_s = interval_s
        self.samples: list[float] = []
        self._reader = reader
        self._stop = threading.Event()
        self._thread = threading.Thread(target=self._run, daemon=True)

    def _run(self) -> None:
        while not self._stop.is_set():
            value = self._reader()
            if value is not None:
                self.samples.append(value)
            self._stop.wait(self.interval_s)

    def __enter__(self) -> Self:
        self._thread.start()
        return self

    def __exit__(self, *exc: object) -> None:
        self._stop.set()
        self._thread.join()

    def summary(self, n_items: int | None = None, price_eur_per_kwh: float | None = None) -> dict[str, float | None]:
        """Énergie en Wh, puissance moyenne et maximale ; avec `n_items` et un prix : coût pour 1 000 éléments."""
        if not self.samples:
            return {"energie_wh": None, "puissance_moyenne_w": None, "puissance_max_w": None}
        arr = np.array(self.samples)
        out: dict[str, float | None] = {"energie_wh": round(servicecost.energy_wh(arr, self.interval_s), 3), "puissance_moyenne_w": round(float(arr.mean()), 1), "puissance_max_w": round(float(arr.max()), 1)}
        if n_items and price_eur_per_kwh is not None:
            out.update(servicecost.per_1000(float(out["energie_wh"] or 0.0), n_items, price_eur_per_kwh))
        return out


def measure_repeated(fn: Callable[[], int], min_seconds: float = 15.0, interval_s: float = 1.0, reader: Callable[[], float | None] = read_gpu_power_w) -> dict[str, float | None]:
    """Répète `fn` (qui renvoie le nombre d'éléments traités) pendant au moins `min_seconds` sous échantillonnage de puissance : une mesure de moins d'une seconde ne contient pas assez d'échantillons.

    Renvoie secondes écoulées, éléments traités, débit par seconde, énergie en Wh et Wh pour 1 000 éléments."""
    import time

    done = 0
    with PowerSampler(interval_s=interval_s, reader=reader) as ps:
        t0 = time.perf_counter()
        while time.perf_counter() - t0 < min_seconds:
            done += fn()
        elapsed = time.perf_counter() - t0
    wh = ps.summary()["energie_wh"]
    return {"secondes": round(elapsed, 2), "elements": float(done), "debit_par_s": round(done / elapsed, 2), "echantillons_puissance": float(len(ps.samples)),
            "energie_wh": wh, "wh_pour_1000": None if wh is None else round(float(wh) / done * 1000.0, 3)}
