"""Tokenisation dans un sous-processus épinglé sur un cœur, contre les erreurs de segmentation du tokenizer Rust de Hugging Face (tokenizers 0.23.2).

Mesuré le 05/10/2026 (run `20261005-224632-tokenizers-course-threads-qwen35`, diagnostic exploratoire) avec le tokenizer de Qwen3.5-4B sur les 3 586 textes de
développement : 25 plantages sur 31 runs sans épinglage (signal 11 ou panique `normalizer.rs:373`, à un indice différent à chaque fois), même avec
`TOKENIZERS_PARALLELISM=false`, `RAYON_NUM_THREADS=1`, dans un processus qui n'importe que `tokenizers`, et avec la bibliothèque copiée sur le disque ext4.
Aucun échec sur 78 runs épinglés sur un cœur dès le lancement et sur 6 runs avec l'ASLR coupé ; 8 échecs sur 34 quand l'épinglage est partiel ou posé après coup.
Une course entre threads du processus est la piste, pas un texte, pas la mémoire (4 passes de 4 Gio sans écart), pas un cœur, pas le disque.
Le contournement : tokeniser dans un processus fils épinglé avant ses imports, relancé en cas de plantage."""
import hashlib
import os
import pickle
import subprocess
import sys
import tempfile
from collections.abc import Sequence
from importlib.metadata import version
from pathlib import Path
from typing import Any

from llmft import lora_train

SRC = Path(__file__).resolve().parents[1]
DEFAULT_CACHE = SRC.parent / "artifacts" / "token_cache"


def build_inputs_local(tok: Any, texts: Sequence[str], max_len: int) -> list[list[int]]:
    """Tokens avec jetons spéciaux du modèle, troncature tête et fin avec marqueur `[...]` (calcul dans le processus courant)."""
    marker = tok.encode("[...]", add_special_tokens=False)
    prefix, suffix = lora_train.special_affixes(tok.encode)
    out = []
    for t in texts:
        ids = tok.encode(t, add_special_tokens=False)
        ids = lora_train.truncate_head_tail(ids, max_len, marker)  # max_len/2 tokens de tête et de fin, comme PROTOCOLE.md section 1
        out.append([*prefix, *ids, *suffix])
    return out


def run_child(name: str, texts: Sequence[str], max_len: int) -> tuple[list[list[int]], int]:
    """Un essai : renvoie les identifiants et le nombre de cœurs autorisés au fils pendant la tokenisation. Lève RuntimeError si le fils échoue."""
    with tempfile.TemporaryDirectory() as tmp:
        inp, out = Path(tmp) / "in.pkl", Path(tmp) / "out.pkl"
        inp.write_bytes(pickle.dumps((name, list(texts), max_len)))
        env = {**os.environ, "PYTHONPATH": os.pathsep.join(p for p in (str(SRC), os.environ.get("PYTHONPATH", "")) if p)}
        done = subprocess.run([sys.executable, "-m", "llmft.tokenizer_child", str(inp), str(out)], env=env, capture_output=True, text=True, check=False)
        if done.returncode != 0:
            raise RuntimeError(f"code {done.returncode} : {done.stderr.strip()[-300:]}")
        ids, cpus = pickle.loads(out.read_bytes())
        return ids, cpus


def _cache_file(cache_dir: Path, name: str, texts: Sequence[str], max_len: int) -> Path:
    """Clé : nom du tokenizer, longueur, versions de `tokenizers` et `transformers`, empreinte de chaque texte (un texte, un nom ou une version différents donnent un autre fichier)."""
    digest = hashlib.sha256()
    for part in (name, str(max_len), version("tokenizers"), version("transformers"), *(hashlib.sha256(t.encode("utf-8")).hexdigest() for t in texts)):
        digest.update(part.encode("utf-8") + b"\0")
    return cache_dir / f"{digest.hexdigest()}.pkl"


def isolated_build_inputs(name: str, texts: Sequence[str], max_len: int, *, attempts: int = 6, cache_dir: Path | None = DEFAULT_CACHE) -> list[list[int]]:
    """`build_inputs_local` dans un fils épinglé sur un cœur, relancé jusqu'à `attempts` fois (code de sortie 134, 139 ou 1 : plantage du tokenizer).

    Le résultat est mémorisé dans `cache_dir` (None : pas de cache) : le fils coûte 75 à 132 s par appel (mesuré le 06/10/2026), le cache le supprime aux appels suivants.
    Limite : la clé ne contient pas l'empreinte des fichiers du tokenizer ; vider `artifacts/token_cache` si le tokenizer d'un nom change sans changer de version de bibliothèque."""
    cache_file = _cache_file(cache_dir, name, texts, max_len) if cache_dir is not None else None
    if cache_file is not None and cache_file.exists():
        try:
            cached: list[list[int]] = pickle.loads(cache_file.read_bytes())
            return cached
        except (pickle.UnpicklingError, EOFError, AttributeError, ValueError):
            print(f"[tokenizer_guard] cache illisible, recalcul : {cache_file.name}", file=sys.stderr, flush=True)
    last = ""
    for attempt in range(1, attempts + 1):
        try:
            ids = run_child(name, texts, max_len)[0]
        except RuntimeError as err:
            last = str(err)
            print(f"[tokenizer_guard] essai {attempt}/{attempts} : {last}", file=sys.stderr, flush=True)
            continue
        if cache_file is not None:
            cache_file.parent.mkdir(parents=True, exist_ok=True)
            tmp = cache_file.with_suffix(".tmp")
            tmp.write_bytes(pickle.dumps(ids))
            tmp.replace(cache_file)
        return ids
    raise RuntimeError(f"tokenisation impossible après {attempts} essais ({name}) : {last}")
