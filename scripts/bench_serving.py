#!/usr/bin/env python3
"""Mesure de service du bundle d'inférence sur des textes du développement (jamais le test scellé) : latence par patient (p50, p95), débit par lot, taille, mémoire.
Usage : bench_serving.py [dossier du bundle] [--register]"""
import json
import resource
import sys
import time
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent))
import p1_04_06_tfidf
from llmft import serving
from llmft.mini_registry import register_run


def main() -> int:
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    d = Path(args[0]) if args else ROOT / "artifacts/models/tfidf_chapter_charbal_v1"
    texts, _, folds, _, _ = p1_04_06_tfidf.load("chapter")
    sample = [t for t, g in zip(texts, folds, strict=True) if g == 0][:300]
    t0 = time.perf_counter()
    bundle = serving.load_bundle(d)
    load_s = time.perf_counter() - t0
    serving.predict(bundle, sample[:5])  # échauffement
    single = []
    for t in sample[:200]:
        s = time.perf_counter()
        serving.predict(bundle, [t])
        single.append(1000 * (time.perf_counter() - s))
    s = time.perf_counter()
    serving.predict(bundle, sample)
    batch_s = time.perf_counter() - s
    size_mb = sum(p.stat().st_size for p in d.iterdir() if p.is_file()) / 1e6
    out = {"bundle": str(d.relative_to(ROOT)), "taille_mo": round(size_mb, 1), "chargement_s": round(load_s, 2), "latence_ms_p50": round(float(np.percentile(single, 50)), 1), "latence_ms_p95": round(float(np.percentile(single, 95)), 1),
           "debit_patients_par_s_lot_de_300": round(len(sample) / batch_s, 1), "memoire_pic_mo": round(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024), "n_patients_mesures": len(single), "processeur": "CPU, un processus"}
    print(json.dumps(out, indent=1))
    if "--register" in sys.argv:
        print(register_run(ROOT / "results/runs", {"kind": "measure", "slug": "bench-serving-tfidf-charbal-v1", "status": "ok", "summary": f"Service TF-IDF : p50 {out['latence_ms_p50']} ms, p95 {out['latence_ms_p95']} ms, {out['taille_mo']} Mo", "params": {"bundle": out["bundle"]}, "metrics": out}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
