#!/usr/bin/env python3
"""Service HTTP de G en cascade E puis G (RM-60, fiche 2026-10-17-service-g-cascade) : E répond seul si sa probabilité maximale atteint τ = 0,6, sinon G complet.
`serve` : lance le service ; `bench` : lance le service dans ce processus puis le mesure par HTTP sur la boucle locale, lot de 1 : deux passages à τ, chemins E et G forcés,
latence moyenne attendue à la part hors pli de RM-60, quatre clients ; `energie` (fiche 2026-10-17-energie-service-g-cascade) : énergie de la carte par chemin forcé, au moins 15 s de charge chacun.
Développement seulement, texte seul, jamais le test scellé.
`charge` (fiche 2026-10-17-charge-prolongee-service-g) : 30 minutes de charge à quatre clients, 17,74 % des textes forcés sur G par leur empreinte, verdict écrit d'avance.
Usage : service_g_cascade.py serve [--host 127.0.0.1] [--port 8081] [--reference FICHIER.json] | bench [--n 200] [--register] | energie [--n 200] [--register]
        | charge [--minutes 30] [--register] (--minutes plus court : répétition à blanc, jamais enregistrée) ; GPU libre, sous scripts/run_guarded.sh."""
import time

T_PROCESS = time.perf_counter()

import hashlib
import http.client
import json
import subprocess
import sys
import threading
import urllib.request
from collections.abc import Callable
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent))
import numpy as np

import bench_service_g
import p1_04_06_tfidf
import serve_tfidf
from llmft import http_service, machine_health, servicecost, tokenizer_guard
from llmft import service_g as sg
from llmft.energy import PowerSampler
from llmft.mini_registry import register_run

TAU = 0.6  # choisi hors pli dans les cinq plis, run 20261017-012416-cascade-e-puis-g
SHARE_E_OUT_OF_FOLD = 0.8226  # part sans LoRA hors pli, même run
FORCE_E, FORCE_G = 0.0, 1.01
MIN_LOAD_S = 15.0  # au moins 15 s de charge par mesure d'énergie (règle du 07/10 : au moins 14 s)
LOAD_MINUTES, WARMUP_S, CLIENTS, SAMPLE_S, MAX_ERRORS = 30, 60.0, 4, 10.0, 50  # fiche 2026-10-17-charge-prolongee-service-g
P95_RATIO, GPU_GROWTH_MIB, RSS_GROWTH_GIB = 1.2, 500.0, 1.0
PRICE_EUR_KWH = 0.25  # paramètre de lecture, non mesuré


def arg(name: str, default: str) -> str:
    return sys.argv[sys.argv.index(name) + 1] if name in sys.argv else default


def predictor(labels: list[str], tau_for: Callable[[str], float] | None = None) -> tuple[Any, dict[str, Any], dict[str, float]]:
    """Prédicteur de G en cascade chargé une fois (aussi utilisé par la démo locale, P5-11) ; le seuil vit dans `state` pour que le banc puisse forcer un chemin.
    Un verrou sérialise le GPU entre les fils du serveur."""
    svc = bench_service_g.Service("gpu", labels)
    state = {"tau": TAU}
    lock = threading.Lock()

    def first(text: str) -> tuple[list[np.ndarray], np.ndarray]:
        out, _ = svc.predict_one(text, with_lora=False)
        return list(out["encodeurs"]), out["tfidf"]

    def lora(text: str) -> np.ndarray:
        ids = tokenizer_guard.build_inputs_local(svc.lora_tok, [text], 4096)[0]
        return np.asarray(svc._forward(svc.lora, ids, svc.pad_id))

    def predict(texts: list[str]) -> list[dict[str, Any]]:
        with lock:
            return [sg.cascade_predict(t, first, lora, labels, tau_for(t) if tau_for else state["tau"]) for t in texts]

    health = {"status": "ok", "systeme": "G en cascade E puis G (ADR-016, RM-60)", "tau": TAU, "n_labels": len(labels)}
    return predict, health, state


def build(labels: list[str], monitor: Any = None) -> tuple[Any, dict[str, float]]:
    predict, health, state = predictor(labels)
    return http_service.make_json_server(predict, health, arg("--host", "127.0.0.1"), int(arg("--port", "0" if sys.argv[1] == "bench" else "8081")), monitor), state


