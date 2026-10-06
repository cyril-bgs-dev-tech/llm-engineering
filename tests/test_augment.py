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


def test_coupe_de_fin_aleatoire_garde_le_debut_et_retire_au_plus_la_fraction_maximale():
    import random

    from llmft.augment import random_tail_cut

    text = " ".join(f"mot{i}" for i in range(100)) + "\n"
    rng = random.Random(0)
    cuts = [random_tail_cut(text, rng, probability=1.0, max_fraction=0.5) for _ in range(200)]
    assert all(c != text and text.startswith(c[: len(c)]) for c in cuts)
    kept = [len(c.split(" ")) for c in cuts]
    assert min(kept) >= 50 and max(kept) <= 95  # entre 5 % et 50 % des mots retirés


def test_coupe_de_fin_aleatoire_ne_touche_pas_un_texte_avec_probabilite_nulle():
    import random

    from llmft.augment import random_tail_cut

    text = "a b c d e f g h\n"
    assert random_tail_cut(text, random.Random(1), probability=0.0, max_fraction=0.5) == text


def test_coupe_de_fin_aleatoire_respecte_la_probabilite_en_moyenne():
    import random

    from llmft.augment import random_tail_cut

    text = " ".join(str(i) for i in range(40)) + "\n"
    rng = random.Random(2)
    changed = sum(random_tail_cut(text, rng, probability=0.3, max_fraction=0.5) != text for _ in range(2000))
    assert 500 < changed < 700  # 0,3 sur 2 000 tirages


def test_coupe_de_fin_aleatoire_ne_vide_jamais_un_texte_court():
    import random

    from llmft.augment import random_tail_cut

    rng = random.Random(3)
    for text in ("seul\n", "deux mots\n", ""):
        assert random_tail_cut(text, rng, probability=1.0, max_fraction=0.5).strip() != "" or text == ""
