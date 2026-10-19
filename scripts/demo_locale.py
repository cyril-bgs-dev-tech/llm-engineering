#!/usr/bin/env python3
"""Démo locale (P5-11) : page web servie sur la boucle locale seulement, avec la bannière des règles de formulation (page wiki `regles-de-formulation`) ;
classement par chapitre CIM-10 de comptes rendus **fictifs** du corpus PARHAF (CC BY 4.0) choisis dans une liste : aucune saisie libre, aucun texte journalisé.
Les exemples viennent du développement (pli 0), vus à l'entraînement par le modèle servi : la démo montre le fonctionnement, pas la qualité (voir RESULTATS.md).
Usage : demo_locale.py --bundle DOSSIER [--n 12] [--port 8090]   (TF-IDF servi, processeur seulement)
        demo_locale.py --backend g [--n 12] [--port 8090]   (G en cascade E puis G, GPU libre, sous run_guarded.sh) ; adresse toujours 127.0.0.1"""
import argparse
import json
import sys
from collections.abc import Callable
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent))
from llmft import taskspec

LOOPBACK = ("127.0.0.1", "localhost", "::1")
BANNER = "Données fictives (corpus PARHAF), recherche seulement : pas d'usage clinique, ni aide au codage, ni aide au diagnostic."
CONTRACT = ROOT / "task_specs/parhaf_cim10_chapter.yaml"
EXCERPT_CHARS = 1500
MAX_BODY_BYTES = 1_000
CSP = "default-src 'none'; script-src 'unsafe-inline'; style-src 'unsafe-inline'; connect-src 'self'"
Predict = Callable[[list[str]], list[dict[str, Any]]]


def check_host(host: str) -> str:
    """Démo publique interdite (règles de formulation) : seule la boucle locale est acceptée."""
    if host not in LOOPBACK:
        raise ValueError(f"adresse {host!r} refusée : la démo n'écoute que sur la boucle locale ({', '.join(LOOPBACK)})")
    return host


def chapter_names(contract: Path) -> dict[str, str]:
    """Étiquette du modèle (« II », « AUTRE ») vers le nom en clair de la classe dans le contrat."""
    spec = taskspec.load_task_spec(contract)
    return {("AUTRE" if c.id == "autre" else c.id.removeprefix("ch_").upper()): c.name for c in spec.classes}


def render_page(examples: list[dict[str, str]]) -> str:
    data = json.dumps([{"id": e["id"], "extrait": e["texte"][:EXCERPT_CHARS], "chapitre_scenario": e["chapitre_scenario"]} for e in examples], ensure_ascii=False)
    data = data.replace("<", "\\u003c").replace(">", "\\u003e")  # aucun texte d'exemple ne peut fermer la balise script
    return f"""<!doctype html>
<html lang="fr"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>Démo locale, données fictives</title>
<style>
body {{ font-family: system-ui, sans-serif; margin: 0 auto; max-width: 860px; padding: 16px; color: #1d1d1f; background: #fafafa; }}
.banniere {{ background: #fff3cd; border: 2px solid #b8860b; padding: 12px 16px; font-weight: 600; border-radius: 6px; }}
pre {{ white-space: pre-wrap; background: #fff; border: 1px solid #ddd; padding: 12px; max-height: 320px; overflow: auto; }}
.resultat {{ background: #fff; border: 1px solid #ccc; padding: 12px; border-radius: 6px; }}
select, button {{ font-size: 1rem; padding: 6px; }}
small {{ color: #555; }}
</style></head><body>
<p class="banniere">{BANNER}</p>
<h1>Classement par chapitre CIM-10 du scénario</h1>
<p>Choisissez un compte rendu <strong>fictif</strong> du corpus ; le modèle servi propose le chapitre du diagnostic principal de son scénario. L'étiquette du corpus est le diagnostic du scénario suggéré aux rédacteurs, pas un codage médical. Les exemples ont été vus à l'entraînement du modèle servi : cette page montre le fonctionnement, pas la qualité.</p>
<p><select id="choix"></select> <button id="classer">Classer</button></p>
<pre id="texte"></pre>
<div class="resultat" id="resultat">Aucun classement demandé.</div>
<p><small>Corpus PARHAF, licence CC BY 4.0 (attribution aux auteurs du corpus). Démo locale de recherche : aucun texte n'est conservé ni journalisé.</small></p>
<script>
const EXEMPLES = {data};
const choix = document.getElementById("choix"), texte = document.getElementById("texte"), resultat = document.getElementById("resultat");
EXEMPLES.forEach((e, i) => {{ const o = document.createElement("option"); o.value = i; o.textContent = e.id; choix.appendChild(o); }});
function montrer() {{ texte.textContent = EXEMPLES[choix.value].extrait; resultat.textContent = "Aucun classement demandé."; }}
choix.addEventListener("change", montrer); montrer();
document.getElementById("classer").addEventListener("click", async () => {{
  const r = await fetch("/predict", {{ method: "POST", headers: {{ "Content-Type": "application/json" }}, body: JSON.stringify({{ id: EXEMPLES[choix.value].id }}) }});
  const b = await r.json();
  if (!r.ok) {{ resultat.textContent = "Erreur : " + b.error; return; }}
  const p = b.prediction, lignes = ["Chapitre proposé : " + b.nom_chapitre, "Probabilité calibrée : " + (100 * p.probability).toFixed(1) + " %"];
  if ("set" in p) lignes.push("Ensemble conforme à 90 % : " + p.set.join(", "));
  if ("abstain" in p) lignes.push(p.abstain ? "Renvoi à une relecture humaine (incertain)" : "Proposition sans renvoi");
  if ("stage" in p) lignes.push("Étage : " + p.stage);
  lignes.push("Chapitre du scénario (étiquette du corpus) : " + b.nom_chapitre_scenario);
  resultat.textContent = lignes.join("\\n"); resultat.style.whiteSpace = "pre-line";
}});
</script>
</body></html>
"""