def post(base: str, text: str) -> tuple[float, dict[str, Any]]:
    req = urllib.request.Request(base + "/predict", data=json.dumps({"texts": [text]}).encode("utf-8"), headers={"Content-Type": "application/json"})
    t = time.perf_counter()
    body = json.loads(urllib.request.urlopen(req, timeout=120).read())
    return 1000 * (time.perf_counter() - t), body["predictions"][0]


def run_pass(base: str, sample: list[str]) -> dict[str, Any]:
    lat, stages, labels = [], [], []
    for text in sample:
        ms, p = post(base, text)
        lat.append(ms)
        stages.append(p["stage"])
        labels.append(p["label"])
    return {"latence": sg.latency_percentiles(lat), "part_e": round(stages.count("E") / len(stages), 4), "labels": labels}


def concurrent(base: str, sample: list[str], clients: int = 4) -> dict[str, Any]:
    t0 = time.perf_counter()
    with ThreadPoolExecutor(clients) as pool:
        lat = [ms for ms, _ in pool.map(lambda text: post(base, text), sample)]
    return {"clients": clients, "requetes": len(sample), "debit_patients_par_s": round(len(sample) / (time.perf_counter() - t0), 2), **sg.latency_percentiles(lat)}


def bench() -> int:
    import torch

    n = int(arg("--n", "200"))
    start = machine_health.snapshot()
    texts, y, folds, _, _ = p1_04_06_tfidf.load("chapter")
    labels = sorted(set(y))
    sample = [t for t, g in zip(texts, folds, strict=True) if g == 0][:n]
    server, state = build(labels)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    base = f"http://127.0.0.1:{server.server_address[1]}"
    json.loads(urllib.request.urlopen(base + "/health", timeout=30).read())
    ready_s = time.perf_counter() - T_PROCESS
    for tau in (FORCE_G, TAU):  # échauffement des deux chemins : à τ, des patients vus à l'entraînement passeraient tous par E et le LoRA resterait froid
        state["tau"] = tau
        for text in sample[:4]:
            post(base, text)
    torch.cuda.reset_peak_memory_stats()
    passes = [run_pass(base, sample) for _ in range(2)]
    accepted = sg.passes_accepted(passes[0]["latence"]["p50_ms"], passes[1]["latence"]["p50_ms"], same_classes=passes[0]["labels"] == passes[1]["labels"])
    if not accepted:  # fiche : un troisième passage, une seule fois
        passes.append(run_pass(base, sample))
    state["tau"] = FORCE_E
    path_e = run_pass(base, sample)
    state["tau"] = FORCE_G
    path_g = run_pass(base, sample)
    state["tau"] = TAU
    conc = concurrent(base, sample)
    peak = round(torch.cuda.max_memory_allocated() / 2**30, 2)
    server.shutdown()
    expected = SHARE_E_OUT_OF_FOLD * path_e["latence"]["moyenne_ms"] + (1 - SHARE_E_OUT_OF_FOLD) * path_g["latence"]["moyenne_ms"]
    out: dict[str, Any] = {
        "n_patients": len(sample), "tau": TAU, "demarrage_a_froid_s": round(ready_s, 1), "memoire_pic_gib": peak,
        "passages": [{k: v for k, v in p.items() if k != "labels"} for p in passes], "passages_acceptes": accepted,
        "chemin_e_force": path_e["latence"], "chemin_g_force": path_g["latence"],
        "part_e_hors_pli": SHARE_E_OUT_OF_FOLD, "latence_moyenne_attendue_ms": round(expected, 1),
        "accord_cascade_contre_g": round(float(np.mean([a == b for a, b in zip(passes[0]["labels"], path_g["labels"], strict=True)])), 4),
        "essai_concurrent": conc, "reference_g_un_seul_tenant_p50_ms": 91.6, "modele_rm60_ms": 39.6,
    }
    print(json.dumps(out, indent=1, ensure_ascii=False))
    if "--register" in sys.argv:
        (ROOT / "results/measures/service_g_cascade.json").write_text(json.dumps(out, indent=1, ensure_ascii=False), encoding="utf-8")
        print(register_run(ROOT / "results/runs", {"kind": "measure", "slug": "service-g-cascade", "status": "ok",
                                                    "summary": f"Service HTTP de G en cascade : p50 {passes[0]['latence']['p50_ms']} ms, latence moyenne attendue {out['latence_moyenne_attendue_ms']} ms",
                                                    "params": {"fiche": "experiments/2026-10-17-service-g-cascade.md", "n": len(sample), "tau": TAU, "part_e_hors_pli": SHARE_E_OUT_OF_FOLD},
                                                    "metrics": out, "machine_health": machine_health.stamp(start)}))
    return 0


