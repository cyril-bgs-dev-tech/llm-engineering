"""Réserve R-a du contrat de nuit : les valeurs gelées du protocole (δ, K, B, N) ne doivent dériver dans aucun document de référence."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import check_protocol_drift as cpd

ROOT = Path(__file__).resolve().parents[1]


def test_les_valeurs_de_reference_sont_lues_dans_le_protocole_gele():
    assert cpd.reference_values((ROOT / "PROTOCOLE.md").read_text(encoding="utf-8")) == {"delta": 2.0, "K": 5.0, "B": 90.0, "N": 4.0}


def test_une_valeur_conforme_ecrite_autrement_passe():
    ref = {"delta": 2.0, "K": 5.0, "B": 90.0, "N": 4.0}
    assert cpd.drift("δ = 2 points, K = 5 graines, B = 90 h, N = 4 essais", ref) == []


def test_chaque_valeur_qui_derive_est_signalee_avec_sa_ligne():
    ref = {"delta": 2.0, "K": 5.0, "B": 90.0, "N": 4.0}
    found = cpd.drift("intro\nδ = 3,0 points\nB = 80 h et K = 3\nN = 5", ref)
    assert [(line, name) for line, name, _ in found] == [(2, "delta"), (3, "B"), (3, "K"), (4, "N")]


def test_le_controle_mord_sur_un_document_pieges(tmp_path):
    (tmp_path / "PROTOCOLE.md").write_text((ROOT / "PROTOCOLE.md").read_text(encoding="utf-8"), encoding="utf-8")
    (tmp_path / "MICROTACHES.md").write_text("seuil δ = 2,5 points\n", encoding="utf-8")
    assert cpd.main([str(tmp_path)]) == 1
    (tmp_path / "MICROTACHES.md").write_text("seuil δ = 2,0 points\n", encoding="utf-8")
    assert cpd.main([str(tmp_path)]) == 0
