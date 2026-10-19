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


REF = "df902b17"


def libres(n_ok: int, crashes: int = 0, divergent: int = 0) -> list[stress.Trial]:
    return ([stress.Trial("libre", 0, REF)] * n_ok + [stress.Trial("libre", 139, None)] * crashes
            + [stress.Trial("libre", 0, "autre")] * divergent)


def test_une_seule_panne_apres_la_mise_a_jour_signifie_machine_toujours_instable():
    v = stress.bios_verdict(libres(120, crashes=8), libres(127, crashes=1), reference_digest=REF)
    assert v.label == "toujours instable"


def test_une_empreinte_differente_de_la_reference_apres_la_mise_a_jour_signifie_toujours_instable():
    v = stress.bios_verdict(libres(120, crashes=8), libres(127, divergent=1), reference_digest=REF)
    assert v.label == "toujours instable"


def test_zero_panne_apres_et_pannes_avant_significatives_donne_stabilisee():
    v = stress.bios_verdict(libres(118, crashes=10), libres(128), reference_digest=REF)
    assert v.label == "stabilisée"
    assert v.p_value < 0.05


def test_zero_panne_apres_sans_pannes_avant_ne_demontre_pas_l_effet():
    v = stress.bios_verdict(libres(128), libres(128), reference_digest=REF)
    assert v.label == "aucune panne après, effet non démontré"


def test_trop_peu_d_essais_apres_n_est_pas_concluant():
    v = stress.bios_verdict(libres(118, crashes=10), libres(60), reference_digest=REF)
    assert v.label == "non concluant"


def test_la_reference_d_empreinte_est_imposee_et_non_la_majoritaire():
    # tous les essais d'après concordent entre eux mais diffèrent de la référence d'avant la mise à jour : résultat changé
    v = stress.bios_verdict(libres(118, crashes=10), [stress.Trial("libre", 0, "autre")] * 128, reference_digest=REF)
    assert v.label == "toujours instable"
