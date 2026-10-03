"""Règle de choix de l'élève d'ADR-009 (P1-12) : plus haute macro-F1 sous contrainte de mémoire ; égalité apparié : le moins coûteux."""
from llmft import choose

CANDS = {
    "qwen4b": {"macro_f1": 0.60, "cost_s": 2500, "peak_gib": 12.9},
    "gemma": {"macro_f1": 0.64, "cost_s": 3700, "peak_gib": 20.0},
    "qwen9b": {"macro_f1": 0.70, "cost_s": 5000, "peak_gib": 21.0},
}


def test_plus_haute_macro_f1_quand_l_ecart_est_resolu():
    name, why = choose.choose_student(CANDS, ci_for=lambda a, b: (0.02, 0.10), max_peak_gib=28.0)
    assert name == "qwen9b" and "plus haute" in why


def test_egalite_appariee_retient_le_moins_cher_des_deux_meilleurs():
    name, why = choose.choose_student(CANDS, ci_for=lambda a, b: (-0.03, 0.05), max_peak_gib=28.0)
    assert name == "gemma" and "égalité" in why  # gemma (3 700 s) moins cher que qwen9b (5 000 s)


def test_candidat_au_dessus_de_la_limite_de_memoire_est_exclu():
    cands = {**CANDS, "qwen9b": {**CANDS["qwen9b"], "peak_gib": 28.5}}
    name, _ = choose.choose_student(cands, ci_for=lambda a, b: (0.02, 0.10), max_peak_gib=28.0)
    assert name == "gemma"


def test_un_seul_candidat_admissible_est_retenu_sans_comparaison():
    name, _ = choose.choose_student({"qwen4b": CANDS["qwen4b"]}, ci_for=lambda a, b: (_ for _ in ()).throw(AssertionError("pas de comparaison")), max_peak_gib=28.0)
    assert name == "qwen4b"


def test_aucun_candidat_admissible_est_une_erreur():
    import pytest

    with pytest.raises(ValueError):
        choose.choose_student({"x": {"macro_f1": 0.9, "cost_s": 1, "peak_gib": 40.0}}, ci_for=lambda a, b: (0, 0), max_peak_gib=28.0)
