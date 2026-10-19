"""Suite de P5-08 : critère de la fiche 2026-10-17-taille-echantillon-etiquete, écrit et testé avant tout run."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import audit_sample_size


def test_la_taille_recommandee_est_la_plus_petite_qui_atteint_quatre_vingts_pour_cent() -> None:
    power = {"macro_f1": {"100": 0.3, "200": 0.79, "500": 0.80, "1000": 0.95, "2000": 1.0},
             "exactitude": {"100": 0.5, "200": 0.85, "500": 0.99, "1000": 1.0, "2000": 1.0}}
    r = audit_sample_size.recommend(power)
    assert r["taille_par_metrique"] == {"macro_f1": 500, "exactitude": 200}
    assert r["metrique_recommandee"] == "exactitude" and r["taille_recommandee"] == 200


def test_en_cas_d_egalite_la_macro_f1_l_emporte() -> None:
    power = {"macro_f1": {"100": 0.1, "200": 0.9, "500": 1.0, "1000": 1.0, "2000": 1.0}, "exactitude": {"100": 0.2, "200": 0.81, "500": 1.0, "1000": 1.0, "2000": 1.0}}
    assert audit_sample_size.recommend(power)["metrique_recommandee"] == "macro_f1"


def test_aucune_taille_suffisante_se_dit_au_dela_de_deux_mille() -> None:
    power = {"macro_f1": {"100": 0.1, "200": 0.2, "500": 0.3, "1000": 0.5, "2000": 0.79}, "exactitude": {"100": 0.1, "200": 0.2, "500": 0.3, "1000": 0.5, "2000": 0.6}}
    r = audit_sample_size.recommend(power)
    assert r["taille_par_metrique"] == {"macro_f1": None, "exactitude": None}
    assert r["taille_recommandee"] is None and r["lecture"] == "au-delà de 2 000 patients"
