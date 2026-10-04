from llmft import claims


def test_known_slug_and_suffix_references_are_accepted() -> None:
    known = {"20261004-070113-llm-mur2-qwen3-5-4b-ep10-lr1e-4", "tfidf-loao"}
    text = "voir `llm-mur2-qwen3-5-4b-ep10-lr1e-4` et `tfidf-loao` et `20261004-070113-llm-mur2-qwen3-5-4b-ep10-lr1e-4`"
    assert claims.unknown_run_references(text, known, allow=set()) == []


def test_unknown_run_like_token_is_reported() -> None:
    assert claims.unknown_run_references("le run `camembert-inconnu-ep10` a donné", {"tfidf-loao"}, allow=set()) == ["camembert-inconnu-ep10"]


def test_allowlisted_and_short_tokens_and_paths_are_ignored() -> None:
    text = "`claim-gate` `make` `scripts/x.py` `a-b` `RESULTATS.md`"
    assert claims.unknown_run_references(text, set(), allow={"claim-gate"}) == []
