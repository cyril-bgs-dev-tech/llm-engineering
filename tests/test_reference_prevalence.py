"""P5-08 (branchement) : fichier de référence du moniteur de dérive et activation du moniteur par les lanceurs de service."""
import json
import sys
from pathlib import Path

import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import reference_prevalence
import serve_tfidf


def test_le_fichier_de_reference_porte_la_prevalence_le_seuil_mesure_et_sa_source() -> None:
    probs = np.array([[0.9, 0.1], [0.2, 0.8], [0.7, 0.3], [0.6, 0.4]])
    p = reference_prevalence.payload("tfidf", probs, ["IX", "XIX"], "fichier-source")
    assert p["prevalence"] == {"IX": 0.75, "XIX": 0.25}
    assert p["seuil_s2"] == 0.207 and p["fenetre"] == 100 and p["run_seuil"] == "20261017-090325-simulation-derive"
    assert p["systeme"] == "tfidf" and p["source"] == "fichier-source"


def test_la_cascade_prend_e_quand_il_atteint_tau_sinon_g() -> None:
    e = np.array([[0.7, 0.3], [0.55, 0.45]])
    g = np.array([[0.1, 0.9], [0.1, 0.9]])
    assert reference_prevalence.cascade_argmax_probs(e, g, 0.6).argmax(axis=1).tolist() == [0, 1]


def test_sans_reference_le_lanceur_ne_branche_aucun_moniteur() -> None:
    assert serve_tfidf.monitor_from(None) is None


def test_avec_reference_le_lanceur_branche_un_moniteur_au_seuil_du_fichier(tmp_path: Path) -> None:
    f = tmp_path / "ref.json"
    f.write_text(json.dumps({"prevalence": {"IX": 0.5, "XIX": 0.5}, "seuil_s2": 0.3, "fenetre": 7}), encoding="utf-8")
    m = serve_tfidf.monitor_from(str(f))
    assert m is not None and m.threshold == 0.3 and m.window == 7


def test_une_reference_mal_formee_est_refusee(tmp_path: Path) -> None:
    f = tmp_path / "ref.json"
    f.write_text(json.dumps({"prevalence": {"IX": 0.5}, "seuil_s2": 0.3, "fenetre": 7}), encoding="utf-8")
    with pytest.raises(ValueError):
        serve_tfidf.monitor_from(str(f))
