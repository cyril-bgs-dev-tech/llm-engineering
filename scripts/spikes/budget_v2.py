#!/usr/bin/env python3
"""Budget du premier cycle, version du 03/10/2026 : réglage sur une graine (C2), postes ajoutés par la seconde relecture.

Entrées : débits par pli et par époque du run `20261002-115918-p0-45-budget-hypotheses` (mesures P0-08, longueurs P0-21).
Ce sont des HYPOTHÈSES (aucun surcoût de remplissage, 2 époques, pas de relance), pas des durées annoncées : RM-16 les recale.
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))
from llmft.mini_registry import register_run

ROOT = Path(__file__).resolve().parents[2]
SOURCE = json.loads((ROOT / "results/runs/20261002-115918-p0-45-budget-hypotheses.json").read_text(encoding="utf-8"))["metrics"]["per_model"]
EPOCHS, DEV_OVER_FOLD = 2, 3586 / 2868
students = {n.split(" ")[0]: v for n, v in SOURCE.items() if "élève" in n}  # débit par pli et par époque
low = min(v["heures_pli_epoque_optimiste"] for v in students.values())  # élève le moins coûteux (Gemma-4-E4B)
high = max(v["heures_pli_epoque_optimiste"] for v in students.values())  # élève le plus coûteux (Qwen3.5-9B)
teach = {n.split(" ")[0]: v for n, v in SOURCE.items() if "prof" in n}
t_opt = min(v["heures_pli_epoque_optimiste"] for v in teach.values())
t_opt_hi = max(v["heures_pli_epoque_optimiste"] for v in teach.values())
t_pes = min(v["heures_pli_epoque_pessimiste"] for v in teach.values())
t_pes_hi = max(v["heures_pli_epoque_pessimiste"] for v in teach.values())


def student(runs: float, dev: bool = False) -> tuple[float, float]:
    f = DEV_OVER_FOLD if dev else 1.0
    return runs * EPOCHS * f * low, runs * EPOCHS * f * high


lines = {
    "criblage_3_eleves_2_taux (P1-11)": (EPOCHS * 2 * sum(v["heures_pli_epoque_optimiste"] for v in students.values()),) * 2,
    "reglage_reference_4_taux_1_graine (P1-13)": student(4),
    "variance_5_graines_reference (P1-19)": student(5),
    "rejeu_reference (P1-26)": student(1),
    "reglage_3_variantes_4_taux_1_graine": student(12),
    "reglage_taux_professeur_1_taux_1_pli (P2-01)": (EPOCHS * t_opt, EPOCHS * t_opt_hi),
    "professeur_5_plis (P2-02), optimiste": (5 * EPOCHS * t_opt, 5 * EPOCHS * t_opt_hi),
    "confirmatoire_4_recettes_5_graines (P3-07)": student(20, dev=True),
}
total_low = sum(a for a, _ in lines.values())
total_high = sum(b for _, b in lines.values())
student_h = {n.split(" ")[0]: v["heures_pli_epoque_optimiste"] for n, v in SOURCE.items() if "élève" in n}
teacher_h = {n.split(" ")[0]: (v["heures_pli_epoque_optimiste"], v["heures_pli_epoque_pessimiste"]) for n, v in SOURCE.items() if "prof" in n}
FOLD_RUNS = 4 + 5 + 1 + 12  # réglage de la référence, variance, rejeu, réglage des trois variantes (un pli chacun)
combos = {}
for s_name, hs in student_h.items():
    for t_name, (t_o, t_p) in teacher_h.items():
        base = 5.76 + (FOLD_RUNS + 20 * DEV_OVER_FOLD) * EPOCHS * hs
        combos[f"{s_name} + {t_name}"] = [round(base + 6 * EPOCHS * t_o, 1), round(base + 6 * EPOCHS * t_p, 1)]  # optimiste, pessimiste (professeur P2-01 et P2-02)
pess_extra_low = 6 * EPOCHS * (t_pes - t_opt)  # le réglage P2-01 (1 pli) compte aussi au débit pessimiste
pess_extra_high = 6 * EPOCHS * (t_pes_hi - t_opt_hi)
record = {
    "kind": "measure", "slug": "budget-v3-premier-cycle", "status": "ok",
    "summary": "Budget du premier cycle (v3, corrige P2-01 au debit pessimiste ; combinaisons eleve et professeur) apres relecture du 03/10/2026 : reglage sur une graine pour toutes les familles, avec P2-01 et P1-26 ajoutes ; hypotheses, pas des durees ; postes non comptes listes",
    "params": {"source_run": "20261002-115918-p0-45-budget-hypotheses", "epochs": EPOCHS, "dev_over_fold_patients": round(DEV_OVER_FOLD, 4), "student_low": "Gemma-4-E4B", "student_high": "Qwen3.5-9B"},
    "metrics": {
        "lines_hours_low_high": {k: [round(a, 2), round(b, 2)] for k, (a, b) in lines.items()},
        "total_hours_optimistic_low_high": [round(total_low, 1), round(total_high, 1)],
        "total_hours_pessimistic_teacher_incl_p2_01_low_high": [round(total_low + pess_extra_low, 1), round(total_high + pess_extra_high, 1)],
        "total_optimistic_pessimistic_by_student_teacher": combos,
        "not_counted": ["pre-entrainement tache voisine (P2-07)", "spike de distillation (RM-19)", "encodeur 4 taux (P1-07)", "relances apres panne", "inference hors pli", "calibration et conforme", "chargements", "vagues V2 a V5"],
    },
}
print(json.dumps(record, ensure_ascii=False, indent=1))
if "--register" in sys.argv:
    print(register_run(ROOT / "results/runs", record))
