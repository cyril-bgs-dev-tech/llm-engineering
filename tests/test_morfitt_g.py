"""RM-61 : règles de la fiche 2026-10-17-g-gele-morfitt, écrites et testées avant tout entraînement et avant la seconde lecture du test public."""
import sys
from pathlib import Path

import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import morfitt_g


@pytest.mark.parametrize(("lo", "hi", "expected"), [(72.0, 75.0, "dépassé"), (71.0, 74.0, "dans la bande"), (71.95, 74.0, "dans la bande"), (68.0, 71.9, "en dessous")])
def test_le_chiffre_publie_n_est_depasse_que_si_la_borne_basse_est_au_dessus(lo, hi, expected):
    assert morfitt_g.published_verdict(lo, hi, 71.95) == expected


def test_l_intervalle_apparie_est_nul_pour_deux_predictions_identiques():
    y = np.array([[1, 0], [0, 1], [1, 1], [0, 1]])
    d, lo, hi = morfitt_g.paired_diff_ci(y, y.copy(), y.copy(), n_boot=200)
    assert (d, lo, hi) == (0.0, 0.0, 0.0)


def test_l_intervalle_apparie_est_positif_quand_a_corrige_toutes_les_erreurs_de_b():
    rng = np.random.default_rng(1)
    y = rng.integers(0, 2, (300, 3))
    y[y.sum(1) == 0, 0] = 1
    b = y.copy()
    b[:150, 1] = 1 - b[:150, 1]
    d, lo, hi = morfitt_g.paired_diff_ci(y, y.copy(), b, n_boot=500)
    assert d > 0 and lo > 0 and lo <= d <= hi
