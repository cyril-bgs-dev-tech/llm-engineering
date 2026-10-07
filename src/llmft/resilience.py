"""Tolérance aux pannes internes sporadiques de la machine (observées les 05 et 06/10/2026 : TypeError impossibles en Python correct dans scikit-learn, segfaults du tokenizer).

Hypothèse de travail, non prouvée : instabilité matérielle intermittente (processeur ou mémoire). Deux outils, qui ne masquent aucun défaut du code :
- `retry_transient` relance un calcul seulement sur une signature d'erreur connue comme impossible en Python correct, chaque essai consigné ; toute autre erreur est levée aussitôt ;
- `agree_twice` exécute deux fois un calcul qui produit un chiffre publié et refuse un désaccord (avec un troisième essai optionnel pour départager), car une panne sans exception donnerait un résultat faux sans signal."""
from collections.abc import Callable
from typing import Any, TypeVar

T = TypeVar("T")

TRANSIENT_SIGNATURES = (
    "'NoneType' and 'int'",  # `offset = 0` puis `offset + n` avec offset à None (sklearn, _char_wb_ngrams)
    "'list_iterator' object cannot be interpreted as an integer",  # `values.extend(dict.values())` (sklearn, _count_vocab)
    "'builtin_function_or_method' and 'str'",  # observée au test de charge du 07/10 (run `stress-tfidf-par-coeur`), même famille : opérandes impossibles dans sklearn
    "'list_iterator' and 'int'",  # `feature_counter[feature_idx] += 1` avec une valeur corrompue (sklearn, _count_vocab), observée le 07/10 à 12:30Z pendant une rafale de segfaults
    "'int' and 'str'",  # idem ; un vrai défaut de cette forme échoue de façon identique à chaque essai et finit en RuntimeError après les essais bornés
)


class ResultMismatchError(RuntimeError):
    """Deux exécutions du même calcul ne donnent pas le même résultat : aucune n'est crue."""


def _print(message: str) -> None:
    print(f"[resilience] {message}", flush=True)


def retry_transient(fn: Callable[[], T], *, attempts: int = 3, log: Callable[[str], None] = _print) -> T:
    last: Exception | None = None
    for attempt in range(1, attempts + 1):
        try:
            return fn()
        except TypeError as exc:
            if not any(sig in str(exc) for sig in TRANSIENT_SIGNATURES):
                raise
            last = exc
            log(f"essai {attempt}/{attempts} : panne interne connue ({exc})")
    raise RuntimeError(f"calcul impossible après {attempts} essais : {last}") from last


def agree_twice(fn: Callable[[], T], *, equal: Callable[[Any, Any], bool], attempts: int = 2, log: Callable[[str], None] = _print) -> T:
    """Rend le résultat si deux exécutions concordent ; avec `attempts=3`, une troisième départage (deux sur trois identiques) ; sinon ResultMismatchError."""
    results: list[T] = []
    for _ in range(attempts):
        results.append(retry_transient(fn, log=log))
        for earlier in results[:-1]:
            if equal(earlier, results[-1]):
                return earlier
    log(f"{len(results)} exécutions sans deux résultats identiques")
    raise ResultMismatchError(f"{len(results)} exécutions du même calcul, aucun couple identique")
