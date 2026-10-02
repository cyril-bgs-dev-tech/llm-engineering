"""Le profil matériel est lu par le code, jamais codé en dur (P0-11)."""
import pytest

from llmft import hardware as hw


def test_rtx5090_profile_loads_with_required_fields():
    p = hw.load_profile("rtx5090")
    assert p.name == "rtx5090"
    assert p.compute_capability == "sm_120"
    assert p.vram_gib == pytest.approx(32, abs=1)
    assert p.vram_budget_gib < p.vram_gib  # on garde une marge pour l'affichage et les autres processus
    assert p.precision_default == "bf16"


def test_unknown_profile_is_rejected_with_a_clear_message():
    with pytest.raises(FileNotFoundError, match="nope"):
        hw.load_profile("nope")


def test_profile_without_required_field_is_rejected(tmp_path):
    (tmp_path / "bad.yaml").write_text(
        "name: bad\ncompute_capability: sm_90\nvram_budget_gib: 20\nprecision_default: bf16\n", encoding="utf-8"
    )
    with pytest.raises(ValueError, match="vram_gib"):
        hw.load_profile("bad", directory=tmp_path)


def test_budget_above_total_is_rejected(tmp_path):
    (tmp_path / "x.yaml").write_text(
        "name: x\ncompute_capability: sm_90\nvram_gib: 24\nvram_budget_gib: 30\nprecision_default: bf16\n", encoding="utf-8"
    )
    with pytest.raises(ValueError, match="budget"):
        hw.load_profile("x", directory=tmp_path)
