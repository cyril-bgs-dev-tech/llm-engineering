from pathlib import Path

import pytest

from llmft import tokenizer_guard

TEXTS = ["alpha beta", "gamma"]


@pytest.fixture
def calls(monkeypatch: pytest.MonkeyPatch) -> list[tuple[str, int, int]]:
    seen: list[tuple[str, int, int]] = []

    def fake_child(name: str, texts: list[str], max_len: int) -> tuple[list[list[int]], int]:
        seen.append((name, len(texts), max_len))
        return [[len(t), max_len] for t in texts], 1

    monkeypatch.setattr(tokenizer_guard, "run_child", fake_child)
    return seen


def test_le_second_appel_identique_lit_le_cache_sans_lancer_de_fils(tmp_path: Path, calls: list[tuple[str, int, int]]):
    first = tokenizer_guard.isolated_build_inputs("tok", TEXTS, 8, cache_dir=tmp_path)
    second = tokenizer_guard.isolated_build_inputs("tok", TEXTS, 8, cache_dir=tmp_path)
    assert first == second == [[10, 8], [5, 8]]
    assert len(calls) == 1


@pytest.mark.parametrize("name,texts,max_len", [("autre", TEXTS, 8), ("tok", TEXTS + ["delta"], 8), ("tok", ["alpha beta", "gammA"], 8), ("tok", TEXTS, 16)])
def test_un_nom_des_textes_ou_une_longueur_differents_ne_reutilisent_pas_le_cache(tmp_path: Path, calls: list[tuple[str, int, int]], name: str, texts: list[str], max_len: int):
    tokenizer_guard.isolated_build_inputs("tok", TEXTS, 8, cache_dir=tmp_path)
    tokenizer_guard.isolated_build_inputs(name, texts, max_len, cache_dir=tmp_path)
    assert len(calls) == 2


def test_sans_dossier_de_cache_chaque_appel_tokenise(calls: list[tuple[str, int, int]]):
    tokenizer_guard.isolated_build_inputs("tok", TEXTS, 8, cache_dir=None)
    tokenizer_guard.isolated_build_inputs("tok", TEXTS, 8, cache_dir=None)
    assert len(calls) == 2


def test_un_fichier_de_cache_corrompu_est_recalcule_puis_remplace(tmp_path: Path, calls: list[tuple[str, int, int]]):
    tokenizer_guard.isolated_build_inputs("tok", TEXTS, 8, cache_dir=tmp_path)
    (cache_file,) = tmp_path.glob("*.pkl")
    cache_file.write_bytes(b"pas un pickle")
    assert tokenizer_guard.isolated_build_inputs("tok", TEXTS, 8, cache_dir=tmp_path) == [[10, 8], [5, 8]]
    assert len(calls) == 2
    tokenizer_guard.isolated_build_inputs("tok", TEXTS, 8, cache_dir=tmp_path)
    assert len(calls) == 2


def test_un_echec_du_fils_n_ecrit_rien_dans_le_cache(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    def broken(name: str, texts: list[str], max_len: int) -> tuple[list[list[int]], int]:
        raise RuntimeError("code 139")

    monkeypatch.setattr(tokenizer_guard, "run_child", broken)
    with pytest.raises(RuntimeError):
        tokenizer_guard.isolated_build_inputs("tok", TEXTS, 8, attempts=2, cache_dir=tmp_path)
    assert not list(tmp_path.glob("*.pkl"))
