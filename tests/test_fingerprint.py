from llmft.fingerprint import dir_sha256


def test_same_content_same_hash_regardless_of_creation_order(tmp_path) -> None:
    a, b = tmp_path / "a", tmp_path / "b"
    for d, order in ((a, ("x.bin", "y.bin")), (b, ("y.bin", "x.bin"))):
        d.mkdir()
        for name in order:
            (d / name).write_bytes(name.encode() * 10)
    assert dir_sha256(a) == dir_sha256(b)


def test_hash_changes_when_a_file_changes_or_is_renamed(tmp_path) -> None:
    (tmp_path / "x.bin").write_bytes(b"1")
    before = dir_sha256(tmp_path)
    (tmp_path / "x.bin").write_bytes(b"2")
    assert dir_sha256(tmp_path) != before
    (tmp_path / "x.bin").rename(tmp_path / "z.bin")
    assert dir_sha256(tmp_path) != before
