#!/usr/bin/env python3
"""Audit GLM v3, C3-A6 : patients dont le texte dépasse 4 096 tokens (troncature tête+fin des LLM), par chapitre. Agrégats seulement.

Lancer avec HF_HOME=$PWD/artifacts/hf_cache TOKENIZERS_PARALLELISM=false."""
import json
import sys
from collections import Counter
from pathlib import Path

from transformers import AutoTokenizer

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(Path(__file__).resolve().parent))
import p1_04_06_tfidf

MAX_LEN = 4096


def main() -> int:
    texts, y, _, _, _ = p1_04_06_tfidf.load("chapter")
    tok = AutoTokenizer.from_pretrained("Qwen/Qwen3.5-9B")
    lengths = [len(tok(t, add_special_tokens=False)["input_ids"]) for t in texts]
    over = [c for n, c in zip(lengths, y, strict=True) if n > MAX_LEN]
    out = {"n": len(texts), "tronques": len(over), "par_chapitre": dict(Counter(over)), "max": max(lengths)}
    (ROOT / "results/measures/glm_v3_truncated.json").write_text(json.dumps(out, indent=1), encoding="utf-8")
    print(out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
