"""Fils de `tokenizer_guard` : s'épingle sur un cœur AVANT tout import lourd, tokenise, écrit le résultat. Usage : python -m llmft.tokenizer_child ENTREE SORTIE."""
import os
import pickle
import sys
from pathlib import Path


def main(argv: list[str]) -> int:
    if hasattr(os, "sched_setaffinity"):
        os.sched_setaffinity(0, {min(os.sched_getaffinity(0))})
    from transformers import AutoTokenizer

    from llmft import tokenizer_guard

    name, texts, max_len = pickle.loads(Path(argv[1]).read_bytes())
    ids = tokenizer_guard.build_inputs_local(AutoTokenizer.from_pretrained(name), texts, max_len)
    cpus = len(os.sched_getaffinity(0)) if hasattr(os, "sched_getaffinity") else 0
    Path(argv[2]).write_bytes(pickle.dumps((ids, cpus)))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
