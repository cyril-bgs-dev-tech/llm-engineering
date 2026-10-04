#!/usr/bin/env python3
"""Génère `docs/TABLEAUX_GENERES.md` à partir du registre (`results/runs/*.json`) : une seule source de vérité pour les chiffres des runs d'entraînement, sans recopie manuelle.
Usage : make_tables.py"""
import glob
import json
import statistics as st
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs/TABLEAUX_GENERES.md"
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent))
SYSTEMS = {"TF-IDF caractères équilibré": "tfidf-variant-char-balanced", "Encodeur moyenné (5 graines)": "cinq-plis-ensemble-encodeur5", "Ensemble encodeur + TF-IDF": "cinq-plis-ensemble-encodeur5-tfidf-charbal"}


def five_fold_section() -> list[str]:
    """Macro-F1 par pli et regroupée des prédictions hors pli à cinq plis, recalculée depuis les fichiers de probabilités (aucune recopie)."""
    import p1_04_06_tfidf
    from llmft.power_rule import _macro_f1

    _, y, folds, other, ids = p1_04_06_tfidf.load("chapter")
    fold_of = dict(zip(ids, folds.tolist(), strict=True))
    truth_of = dict(zip(ids, y, strict=True))
    lines = ["", "## Systèmes hors pli à cinq plis : macro-F1 (17 chapitres, AUTRE exclu) par pli et regroupée", "", "| système | pli 0 | pli 1 | pli 2 | pli 3 | pli 4 | regroupée (3 586) |", "|---|---|---|---|---|---|---|"]
    for name, slug in SYSTEMS.items():
        path = ROOT / "results/predictions" / f"{slug}.probs.npz"
        if not path.exists():
            continue
        z = np.load(path, allow_pickle=False)
        labels = [str(c) for c in z["labels"]]
        pid = [str(i) for i in z["ids"]]
        t = np.array([labels.index(truth_of[i]) for i in pid])
        pred = z["probs"].argmax(1)
        f = np.array([fold_of[i] for i in pid])
        scored = [labels.index(c) for c in labels if c != other]
        cells = [f4(_macro_f1(t[f == k][None, :], pred[f == k][None, :], scored)[0]) for k in range(5)]
        cells.append(f4(_macro_f1(t[None, :], pred[None, :], scored)[0]))
        lines.append(f"| {name} | " + " | ".join(cells) + " |")
    return lines


def show(x: object) -> str:
    return "" if x is None else str(x)


def f4(x: object) -> str:
    return f"{x:.4f}".replace(".", ",") if isinstance(x, int | float) else ""


def main() -> int:
    runs = []
    for f in sorted(glob.glob(str(ROOT / "results/runs/*.json"))):
        d = json.loads(Path(f).read_text(encoding="utf-8"))
        m = d.get("metrics", {})
        if d.get("kind") in ("train", "preflight") and d.get("status") == "ok" and isinstance(m.get("macro_f1"), int | float):
            runs.append({"slug": d["slug"], "run_id": d["run_id"], "fold": d.get("params", {}).get("fold"), "model": str(d.get("params", {}).get("model", "")), "lr": d.get("params", {}).get("lr"),
                         "epochs": d.get("params", {}).get("epochs"), "seed": d.get("params", {}).get("seed"), "variante": ("fenêtres " if d.get("params", {}).get("windows") else "") + ("perte pondérée " if d.get("params", {}).get("class_weights") not in (None, "none") else "") + ("duplication " if (d.get("params", {}).get("dup_factor") or 1) > 1 else "") + ("synthétique" if d.get("params", {}).get("synthetic") else ""), **{k: m.get(k) for k in ("macro_f1", "accuracy", "log_loss", "ece", "seconds_train")}})
    lines = ["# Tableaux générés depuis le registre (ne pas éditer à la main)", "", f"{len(runs)} runs d'entraînement terminés avec une macro-F1 au registre. Regénérer : `.venv/bin/python scripts/make_tables.py`.", "",
             "## Tous les runs d'entraînement (pli, modèle, taux, époques, graine)", "", "| slug | pli | modèle | taux | époques | graine | macro-F1 | exactitude | log loss | ECE | secondes |", "|---|---|---|---|---|---|---|---|---|---|---|"]
    for r in sorted(runs, key=lambda r: (r["model"], r["fold"] if r["fold"] is not None else -1, r["epochs"] or 0, str(r["lr"]), r["slug"])):
        lines.append(f"| `{r['slug']}` | {show(r['fold'])} | {r['model'].split('/')[-1]} | {show(r['lr'])} | {show(r['epochs'])} | {show(r['seed'])} | {f4(r['macro_f1'])} | {f4(r['accuracy'])} | {f4(r['log_loss'])} | {f4(r['ece'])} | {r['seconds_train'] if r['seconds_train'] is not None else ''} |")
    groups: dict[tuple, list[float]] = {}
    for r in runs:
        if r["model"] and r["epochs"] and r["fold"] is not None:
            groups.setdefault((r["model"].split("/")[-1], r["fold"], r["epochs"], str(r["lr"]), r["variante"].strip() or "recette standard"), []).append(r["macro_f1"])
    lines += ["", "## Variance entre runs de même configuration (au moins deux runs : graines et rejeux)", "", "| modèle | variante | pli | époques | taux | n | moyenne | écart-type | min | max |", "|---|---|---|---|---|---|---|---|---|---|"]
    for (model, fold, ep, lr, var), v in sorted(groups.items(), key=lambda kv: tuple(map(str, kv[0]))):
        if len(v) >= 2:
            lines.append(f"| {model} | {var} | {fold} | {ep} | {lr} | {len(v)} | {f4(st.mean(v))} | {f4(st.stdev(v))} | {f4(min(v))} | {f4(max(v))} |")
    lines += five_fold_section()
    OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(len(runs), "runs ->", OUT.relative_to(ROOT))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
