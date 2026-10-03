"""Empreinte SHA-256 d'un dossier (adaptateurs sauvegardés, audit GLM C6-A4) : noms et contenus, indépendante de l'ordre de création."""
import hashlib
from pathlib import Path


def dir_sha256(directory: Path | str) -> str:
    root = Path(directory)
    digest = hashlib.sha256()
    for path in sorted(p for p in root.rglob("*") if p.is_file()):
        digest.update(path.relative_to(root).as_posix().encode("utf-8") + b"\0")
        with open(path, "rb") as handle:
            for chunk in iter(lambda: handle.read(1 << 20), b""):
                digest.update(chunk)
        digest.update(b"\0")
    return digest.hexdigest()
