"""Suite de RM-60 (fiche 2026-10-17-energie-service-g-cascade) : la mesure d'énergie d'un chemin couvre au moins 15 secondes de charge mesurée."""
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import service_g_cascade as sgc


def test_l_energie_vient_de_la_puissance_moyenne_et_de_la_duree_mesuree():
    assert sgc.energy_wh_from_mean([100.0, 300.0], 36.0) == pytest.approx(2.0)


def test_les_passages_se_repetent_jusqu_a_quinze_secondes_mesurees_meme_si_l_echauffement_etait_lent():
    """Régression du 17/10 : le nombre de passages calculé sur le passage d'échauffement (plus lent) a donné 10,2 s de charge au lieu de 15."""
    now = [0.0]

    def clock() -> float:
        return now[0]

    def one_pass() -> None:
        now[0] += 5.1

    n, seconds = sgc.repeat_until(15.0, one_pass, clock)
    assert n == 3 and seconds >= 15.0


def test_la_part_forcee_vers_g_suit_la_part_hors_pli_et_ne_depend_que_du_texte():
    texts = [f"compte rendu fictif numéro {i}" for i in range(20_000)]
    share = sum(sgc.forced_to_g(t) for t in texts) / len(texts)
    assert share == pytest.approx(1 - sgc.SHARE_E_OUT_OF_FOLD, abs=0.01)
    assert [sgc.forced_to_g(t) for t in texts[:50]] == [sgc.forced_to_g(t) for t in texts[:50]]


def test_les_evenements_sont_agreges_par_minute_apres_l_echauffement():
    events = [(5.0, 999.0, True)] + [(60.0 + 60 * m + k, 10.0 * (m + 1), k != 3 or m != 1) for m in range(3) for k in range(10)]
    minutes = sgc.per_minute(events, start=60.0, n_minutes=3)
    assert [m["requetes"] for m in minutes] == [10, 10, 10]
    assert [m["p50_ms"] for m in minutes] == [10.0, 20.0, 30.0]
    assert [m["erreurs"] for m in minutes] == [0, 1, 0]
    assert minutes[0]["debit_patients_par_s"] == pytest.approx(10 / 60)


def test_la_croissance_compare_le_maximum_de_la_fin_a_la_moyenne_du_debut():
    samples = [(60.0 + 10 * i, 1000.0 + (300.0 if i >= 150 else 0.0) + (i % 2)) for i in range(180)]
    assert sgc.growth(samples, start=60.0, n_minutes=30) == pytest.approx(301.0, abs=0.6)


def test_le_p95_d_une_fenetre_regroupe_les_requetes_reussies_de_cette_fenetre_seulement():
    events = [(100.0 + k, float(k + 1), True) for k in range(100)] + [(150.0, 9999.0, False), (500.0, 9999.0, True)]
    assert sgc.window_p95(events, 100.0, 200.0) == pytest.approx(95.05)


def test_le_service_tient_la_charge_aux_frontieres_exactes():
    assert sgc.load_verdict(0, 100.0, 120.0, gpu_growth_mib=500.0, rss_growth_gib=1.0) == ("tient la charge", [])


def test_une_seule_erreur_ou_une_derive_suffit_a_ne_pas_tenir():
    assert sgc.load_verdict(1, 100.0, 100.0, 0.0, 0.0) == ("ne tient pas", ["erreurs"])
    assert sgc.load_verdict(0, 100.0, 120.1, 0.0, 0.0) == ("ne tient pas", ["latence p95"])
    assert sgc.load_verdict(0, 100.0, 100.0, 500.1, 1.01)[1] == ["mémoire GPU", "mémoire résidente"]
