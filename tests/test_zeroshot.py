import numpy as np
import pytest

from llmft import zeroshot


def test_letters_and_prompt_contain_every_class_and_no_label() -> None:
    classes = [{"name": "Chapitre I", "definition": "A00-B99"}, {"name": "Chapitre II", "definition": "C00-D48"}]
    p = zeroshot.build_prompt(classes, "Patient de 60 ans.")
    assert "A. Chapitre I : A00-B99" in p and "B. Chapitre II : C00-D48" in p and "Patient de 60 ans." in p and "(A à B)" in p


def test_too_many_classes_are_refused() -> None:
    with pytest.raises(ValueError):
        zeroshot.class_letters(27)


def test_letter_probs_are_a_softmax_over_the_letter_tokens_only() -> None:
    logits = np.array([[0.0, 10.0, 1.0, 1.0]])
    p = zeroshot.letter_probs(logits, [0, 2, 3])
    assert np.allclose(p.sum(), 1.0) and np.allclose(p, [[1 / (1 + 2 * np.e), np.e / (1 + 2 * np.e), np.e / (1 + 2 * np.e)]])
