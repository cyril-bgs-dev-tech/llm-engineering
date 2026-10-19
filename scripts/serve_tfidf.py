#!/usr/bin/env python3
"""Lance le service HTTP du classifieur de chapitre (TF-IDF, ensemble conforme, abstention).
Usage : serve_tfidf.py --bundle DOSSIER [--host 0.0.0.0] [--port 8000] [--reference FICHIER.json]   (avec --reference : moniteur de dérive sur GET /drift, P5-08)."""
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from llmft import http_service, serving
from llmft.drift_monitor import DriftMonitor


def monitor_from(path: str | None) -> DriftMonitor | None:
    """Moniteur de dérive lu dans un fichier de `scripts/reference_prevalence.py` ; aucun sans fichier."""
    if path is None:
        return None
    ref = json.loads(Path(path).read_text(encoding="utf-8"))
    return DriftMonitor(ref["prevalence"], window=int(ref["fenetre"]), threshold=float(ref["seuil_s2"]))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--bundle", required=True)
    ap.add_argument("--host", default="127.0.0.1")
    ap.add_argument("--port", type=int, default=8000)
    ap.add_argument("--reference")
    a = ap.parse_args()
    bundle = serving.load_bundle(a.bundle)  # refuse un fichier modifié (empreinte)
    server = http_service.make_server(bundle, a.host, a.port, monitor_from(a.reference))
    print(f"service prêt sur {a.host}:{a.port} ({len(bundle.labels)} classes)", flush=True)
    server.serve_forever()
    return 0


if __name__ == "__main__":
    sys.exit(main())
