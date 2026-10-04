import pytest

from llmft import augment

IDS = ["a1", "a2", "b1", "b2", "c1"]
LABELS = {"a1": "A", "a2": "A", "b1": "B", "b2": "B", "c1": "C"}


def test_duplication_plan_repeats_only_target_classes() -> None:
    plan = augment.duplication_plan(IDS, LABELS, targets={"B", "C"}, factor=3)
    assert plan.count("b1") == 3 and plan.count("b2") == 3 and plan.count("c1") == 3
    assert plan.count("a1") == 1 and plan.count("a2") == 1


def test_duplication_factor_one_is_the_identity() -> None:
    assert sorted(augment.duplication_plan(IDS, LABELS, targets={"B"}, factor=1)) == sorted(IDS)


def test_synthetic_records_are_accepted_only_with_training_sources() -> None:
    good = [{"id": "g1", "source_id": "b1", "label": "B", "text": "texte"}]
    assert augment.validated_synthetic(good, train_ids=set(IDS), targets={"B"}) == good
    with pytest.raises(ValueError, match="source"):
        augment.validated_synthetic([{"id": "g2", "source_id": "zz", "label": "B", "text": "x"}], train_ids=set(IDS), targets={"B"})


def test_synthetic_label_must_match_its_source_and_be_a_target_class() -> None:
    with pytest.raises(ValueError, match="étiquette"):
        augment.validated_synthetic([{"id": "g3", "source_id": "b1", "label": "A", "text": "x"}], train_ids=set(IDS), targets={"A", "B"}, label_of=LABELS)
    with pytest.raises(ValueError, match="cible"):
        augment.validated_synthetic([{"id": "g4", "source_id": "a1", "label": "A", "text": "x"}], train_ids=set(IDS), targets={"B"}, label_of=LABELS)


def test_copy_of_a_validation_text_is_detected() -> None:
    val = {"v1": "le patient est hospitalisé pour une douleur thoracique avec dyspnée et fièvre depuis trois jours"}
    synth = {"g1": "le patient est hospitalisé pour une douleur thoracique avec dyspnée et fièvre depuis trois jours", "g2": "tout autre texte sans rapport avec le premier"}
    assert augment.copies_of_validation(synth, val, threshold=0.8) == ["g1"]
