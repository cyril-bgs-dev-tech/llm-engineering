import time

from llmft.energy import PowerSampler


def test_sampler_collects_samples_and_computes_energy() -> None:
    with PowerSampler(interval_s=0.01, reader=lambda: 100.0) as ps:
        time.sleep(0.15)
    s = ps.summary()
    assert len(ps.samples) >= 5 and s["puissance_moyenne_w"] == 100.0 and s["puissance_max_w"] == 100.0
    assert abs(float(s["energie_wh"] or 0.0) - len(ps.samples) * 100.0 * 0.01 / 3600.0) < 1e-3


def test_sampler_tolerates_a_reader_that_returns_nothing() -> None:
    with PowerSampler(interval_s=0.01, reader=lambda: None) as ps:
        time.sleep(0.05)
    assert ps.summary() == {"energie_wh": None, "puissance_moyenne_w": None, "puissance_max_w": None}


def test_cost_per_1000_items_uses_the_given_price() -> None:
    ps = PowerSampler(interval_s=3600.0, reader=lambda: 0.0)
    ps.samples = [1000.0]  # 1 000 W pendant 3 600 s = 1 000 Wh
    s = ps.summary(n_items=500, price_eur_per_kwh=0.2)
    assert s["energie_wh"] == 1000.0 and s["wh_pour_1000_patients"] == 2000.0 and s["euros_pour_1000_patients"] == 0.4


def test_measure_repeated_runs_for_at_least_the_minimum_duration_and_counts_items() -> None:
    from llmft.energy import measure_repeated

    calls = []

    def work() -> int:
        calls.append(1)
        time.sleep(0.01)
        return 5

    r = measure_repeated(work, min_seconds=0.2, interval_s=0.02, reader=lambda: 50.0)
    assert r["secondes"] >= 0.2 and r["elements"] == 5 * len(calls) and r["echantillons_puissance"] >= 3
    assert r["wh_pour_1000"] is not None and r["wh_pour_1000"] > 0
