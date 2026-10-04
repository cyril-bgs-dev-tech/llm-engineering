"""Contrôle de traçabilité des affirmations : chaque identifiant de run cité entre accents graves dans un document doit exister au registre (claim-gate, audit GLM v4)."""
import re

_TOKEN = re.compile(r"`([a-z0-9][a-z0-9_.\-]*)`")
_FILE_SUFFIXES = (".py", ".sh", ".md", ".json", ".npz", ".yaml", ".yml", ".jsonl", ".txt", ".csv", ".toml")


def unknown_run_references(text: str, known: set[str], allow: set[str]) -> list[str]:
    """Identifiants de type « run » (au moins un tiret, 9 caractères ou plus) absents du registre et de la liste d'exceptions."""
    out = []
    for token in sorted(set(_TOKEN.findall(text))):
        if "-" not in token or len(token) < 9 or token.endswith(_FILE_SUFFIXES) or token in allow:
            continue
        if token in known or any(k.endswith("-" + token) for k in known):
            continue
        out.append(token)
    return out
