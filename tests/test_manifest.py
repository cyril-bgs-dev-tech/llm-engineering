"""Tests du manifeste d'empreintes de données (P0-14) : un jeu téléchargé se vérifie sans le republier."""
import hashlib
import json

import pytest

from llmft import manifest as mf


def make_tree(root):
    (root / "data").mkdir()
    (root / "data" / "train.parquet").write_bytes(b"contenu-a")
    (root / "README.md").write_bytes("fiche déposée\n".encode())
    (root / ".cache").mkdir()
    (root / ".cache" / "ignore-moi").write_bytes(b"x")


def test_sha256_matches_hashlib(tmp_path):
    f = tmp_path / "f.bin"
    f.write_bytes(b"abc" * 100_000)
    assert mf.sha256_file(f) == hashlib.sha256(b"abc" * 100_000).hexdigest()


def test_manifest_lists_files_with_sha_and_size_and_skips_hf_cache(tmp_path):
    make_tree(tmp_path)
    m = mf.build_manifest(tmp_path, source="HealthDataHub/PARHAF", revision="60426cc")
    names = [f["path"] for f in m["files"]]
    assert names == ["README.md", "data/train.parquet"]
    assert m["source"] == "HealthDataHub/PARHAF" and m["revision"] == "60426cc"
    assert m["files"][1]["sha256"] == hashlib.sha256(b"contenu-a").hexdigest()
    assert m["files"][1]["bytes"] == len(b"contenu-a")


def test_manifest_is_deterministic(tmp_path):
    make_tree(tmp_path)
    a = json.dumps(mf.build_manifest(tmp_path, "s", "r"), sort_keys=True)
    b = json.dumps(mf.build_manifest(tmp_path, "s", "r"), sort_keys=True)
    assert a == b


def test_verify_accepts_an_identical_tree(tmp_path):
    make_tree(tmp_path)
    m = mf.build_manifest(tmp_path, "s", "r")
    assert mf.verify_manifest(tmp_path, m) == []


def test_verify_reports_modified_missing_and_extra_files(tmp_path):
    make_tree(tmp_path)
    m = mf.build_manifest(tmp_path, "s", "r")
    (tmp_path / "data" / "train.parquet").write_bytes(b"corrompu")
    (tmp_path / "README.md").unlink()
    (tmp_path / "data" / "nouveau.parquet").write_bytes(b"?")
    problems = mf.verify_manifest(tmp_path, m)
    assert any("train.parquet" in p and "empreinte" in p for p in problems)
    assert any("README.md" in p and "manquant" in p for p in problems)
    assert any("nouveau.parquet" in p and "inattendu" in p for p in problems)


def test_write_then_load_round_trip(tmp_path):
    make_tree(tmp_path)
    m = mf.build_manifest(tmp_path, "s", "r")
    target = tmp_path.parent / (tmp_path.name + "_manifest.json")
    mf.write_manifest(m, target)
    assert mf.load_manifest(target) == m


def test_revision_is_mandatory(tmp_path):
    make_tree(tmp_path)
    with pytest.raises(ValueError, match="revision"):
        mf.build_manifest(tmp_path, "s", "")
