"""P5-11 : démo locale, règles de la page wiki regles-de-formulation (locale, textes fictifs du corpus, bannière, aucune aide au codage ou au diagnostic)."""
import json
import sys
import threading
import urllib.error
import urllib.request
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import demo_locale

EXAMPLES = [{"id": "PAT-1", "texte": "Compte rendu fictif : douleur thoracique </script><b>gras</b>", "chapitre_scenario": "IX"},
            {"id": "PAT-2", "texte": "Compte rendu fictif : fracture du fémur", "chapitre_scenario": "XIX"}]
NAMES = {"IX": "Chapitre IX : Maladies de l'appareil circulatoire", "XIX": "Chapitre XIX : Lésions traumatiques"}


def fake_predict(texts: list[str]) -> list[dict]:
    return [{"label": "IX" if "thoracique" in t else "XIX", "probability": 0.9} for t in texts]


@pytest.mark.parametrize("host", ["127.0.0.1", "localhost", "::1"])
def test_la_boucle_locale_est_acceptee(host: str) -> None:
    assert demo_locale.check_host(host) == host


@pytest.mark.parametrize("host", ["0.0.0.0", "192.168.1.10", "", "::"])
def test_toute_autre_adresse_est_refusee(host: str) -> None:
    with pytest.raises(ValueError, match="locale"):
        demo_locale.check_host(host)


def test_la_page_porte_la_banniere_et_l_attribution_sans_ressource_externe() -> None:
    page = demo_locale.render_page(EXAMPLES)
    assert demo_locale.BANNER in page
    assert "CC BY 4.0" in page
    assert "http://" not in page and "https://" not in page


def test_le_texte_d_un_exemple_ne_peut_pas_fermer_le_script_de_la_page() -> None:
    page = demo_locale.render_page(EXAMPLES)
    assert "</script><b>" not in page
    assert page.count("</script>") == 1


def test_un_exemple_de_la_liste_est_classe_avec_le_nom_du_chapitre_et_l_etiquette_du_scenario() -> None:
    status, body = demo_locale.handle({"id": "PAT-2"}, {e["id"]: e for e in EXAMPLES}, fake_predict, NAMES)
    assert status == 200
    assert body["prediction"]["label"] == "XIX"
    assert body["nom_chapitre"] == NAMES["XIX"]
    assert body["chapitre_scenario"] == "XIX"


@pytest.mark.parametrize("payload", [{"texts": ["un texte libre"]}, {"id": "PAT-1", "texts": ["x"]}, "PAT-1", None, {"id": 3}])
def test_aucune_saisie_libre_n_est_acceptee(payload: object) -> None:
    status, body = demo_locale.handle(payload, {e["id"]: e for e in EXAMPLES}, fake_predict, NAMES)
    assert status == 400 and "error" in body


def test_un_identifiant_inconnu_rend_404() -> None:
    status, _ = demo_locale.handle({"id": "PAT-9"}, {e["id"]: e for e in EXAMPLES}, fake_predict, NAMES)
    assert status == 404


def test_chapter_names_relie_les_etiquettes_du_modele_aux_noms_du_contrat() -> None:
    names = demo_locale.chapter_names(Path(__file__).resolve().parents[1] / "task_specs/parhaf_cim10_chapter.yaml")
    assert names["II"] == "Chapitre II : Tumeurs"
    assert "AUTRE" in names and len(names) == 18


def test_le_serveur_sert_la_page_et_classe_un_exemple_sans_journaliser() -> None:
    server = demo_locale.make_demo_server(EXAMPLES, fake_predict, NAMES, "127.0.0.1", 0)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    base = f"http://127.0.0.1:{server.server_address[1]}"
    try:
        with urllib.request.urlopen(base + "/") as r:
            assert r.headers["Content-Type"].startswith("text/html")
            assert "default-src 'none'" in r.headers["Content-Security-Policy"]
            assert demo_locale.BANNER in r.read().decode("utf-8")
        req = urllib.request.Request(base + "/predict", data=json.dumps({"id": "PAT-1"}).encode(), headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req) as r:
            assert json.loads(r.read())["prediction"]["label"] == "IX"
        free = urllib.request.Request(base + "/predict", data=json.dumps({"texts": ["libre"]}).encode(), headers={"Content-Type": "application/json"})
        with pytest.raises(urllib.error.HTTPError) as err:
            urllib.request.urlopen(free)
        assert err.value.code == 400
    finally:
        server.shutdown()
        server.server_close()
