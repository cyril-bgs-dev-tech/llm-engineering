#!/usr/bin/env python3
"""Test de charge du TF-IDF par cœur (fiche 2026-10-07-stress-tfidf-par-coeur) : un processus fils par essai, panne brute (sans relance), empreinte du résultat.
Usage : stress_tfidf_ab.py [--tours 3] [--register] ; le fils est lancé avec --child {libre|N}.
RM-64 (fiche 2026-10-17-verification-machine-apres-bios) : stress_tfidf_ab.py --bios {avant|apres} --register (128 essais libres, verdict à la phase « après »)."""
import hashlib
import json
import os
import random
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SEED = 20261007
N_TEXTS = 1500
STOP_AFTER_CRASHES = 5
MIN_AVAILABLE_MIB = 20000
TRIAL_TIMEOUT = 300
BIOS_TRIALS = 128  # RM-64 : même effectif que la fiche libre contre épinglé (64 + 64)
REFERENCE_DIGEST = "df902b173fead1da949e4e029d11a531b6c3e582a0594c45943db489cb0191b5"  # empreinte de 119 succès sur 120 le 07/10 (results/measures/stress_tfidf_ab*.json)


def child(arm: str) -> int:
    if arm != "libre":
        os.sched_setaffinity(0, {int(arm)})  # avant l'import de scikit-learn : voir llmft.tokenizer_guard
    sys.path.insert(0, str(ROOT / "src"))
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from sklearn.feature_extraction.text import TfidfVectorizer

    import p1_04_06_tfidf
    texts = p1_04_06_tfidf.load("chapter")[0][:N_TEXTS]
    x = TfidfVectorizer(sublinear_tf=True, min_df=2, max_features=200000, ngram_range=(3, 5), analyzer="char_wb").fit_transform(texts)
    digest = hashlib.sha256(x.data.tobytes() + x.indices.tobytes() + x.indptr.tobytes()).hexdigest()
    print(json.dumps({"digest": digest, "shape": list(x.shape)}))
    return 0


def available_mib() -> int:
    for line in Path("/proc/meminfo").read_text().splitlines():
        if line.startswith("MemAvailable:"):
            return int(line.split()[1]) // 1024
    return 0


def one_trial(arm: str):
    from llmft import stress
    t0 = time.time()
    label, _, core = arm.partition(":")
    try:
        proc = subprocess.run(["nice", "-n", "10", sys.executable, __file__, "--child", core or label], capture_output=True, text=True, timeout=TRIAL_TIMEOUT, cwd=ROOT, check=False)
    except subprocess.TimeoutExpired:
        return stress.Trial(label, 124, None, "timeout"), time.time() - t0
    if proc.returncode == 0:
        return stress.Trial(label, 0, json.loads(proc.stdout.strip().splitlines()[-1])["digest"]), time.time() - t0
    last = (proc.stderr.strip().splitlines() or [""])[-1]
    return stress.Trial(label, proc.returncode, None, last[:120] if "Error" in last else None), time.time() - t0


