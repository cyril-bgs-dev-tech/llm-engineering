"""RM-62 : le LoRA doit pouvoir s'entraîner en plis groupés par auteur, comme l'encodeur (RM-39), sans changer le défaut par patient."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import p1_finetune

REQUIRED = ["Qwen/Qwen3.5-4B", "--mode", "lora", "--lr", "1e-4", "--slug", "essai"]


def test_les_plis_restent_par_patient_par_defaut():
    assert p1_finetune.build_parser().parse_args(REQUIRED).fold_key == "folds"


def test_les_plis_par_auteur_se_demandent_par_la_cle_de_la_partition():
    assert p1_finetune.build_parser().parse_args([*REQUIRED, "--fold-key", "control_folds_by_author"]).fold_key == "control_folds_by_author"


def test_une_cle_de_plis_inconnue_est_refusee():
    import pytest

    with pytest.raises(SystemExit):
        p1_finetune.build_parser().parse_args([*REQUIRED, "--fold-key", "plis_inventes"])


def test_la_cle_de_plis_est_bien_transmise_au_chargement_des_donnees():
    source = (Path(__file__).resolve().parents[1] / "scripts/p1_finetune.py").read_text(encoding="utf-8")
    assert 'p1_04_06_tfidf.load("chapter", a.fold_key)' in source
