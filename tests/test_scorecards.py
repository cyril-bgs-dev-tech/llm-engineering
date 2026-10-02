"""Schéma de preuve des scorecards (RM-12) : une note sans preuve est refusée, un artefact modifié est détecté."""
import hashlib

import pytest

from llmft import scorecard


def block(**over):
    data = {
        "q": "Q1", "note": 2, "requirement": "Les comptes sont tirés des données", "artifact": "a.txt", "artifact_sha256": "",
        "command": "python mesure.py", "expected": "4254", "observed": "4254", "date": "2026-10-02",
        "residual_defect": "aucun connu", "justification": "mesuré deux fois",
    }
    data.update(over)
    return data


def render(blocks):
    parts = ["# Scorecard test", ""]
    for b in blocks:
        parts += ["```yaml"] + [f"{k}: {v!r}" if isinstance(v, str) else f"{k}: {v}" for k, v in b.items()] + ["```", ""]
    return "\n".join(parts)


@pytest.fixture
def card(tmp_path):
    (tmp_path / "a.txt").write_text("contenu", encoding="utf-8")
    sha = hashlib.sha256(b"contenu").hexdigest()
    return tmp_path, sha


def check(tmp_path, blocks, floors=None):
    p = tmp_path / "card.md"
    p.write_text(render(blocks), encoding="utf-8")
    return scorecard.check_scorecard(p, root=tmp_path, floors=floors or {})


def test_a_complete_note_passes(card):
    root, sha = card
    assert check(root, [block(artifact_sha256=sha)]) == []


def test_note_zero_needs_no_proof_but_a_remediation_when_below_floor(card):
    root, _ = card
    bare = {"q": "Q1", "note": 0}
    assert check(root, [bare]) == []
    assert any("plan de rattrapage" in p for p in check(root, [bare], floors={"Q1": 1}))
    assert check(root, [{**bare, "remediation": "écrire le protocole d'ici G-P1"}], floors={"Q1": 1}) == []


@pytest.mark.parametrize("missing", ["requirement", "artifact", "command", "expected", "observed", "date", "residual_defect", "justification"])
def test_a_note_without_one_proof_field_is_refused(card, missing):
    root, sha = card
    b = block(artifact_sha256=sha)
    b[missing] = ""
    assert any(missing in p for p in check(root, [b]))


def test_a_modified_artifact_is_detected_by_its_hash(card):
    root, sha = card
    (root / "a.txt").write_text("contenu modifié", encoding="utf-8")
    assert any("empreinte" in p for p in check(root, [block(artifact_sha256=sha)]))


def test_a_missing_artifact_is_refused(card):
    root, sha = card
    assert any("introuvable" in p for p in check(root, [block(artifact="absent.txt", artifact_sha256=sha)]))


def test_note_three_requires_an_independent_confirmation_with_its_degree(card):
    root, sha = card
    assert any("confirmation indépendante" in p for p in check(root, [block(note=3, artifact_sha256=sha)]))
    ok = block(note=3, artifact_sha256=sha, independent_confirmation="relecture en contexte neuf", independence_degree="personne ou contexte")
    assert check(root, [ok]) == []
    bad = block(note=3, artifact_sha256=sha, independent_confirmation="x", independence_degree="amitié")
    assert any("degré" in p for p in check(root, [bad]))


def test_note_out_of_range_and_duplicate_categories_are_refused(card):
    root, sha = card
    assert any("note" in p for p in check(root, [block(note=4, artifact_sha256=sha)]))
    assert any("deux fois" in p for p in check(root, [block(artifact_sha256=sha), block(artifact_sha256=sha)]))