def main() -> int:
    sys.path.insert(0, str(ROOT / "src"))
    from llmft import stress
    tours = int(sys.argv[sys.argv.index("--tours") + 1]) if "--tours" in sys.argv else 3
    libre_contre_epingle = int(sys.argv[sys.argv.index("--libre-contre-epingle") + 1]) if "--libre-contre-epingle" in sys.argv else 0
    bios = sys.argv[sys.argv.index("--bios") + 1] if "--bios" in sys.argv else ""
    if bios not in ("", "avant", "apres"):
        raise SystemExit("--bios avant|apres")
    from llmft import machine_health
    health_start = machine_health.snapshot()
    rng = random.Random(SEED)
    if bios:
        plan = ["libre"] * BIOS_TRIALS
    elif libre_contre_epingle:  # fiche 2026-10-07-stress-tfidf-libre-contre-epingle : n essais libres et n essais épinglés sur un cœur tiré au hasard
        plan = ["libre"] * libre_contre_epingle + [f"epingle:{rng.randrange(32)}" for _ in range(libre_contre_epingle)]
    else:
        plan = [arm for _ in range(tours) for arm in ["libre", *map(str, range(32))]]
    rng.shuffle(plan)
    stop_after = 10 if (libre_contre_epingle or bios) else STOP_AFTER_CRASHES
    suffix = f"_bios_{bios}" if bios else ("_libre_contre_epingle" if libre_contre_epingle else "")
    trials, times, crashes, stopped = [], [], 0, None
    for i, arm in enumerate(plan):
        if available_mib() < MIN_AVAILABLE_MIB:
            stopped = f"mémoire disponible sous {MIN_AVAILABLE_MIB} Mio avant l'essai {i}"
            break
        trial, dt = one_trial(arm)
        trials.append(trial)
        times.append(dt)
        crashes += trial.returncode != 0
        print(f"{time.strftime('%FT%TZ', time.gmtime())} essai {i + 1}/{len(plan)} bras={arm} code={trial.returncode} {dt:.0f}s {trial.error or ''}", flush=True)
        if crashes >= stop_after:
            stopped = f"{crashes} pannes (règle d'arrêt N31)"
            break
    summary = stress.summarize(trials)
    out = {"n_trials": len(trials), "planned": len(plan), "stopped": stopped, "seconds_total": round(sum(times), 1),
           "arms": {a: {"n": s.n, "crashes": s.crashes, "mismatches": s.mismatches, "signatures": s.signatures} for a, s in sorted(summary.items(), key=lambda kv: (kv[0] != "libre", int(kv[0]) if kv[0].isdigit() else 0))},
           "trials": [{"arm": t.arm, "code": t.returncode, "digest": t.digest, "error": t.error} for t in trials]}
    out["machine_health"] = machine_health.stamp(health_start)
    if bios == "apres":
        before = json.loads((ROOT / "results/measures/stress_tfidf_ab_bios_avant.json").read_text(encoding="utf-8"))["trials"]
        v = stress.bios_verdict([stress.Trial(t["arm"], t["code"], t["digest"], t["error"]) for t in before], trials, reference_digest=REFERENCE_DIGEST)
        out["verdict"] = {"label": v.label, "crashes_before": v.crashes_before, "n_before": v.n_before, "crashes_after": v.crashes_after, "divergent_after": v.divergent_after, "n_after": v.n_after, "p_value": v.p_value}
    (ROOT / "results/measures").mkdir(exist_ok=True)
    (ROOT / f"results/measures/stress_tfidf_ab{suffix}.json").write_text(json.dumps(out, indent=1, ensure_ascii=False), encoding="utf-8")
    bad = {a: (s.crashes, s.mismatches) for a, s in summary.items() if s.crashes or s.mismatches}
    print(json.dumps({"n": len(trials), "stopped": stopped, "arms_with_problems": bad}, ensure_ascii=False))
    if "--register" in sys.argv:
        if bios:
            from llmft.mini_registry import register_run as register_bios
            n_div = sum(t.returncode == 0 and t.digest != REFERENCE_DIGEST for t in trials)
            print(register_bios(ROOT / "results/runs", {"kind": "measure", "slug": f"verification-machine-bios-{bios}", "status": "ok",
                                                        "summary": f"RM-64 : test de charge du TF-IDF, {len(trials)} essais libres, phase {bios} la mise à jour du BIOS",
                                                        "params": {"fiche": "experiments/2026-10-17-verification-machine-apres-bios.md", "n_texts": N_TEXTS, "seed": SEED, "planned": len(plan), "reference_digest": REFERENCE_DIGEST},
                                                        "metrics": {"n_trials": len(trials), "crashes": sum(s.crashes for s in summary.values()), "divergent_from_reference": n_div, "stopped": stopped, **({"verdict": out["verdict"]} if bios == "apres" else {})},
                                                        "machine_health": out["machine_health"],
                                                        "health_waiver": "mesure de l'instabilité elle-même : un segfault pendant ce run est une donnée mesurée, pas un défaut du run"}))
            return 0
        from llmft.mini_registry import register_run
        print(register_run(ROOT / "results/runs", {"kind": "measure", "slug": "stress-tfidf-libre-contre-epingle" if libre_contre_epingle else "stress-tfidf-par-coeur", "status": "ok", "summary": "Test de charge du TF-IDF par cœur logique (panne brute, empreinte du résultat)",
                                                    "params": {"fiche": "experiments/2026-10-07-stress-tfidf-libre-contre-epingle.md" if libre_contre_epingle else "experiments/2026-10-07-stress-tfidf-par-coeur.md", "tours": tours, "n_texts": N_TEXTS, "seed": SEED}, "metrics": {"n_trials": len(trials), "crashes": sum(s.crashes for s in summary.values()), "mismatches": sum(s.mismatches for s in summary.values()), "stopped": stopped}}))
    return 0


if __name__ == "__main__":
    sys.exit(child(sys.argv[sys.argv.index("--child") + 1]) if "--child" in sys.argv else main())
