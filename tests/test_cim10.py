"""Hiérarchie CIM-10 reconstruite depuis le ClaML de l'ATIH (P0-27). Le fichier source n'est jamais versionné."""
from pathlib import Path

import pytest

from llmft import cim10

MINI = """<?xml version="1.0" encoding="UTF-8"?>
<ClaML version="2.0.0">
 <Class code="II" kind="chapter"><SubClass code="C00-C97"/><Rubric kind="preferred"><Label xml:lang="fr">Tumeurs</Label></Rubric></Class>
 <Class code="C00-C97" kind="block"><SuperClass code="II"/><SubClass code="C30-C39"/><Rubric kind="preferred"><Label xml:lang="fr">Tumeurs malignes</Label></Rubric></Class>
 <Class code="C30-C39" kind="block"><SuperClass code="C00-C97"/><SubClass code="C34"/><Rubric kind="preferred"><Label xml:lang="fr">Organes respiratoires</Label></Rubric></Class>
 <Class code="C34" kind="category"><SuperClass code="C30-C39"/><SubClass code="C34.1"/><Rubric kind="preferred"><Label xml:lang="fr">Bronches et poumon</Label></Rubric></Class>
 <Class code="C34.1" kind="category"><SuperClass code="C34"/><Rubric kind="preferred"><Label xml:lang="fr">Lobe supérieur</Label></Rubric></Class>
 <Class code="D50-D89" kind="block"><SuperClass code="III"/><SubClass code="D50"/></Class>
 <Class code="III" kind="chapter"><SubClass code="D50-D89"/><Rubric kind="preferred"><Label xml:lang="fr">Sang</Label></Rubric></Class>
 <Class code="D50" kind="category"><SuperClass code="D50-D89"/><Rubric kind="preferred"><Label xml:lang="fr">Anémie</Label></Rubric></Class>
</ClaML>
"""


@pytest.fixture
def mini(tmp_path):
    p = tmp_path / "mini.xml"
    p.write_text(MINI, encoding="utf-8")
    return cim10.load_claml(p)


def test_a_full_code_gets_chapter_leaf_block_and_three_char_category(mini):
    h = mini.lookup("C341")
    assert h.chapter == "II"
    assert h.block == "C30-C39"
    assert h.category3 == "C34"


def test_normalisation_handles_dots_lowercase_and_pmsi_suffixes(mini):
    for raw in ("C34.1", "c341", "C341+8", "C34"):
        assert mini.lookup(raw).category3 == "C34"


def test_letter_d_is_split_across_chapters_by_range_not_by_letter(mini):
    assert mini.lookup("D50").chapter == "III"
    assert mini.lookup("D50").chapter != mini.lookup("C34").chapter


def test_unknown_code_is_reported_not_guessed(mini):
    assert mini.lookup("Z99") is None


def test_every_category_has_a_block_and_a_chapter(mini):
    assert mini.check_consistency() == []


def test_consistency_check_flags_an_orphan(tmp_path):
    p = tmp_path / "orphan.xml"
    p.write_text(MINI.replace('<SuperClass code="C00-C97"/><SubClass code="C34"/>', '<SubClass code="C34"/>', 1), encoding="utf-8")
    problems = cim10.load_claml(p).check_consistency()
    assert any("C30-C39" in x for x in problems)


REAL = Path(__file__).resolve().parents[1] / "data/raw/cim10/cim10fr2019.xml"


@pytest.mark.skipif(not REAL.exists(), reason="fichier ClaML de l'ATIH absent (non versionné, voir data/scripts/build_cim10.md)")
def test_real_claml_has_22_chapters_and_resolves_c341():
    h = cim10.load_claml(REAL)
    assert len(h.chapters) == 22
    assert h.check_consistency() == []
    # Erreur de la source (l'ATIH l'a corrigée dans le SMT, pas dans le ClaML) : C85 est rattaché à C84, pas à un bloc
    assert h.anomalies() == ["C85 a pour parent la catégorie C84"]
    assert h.lookup("C85").block == "C81-C96"
    r = h.lookup("C341")
    assert (r.chapter, r.block, r.category3) == ("II", "C30-C39", "C34")
