#!/usr/bin/env python3
"""Recoupement N36 du TF-IDF de référence A (fiche 2026-10-07-recoupement-tfidf-reference) : deux recalculs indépendants (un processus fils chacun) des cinq plis de
`tfidf_variants.py char-balanced`, comparés aux probabilités enregistrées. N'écrase jamais les prédictions enregistrées.
Usage : recoupement_tfidf.py WORKDIR [--register] ; le fils est lancé avec --child SORTIE.npz."""
import json
import subprocess
import sys
import time
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent))
REFERENCE = ROOT / "results/predictions/tfidf-variant-char-balanced.probs.npz"
CHILD_TIMEOUT = 3000
RETRY_PAUSE = 120
MAX_ATTEMPTS = 6


def child(out: Path) -> int:
    import p1_04_06_tfidf
    from llmft import tfidf

    texts, y, folds, excluded, ids = p1_04_06_tfidf.load("chapter", "folds")
    labels = sorted(set(y))
    scored = [lab for lab in labels if lab != excluded]
    grid = [(c, (3, 5)) for c in (10.0, 100.0, 1000.0)]
    oof = np.zeros((len(y), len(labels)))
    for k in range(5):
        tr, te = np.where(folds != k)[0], np.where(folds == k)[0]
        cfg = tfidf.select_config([texts[i] for i in tr], [y[i] for i in tr], folds[tr], (k + 1) % 5, labels, scored, grid, "balanced", "char_wb")
        oof[te] = tfidf.fit_predict_proba([texts[i] for i in tr], [y[i] for i in tr], [texts[i] for i in te], labels, cfg[0], cfg[1], "balanced", "char_wb")
        print(f"pli {k} C={cfg[0]}", flush=True)
    np.savez_compressed(out, ids=np.array(ids), probs=oof, labels=np.array(labels), folds=folds)
    return 0


def run_child(out: Path) -> dict:
    t0 = time.time()
    proc = subprocess.run([sys.executable, __file__, "--child", str(out)], capture_output=True, text=True, timeout=CHILD_TIMEOUT, check=False)
    ok = proc.returncode == 0 and out.exists()
    return {"ok": ok, "returncode": proc.returncode, "seconds": round(time.time() - t0), "stderr_tail": proc.stderr[-400:] if not ok else ""}


def main() -> int:
    if len(sys.argv) > 2 and sys.argv[1] == "--child":
        return child(Path(sys.argv[2]))
    import p1_04_06_tfidf
    from llmft import evaluation, recoupement
    from llmft.mini_registry import register_run

    work = Path(sys.argv[1])
    work.mkdir(parents=True, exist_ok=True)
    ref = np.load(REFERENCE, allow_pickle=False)
    _, y, _, excluded, _ = p1_04_06_tfidf.load("chapter", "folds")
    labels = sorted(set(y))
    idx = np.array([labels.index(v) for v in y])
    macro_reference = evaluation.chapter_report(idx, ref["probs"], labels, excluded=(excluded,))["macro_f1"]
    results = []
    for n in (1, 2):
        out = work / f"recalcul{n}.npz"
        failures = []
        for attempt in range(1, MAX_ATTEMPTS + 1):  # fiche v2 : essais répétés, chaque panne brute consignée
            out.unlink(missing_ok=True)
            info = run_child(out)
            if info["ok"]:
                break
            failures.append({"attempt": attempt, "returncode": info["returncode"], "seconds": info["seconds"], "stderr_tail": info["stderr_tail"]})
            print(json.dumps(failures[-1]), flush=True)
            if attempt < MAX_ATTEMPTS:
                time.sleep(RETRY_PAUSE)
        info = {**info, "failures": failures, "attempts": len(failures) + (1 if info["ok"] else 0)}
        if info["ok"]:
            new = np.load(out, allow_pickle=False)
            if not np.array_equal(new["ids"], ref["ids"]) or not np.array_equal(new["labels"], ref["labels"]):
                raise RuntimeError("identifiants ou classes différents de l'enregistré : comparaison impossible")
            info["comparison"] = recoupement.compare_probs(ref["probs"], new["probs"], new["folds"])
            info["macro_f1_recomputed"] = evaluation.chapter_report(idx, new["probs"], labels, excluded=(excluded,))["macro_f1"]
        results.append(info)
        print(json.dumps({k: v for k, v in info.items() if k != "stderr_tail"}), flush=True)
    verdicts = [r["comparison"]["verdict"] for r in results if r["ok"]]
    out_json = {"reference": str(REFERENCE.relative_to(ROOT)), "macro_f1_reference": macro_reference, "runs": results, "verdicts": verdicts, "crashes": sum(len(r["failures"]) for r in results), "impossible": sum(1 for r in results if not r["ok"])}
    path = ROOT / "results/measures/recoupement_tfidf.json"
    path.write_text(json.dumps(out_json, indent=1, ensure_ascii=False), encoding="utf-8")
    print(json.dumps({"verdicts": verdicts, "crashes": out_json["crashes"]}))
    if "--register" in sys.argv:
        f1s = [r["macro_f1_recomputed"] for r in results if r["ok"]]
        print(register_run(ROOT / "results/runs", {"kind": "measure", "slug": "recoupement-tfidf-reference", "status": "ok" if len(verdicts) == 2 else "failed",  # deux recalculs impossibles = « non résolu » (fiche v2)
              "summary": f"Recoupement de A par deux recalculs : {verdicts}, macro-F1 {f1s} contre {macro_reference:.4f} enregistré, {out_json['crashes']} panne(s) brute(s)",
              "params": {"reference_run": "20261004-002944-tfidf-variant-char-balanced"}, "metrics": out_json}))
    return 0 if len(verdicts) == 2 else 1


if __name__ == "__main__":
    sys.exit(main())
