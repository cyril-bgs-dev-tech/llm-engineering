"""Chargeur générique (P0-43) et tâche jouet (P0-39) : aucune branche propre à une tâche, empreinte des partitions vérifiée."""
import json
from pathlib import Path

import pandas as pd
import pytest

from llmft import loader, splits, taskspec, toy

ROOT = Path(__file__).resolve().parents[1]


def test_toy_dataset_is_deterministic_balanced_and_unique():
    a, b = toy.make_toy(n=50, seed=3), toy.make_toy(n=50, seed=3)
    assert a.equals(b)
    assert not a.equals(toy.make_toy(n=50, seed=4))
    assert len(a) == 50 and a["id"].is_unique
    assert a["label"].value_counts().to_dict() == {"positif": 25, "negatif": 25}
    assert set(a.columns) == {"id", "text", "label", "author"}


def test_loader_returns_a_validated_dataset_for_the_toy_task():
    spec = taskspec.load_task_spec(ROOT / "task_specs/toy_sentiment.yaml")
    ds = loader.load_dataset(spec, toy.ToyAdapter(n=50, seed=3))
    assert len(ds.frame) == 50 and ds.spec.task_id == "toy_sentiment"


def test_loader_rejects_a_label_outside_the_closed_list():
    spec = taskspec.load_task_spec(ROOT / "task_specs/toy_sentiment.yaml")

    class Bad:
        def load(self) -> pd.DataFrame:
            return pd.DataFrame({"id": ["a", "b"], "text": ["x", "y"], "label": ["positif", "neutre"], "author": ["u", "v"]})

    with pytest.raises(loader.DataError, match="neutre"):
        loader.load_dataset(spec, Bad())


@pytest.mark.parametrize(
    "frame, message",
    [
        (pd.DataFrame({"id": ["a", "a"], "text": ["x", "y"], "label": ["positif", "negatif"], "author": ["u", "v"]}), "dupliqu"),
        (pd.DataFrame({"id": ["a", "b"], "text": ["x", ""], "label": ["positif", "negatif"], "author": ["u", "v"]}), "texte vide"),
        (pd.DataFrame({"id": ["a", "b"], "text": ["x", "y"], "label": ["positif", "negatif"]}), "author"),
    ],
)
def test_loader_rejects_malformed_frames(frame, message):
    spec = taskspec.load_task_spec(ROOT / "task_specs/toy_sentiment.yaml")

    class Adapter:
        def load(self) -> pd.DataFrame:
            return frame

    with pytest.raises(loader.DataError, match=message):
        loader.load_dataset(spec, Adapter())


def test_two_different_tasks_go_through_the_same_loader():
    toy_spec = taskspec.load_task_spec(ROOT / "task_specs/toy_sentiment.yaml")
    doc_spec = taskspec.load_task_spec(ROOT / "task_specs/parhaf_doctype.yaml")

    class Docs:
        def load(self) -> pd.DataFrame:
            ids = [f"d{i}" for i in range(14)]
            return pd.DataFrame({"id": ids, "text": ["t"] * 14, "label": [doc_spec.class_ids[i % 7] for i in range(14)], "author": ["a"] * 14})

    assert len(loader.load_dataset(toy_spec, toy.ToyAdapter(n=50, seed=1)).frame) == 50
    assert len(loader.load_dataset(doc_spec, Docs()).frame) == 14


def test_loader_source_contains_nothing_specific_to_a_task():
    source = (ROOT / "src/llmft/loader.py").read_text(encoding="utf-8").lower()
    for word in ("parhaf", "toy", "cim10", "doctype", "specialty", "sentiment"):
        assert word not in source


def test_partition_fingerprint_is_compared_with_the_reference(tmp_path):
    s = splits.make_splits(toy.make_toy(n=50, seed=3)[["id", "author", "label"]], seed=5)
    path = tmp_path / "p.json"
    path.write_text(s.to_json(), encoding="utf-8")
    ref = tmp_path / "p.sha256"
    ref.write_text(s.sha256() + "\n", encoding="ascii")
    assert loader.load_partitions(path, ref)["seed"] == 5
    path.write_text(path.read_text(encoding="utf-8").replace('"seed": 5', '"seed": 6'), encoding="utf-8")
    with pytest.raises(loader.DataError, match="empreinte"):
        loader.load_partitions(path, ref)


def test_partitions_can_be_selected_by_name(tmp_path):
    frame = toy.make_toy(n=50, seed=3)
    s = splits.make_splits(frame[["id", "author", "label"]], seed=5)
    spec = taskspec.load_task_spec(ROOT / "task_specs/toy_sentiment.yaml")
    ds = loader.load_dataset(spec, toy.ToyAdapter(n=50, seed=3))
    part = json.loads(s.to_json())
    train = loader.select(ds, part, fold=0, role="validation")
    assert set(train["id"]) == set(part["folds"][0])
    dev = loader.select(ds, part, fold=0, role="train")
    assert not set(dev["id"]) & set(part["folds"][0]) and not set(dev["id"]) & set(part["test"])
