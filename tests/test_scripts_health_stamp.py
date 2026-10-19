"""RM-59 appliqué aux scripts des runs longs (RM-61, RM-62) : `check_run_health` refuse tout run « ok » sans tampon de santé ; les scripts du LoRA doivent donc le poser."""
from pathlib import Path

import pytest

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"


@pytest.mark.parametrize("name", ["p1_finetune.py", "robustness_lora_diag.py"])
def test_les_scripts_du_lora_prennent_un_instantane_au_debut_et_tamponnent_le_run(name):
    source = (SCRIPTS / name).read_text(encoding="utf-8")
    assert "machine_health.snapshot()" in source and "machine_health.stamp(" in source, f"{name} n'enregistre pas la santé de la machine"
