"""Tests du mini-registre de runs (RM-05) : écriture en ajout seul, schéma minimal, bibliothèque standard."""
import ast
import json
import sys
from pathlib import Path

import pytest

from llmft import mini_registry as reg


def record(**over):
    base = {"kind": "spike", "slug": "pytorch-sm120", "status": "ok", "summary": "essai"}
    base.update(over)
    return base


def test_register_creates_a_json_file_named_after_its_run_id(tmp_path):
    path = reg.register_run(tmp_path, record())
    assert path.parent == tmp_path
    data = json.loads(path.read_text(encoding="utf-8"))
    assert path.name == data["run_id"] + ".json"
    assert data["run_id"].endswith("-pytorch-sm120")
    assert data["status"] == "ok"
    assert data["schema"] == "mini-1"


def test_overwriting_an_existing_run_is_refused(tmp_path):
    first = reg.register_run(tmp_path, record(run_id="20261001-120000-essai"))
    before = first.read_bytes()
    with pytest.raises(FileExistsError):
        reg.register_run(tmp_path, record(run_id="20261001-120000-essai", summary="modifié"))
    assert first.read_bytes() == before


def test_unknown_status_is_rejected(tmp_path):
    with pytest.raises(ValueError, match="status"):
        reg.register_run(tmp_path, record(status="reussi"))
    assert list(tmp_path.iterdir()) == []


@pytest.mark.parametrize("missing", ["kind", "slug", "status", "summary"])
def test_missing_required_field_is_rejected(tmp_path, missing):
    rec = record()
    del rec[missing]
    with pytest.raises(ValueError, match=missing):
        reg.register_run(tmp_path, rec)


def test_slug_is_restricted_to_safe_characters(tmp_path):
    with pytest.raises(ValueError, match="slug"):
        reg.register_run(tmp_path, record(slug="../evasion"))


def test_accents_and_nested_metrics_survive_a_round_trip(tmp_path):
    path = reg.register_run(tmp_path, record(summary="mémoire réservée", metrics={"vram_go": 21.4, "pas": [1, 2]}))
    loaded = reg.load_run(path)
    assert loaded["summary"] == "mémoire réservée"
    assert loaded["metrics"] == {"vram_go": 21.4, "pas": [1, 2]}


def test_list_runs_is_sorted_by_run_id(tmp_path):
    reg.register_run(tmp_path, record(run_id="20261001-130000-b"))
    reg.register_run(tmp_path, record(run_id="20261001-120000-a"))
    assert [r["run_id"] for r in reg.list_runs(tmp_path)] == ["20261001-120000-a", "20261001-130000-b"]


def test_record_is_not_mutated_and_run_is_stamped(tmp_path):
    rec = record()
    reg.register_run(tmp_path, rec)
    assert "run_id" not in rec
    stored = reg.list_runs(tmp_path)[0]
    assert stored["created_at"].endswith("Z")


def test_module_depends_on_the_standard_library_only():
    src = Path(reg.__file__).read_text(encoding="utf-8")
    roots = set()
    for node in ast.walk(ast.parse(src)):
        if isinstance(node, ast.Import):
            roots |= {a.name.split(".")[0] for a in node.names}
        elif isinstance(node, ast.ImportFrom) and node.level == 0:
            roots.add((node.module or "").split(".")[0])
    assert roots <= set(sys.stdlib_module_names) | {"__future__"}


def test_two_runs_registered_in_the_same_second_get_distinct_generated_ids(tmp_path, monkeypatch):
    from datetime import UTC, datetime

    class FrozenDatetime(datetime):
        @classmethod
        def now(cls, tz=None):
            return datetime(2026, 10, 2, 12, 0, 0, tzinfo=UTC)

    monkeypatch.setattr(reg, "datetime", FrozenDatetime)
    first = reg.register_run(tmp_path, record())
    second = reg.register_run(tmp_path, record())
    third = reg.register_run(tmp_path, record())
    assert first.name == "20261002-120000-pytorch-sm120.json"
    assert second.name == "20261002-120000-pytorch-sm120-2.json"
    assert third.name == "20261002-120000-pytorch-sm120-3.json"
    assert json.loads(second.read_text(encoding="utf-8"))["run_id"] == "20261002-120000-pytorch-sm120-2"
    assert first.read_text(encoding="utf-8") != second.read_text(encoding="utf-8")  # le premier n'a pas été touché


def test_an_explicit_run_id_that_exists_is_still_refused_not_renamed(tmp_path):
    reg.register_run(tmp_path, record(run_id="20261001-120000-essai"))
    with pytest.raises(FileExistsError):
        reg.register_run(tmp_path, record(run_id="20261001-120000-essai"))
    assert len(list(tmp_path.glob("*.json"))) == 1


def test_un_run_sans_tampon_recoit_celui_du_registre_de_l_import_a_l_enregistrement(tmp_path):
    """RM-59 rendu préventif (incident du 17/10 : 56 scripts enregistraient sans tampon, refusés seulement après coup par check_run_health)."""
    data = json.loads(reg.register_run(tmp_path, record()).read_text(encoding="utf-8"))
    assert data["machine_health"]["verdict"] in ("ok", "suspect") and data["machine_health"]["source"].startswith("registre")


def test_un_tampon_pose_par_le_script_n_est_jamais_remplace(tmp_path):
    stamp = {"verdict": "ok", "reasons": [], "start": {"boot_id": "a"}, "end": {"boot_id": "a"}}
    data = json.loads(reg.register_run(tmp_path, record(machine_health=stamp)).read_text(encoding="utf-8"))
    assert data["machine_health"] == stamp


def test_une_derogation_ecrite_n_est_pas_doublee_d_un_tampon_automatique(tmp_path):
    data = json.loads(reg.register_run(tmp_path, record(health_waiver="mesure de l'instabilité elle-même")).read_text(encoding="utf-8"))
    assert "machine_health" not in data


def test_le_module_de_sante_reste_en_bibliotheque_standard_comme_le_registre():
    src = (Path(reg.__file__).parent / "machine_health.py").read_text(encoding="utf-8")
    roots = set()
    for node in ast.walk(ast.parse(src)):
        if isinstance(node, ast.Import):
            roots |= {a.name.split(".")[0] for a in node.names}
        elif isinstance(node, ast.ImportFrom) and node.level == 0:
            roots.add((node.module or "").split(".")[0])
    assert roots <= set(sys.stdlib_module_names) | {"__future__"}
