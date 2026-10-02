"""Découpages par patient (P0-28, P0-29) : aucune fuite entre partitions, déterminisme, tolérance de déséquilibre."""
import numpy as np
import pandas as pd

from llmft import splits


def toy(n=900, n_authors=40, seed=1):
    rng = np.random.default_rng(seed)
    labels = rng.choice(["A", "B", "C", "D"], size=n, p=[0.5, 0.3, 0.15, 0.05])
    return pd.DataFrame({"id": [f"P{i:04d}" for i in range(n)], "author": rng.choice([f"a{j:02d}" for j in range(n_authors)], size=n), "label": labels})


def test_apply_rare_class_policy_merges_small_classes_into_autre():
    labels = pd.Series(["X"] * 30 + ["Y"] * 25 + ["R1"] * 4 + ["R2"] * 10)
    out = splits.apply_rare_class_policy(labels, min_count=20)
    assert set(out) == {"X", "Y", "AUTRE"}
    assert (out == "AUTRE").sum() == 14


def test_no_patient_in_two_partitions():
    s = splits.make_splits(toy(), seed=7)
    parts = [set(s.test)] + [set(f) for f in s.folds]
    assert sum(len(p) for p in parts) == len(set().union(*parts)) == 900


def test_test_set_is_fifteen_percent_and_stratified():
    df = toy()
    s = splits.make_splits(df, seed=7)
    assert abs(len(s.test) / len(df) - 0.15) < 0.01
    assert splits.check_tolerance(df, s) == []


def test_control_folds_never_share_an_author():
    df = toy()
    s = splits.make_splits(df, seed=7)
    author = df.set_index("id").author
    seen: dict[str, int] = {}
    for k, fold in enumerate(s.control_folds):
        for a in set(author[fold]):
            assert seen.setdefault(a, k) == k, f"auteur {a} dans deux plis de contrôle"


def test_control_folds_cover_exactly_the_development_patients():
    s = splits.make_splits(toy(), seed=7)
    dev = set().union(*map(set, s.folds))
    assert dev == set().union(*map(set, s.control_folds))
    assert not (dev & set(s.test))


def test_same_seed_same_split_and_other_seed_differs():
    df = toy()
    a, b, c = splits.make_splits(df, 7), splits.make_splits(df, 7), splits.make_splits(df, 8)
    assert a.to_json() == b.to_json()
    assert a.to_json() != c.to_json()


def test_sha256_changes_when_the_split_changes():
    df = toy()
    assert splits.make_splits(df, 7).sha256() != splits.make_splits(df, 8).sha256()


def test_tolerance_check_flags_an_unbalanced_fold():
    df = toy()
    s = splits.make_splits(df, seed=7)
    lab = df.set_index("id").label
    a_ids = [i for i in s.folds[0] if lab[i] == "A"]
    s.folds[1].extend(a_ids)  # on déséquilibre volontairement un pli (et on crée un doublon)
    s.folds[0] = [i for i in s.folds[0] if i not in set(a_ids)]
    assert splits.check_tolerance(df, s)


def test_overlap_check_detects_a_leak():
    s = splits.make_splits(toy(), seed=7)
    s.folds[0].append(s.test[0])
    assert splits.check_no_overlap(s)


def test_clusters_of_near_duplicates_are_never_split_across_partitions():
    df = toy(n=900)
    df["cluster"] = [i // 3 for i in range(len(df))]  # des groupes de 3 quasi-doublons
    s = splits.make_splits(df, seed=7)
    part = {i: "test" for i in s.test} | {i: f"f{k}" for k, f in enumerate(s.folds) for i in f}
    owner: dict[int, str] = {}
    for pid, cl in zip(df["id"], df["cluster"], strict=True):
        assert owner.setdefault(cl, part[pid]) == part[pid], f"groupe {cl} réparti entre partitions"
    assert abs(len(s.test) / len(df) - 0.15) < 0.03
    assert splits.check_no_overlap(s) == []


def test_plant_leak_returns_a_copy_with_one_patient_in_test_and_fold_0():
    s = splits.make_splits(toy(), seed=7)
    leaked, pid = splits.plant_leak(s)
    assert splits.check_no_overlap(s) == []  # l'original reste intact
    assert splits.check_no_overlap(leaked) == [pid]
    assert pid in leaked.test and pid in leaked.folds[0]
