import numpy as np

from llmft import cascade
from llmft.cascade import cascade_probs, choose_threshold


def test_cascade_keeps_confident_first_answers_and_escalates_the_rest() -> None:
    first = np.array([[0.9, 0.1], [0.55, 0.45]])
    second = np.array([[0.2, 0.8], [0.1, 0.9]])
    probs, keep = cascade_probs(first, second, 0.8)
    assert keep.tolist() == [True, False] and np.allclose(probs, [[0.9, 0.1], [0.1, 0.9]])


def test_threshold_is_the_smallest_one_within_tolerance_of_the_second_model() -> None:
    truth = np.array([0, 0, 1, 1])
    first = np.array([[0.95, 0.05], [0.6, 0.4], [0.9, 0.1], [0.3, 0.7]])  # faux sur le 3e cas, confiant
    second = np.array([[0.9, 0.1], [0.8, 0.2], [0.1, 0.9], [0.2, 0.8]])  # parfait

    def accuracy(p: np.ndarray) -> float:
        return float((p.argmax(1) == truth).mean())

    assert choose_threshold(first, second, accuracy, [0.5, 0.7, 0.99], tolerance=0.0) == 0.99
    assert choose_threshold(first, second, accuracy, [0.5, 0.7], tolerance=0.0) is None
    assert choose_threshold(first, second, accuracy, [0.5, 0.7], tolerance=0.3) == 0.5


def test_conformal_routing_keeps_only_singleton_sets_for_the_first_model() -> None:
    from llmft.cascade import route_by_set_size

    first = np.array([[0.9, 0.1], [0.5, 0.5], [0.6, 0.4]])
    second = np.array([[0.1, 0.9], [0.2, 0.8], [0.3, 0.7]])
    sets = [{0}, {0, 1}, set()]  # singleton, deux classes, ensemble vide
    probs, keep = route_by_set_size(sets, first, second)
    assert keep.tolist() == [True, False, False]
    assert np.allclose(probs, [[0.9, 0.1], [0.2, 0.8], [0.3, 0.7]])


def test_le_seuil_par_fidelite_est_le_plus_petit_qui_garde_la_classe_du_second_modele():
    # trois patients : le premier modèle est sûr et d'accord (0), sûr mais en désaccord à 0,65 (1), peu sûr (2)
    first = np.array([[0.9, 0.1], [0.65, 0.35], [0.55, 0.45]])
    second = np.array([[0.8, 0.2], [0.2, 0.8], [0.3, 0.7]])
    # τ = 0,5 : le premier répond partout, 1 accord sur 3 ; τ = 0,6 : le patient 2 passe au second, 2 sur 3 ; τ = 0,7 : 3 sur 3
    assert cascade.choose_threshold_by_agreement(first, second, grid=(0.5, 0.6, 0.7, 0.8), min_agreement=0.98) == 0.7
    assert cascade.choose_threshold_by_agreement(first, second, grid=(0.5, 0.6, 0.7, 0.8), min_agreement=0.6) == 0.6


def test_le_seuil_par_fidelite_renvoie_none_si_aucun_seuil_de_la_grille_ne_suffit():
    first = np.array([[0.99, 0.01], [0.99, 0.01]])
    second = np.array([[0.2, 0.8], [0.2, 0.8]])
    assert cascade.choose_threshold_by_agreement(first, second, grid=(0.5, 0.9), min_agreement=0.5) is None


def test_la_grille_est_parcourue_dans_l_ordre_croissant_quel_que_soit_l_ordre_donne():
    first = np.array([[0.9, 0.1], [0.65, 0.35]])
    second = np.array([[0.8, 0.2], [0.2, 0.8]])
    assert cascade.choose_threshold_by_agreement(first, second, grid=(0.8, 0.5, 0.7), min_agreement=1.0) == 0.7