def repeat_until(min_seconds: float, one_pass: Callable[[], object], clock: Callable[[], float] = time.perf_counter) -> tuple[int, float]:
    """Passages complets répétés jusqu'à `min_seconds` de charge mesurée (pas estimée sur l'échauffement) ; rend (passages, secondes)."""
    t0, n = clock(), 0
    while n == 0 or clock() - t0 < min_seconds:
        one_pass()
        n += 1
    return n, clock() - t0


def energy_wh_from_mean(power_w: list[float], seconds: float) -> float:
    """Énergie (Wh) = puissance moyenne de la carte × durée mesurée : ne dépend pas du temps de lecture de chaque échantillon, qui allonge l'intervalle réel."""
    return float(np.mean(power_w)) * seconds / 3600.0


def energy_path(base: str, sample: list[str], state: dict[str, float], tau: float) -> dict[str, Any]:
    state["tau"] = tau
    run_pass(base, sample)  # échauffement du chemin, non mesuré
    with PowerSampler(interval_s=0.5) as ps:
        n, seconds = repeat_until(MIN_LOAD_S, lambda: run_pass(base, sample))
    wh = energy_wh_from_mean(ps.samples, seconds)
    return {"passages": n, "secondes_de_charge": round(seconds, 1), "echantillons": len(ps.samples), "puissance_moyenne_w": round(float(np.mean(ps.samples)), 1),
            **servicecost.per_1000(wh, n * len(sample), PRICE_EUR_KWH)}


def energy() -> int:
    n = int(arg("--n", "200"))
    start = machine_health.snapshot()
    texts, y, folds, _, _ = p1_04_06_tfidf.load("chapter")
    sample = [t for t, g in zip(texts, folds, strict=True) if g == 0][:n]
    server, state = build(sorted(set(y)))
    threading.Thread(target=server.serve_forever, daemon=True).start()
    base = f"http://127.0.0.1:{server.server_address[1]}"
    json.loads(urllib.request.urlopen(base + "/health", timeout=30).read())
    path_e = energy_path(base, sample, state, FORCE_E)
    path_g = energy_path(base, sample, state, FORCE_G)
    server.shutdown()
    expected = SHARE_E_OUT_OF_FOLD * path_e["wh_pour_1000_patients"] + (1 - SHARE_E_OUT_OF_FOLD) * path_g["wh_pour_1000_patients"]
    out: dict[str, Any] = {"n_patients": len(sample), "chemin_e_force": path_e, "chemin_g_force": path_g, "part_e_hors_pli": SHARE_E_OUT_OF_FOLD,
                           "energie_attendue_wh_pour_1000_patients": round(expected, 2), "prix_eur_kwh_parametre": PRICE_EUR_KWH,
                           "reference_g_un_seul_tenant_wh_pour_1000": 10.5, "methode": "puissance moyenne de la carte × durée mesurée, au moins 15 s de charge par chemin"}
    print(json.dumps(out, indent=1, ensure_ascii=False))
    if "--register" in sys.argv:
        (ROOT / "results/measures/energie_service_g_cascade.json").write_text(json.dumps(out, indent=1, ensure_ascii=False), encoding="utf-8")
        print(register_run(ROOT / "results/runs", {"kind": "measure", "slug": "energie-service-g-cascade", "status": "ok",
                                                    "summary": f"Énergie du service de G en cascade : {out['energie_attendue_wh_pour_1000_patients']} Wh attendus pour 1 000 patients (E {path_e['wh_pour_1000_patients']}, G {path_g['wh_pour_1000_patients']})",
                                                    "supersedes": "20261017-025421-energie-service-g-cascade",  # chemin E à 10,2 s de charge au lieu de 15 (écart déclaré à l'INDEX)
                                                    "params": {"fiche": "experiments/2026-10-17-energie-service-g-cascade.md", "n": len(sample), "tau": TAU, "part_e_hors_pli": SHARE_E_OUT_OF_FOLD, "min_load_s": MIN_LOAD_S},
                                                    "metrics": out, "machine_health": machine_health.stamp(start)}))
    return 0


