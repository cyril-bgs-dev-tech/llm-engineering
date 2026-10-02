"""Couverture des lignes modifiées (P0-42) : l'intersection du diff et du rapport de couverture, sans relancer la suite."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import check_changed_coverage as cc

DIFF = """diff --git a/src/llmft/a.py b/src/llmft/a.py
--- a/src/llmft/a.py
+++ b/src/llmft/a.py
@@ -1,0 +2,3 @@
+x = 1
+y = 2
+z = 3
@@ -10 +20 @@
+w = 4
diff --git a/README.md b/README.md
--- a/README.md
+++ b/README.md
@@ -0,0 +1 @@
+texte
"""
REPORT = {"files": {"src/llmft/a.py": {"executed_lines": [2, 3, 20], "missing_lines": [4]}}}


def test_added_lines_are_parsed_per_python_source_file():
    assert cc.added_lines(DIFF) == {"src/llmft/a.py": {2, 3, 4, 20}}


def test_ratio_counts_only_executable_changed_lines():
    covered, total = cc.changed_coverage({"src/llmft/a.py": {2, 3, 4, 20, 99}}, REPORT)
    assert (covered, total) == (3, 4)  # la ligne 99 n'est pas exécutable : ignorée


def test_nothing_changed_means_nothing_to_enforce():
    assert cc.changed_coverage({}, REPORT) == (0, 0)


def test_diff_base_defaults_to_head_or_empty_tree_when_no_base_is_given():
    assert cc.diff_base(None, has_head=True) == "HEAD"
    assert cc.diff_base("", has_head=True) == "HEAD"
    assert cc.diff_base(None, has_head=False) == cc.EMPTY_TREE


def test_diff_base_uses_the_merge_base_with_the_given_ref_in_ci():
    # en CI l'arbre est propre : sans base explicite le diff serait vide et la porte passerait à vide
    assert cc.diff_base("origin/main", has_head=True) == "origin/main...HEAD"
    assert cc.diff_base("origin/main", has_head=False) == cc.EMPTY_TREE  # sans HEAD, la base n'a pas de sens


def test_first_push_in_ci_compares_the_whole_tree_to_the_empty_tree():
    assert cc.diff_base(cc.EMPTY_TREE, has_head=True) == cc.EMPTY_TREE  # « arbre...HEAD » n'a pas de sens pour un arbre
