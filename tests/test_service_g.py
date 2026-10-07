import numpy as np
import pytest

from llmft import service_g


def test_g_est_la_moyenne_a_parts_egales_du_lora_de_l_encodeur_moyenne_et_du_tfidf():
    lora = np.array([[0.7, 0.3]])
    encoders = [np.array([[0.4, 0.6]]), np.array([[0.2, 0.8]])]
    tfidf = np.array([[0.1, 0.9]])
    out = service_g.combine_g(lora, encoders, tfidf)
    assert out == pytest.approx(np.array([[(0.7 + 0.3 + 0.1) / 3, (0.3 + 0.7 + 0.9) / 3]]))


def test_combine_g_refuse_une_liste_d_encodeurs_vide_ou_des_formes_differentes():
    with pytest.raises(ValueError, match="encodeur"):
        service_g.combine_g(np.zeros((1, 2)), [], np.zeros((1, 2)))
    with pytest.raises(ValueError, match="forme"):
        service_g.combine_g(np.zeros((1, 2)), [np.zeros((1, 3))], np.zeros((1, 2)))


def test_latence_moyenne_d_une_cascade_ajoute_le_second_etage_aux_cas_escalades_seulement():
    assert service_g.cascade_mean_latency(first_ms=10.0, second_ms=60.0, share_first=0.9) == pytest.approx(10.0 + 0.1 * 60.0)
    assert service_g.cascade_mean_latency(first_ms=10.0, second_ms=60.0, share_first=1.0) == 10.0


def test_part_du_premier_etage_hors_de_zero_un_est_refusee():
    with pytest.raises(ValueError, match="part"):
        service_g.cascade_mean_latency(10.0, 60.0, 1.2)


def test_deux_passages_sont_acceptes_si_les_p50_different_de_moins_de_dix_pour_cent_et_les_classes_sont_identiques():
    assert service_g.passes_accepted(100.0, 105.0, same_classes=True)
    assert not service_g.passes_accepted(100.0, 115.0, same_classes=True)
    assert not service_g.passes_accepted(100.0, 101.0, same_classes=False)


def test_resume_de_latences_ajoute_le_p99():
    out = service_g.latency_percentiles([float(i) for i in range(1, 101)])
    assert out["p50_ms"] == pytest.approx(50.5, abs=0.1) and out["p99_ms"] == pytest.approx(99.0, abs=0.1)
    with pytest.raises(ValueError, match="latence"):
        service_g.latency_percentiles([])
