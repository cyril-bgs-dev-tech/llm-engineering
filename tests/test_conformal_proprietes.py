"""RM-22 : la prédiction conforme validée au-delà de la proximité des outils, sur des cas synthétiques dont la théorie donne la réponse :
bornes d'échantillon fini, invariants (emboîtement, renumérotation des classes), couverture conditionnelle par famille (Mondrian) et perte de garantie
quand l'échangeabilité est rompue. Données synthétiques déterministes (graines fixes) ; aucun modèle, aucune donnée du corpus."""
import numpy as np
import pytest

from llmft import conformal

ALPHA = 0.1


def _calibrated(rng: np.random.Generator, n: int, k: int = 5) -> tuple[np.ndarray, np.ndarray]:
    """Modèle parfaitement calibré : étiquette tirée de ses propres probabilités, donc exemples échangeables."""
    probs = rng.dirichlet(np.ones(k), size=n)
    y = np.array([rng.choice(k, p=p) for p in probs])
    return probs, y


@pytest.mark.parametrize(("method", "repeats"), [("lac", 400), ("aps", 150)])
def test_la_couverture_moyenne_tient_entre_les_deux_bornes_d_echantillon_fini(method: str, repeats: int) -> None:
    rng = np.random.default_rng(20261017)
    n_cal = n_test = 200
    cov = []
    for _ in range(repeats):
        pc, yc = _calibrated(rng, n_cal)
        pt, yt = _calibrated(rng, n_test)
        cov.append(conformal.evaluate(conformal.predict_sets(pt, conformal.fit(pc, yc, ALPHA, method), method), yt)["coverage"])
    se = np.std(cov) / np.sqrt(repeats)
    assert np.mean(cov) >= 1 - ALPHA - 4 * se
    assert np.mean(cov) <= 1 - ALPHA + 1 / (n_cal + 1) + 4 * se


@pytest.mark.parametrize("method", ["lac", "aps"])
def test_les_ensembles_sont_emboites_quand_alpha_grandit(method: str) -> None:
    rng = np.random.default_rng(1)
    pc, yc = _calibrated(rng, 300)
    pt, _ = _calibrated(rng, 300)
    sets = {a: conformal.predict_sets(pt, conformal.fit(pc, yc, a, method), method) for a in (0.05, 0.1, 0.2, 0.4)}
    for small, large in ((0.05, 0.1), (0.1, 0.2), (0.2, 0.4)):
        assert all(b <= a for a, b in zip(sets[small], sets[large], strict=True))


@pytest.mark.parametrize("method", ["lac", "aps"])
def test_renumeroter_les_classes_renumerote_les_ensembles(method: str) -> None:
    rng = np.random.default_rng(2)
    pc, yc = _calibrated(rng, 300)
    pt, _ = _calibrated(rng, 100)
    perm = rng.permutation(5)  # nouvelle colonne j = ancienne classe perm[j]
    inverse = np.argsort(perm)
    q = conformal.fit(pc, yc, ALPHA, method)
    q_perm = conformal.fit(pc[:, perm], inverse[yc], ALPHA, method)
    assert q_perm == pytest.approx(q)
    original = conformal.predict_sets(pt, q, method)
    relabelled = conformal.predict_sets(pt[:, perm], q_perm, method)
    assert [{int(perm[j]) for j in s} for s in relabelled] == original


def _two_families(rng: np.random.Generator, n: int, hard_share: float = 0.3) -> tuple[np.ndarray, np.ndarray]:
    """Classes 0 et 1 faciles (bien prédites) ; classes 2 et 3 difficiles : le modèle est sûr de lui mais se trompe une fois sur deux entre 2 et 3."""
    probs, y = np.zeros((n, 4)), np.zeros(n, dtype=int)
    for i in range(n):
        if rng.random() < hard_share:
            y[i] = rng.choice([2, 3])
            top = y[i] if rng.random() < 0.5 else 5 - y[i]
        else:
            y[i] = top = rng.choice([0, 1])
        p_top = rng.uniform(0.8, 0.95)
        probs[i] = (1 - p_top) / 3
        probs[i, top] = p_top
    return probs, y


def test_l_etalonnage_par_famille_retablit_la_couverture_d_une_famille_difficile_que_l_etalonnage_marginal_sous_couvre() -> None:
    rng = np.random.default_rng(3)
    families = {0: 0, 1: 0, 2: 1, 3: 1}
    marginal_hard, by_family_hard = [], []
    for _ in range(40):
        pc, yc = _two_families(rng, 1000)
        pt, yt = _two_families(rng, 1000)
        hard = yt >= 2
        hit_marginal = np.array([t in s for s, t in zip(conformal.predict_sets(pt, conformal.fit(pc, yc, ALPHA)), yt, strict=True)])
        q_family = conformal.fit_by_group(pc, yc, families, ALPHA)
        hit_family = np.array([t in s for s, t in zip(conformal.predict_sets_by_group(pt, q_family, families), yt, strict=True)])
        marginal_hard.append(hit_marginal[hard].mean())
        by_family_hard.append(hit_family[hard].mean())
    assert np.mean(marginal_hard) < 0.8
    assert np.mean(by_family_hard) >= 1 - ALPHA - 0.02


def test_la_garantie_tombe_quand_le_test_n_est_plus_echangeable_avec_la_calibration() -> None:
    rng = np.random.default_rng(4)
    cov = []
    for _ in range(100):
        pc, yc = _calibrated(rng, 300)
        pt = rng.dirichlet(np.ones(5), size=300)
        yt = np.array([rng.choice(5, p=0.4 * p + 0.6 / 5) for p in pt])  # même modèle, étiquettes bien plus bruitées qu'à la calibration
        cov.append(conformal.evaluate(conformal.predict_sets(pt, conformal.fit(pc, yc, ALPHA)), yt)["coverage"])
    assert np.mean(cov) < 1 - ALPHA - 0.03


@pytest.mark.parametrize(("alpha", "expected"), [(0.2, 0.9), (0.1, 1.0), (0.5, 0.6), (0.05, float("inf"))])
def test_le_quantile_est_exactement_le_k_ieme_score_avec_k_egal_plafond_de_n_plus_un_fois_un_moins_alpha(alpha: float, expected: float) -> None:
    """Cas analytique : dix scores 0,1 à 1,0 ; k = ceil(11 (1 − α)) ; k > 10 donne un quantile infini (garantie impossible avec dix exemples)."""
    scores = np.arange(1, 11) / 10
    assert conformal.conformal_quantile(scores, alpha) == pytest.approx(expected)
