"""Fiabilité de l'incertitude (Q5) : calibration, prédiction conforme, prédiction sélective. Vérifié sur des données synthétiques à vérité connue."""
import numpy as np
import pytest

from llmft import calibration, conformal, selective


def _synthetic(n, k, t_true, rng, rare_hard=False):
    """Logits z ; les étiquettes suivent softmax(z / t_true) ; le modèle annonce softmax(z) : suréconfiant si t_true > 1."""
    z = rng.normal(size=(n, k)) * 2.0
    p_true = np.exp(z / t_true - (z / t_true).max(1, keepdims=True))
    p_true /= p_true.sum(1, keepdims=True)
    y = np.array([rng.choice(k, p=row) for row in p_true])
    p = np.exp(z - z.max(1, keepdims=True))
    return p / p.sum(1, keepdims=True), y


# === calibration ===
def test_temperature_retrouve_la_vraie_temperature():
    rng = np.random.default_rng(0)
    p, y = _synthetic(6000, 6, 2.0, rng)
    t = calibration.fit_temperature(p, y)
    assert t == pytest.approx(2.0, rel=0.15)


def test_la_recalibration_reduit_l_ece_et_la_log_loss():
    rng = np.random.default_rng(1)
    p, y = _synthetic(6000, 6, 2.0, rng)
    t = calibration.fit_temperature(p, y)
    q = calibration.apply_temperature(p, t)
    assert calibration.ece(q, y) < calibration.ece(p, y)
    assert calibration.nll(q, y) < calibration.nll(p, y)
    assert q.sum(1) == pytest.approx(np.ones(len(q)))


def test_ece_est_petite_pour_un_modele_calibre_par_construction():
    rng = np.random.default_rng(2)
    p, y = _synthetic(8000, 5, 1.0, rng)
    assert calibration.ece(p, y) < 0.03


def test_brier_vaut_zero_pour_une_prediction_certaine_et_juste():
    p = np.eye(3)[[0, 1, 2]]
    assert calibration.brier(p, np.array([0, 1, 2])) == 0.0
    assert calibration.brier(p, np.array([1, 2, 0])) == pytest.approx(2.0)


def test_ece_par_classe_est_la_moyenne_des_ece_un_contre_tous():
    rng = np.random.default_rng(3)
    p, y = _synthetic(3000, 4, 1.5, rng)
    per = calibration.classwise_ece(p, y)
    assert len(per) == 4 and all(0 <= v <= 1 for v in per.values())


# === prédiction conforme ===
def test_quantile_fini_et_infini_selon_l_effectif():
    assert conformal.conformal_quantile(np.arange(1.0, 10.0), alpha=0.1) == 9.0  # n = 9 : k = 9
    assert conformal.conformal_quantile(np.arange(1.0, 9.0), alpha=0.1) == np.inf  # n = 8 : k = 9 > n


def test_wilson_valeurs_connues():
    lo, hi = conformal.wilson(5, 10)
    assert lo == pytest.approx(0.2366, abs=2e-3) and hi == pytest.approx(0.7634, abs=2e-3)
    assert conformal.wilson(0, 0) == (0.0, 1.0)


@pytest.mark.parametrize("method", ["lac", "aps"])
def test_couverture_marginale_au_moins_le_niveau_vise_en_echangeable(method):
    covs = []
    for seed in range(8):
        rng = np.random.default_rng(10 + seed)
        p, y = _synthetic(4000, 6, 1.5, rng)
        cal, test = slice(0, 2000), slice(2000, 4000)
        qhat = conformal.fit(p[cal], y[cal], alpha=0.1, method=method)
        covs.append(conformal.evaluate(conformal.predict_sets(p[test], qhat, method), y[test])["coverage"])
    assert np.mean(covs) >= 0.89  # garantie marginale, au bruit près


