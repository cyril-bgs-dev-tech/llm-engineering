"""N37 : une entrée de journal reçoit son heure de `date -u` et garde son texte tel quel (accents graves et dollars non exécutés)."""
import re
import subprocess
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "scripts/journal_entry.sh"


def test_l_entree_est_horodatee_par_l_horloge_et_son_corps_n_est_pas_interprete(tmp_path: Path) -> None:
    journal = tmp_path / "dossier avec espaces" / "journal.md"
    journal.parent.mkdir()
    journal.write_text("# Journal\n", encoding="utf-8")
    body = "- run `20261017-x` : $HOME et $(echo piege) restent du texte\n"
    subprocess.run(["bash", str(SCRIPT), "reprise par surveilleur"], input=body, text=True, check=True, env={"JOURNAL": str(journal), "PATH": "/usr/bin:/bin"})
    text = journal.read_text(encoding="utf-8")
    assert re.search(r"\n### \d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z : reprise par surveilleur\n\n", text)
    assert text.endswith(body)


def test_un_titre_vide_est_refuse(tmp_path: Path) -> None:
    journal = tmp_path / "journal.md"
    journal.write_text("", encoding="utf-8")
    r = subprocess.run(["bash", str(SCRIPT), ""], input="x\n", text=True, check=False, env={"JOURNAL": str(journal), "PATH": "/usr/bin:/bin"})
    assert r.returncode != 0 and journal.read_text(encoding="utf-8") == ""
