#!/usr/bin/env python3
"""P1-26 : compare un run et son rejeu (même graine) : historiques de perte et prédictions. Usage : compare_determinism.py RUN_ID_A RUN_ID_B SLUG_PRED_A SLUG_PRED_B"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from llmft.determinism import compare


def main() -> int:
    run_a, run_b, slug_a, slug_b = sys.argv[1:5]
    la = json.loads((ROOT / f"results/runs/{run_a}.json").read_text(encoding="utf-8"))["loss_history"]
    lb = json.loads((ROOT / f"results/runs/{run_b}.json").read_text(encoding="utf-8"))["loss_history"]
    pa = json.loads((ROOT / f"results/predictions/{slug_a}.json").read_text(encoding="utf-8"))
    pb = json.loads((ROOT / f"results/predictions/{slug_b}.json").read_text(encoding="utf-8"))
    ma, mb = dict(zip(pa["ids"], pa["pred"], strict=True)), dict(zip(pb["ids"], pb["pred"], strict=True))
    ids = sorted(set(ma) & set(mb))
    out = compare(la, lb, [ma[i] for i in ids], [mb[i] for i in ids])
    print(json.dumps(out, indent=1))
    (ROOT / "results/measures/p1_26_determinism.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
