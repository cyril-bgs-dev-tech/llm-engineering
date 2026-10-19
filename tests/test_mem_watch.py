import os
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_le_temoin_memoire_consigne_demarrage_segfaults_et_puissance_gpu(tmp_path):
    out = tmp_path / "memoire.log"
    env = {**os.environ, "OUT": str(out), "INTERVALLE": "1"}
    subprocess.run(["timeout", "3", "bash", str(ROOT / "scripts/mem_watch.sh")], env=env, check=False, capture_output=True)
    lines = out.read_text(encoding="utf-8").splitlines()
    assert lines, "aucune ligne écrite dans le fichier demandé"
    first = lines[0]
    assert re.search(r" boot=[0-9a-f]{8} ", first)
    assert re.search(r" segv=\d+ ", first)
    assert re.search(r" pgpu=(\d+(\.\d+)?|na) ", first)
