import json

import pandas as pd
import pytest

from llmft import sealed

FRAME = pd.DataFrame({"id": ["P1", "P2", "P3", "P4"], "text": list("abcd"), "label": ["l1", "l2", "l3", "l4"]})
SPLIT = {"test": ["P4", "P2"], "folds": [["P1"], ["P3"]]}  # ordre des ids du test différent de celui du frame
PRED = {"P2": "p2", "P4": "p4"}


def capture(store):
    def compute(y, p):
        store.update(y=list(y), p=list(p))
        return {"n": len(y)}
    return compute


@pytest.mark.parametrize("rehearsal", [True, False])
def test_labels_and_predictions_are_both_aligned_on_the_order_of_the_test_ids(tmp_path, rehearsal):
    seen = {}
    sealed.sealed_labels_and_score(SPLIT, FRAME, "label", PRED, capture(seen), marker=tmp_path / "m", reason="r", out_path=tmp_path / "o.json", rehearsal=rehearsal)
    assert seen == {"y": ["l4", "l2"], "p": ["p4", "p2"]}


def test_predictions_for_ids_outside_the_test_are_refused_before_the_marker(tmp_path):
    with pytest.raises(ValueError, match="identifiants"):
        sealed.sealed_labels_and_score(SPLIT, FRAME, "label", {**PRED, "P1": "x"}, capture({}), marker=tmp_path / "m", reason="r", out_path=tmp_path / "o.json")
    assert not (tmp_path / "m").exists()


@pytest.mark.parametrize("rehearsal", [True, False])
def test_an_empty_reason_is_refused_without_writing_anything(tmp_path, rehearsal):
    with pytest.raises(ValueError, match="reason"):
        sealed.sealed_labels_and_score(SPLIT, FRAME, "label", PRED, capture({}), marker=tmp_path / "m", reason="  ", out_path=tmp_path / "o.json", rehearsal=rehearsal)
    assert not (tmp_path / "m").exists() and not (tmp_path / "o.json").exists()


def test_journal_records_the_number_of_ids(tmp_path):
    j = tmp_path / "j.log"
    sealed.sealed_inputs(SPLIT, FRAME, "text", journal=j)
    assert json.loads(j.read_text(encoding="utf-8"))["n_ids"] == 2


def test_a_test_id_missing_from_the_frame_is_refused_before_the_marker(tmp_path):
    split = {"test": ["P2", "P9"]}
    with pytest.raises(ValueError):
        sealed.sealed_labels_and_score(split, FRAME, "label", {"P2": "a", "P9": "b"}, capture({}), marker=tmp_path / "m", reason="r", out_path=tmp_path / "o.json")
    assert not (tmp_path / "m").exists()


def test_a_missing_label_column_is_refused_before_the_marker(tmp_path):
    with pytest.raises(KeyError):
        sealed.sealed_labels_and_score(SPLIT, FRAME, "etiquette_absente", PRED, capture({}), marker=tmp_path / "m", reason="r", out_path=tmp_path / "o.json")
    assert not (tmp_path / "m").exists()


def test_duplicate_ids_in_the_frame_are_refused(tmp_path):
    frame = pd.concat([FRAME, FRAME.iloc[[1]].assign(label="autre")], ignore_index=True)
    with pytest.raises(ValueError):
        sealed.sealed_labels_and_score(SPLIT, frame, "label", PRED, capture({}), marker=tmp_path / "m", reason="r", out_path=tmp_path / "o.json", rehearsal=True)
