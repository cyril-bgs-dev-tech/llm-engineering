from pathlib import Path

import pytest

from llmft import tokenizer_guard as tg


@pytest.fixture
def calls(monkeypatch):
    seen = []

    def child(name, texts, max_len):
        seen.append((name, tuple(texts), max_len))
        return [[len(t)] for t in texts], 1

    monkeypatch.setattr(tg, "run_child", child)
    return seen


def test_text_order_is_part_of_the_cache_key(tmp_path: Path, calls):
    first = tg.isolated_build_inputs("tok", ["aa", "bbb"], 8, cache_dir=tmp_path)
    second = tg.isolated_build_inputs("tok", ["bbb", "aa"], 8, cache_dir=tmp_path)
    assert first == [[2], [3]] and second == [[3], [2]] and len(calls) == 2


def test_name_and_length_cannot_be_confused_in_the_cache_key(tmp_path: Path, calls):
    tg.isolated_build_inputs("tok", ["aa"], 16, cache_dir=tmp_path)
    tg.isolated_build_inputs("tok1", ["aa"], 6, cache_dir=tmp_path)
    assert len(calls) == 2


def test_a_new_transformers_version_gives_another_cache_file(tmp_path: Path, calls, monkeypatch):
    tg.isolated_build_inputs("tok", ["aa"], 8, cache_dir=tmp_path)
    real = tg.version
    monkeypatch.setattr(tg, "version", lambda pkg: "9.9.9" if pkg == "transformers" else real(pkg))
    tg.isolated_build_inputs("tok", ["aa"], 8, cache_dir=tmp_path)
    assert len(calls) == 2


def test_the_child_is_tried_exactly_attempts_times_before_giving_up(monkeypatch):
    n = []

    def broken(name, texts, max_len):
        n.append(1)
        raise RuntimeError("code 139")

    monkeypatch.setattr(tg, "run_child", broken)
    with pytest.raises(RuntimeError):
        tg.isolated_build_inputs("tok", ["aa"], 8, attempts=4, cache_dir=None)
    assert len(n) == 4


def test_a_cache_entry_of_the_wrong_length_is_recomputed(tmp_path: Path, calls):
    import pickle

    tg.isolated_build_inputs("tok", ["aa", "bbb"], 8, cache_dir=tmp_path)
    (cache_file,) = tmp_path.glob("*.pkl")
    cache_file.write_bytes(pickle.dumps([[1]]))
    assert tg.isolated_build_inputs("tok", ["aa", "bbb"], 8, cache_dir=tmp_path) == [[2], [3]]


def test_a_pickle_referring_to_a_missing_attribute_is_recomputed(tmp_path: Path, calls):
    import json
    import pickle

    tg.isolated_build_inputs("tok", ["aa"], 8, cache_dir=tmp_path)
    (cache_file,) = tmp_path.glob("*.pkl")
    cache_file.write_bytes(pickle.dumps(json.dumps).replace(b"dumps", b"dumpz"))  # AttributeError au chargement
    assert tg.isolated_build_inputs("tok", ["aa"], 8, cache_dir=tmp_path) == [[2]]
    assert len(calls) == 2
