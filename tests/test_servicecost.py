import numpy as np
import pytest

from llmft import servicecost


def test_latency_summary_percentiles() -> None:
    s = servicecost.latency_summary(list(range(1, 101)))
    assert s["p50_ms"] == 50.5 and s["p95_ms"] == 95.0 and s["moyenne_ms"] == 50.5


def test_energy_of_constant_power() -> None:
    assert servicecost.energy_wh(np.full(3600, 100.0), 1.0) == pytest.approx(100.0)


def test_per_1000_scales_and_prices_energy() -> None:
    r = servicecost.per_1000(total_wh=2.0, n_patients=500, price_eur_per_kwh=0.25)
    assert r == {"wh_pour_1000_patients": 4.0, "euros_pour_1000_patients": 0.001}


def test_invalid_inputs_are_refused() -> None:
    with pytest.raises(ValueError):
        servicecost.latency_summary([])
    with pytest.raises(ValueError):
        servicecost.per_1000(1.0, 0, 0.2)