def forced_to_g(text: str, share: float = 1 - SHARE_E_OUT_OF_FOLD) -> bool:
    """Profil de routage de la charge prolongée : une part fixe des textes, choisie par l'empreinte SHA-1 du texte, passe par le chemin G."""
    return int(hashlib.sha1(text.encode("utf-8")).hexdigest(), 16) % 10_000 < round(share * 10_000)


def per_minute(events: list[tuple[float, float, bool]], start: float, n_minutes: int) -> list[dict[str, Any]]:
    """Événements (instant d'envoi, latence en ms, succès) agrégés par minute à partir de `start` (après l'échauffement)."""
    out = []
    for m in range(n_minutes):
        window = [(lat, ok) for t, lat, ok in events if start + 60 * m <= t < start + 60 * (m + 1)]
        ok_lat = [lat for lat, ok in window if ok]
        out.append({"minute": m + 1, "requetes": len(window), "erreurs": sum(1 for _, ok in window if not ok), "debit_patients_par_s": len(ok_lat) / 60,
                    **(sg.latency_percentiles(ok_lat) if ok_lat else {})})
    return out


def window_p95(events: list[tuple[float, float, bool]], lo: float, hi: float) -> float:
    """p95 des requêtes réussies envoyées dans [lo, hi), regroupées."""
    return float(np.percentile([lat for t, lat, ok in events if ok and lo <= t < hi], 95))


def growth(samples: list[tuple[float, float]], start: float, n_minutes: int) -> float:
    """Croissance d'une mesure : maximum des 5 dernières minutes moins moyenne des 5 premières."""
    first = [v for t, v in samples if start <= t < start + 300]
    last = [v for t, v in samples if start + 60 * (n_minutes - 5) <= t < start + 60 * n_minutes]
    return float(max(last) - np.mean(first))


def load_verdict(errors: int, p95_first: float, p95_last: float, gpu_growth_mib: float, rss_growth_gib: float) -> tuple[str, list[str]]:
    """Critère écrit d'avance : aucune erreur, p95 final au plus 1,2 fois l'initial, mémoire GPU +500 Mio au plus, mémoire résidente +1 Gio au plus."""
    failed = [name for name, bad in (("erreurs", errors > 0), ("latence p95", round(p95_last - P95_RATIO * p95_first, 6) > 0),
                                     ("mémoire GPU", round(gpu_growth_mib - GPU_GROWTH_MIB, 6) > 0), ("mémoire résidente", round(rss_growth_gib - RSS_GROWTH_GIB, 6) > 0)) if bad]
    return ("tient la charge" if not failed else "ne tient pas"), failed


def _rss_gib() -> float:
    for line in Path("/proc/self/status").read_text(encoding="utf-8").splitlines():
        if line.startswith("VmRSS:"):
            return int(line.split()[1]) / 2**20
    return float("nan")


def _gpu() -> tuple[float, float, float]:
    out = subprocess.run(["nvidia-smi", "--query-gpu=memory.used,power.draw,temperature.gpu", "--format=csv,noheader,nounits"], capture_output=True, text=True, timeout=10, check=True).stdout
    mem, power, temp = (float(x) for x in out.splitlines()[0].split(","))
    return mem, power, temp


