from llmft import leakage


def test_a_pair_exactly_at_the_threshold_is_reported():
    # 4 5-grammes communs sur 5 au total : Jaccard = 0,8 pile
    assert leakage.near_duplicate_pairs({"a": "abcdefgh", "b": "abcdefghi"}, threshold=0.8) == [("a", "b", 0.8)]


def test_a_pair_just_below_the_threshold_is_not_reported():
    assert leakage.near_duplicate_pairs({"a": "abcdefgh", "b": "abcdefghi"}, threshold=0.81) == []


def test_the_similarity_uses_five_character_ngrams():
    # 1 5-gramme commun sur 11 (0,09) ; en 3-grammes ce serait 5 sur 11 (0,45)
    assert leakage.near_duplicate_pairs({"a": "abcdefghij", "b": "abcdeXghij"}, threshold=0.2) == []


def test_repeated_ngrams_count_once_so_a_repetitive_text_is_not_a_duplicate():
    assert leakage.near_duplicate_pairs({"a": "aaaaaaaaaa", "b": "aaaaabbbbb"}, threshold=0.8) == []


def test_pairs_found_in_later_blocks_carry_the_right_identifiers(monkeypatch):
    monkeypatch.setattr(leakage, "_BLOCK", 2)
    base = "Compte rendu d'hospitalisation pour pneumopathie aigue communautaire traitee par antibiotherapie. "
    texts = {f"x{i}": f"texte distinct numero {i} " + chr(97 + i) * 30 for i in range(5)}
    texts["x3"] = base * 2
    texts["x4"] = base * 2 + "fin"
    pairs = leakage.near_duplicate_pairs(texts, threshold=0.8)
    assert [(a, b) for a, b, _ in pairs] == [("x3", "x4")]


def test_clusters_merge_a_star_of_pairs_through_the_first_member():
    c = leakage.clusters(["a", "b", "c", "d"], [("a", "b", 0.9), ("a", "c", 0.9)])
    assert c["a"] == c["b"] == c["c"] != c["d"]


def test_clusters_merge_two_chains_joined_by_their_ends():
    c = leakage.clusters(list("abcdef"), [("a", "b", 1), ("c", "d", 1), ("b", "d", 1), ("e", "f", 1)])
    assert c["a"] == c["b"] == c["c"] == c["d"] != c["e"] == c["f"]


def test_identical_short_texts_are_reported_as_duplicates():
    assert leakage.near_duplicate_pairs({"a": "ok", "b": "ok"}) != []
