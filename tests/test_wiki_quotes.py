"""Les citations littérales du wiki existent mot pour mot dans les lignes citées du fichier brut."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import check_wiki_quotes as cq

RAW = "ligne un\nle modèle utilise 8 têtes d'attention\nligne trois\nfin\n"


def box(tmp_path, footnote, page_text="Un fait.[^1]\n\n"):
    (tmp_path / "raw").mkdir()
    (tmp_path / "raw/src.txt").write_text(RAW, encoding="utf-8")
    (tmp_path / "wiki/pages").mkdir(parents=True)
    (tmp_path / "wiki/pages/p.md").write_text(page_text + footnote + "\n", encoding="utf-8")
    return cq.check(tmp_path)


def test_an_exact_quote_in_the_cited_lines_passes(tmp_path):
    assert box(tmp_path, '[^1]: raw/src.txt L2 — "le modèle utilise 8 têtes d\'attention"') == []


def test_a_quote_split_over_two_lines_still_matches(tmp_path):
    assert box(tmp_path, '[^1]: raw/src.txt L2-L3 — "d\'attention ligne trois"') == []


def test_an_altered_quote_is_reported(tmp_path):
    problems = box(tmp_path, '[^1]: raw/src.txt L2 — "le modèle utilise 9 têtes d\'attention"')
    assert len(problems) == 1 and "p.md" in problems[0]


def test_a_quote_outside_the_cited_lines_is_reported(tmp_path):
    assert box(tmp_path, '[^1]: raw/src.txt L1 — "le modèle utilise 8 têtes d\'attention"')


def test_synthesis_citations_only_need_a_valid_line_range(tmp_path):
    assert box(tmp_path, "[^1]: raw/src.txt L1-L3 [synthesis] — résumé des trois lignes") == []
    assert box_again(tmp_path, "[^1]: raw/src.txt L1-L99 [synthesis] — hors du fichier")


def box_again(tmp_path, footnote):
    (tmp_path / "wiki/pages/p.md").write_text("Un fait.[^1]\n\n" + footnote + "\n", encoding="utf-8")
    return cq.check(tmp_path)


def test_a_missing_raw_file_is_reported(tmp_path):
    assert box(tmp_path, '[^1]: raw/absent.txt L1 — "x"')
