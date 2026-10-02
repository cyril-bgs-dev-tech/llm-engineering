"""Bibliothèque anti-fuite (P0-40) : chaque contrôle détecte un cas piégé volontairement."""
import pytest

from llmft import leakage

BASE = "Compte rendu d'hospitalisation. Patient de soixante ans admis pour pneumopathie aiguë communautaire, antibiothérapie, évolution favorable. " * 3


def test_normalize_ignores_case_punctuation_and_spacing():
    assert leakage.normalize("  Bonjour,  MONDE !\n") == leakage.normalize("bonjour monde")


def test_near_duplicates_are_found_even_when_slightly_edited():
    texts = {"a": BASE, "b": BASE.replace("soixante", "soixante-deux"), "c": "Texte tout à fait différent sur une fracture du poignet traitée chirurgicalement."}
    pairs = leakage.near_duplicate_pairs(texts, threshold=0.8)
    assert [(i, j) for i, j, _ in pairs] == [("a", "b")]


def test_clusters_group_transitive_duplicates():
    c = leakage.clusters(["a", "b", "c", "d"], [("a", "b", 0.9), ("b", "c", 0.85)])
    assert c["a"] == c["b"] == c["c"] != c["d"]


def test_cross_partition_pairs_flags_a_leak_and_ignores_same_partition():
    pairs = [("a", "b", 0.9), ("a", "c", 0.9)]
    part = {"a": "test", "b": "fold0", "c": "test"}
    assert leakage.cross_partition_pairs(pairs, part) == [("a", "b", 0.9)]


def test_out_of_fold_check_catches_a_teacher_that_saw_the_example():
    fold_of = {"x": 0, "y": 1}
    teacher_trained_on = {"x": {1, 2, 3, 4}, "y": {1, 2}}  # y a été vu par le professeur du pli 1
    problems = leakage.check_out_of_fold(fold_of, teacher_trained_on)
    assert len(problems) == 1 and "y" in problems[0]
    assert leakage.check_out_of_fold(fold_of, {"x": {1, 2}, "y": {0, 2}}) == []


def test_synthetic_examples_must_come_from_training_sources():
    generated = [{"id": "g1", "source_id": "t1"}, {"id": "g2", "source_id": "v9"}]
    problems = leakage.check_synthetic_sources(generated, train_ids={"t1", "t2"})
    assert problems == ["g2 : source v9 hors de l'entraînement"]
    assert leakage.check_synthetic_sources([{"id": "g3"}], {"t1"}) == ["g3 : source inconnue"]


def test_threshold_is_part_of_the_signature_and_never_silently_relaxed():
    assert leakage.NEAR_DUPLICATE_THRESHOLD == pytest.approx(0.8)
