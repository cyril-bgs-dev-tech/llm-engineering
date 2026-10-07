#!/usr/bin/env python3
"""Lance le service HTTP du classifieur de chapitre (TF-IDF, ensemble conforme, abstention). Usage : serve_tfidf.py --bundle DOSSIER [--host 0.0.0.0] [--port 8000]."""
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from llmft import http_service, serving


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--bundle", required=True)
    ap.add_argument("--host", default="127.0.0.1")
    ap.add_argument("--port", type=int, default=8000)
    a = ap.parse_args()
    bundle = serving.load_bundle(a.bundle)  # refuse un fichier modifié (empreinte)
    server = http_service.make_server(bundle, a.host, a.port)
    print(f"service prêt sur {a.host}:{a.port} ({len(bundle.labels)} classes)", flush=True)
    server.serve_forever()
    return 0


if __name__ == "__main__":
    sys.exit(main())
