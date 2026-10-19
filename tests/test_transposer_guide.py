"""P5-07 : le guide docs/TRANSPOSER_AU_CHU.md est exécuté à blanc à chaque make check : ses blocs marqués sont extraits et exécutés tels quels sur la tâche factice."""
import hashlib
import math
import re
import runpy
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GUIDE = ROOT / "docs/TRANSPOSER_AU_CHU.md"
CORE = ("pipeline.py", "models.py", "metrics.py", "loader.py", "taskspec.py", "splits.py", "registry.py")


def block(marker: str) -> str:
    found = re.findall(rf"```(?:yaml|python)\n# {marker}\n(.*?)```", GUIDE.read_text(encoding="utf-8"), re.DOTALL)
    assert len(found) == 1, f"le guide doit contenir exactement un bloc « {marker} »"
    return found[0]


def test_les_blocs_du_guide_font_tourner_la_chaine_sur_la_tache_factice_sans_toucher_au_noyau(tmp_path: Path) -> None:
    before = {n: hashlib.sha256((ROOT / "src/llmft" / n).read_bytes()).hexdigest() for n in CORE}
    contract = tmp_path / "orientation_message_factice.yaml"
    contract.write_text(block("contrat-factice"), encoding="utf-8")
    namespace: dict = {"CONTRAT": contract, "RUNS": tmp_path / "runs"}
    for marker in ("adaptateur-factice", "chaine-factice"):  # blocs du guide, exécutés tels quels et dans l'ordre
        script = tmp_path / f"{marker}.py"
        script.write_text(block(marker), encoding="utf-8")
        namespace = runpy.run_path(str(script), init_globals=namespace)
    record = namespace["record"]
    assert record["status"] == "ok" and record["data"]["task"] == "orientation_message_factice"
    assert record["data"]["n_train"] > 0 and record["data"]["n_validation"] > 0
    assert set(record["metrics"]) == {"macro_f1", "accuracy", "log_loss", "ece"}
    assert all(math.isfinite(v) for v in record["metrics"].values())
    assert (tmp_path / "runs" / f"{record['run_id']}.json").exists()
    assert {n: hashlib.sha256((ROOT / "src/llmft" / n).read_bytes()).hexdigest() for n in CORE} == before


def test_le_guide_cite_des_modules_et_des_scripts_qui_existent() -> None:
    text = GUIDE.read_text(encoding="utf-8")
    for module in set(re.findall(r"`llmft\.([a-z_]+)", text)):
        assert (ROOT / "src/llmft" / f"{module}.py").exists(), f"module absent : llmft.{module}"
    for script in set(re.findall(r"`(scripts/[a-z0-9_]+\.py)", text)):
        assert (ROOT / script).exists(), f"script absent : {script}"
    for doc in set(re.findall(r"`(docs/[A-Za-z_]+\.md|tests/[a-z_]+\.py)`", text)):
        assert (ROOT / doc).exists(), f"fichier absent : {doc}"
