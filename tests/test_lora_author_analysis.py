"""RM-62 : règles de lecture de la fiche 2026-10-17-lora-fin-aleatoire-plis-auteurs, écrites et testées avant tout run."""
import sys
from pathlib import Path

import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import lora_author_analysis as laa


@pytest.mark.parametrize(("lo", "hi", "expected"), [(2.1, 6.0, "gain confirmé"), (-3.0, 1.9, "absence de gain utile"), (1.0, 5.0, "non résolu"), (2.0, 4.0, "non résolu")])
def test_verdict_a_trois_valeurs_avec_delta_de_deux_points(lo, hi, expected):
    assert laa.verdict(lo, hi) == expected


@pytest.mark.parametrize(("loss", "expected"), [(4.0, "plus faible"), (4.23, "comparable"), (6.23, "comparable"), (6.3, "plus forte")])
def test_la_perte_du_lora_se_lit_contre_celle_de_l_encodeur_a_un_point_pres(loss, expected):
    assert laa.loss_reading(loss) == expected


def test_la_correction_est_repliquee_si_quatre_plis_sur_cinq_perdent_au_plus_cinq_points_sans_la_fin():
    assert laa.correction_label([(0.78, 0.76), (0.77, 0.74), (0.79, 0.75), (0.76, 0.72), (0.78, 0.20)]) == "correction répliquée"
    assert laa.correction_label([(0.78, 0.76), (0.77, 0.70), (0.79, 0.75), (0.76, 0.72), (0.78, 0.20)]) == "non répliquée"


def test_l_etalonnage_croise_par_plis_n_utilise_jamais_le_pli_evalue_et_couvre_pres_du_niveau_vise():
    rng = np.random.default_rng(0)
    n, k = 2000, 4
    t = rng.integers(0, k, n)
    logits = rng.normal(0, 1, (n, k))
    logits[np.arange(n), t] += 1.5
    probs = np.exp(logits) / np.exp(logits).sum(1, keepdims=True)
    split = np.arange(n) % 5
    out = laa.conformal_cross_fit(probs, t, split, {0: 0, 1: 0, 2: 1, 3: 1}, alpha=0.10)
    assert out["marginal"]["couverture"] == pytest.approx(0.90, abs=0.03)
    assert set(out["famille"]["par_famille"]) == {0, 1}
    assert out["famille"]["couverture_minimale_famille"] <= max(v["couverture"] for v in out["famille"]["par_famille"].values())


def test_un_pli_unique_est_refuse_car_il_n_y_aurait_rien_pour_etalonner():
    with pytest.raises(ValueError, match="pli"):
        laa.conformal_cross_fit(np.full((4, 2), 0.5), np.array([0, 1, 0, 1]), np.zeros(4, int), {0: 0, 1: 0}, alpha=0.1)


def test_chaque_etalonnage_exclut_exactement_les_patients_du_pli_evalue(monkeypatch):
    sizes: list[int] = []
    real_fit = laa.conformal.fit

    def spy(probs, t, alpha, method="lac"):
        sizes.append(len(t))
        return real_fit(probs, t, alpha, method)

    monkeypatch.setattr(laa.conformal, "fit", spy)
    split = np.array([0] * 10 + [1] * 20 + [2] * 30)
    probs = np.full((60, 2), 0.5)
    laa.conformal_cross_fit(probs, np.zeros(60, int), split, {0: 0, 1: 0}, alpha=0.1)
    assert sizes == [50, 40, 30]


def test_regle_d_arret_seulement_si_les_deux_premiers_plis_sont_a_plus_de_dix_points_sous_le_tfidf():
    assert laa.early_stop([0.55, 0.56], [0.67, 0.68]) is True
    assert laa.early_stop([0.55, 0.60], [0.67, 0.68]) is False
    assert laa.early_stop([0.57, 0.58], [0.67, 0.68]) is False


def test_pause_si_les_deux_derniers_runs_du_lot_ont_un_tampon_suspect():
    assert laa.health_pause(["ok", "suspect", "suspect"]) is True
    assert laa.health_pause(["suspect", "ok"]) is False
    assert laa.health_pause(["suspect"]) is False
    assert laa.health_pause(["suspect", "absent"]) is True  # un tampon manquant ne vaut pas un tampon sain


def test_le_controle_de_sante_lit_le_run_d_entrainement_et_pas_celui_de_robustesse_du_meme_pli():
    names = ["20261018-010000-lora-fin-aleatoire-auteur-pli0.json", "20261018-040000-robustesse-lora-diagnostic-fin-retiree-lora-fin-aleatoire-auteur-pli0.json"]
    assert laa.training_runs(names, "lora-fin-aleatoire-auteur-pli0") == ["20261018-010000-lora-fin-aleatoire-auteur-pli0.json"]


def test_une_perte_d_exactement_cinq_points_compte_comme_repliquee_malgre_l_arrondi_binaire():
    """Trouvé par mutation le 17/10 : 0,7800 − 0,7300 vaut 5,000000000000004 points en flottant ; la fiche dit « au plus 5,0 points »."""
    assert laa.correction_label([(0.78, 0.73), (0.78, 0.73), (0.78, 0.73), (0.78, 0.73), (0.78, 0.20)]) == "correction répliquée"
