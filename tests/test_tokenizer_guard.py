import os
import subprocess
import sys
from pathlib import Path
from typing import Any

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import p1_finetune
from llmft import tokenizer_guard

linux_only = pytest.mark.skipif(not hasattr(os, "sched_setaffinity"), reason="affinité CPU absente hors Linux")


@pytest.fixture(scope="module")
def tiny_tokenizer_path(tmp_path_factory: pytest.TempPathFactory) -> str:
    from tokenizers import Tokenizer, models, pre_tokenizers
    from transformers import PreTrainedTokenizerFast

    vocab = {"[UNK]": 0, "[PAD]": 1, "a": 2, "b": 3, "c": 4}
    core = Tokenizer(models.WordLevel(vocab, unk_token="[UNK]"))
    core.pre_tokenizer = pre_tokenizers.WhitespaceSplit()
    path = tmp_path_factory.mktemp("tiny_tok")
    PreTrainedTokenizerFast(tokenizer_object=core, unk_token="[UNK]", pad_token="[PAD]").save_pretrained(path)
    return str(path)


TEXTS = ["a b c", "c c c a b a b", "b"]


def test_sous_processus_donne_les_memes_identifiants_que_le_calcul_local(tiny_tokenizer_path: str):
    from transformers import AutoTokenizer

    expected = tokenizer_guard.build_inputs_local(AutoTokenizer.from_pretrained(tiny_tokenizer_path), TEXTS, 4)
    assert tokenizer_guard.isolated_build_inputs(tiny_tokenizer_path, TEXTS, 4, cache_dir=None) == expected


@linux_only
def test_le_sous_processus_tokenise_sur_un_seul_cpu(tiny_tokenizer_path: str):
    before = os.sched_getaffinity(0)
    _, cpus = tokenizer_guard.run_child(tiny_tokenizer_path, TEXTS, 4)
    assert cpus == 1
    assert os.sched_getaffinity(0) == before  # le parent garde son masque


def test_build_inputs_delegue_au_sous_processus_pour_un_vrai_tokenizer(tiny_tokenizer_path: str, monkeypatch: pytest.MonkeyPatch):
    from transformers import AutoTokenizer

    calls: list[str] = []
    real = tokenizer_guard.isolated_build_inputs

    def spy(name: str, texts: list[str], max_len: int, **kw: Any) -> list[list[int]]:
        calls.append(name)
        return real(name, texts, max_len, **{**kw, "cache_dir": None})

    monkeypatch.setattr(tokenizer_guard, "isolated_build_inputs", spy)
    out = p1_finetune.build_inputs(AutoTokenizer.from_pretrained(tiny_tokenizer_path), TEXTS, 4)
    assert calls == [tiny_tokenizer_path] and len(out) == len(TEXTS)


def test_un_plantage_du_sous_processus_est_relance_puis_abandonne(tiny_tokenizer_path: str, monkeypatch: pytest.MonkeyPatch):
    real_run = subprocess.run
    codes = [139, 1]  # deux plantages, puis un succès

    def flaky(argv: list[str], **kw: Any) -> subprocess.CompletedProcess[str]:
        if codes:
            return subprocess.CompletedProcess(argv, codes.pop(0), "", "plantage simulé")
        return real_run(argv, **kw)

    monkeypatch.setattr(tokenizer_guard.subprocess, "run", flaky)
    assert len(tokenizer_guard.isolated_build_inputs(tiny_tokenizer_path, TEXTS, 4, cache_dir=None)) == len(TEXTS)

    def always(argv: list[str], **kw: Any) -> subprocess.CompletedProcess[str]:
        return subprocess.CompletedProcess(argv, 139, "", "plantage simulé")

    monkeypatch.setattr(tokenizer_guard.subprocess, "run", always)
    with pytest.raises(RuntimeError, match="3 essais"):
        tokenizer_guard.isolated_build_inputs(tiny_tokenizer_path, TEXTS, 4, attempts=3, cache_dir=None)


@linux_only
def test_main_du_fils_ecrit_le_resultat_et_s_epingle(tiny_tokenizer_path: str, tmp_path: Path):
    import pickle

    from llmft import tokenizer_child

    inp, out = tmp_path / "in.pkl", tmp_path / "out.pkl"
    inp.write_bytes(pickle.dumps((tiny_tokenizer_path, TEXTS, 4)))
    before = os.sched_getaffinity(0)
    try:
        assert tokenizer_child.main(["prog", str(inp), str(out)]) == 0
    finally:
        os.sched_setaffinity(0, before)  # main() épingle le processus courant : on restitue le masque du test
    ids, cpus = pickle.loads(out.read_bytes())
    assert cpus == 1 and len(ids) == len(TEXTS)
