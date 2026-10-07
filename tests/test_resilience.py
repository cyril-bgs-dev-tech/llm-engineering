import numpy as np
import pytest

from llmft import resilience

SIGNATURE_ERROR = TypeError("unsupported operand type(s) for +: 'NoneType' and 'int'")


def flaky(failures: int, error: Exception = SIGNATURE_ERROR):
    state = {"calls": 0}

    def fn() -> int:
        state["calls"] += 1
        if state["calls"] <= failures:
            raise error
        return 42

    return fn, state


def test_une_panne_interne_connue_est_relancee_puis_le_resultat_est_rendu():
    fn, state = flaky(2)
    assert resilience.retry_transient(fn, attempts=3, log=lambda _: None) == 42
    assert state["calls"] == 3


def test_une_erreur_de_type_inconnue_n_est_jamais_relancee():
    fn, state = flaky(1, TypeError("autre message : un vrai défaut"))
    with pytest.raises(TypeError, match="vrai défaut"):
        resilience.retry_transient(fn, attempts=3, log=lambda _: None)
    assert state["calls"] == 1


def test_apres_le_dernier_essai_l_erreur_est_levee_avec_le_nombre_d_essais():
    fn, state = flaky(5)
    with pytest.raises(RuntimeError, match="3 essais"):
        resilience.retry_transient(fn, attempts=3, log=lambda _: None)
    assert state["calls"] == 3


def test_chaque_essai_est_consigne():
    fn, _ = flaky(2)
    seen: list[str] = []
    resilience.retry_transient(fn, attempts=3, log=seen.append)
    assert len(seen) == 2 and all("essai" in line for line in seen)


def test_deux_executions_identiques_rendent_la_premiere():
    values = iter([np.array([1.0, 2.0]), np.array([1.0, 2.0])])
    assert np.array_equal(resilience.agree_twice(lambda: next(values), equal=np.array_equal, log=lambda _: None), np.array([1.0, 2.0]))


def test_deux_executions_qui_different_sont_refusees_au_lieu_de_choisir():
    values = iter([np.array([1.0, 2.0]), np.array([1.0, 2.5])])
    with pytest.raises(resilience.ResultMismatchError):
        resilience.agree_twice(lambda: next(values), equal=np.array_equal, log=lambda _: None)


def test_un_resultat_corrompu_en_premiere_execution_est_detecte_par_la_seconde():
    outputs = iter([[0.1, 0.9], [0.1, 0.8], [0.1, 0.9]])
    result = resilience.agree_twice(lambda: next(outputs), equal=lambda a, b: a == b, log=lambda _: None, attempts=3)
    assert result == [0.1, 0.9]  # la troisième exécution départage : deux sur trois identiques


@pytest.mark.parametrize("message", [
    "unsupported operand type(s) for +: 'builtin_function_or_method' and 'str'",
    "unsupported operand type(s) for +: 'int' and 'str'",
])
def test_les_signatures_observees_au_test_de_charge_du_07_10_sont_relancees(message):
    fn, state = flaky(1, TypeError(message))
    assert resilience.retry_transient(fn, attempts=3, log=lambda _: None) == 42
    assert state["calls"] == 2
