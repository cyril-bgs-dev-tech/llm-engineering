"""Gardes des fiches préenregistrées (règles N29, N37 et N41 du contrat de nuit) : empreintes, heures futures, constantes de décision."""
import hashlib
from datetime import UTC, datetime
from pathlib import Path

from llmft import fiches


def _index(rel: str, digest: str) -> str:
    return f"| 2026-10-17 | Fiche | `{rel}` | `{digest}` | premier run |\n"


def test_une_fiche_modifiee_apres_son_hachage_est_signalee(tmp_path: Path) -> None:
    (tmp_path / "experiments").mkdir()
    fiche = tmp_path / "experiments/2026-10-17-x.md"
    fiche.write_text("question : avant\n", encoding="utf-8")
    index = _index("experiments/2026-10-17-x.md", hashlib.sha256(fiche.read_bytes()).hexdigest())
    assert fiches.check_fiche_hashes(index, tmp_path) == ([], 1)
    fiche.write_text("question : après\n", encoding="utf-8")
    problems, _ = fiches.check_fiche_hashes(index, tmp_path)
    assert problems == ["fiche modifiée après son hachage : experiments/2026-10-17-x.md"]


def test_une_fiche_absente_ou_sans_empreinte_est_signalee(tmp_path: Path) -> None:
    (tmp_path / "experiments").mkdir()
    (tmp_path / "experiments/2026-10-17-orpheline.md").write_text("q\n", encoding="utf-8")
    problems, n = fiches.check_fiche_hashes(_index("experiments/2026-10-17-absente.md", "0" * 64), tmp_path)
    assert n == 1
    assert "fiche citée absente : experiments/2026-10-17-absente.md" in problems
    assert "fiche sans empreinte dans l'index : experiments/2026-10-17-orpheline.md" in problems


def test_une_heure_posterieure_au_moment_de_l_ecriture_est_refusee() -> None:
    now = datetime(2026, 10, 17, 19, 44, 13, tzinfo=UTC)
    assert fiches.future_times("Écrite le 17/10/2026 vers 20:10Z, avant tout run.", now) == ["17/10/2026 20:10Z"]
    assert fiches.future_times("Écrite le 17/10/2026 à 19:44Z ; panne le 16/10/2026 à 23:02Z ; 2026-10-17T10:09:52Z.", now) == []
    assert fiches.future_times("fin prévue le 2026-10-18T06:15:00Z", now) == ["2026-10-18T06:15:00Z"]


def test_une_heure_sans_date_n_est_pas_jugee() -> None:
    assert fiches.future_times("pli 2 lancé à 23:59Z", datetime(2026, 10, 17, 1, 0, tzinfo=UTC)) == []


def test_les_constantes_de_decision_sont_cherchees_sous_leur_forme_ecrite_en_francais() -> None:
    text = "seuil 0,05 ; au moins 0,08 ; 2 000 tirages, graine 20261017 ; moitiés graine 1000 ; α = 0,10"
    assert fiches.missing_constants(text, (0.05, 0.08, 2000, 20261017, 1000, 0.1)) == []
    assert fiches.missing_constants(text, (0.06, 0.5, 200, 3000)) == [0.06, 0.5, 200, 3000]


def test_une_constante_ne_se_retrouve_pas_dans_un_nombre_plus_long() -> None:
    assert fiches.missing_constants("au plus 0,15 et 20 001 patients", (0.1, 1, 2000)) == [0.1, 1, 2000]
