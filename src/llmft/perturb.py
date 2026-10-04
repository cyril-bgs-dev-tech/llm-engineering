"""Perturbations de texte pour l'analyse de robustesse (audit GLM C5-A4). Elles ne touchent que le texte, jamais l'étiquette."""
import random
import unicodedata
from collections.abc import Callable

TYPO_RATE = 0.05


def drop_accents(text: str, rng: random.Random) -> str:
    del rng
    return "".join(c for c in unicodedata.normalize("NFD", text) if unicodedata.category(c) != "Mn")


def swap_typos(text: str, rng: random.Random) -> str:
    """Échange deux lettres adjacentes à l'intérieur de 5 % des mots d'au moins 5 lettres."""
    words = text.split(" ")
    for i, w in enumerate(words):
        if len(w) >= 5 and rng.random() < TYPO_RATE:
            j = rng.randrange(1, len(w) - 2)
            words[i] = w[:j] + w[j + 1] + w[j] + w[j + 2 :]
    return " ".join(words)


def uppercase_abbreviations(text: str, rng: random.Random) -> str:
    """Met en majuscules 5 % des mots, comme le font des saisies pressées."""
    return " ".join(w.upper() if rng.random() < TYPO_RATE else w for w in text.split(" "))


PERTURBATIONS: dict[str, Callable[[str, random.Random], str]] = {"accents": drop_accents, "typos": swap_typos, "casse": uppercase_abbreviations}


def _drop_tail(text: str, rng: random.Random) -> str:
    del rng
    words = text.split(" ")
    return " ".join(words[: max(1, round(0.7 * len(words)))])


def _drop_head(text: str, rng: random.Random) -> str:
    del rng
    words = text.split(" ")
    return " ".join(words[round(0.3 * len(words)) :]) if len(words) > 1 else text


# Ablations de contenu (la conclusion et le diagnostic sont souvent en fin de compte rendu) : même interface, évaluées avec les mêmes scripts que les perturbations de forme
ABLATIONS: dict[str, Callable[[str, random.Random], str]] = {"fin_retiree_30pct": _drop_tail, "debut_retire_30pct": _drop_head}
