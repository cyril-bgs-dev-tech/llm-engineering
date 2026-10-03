"""Classement d'un échec par le code, à partir de l'historique de perte (PROTOCOLE.md 6.4, P1-19)."""
import json
import math

import pytest

from llmft import failures


def test_perte_non_finie_est_une_divergence():
    assert failures.classify([2.3, 1.9, float("nan")]) == "divergence"
    assert failures.classify([2.3, math.inf]) == "divergence"


def test_perte_non_finie_puis_memoire_reste_une_divergence():
    # cas piégé : la panne mémoire arrive après la perte non finie ; l'historique décide, pas le message d'erreur
    assert failures.classify([2.3, float("nan")], error="CUDA out of memory") == "divergence"


def test_memoire_seule_est_une_panne_d_infrastructure():
    assert failures.classify([2.3, 1.9, 1.7], error="CUDA out of memory") == "infrastructure"
    assert failures.classify([], error="coupure") == "infrastructure"


def test_relance_de_la_meme_graine_autorisee_apres_panne_seulement():
    outage = {"status": "failed", "loss_history": [2.0, 1.8], "failure_class": "infrastructure"}
    crash = {"status": "failed", "loss_history": [2.0, float("inf")], "failure_class": "divergence"}
    assert failures.may_retry([outage]) is True
    assert failures.may_retry([crash]) is False
    assert failures.may_retry([crash, {"status": "failed", "loss_history": [1.0], "failure_class": "infrastructure"}]) is False  # une divergence passée ferme la graine
    assert failures.may_retry([outage, {"status": "ok"}]) is False  # déjà abouti
    assert failures.may_retry([]) is False  # rien à relancer


def test_enregistrement_d_un_echec_exige_l_historique_et_pose_le_classement(tmp_path):
    with pytest.raises(ValueError, match="loss_history"):
        failures.register_failed(tmp_path, {"kind": "train", "slug": "x", "summary": "s"})
    path = failures.register_failed(tmp_path, {"kind": "train", "slug": "x", "summary": "s", "loss_history": [1.0, float("nan")], "error": "oom"})
    rec = json.loads(path.read_text(encoding="utf-8"))
    assert rec["status"] == "failed" and rec["failure_class"] == "divergence"
