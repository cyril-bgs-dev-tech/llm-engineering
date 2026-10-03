import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import rm14_pair


def test_signale_si_ecart_d_au_moins_trois_points_et_borne_basse_positive():
    assert rm14_pair.decide(0.005, 0.06, 0.035) == "signalé"


def test_ecart_de_trois_points_mais_borne_basse_negative_reste_non_resolu():
    assert rm14_pair.decide(-0.01, 0.07, 0.035) == "non résolu"


def test_non_signale_si_la_borne_haute_est_sous_trois_points():
    assert rm14_pair.decide(-0.02, 0.01, -0.005) == "non signalé"


def test_zone_grise_non_resolue():
    assert rm14_pair.decide(-0.01, 0.05, 0.02) == "non résolu"
