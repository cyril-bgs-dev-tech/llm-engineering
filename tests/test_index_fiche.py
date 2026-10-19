"""N37 : hacher une fiche et écrire sa ligne d'index en une commande, qui refuse une heure future dans la fiche."""
import hashlib
import sys
from datetime import UTC, datetime
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import index_fiche


def test_la_ligne_d_index_porte_la_date_et_l_empreinte_lues_et_non_tapees(tmp_path: Path) -> None:
    fiche = tmp_path / "2026-10-17-x.md"
    fiche.write_text("Écrite le 17/10/2026 à 19:44Z.\n", encoding="utf-8")
    line = index_fiche.index_line(fiche, "experiments/2026-10-17-x.md", "Fiche préenregistrée : x", "premier run", datetime(2026, 10, 17, 19, 45, tzinfo=UTC))
    digest = hashlib.sha256(fiche.read_bytes()).hexdigest()
    assert line == f"| 2026-10-17 | Fiche préenregistrée : x | `experiments/2026-10-17-x.md` | `{digest}` | premier run |"


def test_une_heure_future_dans_la_fiche_bloque_le_hachage(tmp_path: Path) -> None:
    fiche = tmp_path / "2026-10-17-x.md"
    fiche.write_text("Écrite le 17/10/2026 vers 20:10Z.\n", encoding="utf-8")
    with pytest.raises(SystemExit, match="20:10Z"):
        index_fiche.index_line(fiche, "experiments/2026-10-17-x.md", "t", "d", datetime(2026, 10, 17, 19, 44, 13, tzinfo=UTC))


def test_une_barre_verticale_dans_le_titre_est_refusee(tmp_path: Path) -> None:
    fiche = tmp_path / "2026-10-17-x.md"
    fiche.write_text("q\n", encoding="utf-8")
    with pytest.raises(SystemExit, match="barre"):
        index_fiche.index_line(fiche, "experiments/2026-10-17-x.md", "a | b", "d", datetime(2026, 10, 17, tzinfo=UTC))
