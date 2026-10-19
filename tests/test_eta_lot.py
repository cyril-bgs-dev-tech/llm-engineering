"""N39 : la fin d'un lot se projette depuis les durées mesurées dans son journal, jamais à la main."""
import sys
from datetime import UTC, datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import eta_lot

LOG = """2026-10-17T11:39:50Z DEBUT pli0 essai=1
2026-10-17T15:05:48Z FIN pli0 essai=1 code=0
2026-10-17T15:06:06Z DEBUT robustesse-pli0 essai=1
2026-10-17T15:26:29Z FIN robustesse-pli0 essai=1 code=0
2026-10-17T15:26:29Z DEBUT pli1 essai=1
2026-10-17T18:50:17Z FIN pli1 essai=1 code=0
2026-10-17T18:50:28Z DEBUT robustesse-pli1 essai=1
2026-10-17T19:05:43Z FIN robustesse-pli1 essai=1 code=0
2026-10-17T19:05:54Z DEBUT pli2 essai=1
"""


def test_la_fin_se_projette_sur_la_duree_moyenne_des_cycles_mesures() -> None:
    p = eta_lot.project(LOG, r"pli\d+", total=5)
    assert p["cycles_mesures_s"] == [13599.0, 13165.0]
    assert p["cycles_restants"] == 3
    assert p["fin_estimee"] == datetime(2026, 10, 17, 19, 5, 54, tzinfo=UTC).timestamp() + 3 * 13382.0


def test_une_relance_compte_dans_la_duree_du_cycle_ou_elle_a_lieu() -> None:
    log = LOG.replace("2026-10-17T15:26:29Z DEBUT pli1 essai=1", "2026-10-17T15:26:29Z DEBUT pli1 essai=1\n2026-10-17T16:00:00Z FIN pli1 essai=1 code=139\n2026-10-17T16:00:01Z DEBUT pli1 essai=2")
    assert eta_lot.project(log, r"pli\d+", total=5)["cycles_mesures_s"] == [13599.0, 13165.0]


def test_sans_cycle_termine_aucune_projection() -> None:
    assert eta_lot.project("2026-10-17T11:39:50Z DEBUT pli0 essai=1\n", r"pli\d+", total=5)["fin_estimee"] is None