def handle(payload: Any, examples: dict[str, dict[str, str]], predict: Predict, names: dict[str, str]) -> tuple[int, dict[str, Any]]:
    """Seul un identifiant d'exemple fictif de la liste est accepté (aucune saisie libre) ; rend (code HTTP, corps JSON)."""
    if not isinstance(payload, dict) or set(payload) != {"id"} or not isinstance(payload["id"], str):
        return 400, {"error": "la démo ne classe que les exemples fictifs de la liste (corps attendu : {\"id\": ...}, aucune saisie libre)"}
    ex = examples.get(payload["id"])
    if ex is None:
        return 404, {"error": "exemple inconnu"}
    pred = predict([ex["texte"]])[0]
    return 200, {"id": ex["id"], "prediction": pred, "nom_chapitre": names.get(pred["label"], pred["label"]),
                 "chapitre_scenario": ex["chapitre_scenario"], "nom_chapitre_scenario": names.get(ex["chapitre_scenario"], ex["chapitre_scenario"])}


def make_demo_server(examples: list[dict[str, str]], predict: Predict, names: dict[str, str], host: str, port: int) -> ThreadingHTTPServer:
    page = render_page(examples).encode("utf-8")
    by_id = {e["id"]: e for e in examples}

    class Handler(BaseHTTPRequestHandler):
        def _send(self, status: int, raw: bytes, content_type: str) -> None:
            self.send_response(status)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(len(raw)))
            self.send_header("Content-Security-Policy", CSP)
            self.send_header("X-Content-Type-Options", "nosniff")
            self.end_headers()
            self.wfile.write(raw)

        def _json(self, status: int, body: dict[str, Any]) -> None:
            self._send(status, json.dumps(body, ensure_ascii=False).encode("utf-8"), "application/json; charset=utf-8")

        def do_GET(self) -> None:
            if self.path == "/":
                self._send(200, page, "text/html; charset=utf-8")
            else:
                self._json(404, {"error": "inconnu"})

        def do_POST(self) -> None:
            length = int(self.headers.get("Content-Length", "0"))
            if self.path != "/predict" or length <= 0 or length > MAX_BODY_BYTES:
                self._json(400 if self.path == "/predict" else 404, {"error": "requête refusée"})
                return
            try:
                payload = json.loads(self.rfile.read(length))
            except ValueError:
                self._json(400, {"error": "JSON invalide"})
                return
            self._json(*handle(payload, by_id, predict, names))

        def log_message(self, format: str, *args: Any) -> None:  # aucune ligne de journal : ni chemins ni contenu
            return

    return ThreadingHTTPServer((check_host(host), port), Handler)


def load_examples(n: int) -> list[dict[str, str]]:
    """Les n premiers patients du pli 0 du développement par identifiant, un par chapitre tant que possible (test scellé jamais lu)."""
    import p1_04_06_tfidf

    texts, y, folds, _, ids = p1_04_06_tfidf.load("chapter")
    rows = sorted((i, t, c) for i, t, c, k in zip(ids, texts, y, folds.tolist(), strict=True) if k == 0)
    first: dict[str, tuple[str, str, str]] = {}
    for i, t, c in rows:
        first.setdefault(c, (i, t, c))
    chosen = sorted(first.values())[:n]
    chosen += [r for r in rows if r not in chosen][: max(0, n - len(chosen))]
    return [{"id": i, "texte": t, "chapitre_scenario": c} for i, t, c in chosen]


def main() -> int:
    from llmft import serving

    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--backend", choices=["tfidf", "g"], default="tfidf")
    ap.add_argument("--bundle")
    ap.add_argument("--n", type=int, default=12)
    ap.add_argument("--port", type=int, default=8090)
    a = ap.parse_args()
    examples = load_examples(a.n)
    if a.backend == "g":
        import p1_04_06_tfidf
        import service_g_cascade

        predict, _, _ = service_g_cascade.predictor(sorted(set(p1_04_06_tfidf.load("chapter")[1])))
    else:
        if not a.bundle:
            ap.error("--bundle requis avec le TF-IDF")
        bundle = serving.load_bundle(a.bundle)
        predict = lambda texts: serving.predict(bundle, texts, "marginal")
    server = make_demo_server(examples, predict, chapter_names(CONTRACT), "127.0.0.1", a.port)
    print(f"démo locale : http://127.0.0.1:{server.server_address[1]}/  ({BANNER})")
    server.serve_forever()
    return 0


if __name__ == "__main__":
    sys.exit(main())
