"""P5-08 : critère de décision de la fiche 2026-10-17-simulation-derive, écrit et testé avant tout run."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import simulate_drift


def _by_n(impact_200: float, det_200: dict[str, float], det_100: dict[str, float] | None = None, det_500: dict[str, float] | None = None) -> dict:
    zero = {s: 0.0 for s in simulate_drift.SIGNALS}
    return {"100": {"detection": {**zero, **(det_100 or {})}, "impact_macro_f1_points": impact_200},
            "200": {"detection": {**zero, **det_200}, "impact_macro_f1_points": impact_200},
            "500": {"detection": {**zero, **(det_500 if det_500 is not None else det_200)}, "impact_macro_f1_points": impact_200}}


def test_un_scenario_a_exactement_moins_deux_points_est_nuisible() -> None:
    d = simulate_drift.decide({"c_textes_courts": _by_n(-2.0, {"s3_ks_longueur": 0.9})})
    assert d["scenarios"]["c_textes_courts"]["nuisible"] is True
    assert simulate_drift.decide({"c_textes_courts": _by_n(-1.99, {})})["scenarios"]["c_textes_courts"]["nuisible"] is False


def test_un_signal_est_retenu_a_partir_de_quatre_vingts_pour_cent_de_detection_a_n_200() -> None:
    d = simulate_drift.decide({"b_prevalence": _by_n(-0.5, {"s2_tv_prevalence_predite": 0.80, "s1_baisse_part_e": 0.79})})
    assert d["scenarios"]["b_prevalence"]["signaux_retenus"] == ["s2_tv_prevalence_predite"]


def test_la_longueur_ne_compte_jamais_pour_les_nouveaux_auteurs() -> None:
    d = simulate_drift.decide({"a_nouveaux_auteurs": _by_n(-5.0, {"s3_ks_longueur": 0.95})})
    assert d["scenarios"]["a_nouveaux_auteurs"]["signaux_retenus"] == []
    assert d["scenarios"]["a_nouveaux_auteurs"]["non_surveillable_sans_etiquettes"] is True
    assert d["regle_alerte"] == {}


def test_la_regle_prend_la_plus_petite_taille_de_lot_qui_atteint_le_seuil() -> None:
    d = simulate_drift.decide({"c_textes_courts": _by_n(-3.0, {"s3_ks_longueur": 0.85}, det_100={"s3_ks_longueur": 0.81}),
                               "a_nouveaux_auteurs": _by_n(-4.0, {"s1_baisse_part_e": 0.5}, det_500={"s1_baisse_part_e": 0.9})})
    assert d["regle_alerte"] == {"s3_ks_longueur": 100}
    assert d["scenarios"]["a_nouveaux_auteurs"]["signaux_a_500"] == ["s1_baisse_part_e"]
    assert d["scenarios"]["a_nouveaux_auteurs"]["non_surveillable_sans_etiquettes"] is False


def test_un_scenario_non_nuisible_n_entre_pas_dans_la_regle() -> None:
    d = simulate_drift.decide({"b_prevalence": _by_n(-0.3, {"s2_tv_prevalence_predite": 0.99})})
    assert d["regle_alerte"] == {}
    assert d["scenarios"]["b_prevalence"]["non_surveillable_sans_etiquettes"] is False
