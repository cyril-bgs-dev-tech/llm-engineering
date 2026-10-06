import os
import subprocess
import time
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "run_guarded.sh"


def run(args: list[str], tmp_path: Path, **env: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run([str(SCRIPT), *args], capture_output=True, text=True, timeout=60, check=False, env={**os.environ, "MEM_LOG": str(tmp_path / "memoire.log"), **env})


def test_le_code_de_sortie_de_la_commande_est_conserve(tmp_path: Path):
    assert run(["bash", "-c", "exit 7"], tmp_path).returncode == 7


def test_la_commande_est_lancee_avec_ses_arguments(tmp_path: Path):
    assert run(["bash", "-c", 'echo "$1"', "x", "bonjour"], tmp_path).stdout.strip() == "bonjour"


def test_le_garde_arrete_la_commande_quand_la_ram_passe_sous_le_seuil(tmp_path: Path):
    start = time.time()
    done = run(["sleep", "40"], tmp_path, SEUIL_MIO="999999999")
    assert done.returncode == 3 and time.time() - start < 30
    assert "GARDE" in (tmp_path / "memoire.log").read_text(encoding="utf-8")


def test_sans_depassement_rien_n_est_ecrit_au_journal(tmp_path: Path):
    run(["true"], tmp_path)
    assert not (tmp_path / "memoire.log").exists()
