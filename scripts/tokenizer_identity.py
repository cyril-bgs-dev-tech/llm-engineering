#!/usr/bin/env python3
"""Identité des identifiants produits par le sous-processus épinglé (`tokenizer_guard.isolated_build_inputs`) et par le calcul local non épinglé (RM-58, question Q24).

Pour chaque tokenizer (CamemBERT-bio à 508, Qwen3.5-4B à 4096), sur les textes de développement : identifiants du fils épinglé contre identifiants d'un fils non épinglé
(relancé après chaque plantage, comptés). Aucune étiquette n'est lue. Usage : tokenizer_identity.py [--register]. Lancer avec HF_HOME=$PWD/artifacts/hf_cache."""
import os
import pickle
import subprocess
import sys
import tempfile
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent))
import p1_04_06_tfidf
from llmft.mini_registry import register_run
from llmft.tokenizer_guard import isolated_build_inputs

MODELS = (("almanach/camembert-bio-base", 508), ("Qwen/Qwen3.5-4B", 4096))
UNPINNED = "import pickle,sys;from transformers import AutoTokenizer;from llmft import tokenizer_guard as g;n,t,m=pickle.load(open(sys.argv[1],'rb'));pickle.dump(g.build_inputs_local(AutoTokenizer.from_pretrained(n),t,m),open(sys.argv[2],'wb'))"


def unpinned(name: str, texts: list[str], max_len: int, attempts: int = 12) -> tuple[list[list[int]] | None, int]:
    """Calcul local sans épinglage dans un fils jetable, relancé après chaque plantage ; renvoie (identifiants ou None, nombre de plantages)."""
    crashes = 0
    with tempfile.TemporaryDirectory() as tmp:
        inp, out = Path(tmp) / "in.pkl", Path(tmp) / "out.pkl"
        inp.write_bytes(pickle.dumps((name, texts, max_len)))
        env = {**os.environ, "PYTHONPATH": os.pathsep.join(p for p in (str(ROOT / "src"), os.environ.get("PYTHONPATH", "")) if p)}
        for _ in range(attempts):
            if subprocess.run([sys.executable, "-c", UNPINNED, str(inp), str(out)], env=env, capture_output=True, check=False).returncode == 0:
                return pickle.loads(out.read_bytes()), crashes
            crashes += 1
    return None, crashes


def main() -> int:
    texts, *_ = p1_04_06_tfidf.load("chapter")
    metrics: dict[str, dict[str, object]] = {}
    for name, max_len in MODELS:
        t0 = time.time()
        pinned = isolated_build_inputs(name, texts, max_len)
        t_pinned = time.time() - t0
        loose, crashes = unpinned(name, texts, max_len)
        identical = loose is not None and loose == pinned
        metrics[name] = {"n_textes": len(texts), "max_len": max_len, "secondes_epingle": round(t_pinned, 1), "plantages_non_epingle": crashes,
                         "non_epingle_abouti": loose is not None, "identiques": identical, "n_identifiants": sum(len(x) for x in pinned)}
        print(name, metrics[name], flush=True)
    ok = all(bool(m["identiques"]) for m in metrics.values())
    if "--register" in sys.argv:
        print(register_run(ROOT / "results/runs", {"kind": "measure", "slug": "tokenizer-identite-sous-processus-epingle", "status": "ok" if ok else "failed",
                                                    "summary": "Identifiants du sous-processus épinglé contre calcul local non épinglé, " + ("identiques" if ok else "DIFFÉRENTS ou non comparables") + " (CamemBERT-bio, Qwen3.5-4B, textes de développement)",
                                                    "params": {"textes": "développement, chapitre CIM-10", "exploratoire": True}, "metrics": metrics}))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
