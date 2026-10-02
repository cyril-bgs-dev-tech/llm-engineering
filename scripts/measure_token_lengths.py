#!/usr/bin/env python3
"""P0-21 : longueurs en tokens des documents et des patients (documents concaténés) pour chaque tokenizer candidat.

Seuls les fichiers du tokenizer sont téléchargés, jamais les poids. Sortie : results/measures/token_lengths.json
"""
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from transformers import AutoTokenizer

ROOT = Path(__file__).resolve().parents[1]
PARQUET = ROOT / "data/raw/parhaf/data/train-00000-of-00001.parquet"
REVISION = "60426ccdbbbb335e0281f2e5c236b89100ffbd42"
TOKENIZERS = [
    "Qwen/Qwen3.5-9B",
    "Qwen/Qwen3.8-27B",
    "google/gemma-4-E4B-it",
    "google/gemma-4-31B-it",
    "mistralai/Mistral-Small-3.2-24B-Instruct-2506",
]
THRESHOLDS = (1024, 2048, 4096, 8192)


def summarize(lengths: list[int]) -> dict[str, float]:
    a = np.asarray(lengths)
    out = {"n": int(a.size), "median": float(np.median(a)), "p95": float(np.percentile(a, 95)),
           "p99": float(np.percentile(a, 99)), "max": int(a.max())}
    out.update({f"share_over_{t}": round(float((a > t).mean()), 4) for t in THRESHOLDS})
    return out


def main() -> int:
    df = pd.read_parquet(PARQUET)
    docs = [list(d["text"]) for d in df.documents]
    flat = [t for ds in docs for t in ds]
    patients = ["\n\n".join(ds) for ds in docs]
    tokenizers: dict[str, object] = {}
    result: dict[str, object] = {"revision": REVISION, "n_patients": len(patients), "n_documents": len(flat), "tokenizers": tokenizers}
    for name in TOKENIZERS:
        try:
            # Le tokenizer Mistral publié a une regex erronée : le correctif est obligatoire pour des longueurs justes
            tok = AutoTokenizer.from_pretrained(name, **({"fix_mistral_regex": True} if "Mistral" in name else {}))
        except (OSError, ValueError, KeyError) as exc:  # modèle absent, conditionné ou tokenizer illisible : on le consigne, on ne l'invente pas
            tokenizers[name] = {"error": f"{type(exc).__name__}: {str(exc)[:160]}"}
            print(f"{name} : ERREUR {type(exc).__name__}", file=sys.stderr)
            continue
        per_doc = [len(x) for x in tok(flat, add_special_tokens=False)["input_ids"]]
        per_patient = [len(x) for x in tok(patients, add_special_tokens=False)["input_ids"]]
        tokenizers[name] = {
            "vocab_size": len(tok), "per_document": summarize(per_doc), "per_patient": summarize(per_patient),
            "tokens_per_word": round(sum(per_doc) / float(df.documents.map(lambda d: sum(d["word_count"])).sum()), 3),
        }
        print(f"{name} ok", file=sys.stderr)
    out = ROOT / "results/measures/token_lengths.json"
    out.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"écrit : {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
