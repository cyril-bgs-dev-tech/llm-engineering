import pytest

from llmft import stress


def trial(arm: str, code: int = 0, digest: str | None = "aaa", error: str | None = None) -> stress.Trial:
    return stress.Trial(arm=arm, returncode=code, digest=digest, error=error)


def test_un_bras_sans_panne_a_un_taux_nul_et_aucune_divergence():
    out = stress.summarize([trial("libre"), trial("libre"), trial("cpu-3")])
    assert out["libre"].n == 2 and out["libre"].crashes == 0 and out["libre"].mismatches == 0
    assert out["cpu-3"].crash_rate == 0.0


def test_un_code_de_sortie_non_nul_compte_comme_panne_et_garde_la_signature():
    out = stress.summarize([trial("libre"), trial("libre", code=139, digest=None), trial("libre", code=1, digest=None, error="TypeError")])
    assert out["libre"].crashes == 2
    assert out["libre"].crash_rate == 2 / 3
    assert out["libre"].signatures == {"139": 1, "TypeError": 1}


def test_une_empreinte_differente_de_la_majoritaire_est_une_divergence_silencieuse():
    out = stress.summarize([trial("cpu-1"), trial("cpu-2"), trial("cpu-2", digest="bbb"), trial("libre")])
    assert out["cpu-2"].mismatches == 1
    assert out["cpu-1"].mismatches == 0


def test_l_empreinte_de_reference_est_la_plus_frequente_parmi_les_succes_seulement():
    out = stress.summarize([trial("a", digest="x"), trial("a", digest="x"), trial("b", digest="y"), trial("b", code=139, digest=None)])
    assert out["b"].mismatches == 1 and out["b"].crashes == 1


def test_sans_essai_la_synthese_est_vide_et_un_essai_reussi_sans_empreinte_est_refuse():
    assert stress.summarize([]) == {}
    with pytest.raises(ValueError, match="empreinte"):
        stress.summarize([trial("a", code=0, digest=None)])