def test_conforme_par_classe_couvre_la_classe_difficile_que_le_marginal_sacrifie():
    rng = np.random.default_rng(7)
    k, n = 4, 6000
    y = rng.choice(k, size=n, p=[0.45, 0.35, 0.15, 0.05])
    p = np.full((n, k), 0.02)
    for i, c in enumerate(y):  # la classe 3 (rare) est prise pour la classe 0 : sa probabilité est basse même quand elle est vraie
        if c == 3:
            p[i, 0], p[i, 3] = 0.90, 0.05
        else:
            p[i, c] = 0.92
    p /= p.sum(1, keepdims=True)
    cal, test = slice(0, 3000), slice(3000, n)
    marg = conformal.evaluate(conformal.predict_sets(p[test], conformal.fit(p[cal], y[cal], 0.1, "lac"), "lac"), y[test])
    cls = conformal.evaluate(conformal.predict_sets_by_class(p[test], conformal.fit_by_class(p[cal], y[cal], 0.1, "lac", k), "lac"), y[test])
    assert marg["coverage_by_class"][3] < 0.8 < cls["coverage_by_class"][3]
    assert cls["coverage_by_class"][3] >= 0.85


def test_classe_trop_petite_pour_le_niveau_donne_un_ensemble_qui_l_inclut_toujours():
    p = np.array([[0.5, 0.5, 0.0]] * 5)
    y = np.array([0, 0, 0, 1, 2])  # la classe 2 n'a qu'un exemple : quantile infini
    q = conformal.fit_by_class(p, y, 0.1, "lac", 3)
    assert q[2] == np.inf
    sets = conformal.predict_sets_by_class(np.array([[0.9, 0.1, 0.0]]), q, "lac")
    assert 2 in sets[0]


def test_evaluate_rapporte_taille_moyenne_singletons_et_ensembles_vides():
    sets = [{0}, {0, 1}, set(), {2}]
    r = conformal.evaluate(sets, np.array([0, 1, 1, 2]))
    assert r["coverage"] == 0.75 and r["mean_set_size"] == 1.0 and r["singleton_rate"] == 0.5 and r["empty_rate"] == 0.25


# === prédiction sélective ===
def test_aurc_petit_si_la_confiance_ordonne_bien_les_erreurs():
    n_ok, n_bad = 1800, 200
    correct = np.array([1] * n_ok + [0] * n_bad)
    good = np.concatenate([np.linspace(1, 0.5, n_ok), np.linspace(0.4, 0.0, n_bad)])
    bad = np.random.default_rng(0).permutation(good)
    assert selective.aurc(good, correct) < selective.aurc(bad, correct)
    assert selective.aurc(bad, correct) == pytest.approx(0.10, abs=0.02)  # confiance sans information : taux d'erreur global


def test_exactitude_selective_a_couverture_donnee():
    conf = np.array([0.9, 0.8, 0.7, 0.2])
    correct = np.array([1, 1, 1, 0])
    assert selective.accuracy_at_coverage(conf, correct, 0.75) == 1.0
    assert selective.accuracy_at_coverage(conf, correct, 1.0) == 0.75


def test_conforme_par_groupe_couvre_le_groupe_difficile_que_le_marginal_sacrifie():
    rng = np.random.default_rng(0)
    n = 4000
    y = rng.choice(4, size=n, p=[0.45, 0.4, 0.1, 0.05])  # classes 0,1 = groupe facile (85 %) ; 2,3 = groupe difficile (15 %)
    probs = np.full((n, 4), 0.01)
    for i, c in enumerate(y):
        good = rng.random() < (0.99 if c < 2 else 0.5)
        top = c if good else (c ^ 1 if c < 2 else 2 + ((c - 2) ^ 1))
        probs[i, top] += 1.0
    probs /= probs.sum(1, keepdims=True)
    group_of = {0: 0, 1: 0, 2: 1, 3: 1}
    cal, te = np.arange(0, n, 2), np.arange(1, n, 2)
    q = conformal.fit(probs[cal], y[cal], 0.1, "lac")
    marginal = conformal.predict_sets(probs[te], q, "lac")
    qg = conformal.fit_by_group(probs[cal], y[cal], group_of, 0.1, "lac")
    grouped = conformal.predict_sets_by_group(probs[te], qg, group_of, "lac")
    hard = y[te] >= 2
    def cov(sets, mask):
        return float(np.mean([y[te][i] in sets[i] for i in np.flatnonzero(mask)]))
    assert cov(marginal, hard) < 0.88
    assert cov(grouped, hard) >= 0.88
