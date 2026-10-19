from llmft import claims


def test_known_slug_and_suffix_references_are_accepted() -> None:
    known = {"20261004-070113-llm-mur2-qwen3-5-4b-ep10-lr1e-4", "tfidf-loao"}
    text = "voir `llm-mur2-qwen3-5-4b-ep10-lr1e-4` et `tfidf-loao` et `20261004-070113-llm-mur2-qwen3-5-4b-ep10-lr1e-4`"
    assert claims.unknown_run_references(text, known, allow=set()) == []


def test_unknown_run_like_token_is_reported() -> None:
    assert claims.unknown_run_references("le run `camembert-inconnu-ep10` a donné", {"tfidf-loao"}, allow=set()) == ["camembert-inconnu-ep10"]


def test_allowlisted_and_short_tokens_and_paths_are_ignored() -> None:
    text = "`claim-gate` `make` `scripts/x.py` `a-b` `RESULTATS.md`"
    assert claims.unknown_run_references(text, set(), allow={"claim-gate"}) == []


RECORDS = {
    "20261007-094900-frontiere-cout-qualite": {"run_id": "20261007-094900-frontiere-cout-qualite", "slug": "frontiere-cout-qualite",
                                               "metrics": {"g": {"macro_f1": 0.77991}, "ic": [-2.789, 6.41], "part": 0.934}},
}


def test_les_chiffres_balises_sont_extraits_avec_leur_cle():
    html = '<p>G fait <span class="n" data-claim="g-f1">0,7799</span> et <span data-claim="part">93,4</span> %</p>'
    assert claims.claim_spans(html) == [("g-f1", "0,7799"), ("part", "93,4")]


def test_le_format_francais_utilise_la_virgule_et_le_vrai_signe_moins():
    assert claims.format_fr(0.77991, 4) == "0,7799"
    assert claims.format_fr(-2.789, 2, signed=True) == "−2,79"
    assert claims.format_fr(6.41, 2, signed=True) == "+6,41"
    assert claims.format_fr(3586, 0) == "3 586"


def test_un_chiffre_conforme_au_registre_passe():
    ledger = {"g-f1": {"run": "20261007-094900-frontiere-cout-qualite", "path": "metrics.g.macro_f1", "decimals": 4}}
    assert claims.check_claim_values([("g-f1", "0,7799")], ledger, RECORDS) == []


def test_un_chiffre_different_du_registre_est_refuse():
    ledger = {"g-f1": {"run": "20261007-094900-frontiere-cout-qualite", "path": "metrics.g.macro_f1", "decimals": 4}}
    errors = claims.check_claim_values([("g-f1", "0,7800")], ledger, RECORDS)
    assert len(errors) == 1 and "0,7799" in errors[0]


def test_une_borne_d_intervalle_se_lit_par_indice_et_echelle():
    ledger = {"bas": {"run": "frontiere-cout-qualite", "path": "metrics.ic.0", "decimals": 2, "signed": True},
              "part": {"run": "frontiere-cout-qualite", "path": "metrics.part", "decimals": 1, "scale": 100}}
    assert claims.check_claim_values([("bas", "−2,79"), ("part", "93,4")], ledger, RECORDS) == []


def test_une_cle_absente_du_registre_des_affirmations_est_refusee():
    assert "inconnue" in claims.check_claim_values([("rien", "1")], {}, RECORDS)[0]


def test_un_run_introuvable_est_refuse():
    ledger = {"x": {"run": "run-qui-n-existe-pas", "path": "metrics.a", "decimals": 1}}
    assert "introuvable" in claims.check_claim_values([("x", "1,0")], ledger, RECORDS)[0]


def test_un_champ_absent_du_run_est_refuse():
    ledger = {"x": {"run": "frontiere-cout-qualite", "path": "metrics.g.latence", "decimals": 1}}
    assert "champ" in claims.check_claim_values([("x", "1,0")], ledger, RECORDS)[0]


def test_un_slug_porte_par_plusieurs_runs_est_ambigu():
    records = {**RECORDS, "20261008-000000-frontiere-cout-qualite": {**RECORDS["20261007-094900-frontiere-cout-qualite"], "run_id": "20261008-000000-frontiere-cout-qualite"}}
    ledger = {"g-f1": {"run": "frontiere-cout-qualite", "path": "metrics.g.macro_f1", "decimals": 4}}
    assert "ambigu" in claims.check_claim_values([("g-f1", "0,7799")], ledger, records)[0]


def test_un_chemin_en_liste_atteint_une_cle_qui_contient_un_point():
    """Le registre a des clés comme « 0.7 » (seuil d'abstention) : un chemin pointé ne peut pas les désigner, une liste de clés le peut (17/10)."""
    records = {"r-1": {"run_id": "r-1", "slug": "s", "metrics": {"abstention": {"0.7": {"exactitude": 0.962}}}}}
    ledger = {"k": {"run": "r-1", "path": ["metrics", "abstention", "0.7", "exactitude"], "decimals": 3}}
    assert claims.check_claim_values([("k", "0,962")], ledger, records) == []
    assert claims.check_claim_values([("k", "0,963")], ledger, records) != []
