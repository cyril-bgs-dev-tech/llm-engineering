"""P5-08 (branchement) : moniteur de dérive du service, fenêtre glissante d'étiquettes prédites, aucun texte conservé."""
import threading

import numpy as np
import pytest

from llmft.drift_monitor import DriftMonitor, reference_prevalence

REF = {"IX": 0.5, "XIX": 0.5}


def test_pas_de_verdict_avant_que_la_fenetre_soit_pleine() -> None:
    m = DriftMonitor(REF, window=4, threshold=0.2)
    for label in ("IX", "XIX", "IX"):
        m.observe({"label": label, "probability": 0.9})
    r = m.report()
    assert r["n"] == 3 and r["s2_tv_prevalence_predite"] is None and r["alerte_s2"] is False


def test_une_fenetre_conforme_a_la_reference_n_alerte_pas() -> None:
    m = DriftMonitor(REF, window=4, threshold=0.2)
    for label in ("IX", "XIX", "IX", "XIX"):
        m.observe({"label": label, "probability": 0.9})
    r = m.report()
    assert r["s2_tv_prevalence_predite"] == pytest.approx(0.0) and r["alerte_s2"] is False


def test_une_fenetre_d_un_seul_chapitre_alerte_et_la_fenetre_glisse() -> None:
    m = DriftMonitor(REF, window=4, threshold=0.2)
    for label in ("IX", "XIX", "IX", "XIX") + ("IX",) * 4:
        m.observe({"label": label, "probability": 0.9})
    r = m.report()
    assert r["n"] == 4 and r["s2_tv_prevalence_predite"] == pytest.approx(0.5) and r["alerte_s2"] is True
    assert r["observations_totales"] == 8


def test_le_depassement_est_strict() -> None:
    m = DriftMonitor(REF, window=4, threshold=0.25)
    for label in ("IX", "IX", "IX", "XIX"):
        m.observe({"label": label, "probability": 0.9})
    assert m.report()["s2_tv_prevalence_predite"] == pytest.approx(0.25)
    assert m.report()["alerte_s2"] is False


def test_la_part_servie_par_e_seul_est_suivie_quand_le_service_donne_l_etage() -> None:
    m = DriftMonitor(REF, window=4, threshold=0.2)
    for stage in ("E", "E", "G", "E"):
        m.observe({"label": "IX", "probability": 0.9, "stage": stage})
    assert m.report()["part_servie_par_e"] == pytest.approx(0.75)
    plain = DriftMonitor(REF, window=4, threshold=0.2)
    plain.observe({"label": "IX", "probability": 0.9})
    assert plain.report()["part_servie_par_e"] is None


def test_le_rapport_ne_contient_aucun_texte_ni_probabilite_individuelle() -> None:
    m = DriftMonitor(REF, window=2, threshold=0.2)
    m.observe({"label": "IX", "probability": 0.123456, "text": "secret"})
    flat = repr(m.report())
    assert "secret" not in flat and "0.123456" not in flat


def test_une_etiquette_inconnue_de_la_reference_compte_comme_un_ecart() -> None:
    m = DriftMonitor(REF, window=2, threshold=0.2)
    m.observe({"label": "AUTRE", "probability": 0.9})
    m.observe({"label": "AUTRE", "probability": 0.9})
    assert m.report()["s2_tv_prevalence_predite"] == pytest.approx(1.0)


def test_les_observations_concurrentes_ne_se_perdent_pas() -> None:
    m = DriftMonitor(REF, window=10_000, threshold=0.2)
    threads = [threading.Thread(target=lambda: [m.observe({"label": "IX", "probability": 0.9}) for _ in range(500)]) for _ in range(8)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    assert m.report()["observations_totales"] == 4000


def test_reference_prevalence_vient_des_predictions_hors_pli() -> None:
    probs = np.array([[0.9, 0.1], [0.2, 0.8], [0.6, 0.4], [0.7, 0.3]])
    assert reference_prevalence(probs, ["IX", "XIX"]) == {"IX": 0.75, "XIX": 0.25}


def test_parametres_invalides_refuses() -> None:
    with pytest.raises(ValueError):
        DriftMonitor(REF, window=0, threshold=0.2)
    with pytest.raises(ValueError):
        DriftMonitor({"IX": 0.4, "XIX": 0.4}, window=10, threshold=0.2)
