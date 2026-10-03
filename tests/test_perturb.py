import random

from llmft.perturb import PERTURBATIONS, drop_accents, swap_typos, uppercase_abbreviations


def test_drop_accents_removes_diacritics_and_keeps_length_of_words() -> None:
    assert drop_accents("Hôpital été à jeun", random.Random(0)) == "Hopital ete a jeun"


def test_swap_typos_is_deterministic_for_a_seed_and_preserves_characters() -> None:
    text = "patient hospitalisé pour douleur thoracique " * 20
    a = swap_typos(text, random.Random(7))
    b = swap_typos(text, random.Random(7))
    assert a == b
    assert a != text
    assert sorted(a) == sorted(text)


def test_swap_typos_leaves_short_words_alone() -> None:
    assert swap_typos("il y a eu", random.Random(1)) == "il y a eu"


def test_uppercase_abbreviations_only_changes_case() -> None:
    text = "Compte rendu du service de cardiologie"
    out = uppercase_abbreviations(text, random.Random(3))
    assert out.lower() == text.lower()


def test_registry_lists_all_perturbations() -> None:
    assert set(PERTURBATIONS) == {"accents", "typos", "casse"}
