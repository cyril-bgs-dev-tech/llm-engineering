"""Coût de service : résumé de latences, énergie par patient et coût pour 1 000 patients à partir d'une mesure de puissance."""
import numpy as np
from numpy.typing import NDArray


def latency_summary(latencies_ms: list[float]) -> dict[str, float]:
    a = np.asarray(latencies_ms, dtype=float)
    if a.size == 0:
        raise ValueError("aucune latence")
    return {"p50_ms": round(float(np.percentile(a, 50)), 1), "p95_ms": round(float(np.percentile(a, 95)), 1), "moyenne_ms": round(float(a.mean()), 1)}


def energy_wh(power_w: NDArray[np.floating], interval_s: float) -> float:
    """Énergie en Wh d'un échantillonnage de puissance à intervalle régulier (somme rectangulaire)."""
    if interval_s <= 0:
        raise ValueError("intervalle > 0")
    return float(np.sum(power_w) * interval_s / 3600.0)


def per_1000(total_wh: float, n_patients: int, price_eur_per_kwh: float) -> dict[str, float]:
    """Énergie (Wh) et coût (euros) pour 1 000 patients ; le prix du kWh est un paramètre explicite, jamais une valeur supposée."""
    if n_patients <= 0 or price_eur_per_kwh < 0:
        raise ValueError("effectif > 0 et prix >= 0")
    wh = total_wh / n_patients * 1000.0
    return {"wh_pour_1000_patients": round(wh, 2), "euros_pour_1000_patients": round(wh / 1000.0 * price_eur_per_kwh, 4)}
