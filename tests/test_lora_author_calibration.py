"""Suite de RM-62 : critère de la fiche 2026-10-17-etalonnage-nouveaux-auteurs et étalonnage croisé, écrits et testés avant tout run. Données synthétiques."""
import sys
from pathlib import Path

import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import lora_author_calibration as cal
from llmft import metrics


def _overconfident(n: int = 1500, k: int = 6, sharpen: float = 3.0, seed: int = 0) -> tuple[np.ndarray, np.ndarray, np.ndarray, list[str]]:
    """Étiquettes tirées des probabilités vraies ; le modèle rend ces probabilités durcies (température vraie = `sharpen`)."""
    rng = np.random.default_rng(seed)
    logits = rng.normal(size=(n, k)) * 1.5
    true = np.exp(logits) / np.exp(logits).sum(1, keepdims=True)
    y = np.array([rng.choice(k, p=p) for p in true])
    probs = np.exp(sharpen * logits) / np.exp(sharpen * logits).sum(1, keepdims=True)
    return probs, y, rng.integers(0, 5, n), [f"auteur{i % 60}" for i in range(n)]


@pytest.mark.parametrize(("ece", "expected"), [(0.05, "étalonnage transportable"), (0.0501, "partiel"), (0.0799, "partiel"), (0.08, "non transportable")])
def test_le_verdict_suit_les_seuils_ecrits_dans_la_fiche(ece: float, expected: str) -> None:
    assert cal.verdict(ece) == expected


def test_la_lecture_des_auteurs_demande_un_ecart_strictement_superieur_a_deux_centiemes() -> None:
    assert cal.author_reading(0.071, 0.05) == "dépend des auteurs"
    assert cal.author_reading(0.07, 0.05) == "ne dépend pas des auteurs"
    assert cal.author_reading(0.04, 0.06) == "ne dépend pas des auteurs"


def test_la_temperature_transportee_retrouve_la_temperature_vraie_et_reduit_l_ece() -> None:
    probs, y, fold, _ = _overconfident()
    calibrated, temps = cal.transported(probs, y, fold)
    assert len(temps) == 5 and all(2.5 < t < 3.5 for t in temps)
    assert metrics.ece(calibrated, y) < 0.5 * metrics.ece(probs, y)
    assert (calibrated.argmax(1) == probs.argmax(1)).all()


def test_la_temperature_d_un_pli_ne_lit_jamais_les_etiquettes_de_ce_pli() -> None:
    probs, y, fold, _ = _overconfident()
    other = y.copy()
    other[fold == 2] = (other[fold == 2] + 1) % probs.shape[1]
    _, temps = cal.transported(probs, y, fold)
    _, temps_other = cal.transported(probs, other, fold)
    assert temps[2] == pytest.approx(temps_other[2])
    assert temps[0] != pytest.approx(temps_other[0])


def test_l_etalonnage_dans_le_meme_pli_couvre_chaque_patient_une_fois_et_reduit_l_ece() -> None:
    probs, y, fold, _ = _overconfident()
    calibrated = cal.within_fold(probs, y, fold)
    assert calibrated.shape == probs.shape and np.allclose(calibrated.sum(1), 1.0)
    assert metrics.ece(calibrated, y) < 0.5 * metrics.ece(probs, y)


def test_l_intervalle_par_blocs_d_auteurs_est_reproductible_et_encadre_le_point() -> None:
    probs, y, _, groups = _overconfident()
    lo, hi = cal.author_block_interval(probs, y, groups, draws=300)
    assert (lo, hi) == cal.author_block_interval(probs, y, groups, draws=300)
    assert lo < metrics.ece(probs, y) < hi
