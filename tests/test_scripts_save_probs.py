"""Garde : tout script qui produit des prédictions de modèle doit en conserver les probabilités (calibration, conforme, sélectif en dépendent)."""
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"


def test_les_scripts_de_prediction_sauvent_les_probabilites():
    for name in ("p1_finetune.py", "p1_04_06_tfidf.py"):
        assert "probs.npz" in (SCRIPTS / name).read_text(encoding="utf-8"), f"{name} ne sauvegarde pas les probabilités"
