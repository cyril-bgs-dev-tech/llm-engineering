#!/usr/bin/env python3
"""Construit l'image de service (Dockerfile.serve), la lance durcie (lecture seule, sans privilège, 1 Gio, 2 processeurs) et mesure : taille, construction, démarrage à froid, latence, débit à 8 clients,
accord des prédictions avec le service en processus, refus d'une entrée invalide, mémoire. Développement seulement (texte fictif PARHAF, pli 0). Usage : smoke_serve_image.py [--register] [--n 50]"""
import json
import shutil
import subprocess
import sys
import time
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent))
import p1_04_06_tfidf
from llmft import service_g as sg
from llmft import serving
from llmft.mini_registry import register_run

BUNDLE = ROOT / "artifacts/models/tfidf_chapter_charbal_v1"
STAGE = ROOT / "deploy/serve-bundle"
TAG = "llmft-serve:smoke"
NAME = "llmft-serve-smoke"
PORT = 18000


def run(*cmd: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(cmd, capture_output=True, text=True, check=False, cwd=ROOT)


def post(texts: list[str]) -> dict:
    req = urllib.request.Request(f"http://127.0.0.1:{PORT}/predict", data=json.dumps({"texts": texts}).encode(), headers={"Content-Type": "application/json"})
    return json.loads(urllib.request.urlopen(req, timeout=30).read())


def timed_post(text: str) -> float:
    start = time.perf_counter()
    post([text])
    return 1000 * (time.perf_counter() - start)


def main() -> int:
    n = int(sys.argv[sys.argv.index("--n") + 1]) if "--n" in sys.argv else 50
    STAGE.mkdir(parents=True, exist_ok=True)
    for f in ("meta.json", "model.joblib"):
        shutil.copy2(BUNDLE / f, STAGE / f)
    t0 = time.perf_counter()
    build = run("docker", "build", "-q", "-t", TAG, "-f", "Dockerfile.serve", ".")
    if build.returncode != 0:
        print(build.stderr[-2000:])
        return 1
    build_s = time.perf_counter() - t0
    size = int(run("docker", "image", "inspect", "--format", "{{.Size}}", TAG).stdout.strip())  # taille du contenu (compressé avec le magasin containerd)
    disk = run("docker", "image", "ls", "--format", "{{.Size}}", TAG).stdout.strip()  # espace disque une fois décompressé
    image_id = run("docker", "image", "inspect", "--format", "{{.Id}}", TAG).stdout.strip()
    run("docker", "rm", "-f", NAME)
    t1 = time.perf_counter()
    started = run("docker", "run", "-d", "--name", NAME, "-p", f"127.0.0.1:{PORT}:8000", "--read-only", "--tmpfs", "/tmp", "--cap-drop", "ALL", "--security-opt", "no-new-privileges",
                  "--memory", "1g", "--cpus", "2", TAG)
    if started.returncode != 0:
        print(started.stderr)
        return 1
    health = None
    try:
        while time.perf_counter() - t1 < 60 and health is None:
            try:
                health = json.loads(urllib.request.urlopen(f"http://127.0.0.1:{PORT}/health", timeout=1).read())
            except (urllib.error.URLError, ConnectionError, TimeoutError):
                time.sleep(0.1)
        cold_start_s = time.perf_counter() - t1
        if health is None:
            print(run("docker", "logs", NAME).stdout, run("docker", "logs", NAME).stderr)
            return 1
        texts, _, folds, _, _ = p1_04_06_tfidf.load("chapter")
        sample = [t for t, g in zip(texts, folds, strict=True) if g == 0][:n]
        post(sample[:2])  # échauffement
        lat = []
        served = []
        for t in sample:
            s = time.perf_counter()
            served.append(post([t])["predictions"][0])
            lat.append(1000 * (time.perf_counter() - s))
        local = serving.predict(serving.load_bundle(BUNDLE), sample)
        same = sum(a["label"] == b["label"] and a["set"] == b["set"] and a["abstain"] == b["abstain"] for a, b in zip(served, local, strict=True))
        concurrency = {}
        for clients in (1, 4, 8, 16):
            s = time.perf_counter()
            with ThreadPoolExecutor(clients) as pool:
                lats = list(pool.map(timed_post, (sample * 4)[:200]))
            concurrency[str(clients)] = {"debit_patients_par_s": round(200 / (time.perf_counter() - s), 1), **sg.latency_percentiles(lats)}
        try:
            urllib.request.urlopen(urllib.request.Request(f"http://127.0.0.1:{PORT}/predict", data=b'{"texts": []}', headers={"Content-Type": "application/json"}), timeout=5)
            invalid_code = 200
        except urllib.error.HTTPError as err:
            invalid_code = err.code
        mem = run("docker", "stats", "--no-stream", "--format", "{{.MemUsage}}", NAME).stdout.strip()
        out = {"image": TAG, "image_id": image_id, "taille_contenu_mo": round(size / 2**20, 1), "taille_disque": disk, "construction_s": round(build_s, 1), "demarrage_a_froid_s": round(cold_start_s, 2), "n_patients": len(sample),
               **sg.latency_percentiles(lat), "charge_concurrente_par_nombre_de_clients": concurrency, "predictions_identiques_au_service_en_processus": f"{same}/{len(sample)}",
               "entree_invalide_code_http": invalid_code, "memoire_conteneur": mem, "options": "lecture seule, sans privilège, 1 Gio, 2 processeurs, utilisateur non root", "modele_sha256": health["model_sha256"]}
        print(json.dumps(out, indent=1, ensure_ascii=False))
        (ROOT / "results/measures/serve_image_smoke.json").write_text(json.dumps(out, indent=1, ensure_ascii=False), encoding="utf-8")
        if "--register" in sys.argv:
            print(register_run(ROOT / "results/runs", {"kind": "measure", "slug": "image-de-service-tfidf-test-de-fumee", "status": "ok" if same == len(sample) and invalid_code == 400 else "failed",
                                                        "summary": f"Image de service TF-IDF : {out['taille_disque']} sur disque, démarrage {out['demarrage_a_froid_s']} s, p50 {out['p50_ms']} ms", "params": {"dockerfile": "Dockerfile.serve", "n": len(sample)}, "metrics": out}))
        return 0 if same == len(sample) and invalid_code == 400 else 1
    finally:
        run("docker", "rm", "-f", NAME)


if __name__ == "__main__":
    sys.exit(main())
