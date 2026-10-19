"""Le script de frontière lit chaque run par son slug exact : « service-g-cascade » ne doit pas attraper « energie-service-g-cascade », plus récent (défaut trouvé le 17/10)."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import pareto_cout_qualite as pcq


def test_le_slug_exact_est_retenu_et_le_plus_recent_d_entre_eux():
    names = ["20261017-015754-service-g-cascade.json", "20261017-025855-energie-service-g-cascade.json", "20261017-010000-service-g-cascade.json"]
    assert pcq.latest_exact(names, "service-g-cascade") == "20261017-015754-service-g-cascade.json"


def test_aucun_run_rend_none():
    assert pcq.latest_exact(["20261017-025855-energie-service-g-cascade.json"], "service-g-cascade") is None
