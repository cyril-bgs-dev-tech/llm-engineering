"""RM-62 : le diagnostic de robustesse du LoRA doit pouvoir tourner sur le pli évalué de chaque run en plis d'auteurs, sans changer son comportement par défaut (pli 0 par patient)."""
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import robustness_lora_diag as rld


def test_par_defaut_le_diagnostic_reste_sur_le_pli_0_par_patient_et_l_adaptateur_historique():
    c = rld.cli(["robustness_lora_diag.py"])
    assert (c["fold"], c["fold_key"], c["adapter"], c["suffix"]) == (0, "folds", "llm-mur2-qwen3-5-4b-ep10-lr1e-4", "")


def test_un_pli_d_auteurs_et_un_adaptateur_se_choisissent_en_ligne_de_commande():
    c = rld.cli(["x", "--adapter", "lora-fin-aleatoire-auteur-pli3", "--fold", "3", "--fold-key", "control_folds_by_author", "--fiche", "experiments/f.md"])
    assert (c["fold"], c["fold_key"], c["suffix"], c["fiche"]) == (3, "control_folds_by_author", "-lora-fin-aleatoire-auteur-pli3", "experiments/f.md")


def test_une_cle_de_plis_inconnue_est_refusee():
    with pytest.raises(SystemExit):
        rld.cli(["x", "--fold-key", "plis_inventes"])


def test_le_pli_et_la_cle_choisis_servent_au_chargement_et_a_la_selection():
    source = (Path(__file__).resolve().parents[1] / "scripts/robustness_lora_diag.py").read_text(encoding="utf-8")
    assert 'p1_04_06_tfidf.load("chapter", c["fold_key"])' in source and 'np.where(folds == c["fold"])' in source
