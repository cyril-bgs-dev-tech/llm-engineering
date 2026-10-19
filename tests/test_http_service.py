import json
import threading
import urllib.error
import urllib.request
from pathlib import Path

import numpy as np
import pytest

from llmft import http_service, serving


@pytest.fixture(scope="module")
def bundle_dir(tmp_path_factory: pytest.TempPathFactory) -> Path:
    texts = ["fièvre toux dyspnée pneumonie"] * 6 + ["fracture du fémur chute"] * 6 + ["douleur thoracique infarctus"] * 6
    y = ["X"] * 6 + ["XIX"] * 6 + ["IX"] * 6
    labels = ["IX", "X", "XIX"]
    oof = np.full((18, 3), 0.1)
    oof_y = np.array([1] * 6 + [2] * 6 + [0] * 6)
    for i, k in enumerate(oof_y):
        oof[i, k] = 0.8
    bundle = serving.train_bundle(texts, y, labels, 10.0, (1, 1), oof, oof_y, alpha=0.1, coverage_target=0.7)
    out = tmp_path_factory.mktemp("bundle")
    serving.save_bundle(bundle, out)
    return out


def test_predict_rend_une_prediction_par_texte_sans_conserver_le_texte(bundle_dir: Path):
    bundle = serving.load_bundle(bundle_dir)
    status, body = http_service.handle_predict(bundle, {"texts": ["fièvre toux dyspnée pneumonie", "fracture du fémur chute"]})
    assert status == 200
    assert [p["label"] for p in body["predictions"]] == ["X", "XIX"]
    assert "texts" not in body and "fièvre" not in json.dumps(body)
    assert set(body["predictions"][0]) == {"label", "probability", "set", "abstain"}


@pytest.mark.parametrize("payload", [{}, {"texts": []}, {"texts": "pas une liste"}, {"texts": [1, 2]}, {"texts": ["a"] * 65}, {"texts": ["x" * 200_001]}, {"mode": "inconnu", "texts": ["a"]}])
def test_une_entree_invalide_est_refusee_avec_le_code_400(bundle_dir: Path, payload: dict):
    status, body = http_service.handle_predict(serving.load_bundle(bundle_dir), payload)
    assert status == 400 and "error" in body


def test_le_serveur_repond_sur_health_et_predict_et_refuse_le_reste(bundle_dir: Path):
    server = http_service.make_server(serving.load_bundle(bundle_dir), "127.0.0.1", 0)
    port = server.server_address[1]
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        base = f"http://127.0.0.1:{port}"
        health = json.loads(urllib.request.urlopen(base + "/health", timeout=5).read())
        assert health["status"] == "ok" and health["n_labels"] == 3 and len(health["model_sha256"]) == 64
        req = urllib.request.Request(base + "/predict", data=json.dumps({"texts": ["fracture du fémur chute"]}).encode(), headers={"Content-Type": "application/json"})
        assert json.loads(urllib.request.urlopen(req, timeout=5).read())["predictions"][0]["label"] == "XIX"
        with pytest.raises(urllib.error.HTTPError) as err:
            urllib.request.urlopen(base + "/inconnu", timeout=5)
        assert err.value.code == 404
        bad = urllib.request.Request(base + "/predict", data=b"pas du json", headers={"Content-Type": "application/json"})
        with pytest.raises(urllib.error.HTTPError) as err2:
            urllib.request.urlopen(bad, timeout=5)
        assert err2.value.code == 400
    finally:
        server.shutdown()
        server.server_close()


def test_la_file_d_attente_des_connexions_tient_plus_que_les_cinq_places_par_defaut(bundle_dir: Path):
    """Régression du test de fumée du 07/10 : à huit clients concurrents, la file par défaut (5) faisait perdre des connexions (latences de 1 à 2 s par retransmission TCP)."""
    server = http_service.make_server(serving.load_bundle(bundle_dir), "127.0.0.1", 0)
    try:
        assert server.request_queue_size >= 128
    finally:
        server.server_close()


def test_le_serveur_json_generique_sert_un_predicteur_quelconque_et_valide_l_entree():
    seen: list[list[str]] = []

    def predict(texts: list[str]) -> list[dict]:
        seen.append(texts)
        return [{"label": "A", "probability": 0.9, "stage": "E"} for _ in texts]

    server = http_service.make_json_server(predict, {"status": "ok", "systeme": "factice"}, "127.0.0.1", 0)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        base = f"http://127.0.0.1:{server.server_address[1]}"
        assert json.loads(urllib.request.urlopen(base + "/health", timeout=5).read()) == {"status": "ok", "systeme": "factice"}
        req = urllib.request.Request(base + "/predict", data=json.dumps({"texts": ["un", "deux"]}).encode(), headers={"Content-Type": "application/json"})
        body = json.loads(urllib.request.urlopen(req, timeout=5).read())
        assert [p["stage"] for p in body["predictions"]] == ["E", "E"] and seen == [["un", "deux"]]
        bad = urllib.request.Request(base + "/predict", data=json.dumps({"texts": []}).encode(), headers={"Content-Type": "application/json"})
        with pytest.raises(urllib.error.HTTPError) as err:
            urllib.request.urlopen(bad, timeout=5)
        assert err.value.code == 400 and seen == [["un", "deux"]]
    finally:
        server.shutdown()
        server.server_close()


def test_le_moniteur_de_derive_est_nourri_par_predict_et_lu_sur_drift_sans_texte():
    from llmft.drift_monitor import DriftMonitor

    monitor = DriftMonitor({"A": 1.0}, window=2, threshold=0.2)

    def predict(texts: list[str]) -> list[dict]:
        return [{"label": "B" if "dérive" in t else "A", "probability": 0.9, "stage": "E"} for t in texts]

    server = http_service.make_json_server(predict, {"status": "ok"}, "127.0.0.1", 0, monitor=monitor)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    try:
        base = f"http://127.0.0.1:{server.server_address[1]}"
        req = urllib.request.Request(base + "/predict", data=json.dumps({"texts": ["texte confidentiel dérive", "autre dérive"]}).encode(), headers={"Content-Type": "application/json"})
        urllib.request.urlopen(req, timeout=5).read()
        raw = urllib.request.urlopen(base + "/drift", timeout=5).read().decode("utf-8")
        report = json.loads(raw)
        assert report["n"] == 2 and report["alerte_s2"] is True and report["part_servie_par_e"] == 1.0
        assert "confidentiel" not in raw
    finally:
        server.shutdown()
        server.server_close()


def test_sans_moniteur_drift_n_existe_pas(bundle_dir: Path):
    server = http_service.make_server(serving.load_bundle(bundle_dir), "127.0.0.1", 0)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    try:
        with pytest.raises(urllib.error.HTTPError) as err:
            urllib.request.urlopen(f"http://127.0.0.1:{server.server_address[1]}/drift", timeout=5)
        assert err.value.code == 404
    finally:
        server.shutdown()
        server.server_close()


def test_le_service_tfidf_nourrit_aussi_le_moniteur(bundle_dir: Path):
    from llmft.drift_monitor import DriftMonitor

    monitor = DriftMonitor({"IX": 1 / 3, "X": 1 / 3, "XIX": 1 / 3}, window=10, threshold=0.2)
    status, _ = http_service.handle_predict(serving.load_bundle(bundle_dir), {"texts": ["fracture du fémur chute"]}, monitor)
    assert status == 200 and monitor.report()["observations_totales"] == 1
    status, _ = http_service.handle_predict(serving.load_bundle(bundle_dir), {"texts": []}, monitor)
    assert status == 400 and monitor.report()["observations_totales"] == 1
