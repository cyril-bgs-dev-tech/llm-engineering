#!/usr/bin/env python3
"""Frontière coût-qualité des systèmes servables (RM-48) : toutes les valeurs sont lues dans le registre (results/runs), aucune n'est saisie à la main.
Qualité : macro-F1 hors pli, cinq plis de développement ; coût d'entraînement : durée des runs finaux ; latence : service d'un seul tenant (run `service-g-bout-en-bout-*`), et pour G en cascade la latence attendue du service HTTP (run `service-g-cascade`).
Usage : pareto_cout_qualite.py [--register] [--supersedes RUN_ID] ; écrit results/measures/pareto_cout_qualite.json et imprime le tableau Markdown."""
import glob
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from llmft import machine_health, pareto
from llmft.mini_registry import register_run

RUNS = ROOT / "results/runs"


def latest_exact(names: list[str], slug: str) -> str | None:
    """Dernier fichier de run dont le slug est exactement `slug` (« service-g-cascade » ne doit pas attraper « energie-service-g-cascade »)."""
    exact = sorted(n for n in names if re.fullmatch(rf"\d{{8}}-\d{{6}}-{re.escape(slug)}\.json", n))
    return exact[-1] if exact else None


def run(slug: str) -> dict:
    name = latest_exact([Path(f).name for f in glob.glob(str(RUNS / "*.json"))], slug)
    if name is None:
        raise SystemExit(f"run introuvable : {slug}")
    return json.loads((RUNS / name).read_text(encoding="utf-8"))


def seconds(slug_prefix: str) -> float:
    return sum(json.loads(Path(f).read_text(encoding="utf-8"))["metrics"]["seconds_total"] for f in sorted(glob.glob(str(RUNS / f"*-{slug_prefix}*.json"))))


def main() -> int:
    start = machine_health.snapshot()
    cand = run("selection-systeme-final-apres-rm56")["metrics"]["candidats"]
    q = {k[0]: v["macro_f1"] for k, v in cand.items()}  # A, B, D, E, F, G
    t_tfidf, t_enc, t_lora, t_student = seconds("final-tfidf"), seconds("final-encoder-s"), seconds("final-lora-s"), seconds("final-student-s")
    gpu, cpu = run("service-g-bout-en-bout-gpu")["metrics"], run("service-g-bout-en-bout-cpu")["metrics"]
    st = gpu["passages"][0]["etages_p50_ms"]
    enc_ms = st["tokenisation_encodeur"] + st["cinq_encodeurs"]
    lora_ms = st["tokenisation_lora"] + st["lora"]
    tfidf_ms = run("bench-serving-tfidf-charbal-v1")["metrics"]["latence_ms_p50"]
    seuil, conforme = run("cascade-cinq-plis-encodeur-lora")["metrics"], run("cascade-conforme-cinq-plis")["metrics"]
    student_ms = st["tokenisation_encodeur"] + 3 * st["cinq_encodeurs"] / 5  # trois élèves, un réseau chacun
    casc_eg, serv_eg = run("cascade-e-puis-g")["metrics"], run("service-g-cascade")["metrics"]  # RM-60 : qualité hors pli, latence attendue des chemins mesurés par HTTP
    points = {
        "A TF-IDF (processeur)": (q["A"], t_tfidf, tfidf_ms, "bench-serving-tfidf-charbal-v1"),
        "D encodeurs x5 (GPU)": (q["D"], t_enc, enc_ms, "service-g-bout-en-bout-gpu"),
        "E encodeurs x5 + TF-IDF (GPU)": (q["E"], t_enc + t_tfidf, enc_ms + st["tfidf"], "service-g-bout-en-bout-gpu"),
        "E encodeurs x5 + TF-IDF (processeur seul)": (q["E"], t_enc + t_tfidf, cpu["passages"][0]["total"]["p50_ms"], "service-g-bout-en-bout-cpu"),
        "F LoRA 4B seul (GPU)": (q["F"], t_lora, lora_ms, "service-g-bout-en-bout-gpu"),
        "G LoRA + encodeurs + TF-IDF (GPU)": (q["G"], t_lora + t_enc + t_tfidf, gpu["passages"][0]["total"]["p50_ms"], "service-g-bout-en-bout-gpu"),
        "Cascade encodeurs puis LoRA, seuil 0,5": (seuil["macro_f1_cascade"], t_enc + t_lora, enc_ms + (1 - seuil["part_traitee_par_le_premier"]) * lora_ms, "cascade-cinq-plis-encodeur-lora"),
        "Cascade encodeurs puis LoRA, routage conforme": (conforme["macro_f1_cascade_conforme"], t_enc + t_lora, enc_ms + (1 - conforme["part_traitee_par_le_premier"]) * lora_ms, "cascade-conforme-cinq-plis"),
        "G servi en cascade E puis G, seuil 0,6 (GPU, HTTP)": (casc_eg["macro_f1"]["cascade"], t_lora + t_enc + t_tfidf, serv_eg["latence_moyenne_attendue_ms"], "cascade-e-puis-g, service-g-cascade"),
        "C2 élève distillé x3, professeurs imbriqués (écarté, RM-56)": (0.753, t_enc + t_tfidf + t_student, student_ms, "final-student-s*"),
    }
    out = pareto.analyse({n: pareto.Point(v[0], v[1], v[2]) for n, v in points.items()})
    rows = [{"systeme": n, "macro_f1": round(v[0], 4), "entrainement_h": round(v[1] / 3600, 2), "latence_ms": round(v[2], 1), "domine_par": out[n].dominated_by, "source": v[3]} for n, v in points.items()]
    print("| Système | macro-F1 | entraînement (h) | latence p50 (ms) | dominé par |\n|---|---|---|---|---|")
    for r in rows:
        print(f"| {r['systeme']} | {r['macro_f1']:.4f} | {r['entrainement_h']} | {r['latence_ms']} | {', '.join(r['domine_par']) or 'aucun (frontière)'} |")
    (ROOT / "results/measures/pareto_cout_qualite.json").write_text(json.dumps(rows, indent=1, ensure_ascii=False), encoding="utf-8")
    if "--register" in sys.argv:
        record = {"kind": "measure", "slug": "frontiere-cout-qualite", "status": "ok", "summary": "Frontière coût-qualité des systèmes servables, valeurs lues dans le registre",
                  "params": {"dimensions": ["macro_f1", "entrainement_s", "latence_ms"]}, "metrics": {"points": rows}, "machine_health": machine_health.stamp(start)}
        if "--supersedes" in sys.argv:
            record["supersedes"] = sys.argv[sys.argv.index("--supersedes") + 1]
        print(register_run(RUNS, record))
    return 0


if __name__ == "__main__":
    sys.exit(main())
