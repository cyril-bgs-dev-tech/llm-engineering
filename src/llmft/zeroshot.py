"""Zéro-shot par lettres (RM-30, P1-09) : invite construite depuis le contrat de tâche, probabilités lues sur les lettres de réponse (une seule passe avant par patient)."""
import string
from collections.abc import Sequence

import numpy as np
from numpy.typing import NDArray


def class_letters(n_classes: int) -> list[str]:
    if n_classes > len(string.ascii_uppercase):
        raise ValueError("trop de classes pour des lettres")
    return list(string.ascii_uppercase[:n_classes])


def build_prompt(classes: Sequence[dict[str, str]], document: str) -> str:
    """Invite : liste de lettres avec nom et définition de chaque classe (contrat de tâche), document, consigne de réponse par une seule lettre ; aucun exemple, aucune étiquette."""
    letters = class_letters(len(classes))
    lines = [f"{lt}. {c['name']} : {c['definition']}" for lt, c in zip(letters, classes, strict=True)]
    return (
        "Tu classes des comptes rendus hospitaliers français selon le chapitre CIM-10 du diagnostic principal.\n\nChapitres possibles :\n"
        + "\n".join(lines)
        + f"\n\nCompte rendu :\n{document}\n\nRéponds uniquement par la lettre du chapitre du diagnostic principal ({letters[0]} à {letters[-1]})."
    )


def letter_probs(logits: NDArray[np.floating], letter_token_ids: Sequence[int]) -> NDArray[np.floating]:
    """Softmax restreint aux jetons des lettres de réponse ; logits de la dernière position, forme (n, vocabulaire)."""
    sub = np.asarray(logits, dtype=np.float64)[:, list(letter_token_ids)]
    sub = sub - sub.max(axis=1, keepdims=True)
    e = np.exp(sub)
    return e / e.sum(axis=1, keepdims=True)
