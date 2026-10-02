"""Contrôles anti-fuite sur le découpage réel versionné (P0-40) ; les cas piégés sont dans test_leakage_lib.py."""
import json
from pathlib import Path

import pytest

from llmft import leakage

ROOT = Path(__file__).resolve().parents[1]
SPLIT = ROOT / "data/splits/parhaf_cim10_chapter.json"
PAIRS = ROOT / "data/splits/near_duplicates.json"

pytestmark = pytest.mark.skipif(not (SPLIT.exists() and PAIRS.exists()), reason="partitions absentes")


def test_no_near_duplicate_pair_straddles_two_partitions():
    split = json.loads(SPLIT.read_text(encoding="utf-8"))
    part = {i: "test" for i in split["test"]} | {i: f"pli{k}" for k, f in enumerate(split["folds"]) for i in f}
    ref = json.loads(PAIRS.read_text(encoding="utf-8"))
    assert ref["threshold"] == leakage.NEAR_DUPLICATE_THRESHOLD  # le fichier de paires suit le seuil du protocole
    pairs = [tuple(p) for p in ref["pairs"]]
    assert pairs, "le fichier de paires est vide : le contrôle ne prouverait rien"
    assert leakage.cross_partition_pairs(pairs, part) == []


def test_the_real_pairs_would_fail_on_a_naive_split():
    """Preuve que le test est actif : le découpage d'avant correction (un patient par partition au hasard) casserait des paires."""
    ref = json.loads(PAIRS.read_text(encoding="utf-8"))
    pairs = [tuple(p) for p in ref["pairs"]]
    naive = {}
    for k, (a, b, _) in enumerate(pairs):
        naive[a], naive[b] = f"pli{k}", f"pli{k + 1}"
    assert len(leakage.cross_partition_pairs(pairs, naive)) == len(pairs)
