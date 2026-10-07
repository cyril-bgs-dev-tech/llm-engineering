"""Service HTTP minimal du classifieur de chapitre (bibliothèque standard seulement, aucune donnée conservée ni journalisée).

GET /health : état et empreinte du modèle. POST /predict : {"texts": [...], "mode": "marginal"|"famille"} -> étiquette, probabilité calibrée, ensemble conforme, indicateur d'abstention.
Limites : 64 textes par requête, 200 000 caractères par texte, 8 Mo de corps. Le texte des patients n'est ni écrit sur disque ni dans les journaux."""
import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any

from llmft import serving

MAX_TEXTS = 64
MAX_CHARS = 200_000
MAX_BODY_BYTES = 8_000_000


def handle_predict(bundle: serving.Bundle, payload: Any) -> tuple[int, dict[str, Any]]:
    """Validation de l'entrée puis prédiction ; rend (code HTTP, corps JSON)."""
    if not isinstance(payload, dict):
        return 400, {"error": "le corps doit être un objet JSON"}
    texts = payload.get("texts")
    if not isinstance(texts, list) or not texts or len(texts) > MAX_TEXTS:
        return 400, {"error": f"« texts » doit être une liste de 1 à {MAX_TEXTS} chaînes"}
    if not all(isinstance(t, str) and t.strip() and len(t) <= MAX_CHARS for t in texts):
        return 400, {"error": f"chaque texte doit être une chaîne non vide d'au plus {MAX_CHARS} caractères"}
    mode = payload.get("mode", "marginal")
    if mode not in ("marginal", "famille"):
        return 400, {"error": "« mode » doit valoir marginal ou famille"}
    try:
        return 200, {"predictions": serving.predict(bundle, texts, mode)}
    except ValueError as exc:  # mode « famille » sans quantiles par famille
        return 400, {"error": str(exc)}


def make_server(bundle: serving.Bundle, host: str, port: int) -> ThreadingHTTPServer:
    """Serveur multi-fils ; l'appelant lance `serve_forever`."""
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
                self._send(200, {"status": "ok", "n_labels": len(bundle.labels), "model_sha256": bundle.meta.get("model_sha256", ""), "alpha": bundle.alpha})
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
            status, body = handle_predict(bundle, payload)
            self._send(status, body)

        def log_message(self, format: str, *args: Any) -> None:  # aucune ligne de journal : ni chemins ni contenu
            return

    class Server(ThreadingHTTPServer):
        request_queue_size = 128  # la valeur par défaut (5) perd des connexions dès huit clients concurrents

    return Server((host, port), Handler)
