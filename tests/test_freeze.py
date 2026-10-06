import json
from pathlib import Path

import pytest

from llmft import freeze

ENC = (1000, 1001)


def write_run(runs: Path, stamp: str, slug: str, sha: str) -> None:
    (runs / f"{stamp}-{slug}.json").write_text(json.dumps({"run_id": f"{stamp}-{slug}", "slug": slug, "status": "ok", "metrics": {"sha256": sha}}), encoding="utf-8")


@pytest.fixture
def runs(tmp_path: Path) -> Path:
    for name in ("tfidf", "encoder-s1000", "encoder-s1001", "lora-s1000"):
        slug = "final-" + name
        write_run(tmp_path, "20261005-100000", slug, f"model-{name}")
        write_run(tmp_path, "20261005-110000", "temps-a-" + name, f"preds-{name}")
    return tmp_path


def test_le_gel_cite_pour_chaque_composant_les_runs_et_les_empreintes(runs: Path):
    frozen = freeze.build_frozen(runs, enc_seeds=ENC, lora_seeds=(1000,))
    lora = frozen["modeles"]["lora-s1000"]
    assert lora == {"run_entrainement": "20261005-100000-final-lora-s1000", "sha256_modele": "model-lora-s1000", "run_temps_a": "20261005-110000-temps-a-lora-s1000", "sha256_temps_a": "preds-lora-s1000"}
    assert set(frozen["modeles"]) == {"tfidf", "encoder-s1000", "encoder-s1001", "lora-s1000"}


def test_le_gel_fixe_le_systeme_la_reference_et_les_parts_egales(runs: Path):
    frozen = freeze.build_frozen(runs, enc_seeds=ENC, lora_seeds=(1000,))
    assert frozen["final"] == "G LoRA + encodeur + TF-IDF" and frozen["reference"] == "A TF-IDF" and frozen["delta"] == 2.0
    assert frozen["composition"]["poids"] == "un tiers LoRA, un tiers encodeur (moyenne de ses graines), un tiers TF-IDF"


def test_un_run_manquant_refuse_le_gel(runs: Path):
    next(runs.glob("*temps-a-lora-s1000.json")).unlink()
    with pytest.raises(FileNotFoundError, match="temps-a-lora-s1000"):
        freeze.build_frozen(runs, enc_seeds=ENC, lora_seeds=(1000,))


def test_deux_runs_du_meme_nom_refusent_le_gel_au_lieu_d_en_choisir_un(runs: Path):
    write_run(runs, "20261006-090000", "final-tfidf", "autre")
    with pytest.raises(ValueError, match="final-tfidf"):
        freeze.build_frozen(runs, enc_seeds=ENC, lora_seeds=(1000,))