def charge() -> int:
    minutes = int(arg("--minutes", str(LOAD_MINUTES)))
    if "--register" in sys.argv and minutes != LOAD_MINUTES:
        raise SystemExit("une répétition à blanc (--minutes) ne s'enregistre pas")
    start_health = machine_health.snapshot()
    texts, y, folds, _, _ = p1_04_06_tfidf.load("chapter")
    sample = [t for t, g in zip(texts, folds, strict=True) if g == 0]
    predict, health, _ = predictor(sorted(set(y)), tau_for=lambda t: FORCE_G if forced_to_g(t) else TAU)
    server = http_service.make_json_server(predict, health, "127.0.0.1", 0)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    base = f"http://127.0.0.1:{server.server_address[1]}"
    json.loads(urllib.request.urlopen(base + "/health", timeout=30).read())
    events: list[tuple[float, float, bool]] = []
    samples: list[tuple[float, float, float, float, float]] = []
    lock, stop = threading.Lock(), threading.Event()
    start = time.perf_counter() + WARMUP_S
    end = start + 60 * minutes

    def client(k: int) -> None:
        i = k
        while not stop.is_set() and time.perf_counter() < end:
            text, i = sample[i % len(sample)], i + CLIENTS
            t = time.perf_counter()
            try:
                ms, ok = post(base, text)[0], True
            except (OSError, http.client.HTTPException, ValueError, KeyError):  # réponse autre que 200 (HTTPError), coupure, délai, JSON invalide : une erreur
                ms, ok = 1000 * (time.perf_counter() - t), False
            with lock:
                events.append((t, ms, ok))
                if sum(1 for e in events if not e[2]) > MAX_ERRORS:
                    stop.set()

    def sampler() -> None:
        while not stop.is_set() and time.perf_counter() < end:
            mem, power, temp = _gpu()
            samples.append((time.perf_counter(), mem, _rss_gib(), power, temp))
            stop.wait(SAMPLE_S)

    threads = [threading.Thread(target=client, args=(k,)) for k in range(CLIENTS)] + [threading.Thread(target=sampler)]
    for th in threads:
        th.start()
    for th in threads:
        th.join()
    server.shutdown()
    measured = [e for e in events if e[0] >= start]
    errors = sum(1 for e in measured if not e[2])
    out: dict[str, Any] = {"minutes": minutes, "clients": CLIENTS, "n_textes": len(sample), "part_forcee_g": round(sum(forced_to_g(t) for t in sample) / len(sample), 4),
                           "requetes_mesurees": len(measured), "erreurs": errors, "erreurs_echauffement": sum(1 for e in events if e[0] < start and not e[2])}
    if stop.is_set():
        out.update({"verdict": "ne tient pas", "criteres_manques": [f"arrêt anticipé : plus de {MAX_ERRORS} erreurs"]})
    else:
        ok_lat = [e[1] for e in measured if e[2]]
        p95_first, p95_last = window_p95(events, start, start + 300), window_p95(events, end - 300, end)
        gpu_g = growth([(s[0], s[1]) for s in samples], start, minutes)
        rss_g = growth([(s[0], s[2]) for s in samples], start, minutes)
        verdict, failed = load_verdict(errors, p95_first, p95_last, gpu_g, rss_g)
        out.update({"debit_patients_par_s": round(len(ok_lat) / (60 * minutes), 2), "latence": sg.latency_percentiles(ok_lat),
                    "p95_minutes_1_5_ms": round(p95_first, 1), "p95_5_dernieres_minutes_ms": round(p95_last, 1),
                    "croissance_memoire_gpu_mib": round(gpu_g, 1), "croissance_memoire_residente_gib": round(rss_g, 3),
                    "puissance_moyenne_w": round(float(np.mean([s[3] for s in samples if s[0] >= start])), 1), "temperature_max_c": max(s[4] for s in samples),
                    "par_minute": per_minute(events, start, minutes), "verdict": verdict, "criteres_manques": failed,
                    "reference_essai_concurrent": {"debit_patients_par_s": 37.57, "p95_ms": 121.8, "run": "20261017-015754-service-g-cascade"}})
    print(json.dumps(out, indent=1, ensure_ascii=False))
    if "--register" in sys.argv:
        (ROOT / "results/measures/charge_prolongee_service_g.json").write_text(json.dumps(out, indent=1, ensure_ascii=False), encoding="utf-8")
        print(register_run(ROOT / "results/runs", {"kind": "measure", "slug": "charge-prolongee-service-g", "status": "ok", "summary": f"Charge prolongée du service de G en cascade : {out['verdict']}",
                                                    "params": {"fiche": "experiments/2026-10-17-charge-prolongee-service-g.md", "minutes": minutes, "clients": CLIENTS, "tau": TAU, "part_forcee_g": out["part_forcee_g"]},
                                                    "metrics": out, "machine_health": machine_health.stamp(start_health)}))
    return 0


def serve() -> int:
    _, y, _, _, _ = p1_04_06_tfidf.load("chapter")
    reference = arg("--reference", "")
    server, _ = build(sorted(set(y)), serve_tfidf.monitor_from(reference) if reference else None)
    print(f"service prêt sur {server.server_address[0]}:{server.server_address[1]} (tau {TAU})", flush=True)
    server.serve_forever()
    return 0


if __name__ == "__main__":
    sys.exit({"bench": bench, "energie": energy, "charge": charge}.get(sys.argv[1], serve)())
