"""Contrôles sur les partitions réelles versionnées (P0-28, P0-29) : rejoués à chaque changement de données ou de découpage."""
import hashlib
import json
from pathlib import Path

import pandas as pd
import pytest

ROOT = Path(__file__).resolve().parents[1]
SPLIT = ROOT / "data/splits/parhaf_cim10_chapter.json"
PARQUET = ROOT / "data/raw/parhaf/data/train-00000-of-00001.parquet"

pytestmark = pytest.mark.skipif(not (SPLIT.exists() and PARQUET.exists()), reason="partitions ou données absentes")


@pytest.fixture(scope="module")
def split():
    return json.loads(SPLIT.read_text(encoding="utf-8"))


def test_recorded_sha256_matches_the_file():
    recorded = SPLIT.with_suffix(".sha256").read_text(encoding="ascii").strip()
    assert hashlib.sha256(SPLIT.read_bytes()).hexdigest() == recorded


def test_no_patient_in_two_partitions(split):
    parts = [split["test"], *split["folds"]]
    flat = [i for p in parts for i in p]
    assert len(flat) == len(set(flat))


def test_control_folds_cover_development_and_share_no_author(split):
    df = pd.read_parquet(PARQUET, columns=["id", "author"]).set_index("id")
    dev = {i for f in split["folds"] for i in f}
    control = split["control_folds_by_author"]
    assert dev == {i for f in control for i in f}
    assert not dev & set(split["test"])
    owner: dict[str, int] = {}
    for k, fold in enumerate(control):
        for a in set(df.loc[fold, "author"]):
            assert owner.setdefault(a, k) == k, f"auteur {a} dans deux plis de contrôle"


def test_quarantined_patients_are_absent(split):
    everyone = {i for p in [split["test"], *split["folds"]] for i in p}
    assert "GYNECOLOGIE-00116" not in everyone  # code CIM-10 invalide (N571)
