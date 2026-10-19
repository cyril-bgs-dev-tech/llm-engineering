"""Service HTTP minimal du classifieur de chapitre (bibliothèque standard seulement, aucune donnée conservée ni journalisée).

GET /health : état et empreinte du modèle. POST /predict : {"texts": [...], "mode": "marginal"|"famille"} -> étiquette, probabilité calibrée, ensemble conforme, indicateur d'abstention.
GET /drift (si un moniteur est branché, P5-08) : agrégats de dérive sur les dernières prédictions (`llmft.drift_monitor`), aucun texte.
Limites : 64 textes par requête, 200 000 caractères par texte, 8 Mo de corps. Le texte des patients n'est ni écrit sur disque ni dans les journaux."""
import json
from collections.abc import Callable
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any

from llmft import serving
from llmft.drift_monitor import DriftMonitor

MAX_TEXTS = 64
MAX_CHARS = 200_000
MAX_BODY_BYTES = 8_000_000


def validate_texts(payload: Any) -> tuple[list[str], str | None]:
    """Textes d'une requête validés à la frontière ; rend (textes, None) ou ([], message d'erreur)."""
    if not isinstance(payload, dict):
        return [], "le corps doit être un objet JSON"
    texts = payload.get("texts")
    if not isinstance(texts, list) or not texts or len(texts) > MAX_TEXTS:
        return [], f"« texts » doit être une liste de 1 à {MAX_TEXTS} chaînes"
    if not all(isinstance(t, str) and t.strip() and len(t) <= MAX_CHARS for t in texts):
        return [], f"chaque texte doit être une chaîne non vide d'au plus {MAX_CHARS} caractères"
    return texts, None


def _observed(predictions: list[dict[str, Any]], monitor: DriftMonitor | None) -> list[dict[str, Any]]:
    if monitor is not None:
        for p in predictions:
            monitor.observe(p)
    return predictions


def handle_predict(bundle: serving.Bundle, payload: Any, monitor: DriftMonitor | None = None) -> tuple[int, dict[str, Any]]:
    """Validation de l'entrée puis prédiction ; rend (code HTTP, corps JSON) ; les prédictions servies nourrissent le moniteur s'il y en a un."""
    texts, error = validate_texts(payload)
    if error is not None:
        return 400, {"error": error}
    mode = payload.get("mode", "marginal")
    if mode not in ("marginal", "famille"):
        return 400, {"error": "« mode » doit valoir marginal ou famille"}
    try:
        return 200, {"predictions": _observed(serving.predict(bundle, texts, mode), monitor)}
    except ValueError as exc:  # mode « famille » sans quantiles par famille
        return 400, {"error": str(exc)}


def make_server(bundle: serving.Bundle, host: str, port: int, monitor: DriftMonitor | None = None) -> ThreadingHTTPServer:
    """Serveur multi-fils du TF-IDF ; l'appelant lance `serve_forever`."""
    health = {"status": "ok", "n_labels": len(bundle.labels), "model_sha256": bundle.meta.get("model_sha256", ""), "alpha": bundle.alpha}
    return _serve(lambda payload: handle_predict(bundle, payload, monitor), health, host, port, monitor)


def make_json_server(predict: Callable[[list[str]], list[dict[str, Any]]], health: dict[str, Any], host: str, port: int,
                     monitor: DriftMonitor | None = None) -> ThreadingHTTPServer:
    """Même serveur pour un prédicteur quelconque (G en cascade, RM-60) : mêmes limites et même validation des textes ; l'appelant protège le GPU par un verrou s'il le faut."""
    def handle(payload: Any) -> tuple[int, dict[str, Any]]:
        texts, error = validate_texts(payload)
        if error is not None:
            return 400, {"error": error}
        return 200, {"predictions": _observed(predict(texts), monitor)}

    return _serve(handle, health, host, port, monitor)


def _serve(handle: Callable[[Any], tuple[int, dict[str, Any]]], health: dict[str, Any], host: str, port: int, monitor: DriftMonitor | None = None) -> ThreadingHTTPServer:
    class Handler(BaseHTTPRequestHandler):
        def _send(self, status: int, body: dict[str, Any]) -> None:
            raw = json.dumps(body, ensure_ascii=False).encode("utf-8")
            self.send_response(status)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(raw)))
            self.end_headers()
            self.wfile.write(raw)

        def do_GET(self) -> None:
            if self.path == "/health":
                self._send(200, health)
            elif self.path == "/drift" and monitor is not None:
                self._send(200, monitor.report())
            else:
                self._send(404, {"error": "inconnu"})

        def do_POST(self) -> None:
            if self.path != "/predict":
                self._send(404, {"error": "inconnu"})
                return
            length = int(self.headers.get("Content-Length", "0"))
            if length <= 0 or length > MAX_BODY_BYTES:
                self._send(400, {"error": "corps absent ou trop grand"})
                return
            try:
                payload = json.loads(self.rfile.read(length))
            except ValueError:
                self._send(400, {"error": "JSON invalide"})
                return
            status, body = handle(payload)
            self._send(status, body)

        def log_message(self, format: str, *args: Any) -> None:  # aucune ligne de journal : ni chemins ni contenu
            return

    class Server(ThreadingHTTPServer):
        request_queue_size = 128  # la valeur par défaut (5) perd des connexions dès huit clients concurrents

    return Server((host, port), Handler)
