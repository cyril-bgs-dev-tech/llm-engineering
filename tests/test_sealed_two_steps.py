"""Ouverture du test scellé en deux temps (PROTOCOLE.md 6.8, RM-20) : A sans étiquettes ni marqueur, B avec marqueur et écriture atomique."""
import json

import pandas as pd
import pytest

from llmft import sealed

SPLIT = {"test": ["P2", "P4"], "folds": [["P1"], ["P3"]]}
FRAME = pd.DataFrame({"id": ["P1", "P2", "P3", "P4"], "text": ["t1", "t2", "t3", "t4"], "label": ["a", "b", "a", "c"]})


def test_time_a_returns_ids_and_texts_only_without_marker(tmp_path):
    marker = tmp_path / "m"
    out = sealed.sealed_inputs(SPLIT, FRAME, text_col="text")
    assert list(out.columns) == ["id", "text"]
    assert out["id"].tolist() == ["P2", "P4"] and out["text"].tolist() == ["t2", "t4"]
    assert not marker.exists()


def test_time_a_refuses_when_a_test_id_is_missing_from_the_frame():
    with pytest.raises(ValueError, match="P4"):
        sealed.sealed_inputs(SPLIT, FRAME[FRAME["id"] != "P4"], text_col="text")


def test_rehearsal_computes_everything_but_writes_nothing(tmp_path):
    marker, out = tmp_path / "m", tmp_path / "res.json"
    res = sealed.sealed_labels_and_score(SPLIT, FRAME, "label", {"P2": "b", "P4": "c"}, lambda y, p: {"acc": sum(a == b for a, b in zip(y, p, strict=True)) / len(y)},
                                         marker=marker, reason="répétition", out_path=out, rehearsal=True)
    assert res == {"acc": 1.0} and not marker.exists() and not out.exists()


def test_time_b_writes_marker_before_reading_labels_then_result_atomically(tmp_path):
    marker, out = tmp_path / "m", tmp_path / "res.json"
    seen = {}

    def compute(y, p):
        seen["marker_existed"] = marker.exists()
        return {"labels": list(y), "preds": list(p)}

    res = sealed.sealed_labels_and_score(SPLIT, FRAME, "label", {"P4": "c", "P2": "a"}, compute, marker=marker, reason="évaluation finale", out_path=out)
    assert seen["marker_existed"] is True
    assert res == {"labels": ["b", "c"], "preds": ["a", "c"]}  # aligné sur l'ordre des identifiants du test
    assert json.loads(out.read_text(encoding="utf-8")) == res
    assert not list(tmp_path.glob("*.tmp"))


def test_predictions_not_covering_exactly_the_test_ids_fail_before_the_marker(tmp_path):
    marker = tmp_path / "m"
    with pytest.raises(ValueError, match="identifiants"):
        sealed.sealed_labels_and_score(SPLIT, FRAME, "label", {"P2": "b"}, lambda y, p: {}, marker=marker, reason="x", out_path=tmp_path / "r.json")
    assert not marker.exists()


def test_failure_after_opening_keeps_the_marker_and_forbids_a_second_opening(tmp_path):
    marker, out = tmp_path / "m", tmp_path / "res.json"

    def boom(y, p):
        raise RuntimeError("calcul impossible")

    with pytest.raises(sealed.ConsumedWithoutResultError):
        sealed.sealed_labels_and_score(SPLIT, FRAME, "label", {"P2": "b", "P4": "c"}, boom, marker=marker, reason="évaluation finale", out_path=out)
    assert marker.exists() and not out.exists()
    with pytest.raises(sealed.AlreadyOpenedError):
        sealed.sealed_labels_and_score(SPLIT, FRAME, "label", {"P2": "b", "P4": "c"}, lambda y, p: {}, marker=marker, reason="encore", out_path=out)


def test_access_journal_records_operations_without_content(tmp_path):
    journal = tmp_path / "j.log"
    sealed.sealed_inputs(SPLIT, FRAME, text_col="text", journal=journal)
    sealed.sealed_labels_and_score(SPLIT, FRAME, "label", {"P2": "b", "P4": "c"}, lambda y, p: {"n": len(y)}, marker=tmp_path / "m", reason="répétition",
                                   out_path=tmp_path / "r.json", rehearsal=True, journal=journal)
    sealed.sealed_labels_and_score(SPLIT, FRAME, "label", {"P2": "b", "P4": "c"}, lambda y, p: {"n": len(y)}, marker=tmp_path / "m", reason="ouverture",
                                   out_path=tmp_path / "r.json", journal=journal)
    lines = [json.loads(x) for x in journal.read_text(encoding="utf-8").splitlines()]
    assert [x["operation"] for x in lines] == ["inputs", "rehearsal", "open"]
    assert all(set(x) == {"at", "operation", "n_ids"} for x in lines)
