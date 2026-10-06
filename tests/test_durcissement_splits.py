import numpy as np
import pandas as pd
import pytest

from llmft import splits


def _df(counts: dict[str, int]) -> pd.DataFrame:
    labels = [c for c, n in counts.items() for _ in range(n)]
    return pd.DataFrame({"id": [f"P{i}" for i in range(len(labels))], "author": "a", "label": labels})


def test_rare_class_policy_keeps_a_class_with_exactly_the_minimum():
    out = splits.apply_rare_class_policy(pd.Series(["a"] * 30 + ["b"] * 20 + ["c"] * 19), min_count=20)
    assert out.value_counts().to_dict() == {"a": 30, "b": 20, "AUTRE": 19}


def test_a_small_class_missing_from_the_test_is_flagged_with_the_test_minimum():
    df = _df({"big": 100, "small": 10})
    ids_small = list(df[df.label == "small"].id)
    ids_big = list(df[df.label == "big"].id)
    s = splits.Splits(1, test=ids_big[:15] + ids_small[:2], folds=[ids_big[15 + 17 * k : 15 + 17 * (k + 1)] + ids_small[2 + k : 3 + k] for k in range(5)])
    msgs = splits.check_tolerance(df, s)
    assert "test : classe small a 2 patients, minimum 3" in msgs


def test_a_small_class_missing_from_a_dev_fold_is_flagged_with_the_fold_minimum():
    df = _df({"big": 100, "small": 10})
    ids_small = list(df[df.label == "small"].id)
    ids_big = list(df[df.label == "big"].id)
    folds = [ids_big[15 + 17 * k : 15 + 17 * (k + 1)] + ids_small[3 + k : 4 + k] for k in range(5)]
    folds[0] = folds[0][:-1]  # le pli 0 n'a plus aucun patient de la petite classe
    s = splits.Splits(1, test=ids_big[:15] + ids_small[:3], folds=folds)
    msgs = splits.check_tolerance(df, s)
    assert "pli 0 : classe small a 0 patients, minimum 2" in msgs


def test_a_class_of_exactly_fifty_patients_is_checked_by_proportion_not_by_minimum():
    df = _df({"big": 150, "edge": 50})
    ids = {c: list(df[df.label == c].id) for c in ("big", "edge")}
    # 'edge' = 25 % des patients ; le pli 0 en contient 0 sur 40 patients : écart relatif 100 %
    s = splits.Splits(1, test=ids["big"][:30] + ids["edge"][:10], folds=[ids["big"][30:70], *[ids["big"][70 + 20 * k : 90 + 20 * k] + ids["edge"][10 + 8 * k : 18 + 8 * k] for k in range(4)]])
    assert any(m.startswith("pli 0 : classe edge a 0 patients pour") for m in splits.check_tolerance(df, s))


def test_a_deficit_is_flagged_as_well_as_an_excess():
    df = _df({"A": 100, "B": 100})
    a, b = list(df[df.label == "A"].id), list(df[df.label == "B"].id)
    s = splits.Splits(1, test=a[:15] + b[:15], folds=[a[15:55] + b[15:25], a[55:70] + b[25:55], a[70:85] + b[55:70], a[85:100] + b[70:85], b[85:100]])
    msgs = splits.check_tolerance(df, s)
    assert any("pli 0 : classe B" in m for m in msgs)  # déficit de B (10 pour 20 attendus)
    assert any("pli 1 : classe A" in m for m in msgs)  # déficit de A (15 pour 20 attendus)


@pytest.mark.parametrize("seed", [3, 4, 5, 6])
def test_every_class_share_is_preserved_in_test_and_dev_folds_within_one_patient(seed):
    rng = np.random.default_rng(seed)
    labels = rng.choice(list("ABCDE"), size=1000, p=[0.4, 0.25, 0.2, 0.1, 0.05])
    df = pd.DataFrame({"id": [f"P{i}" for i in range(1000)], "author": rng.choice([f"a{j}" for j in range(40)], 1000), "label": labels})
    s = splits.make_splits(df, seed)
    lab = df.set_index("id").label
    total = lab.value_counts()
    for c, n in total.items():
        assert abs((lab[s.test] == c).sum() - 0.15 * n) <= 1.01
        for f in s.folds:
            assert abs((lab[f] == c).sum() - 0.17 * n) <= 1.5  # 5 plis d'un développement à 85 %


def test_the_split_hash_does_not_depend_on_the_order_of_ids_inside_partitions():
    a = splits.Splits(1, ["b", "a"], [["d", "c"], ["f", "e"]], [["d", "c"]])
    b = splits.Splits(1, ["a", "b"], [["c", "d"], ["e", "f"]], [["c", "d"]])
    assert a.sha256() == b.sha256()


def test_the_overlap_check_reports_a_duplicate_inside_one_fold():
    assert splits.check_no_overlap(splits.Splits(1, ["t"], [["a", "a"], ["b"]])) == ["a"]


def test_one_author_cannot_be_split_into_five_control_folds():
    df = _df({"A": 60, "B": 40})
    with pytest.raises(ValueError, match="n_splits"):
        splits.make_splits(df, 1)
