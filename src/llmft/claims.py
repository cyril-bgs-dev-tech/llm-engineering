"""Contrôle de traçabilité des affirmations : chaque identifiant de run cité entre accents graves dans un document doit exister au registre (claim-gate, audit GLM v4)."""
import re
from typing import Any

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


# Chiffres balisés des présentations (RM-59) : <span data-claim="clé">valeur</span>, la clé renvoie à `docs/presentation/claims.json`
# (run ou slug unique, chemin pointé dans le run, décimales, échelle, signe), la valeur écrite doit être exactement celle du registre.
_SPAN = re.compile(r"<span\b[^>]*\bdata-claim=\"([^\"]+)\"[^>]*>([^<]*)</span>")
MINUS = "−"
THIN_NBSP = " "


def claim_spans(html: str) -> list[tuple[str, str]]:
    return [(k, v.strip()) for k, v in _SPAN.findall(html)]


def format_fr(value: float, decimals: int, signed: bool = False) -> str:
    """Nombre à la française : virgule décimale, espace fine insécable entre milliers, vrai signe moins, « + » si `signed`."""
    text = f"{abs(value):,.{decimals}f}".replace(",", THIN_NBSP).replace(".", ",")
    if round(value, decimals) < 0:
        return MINUS + text
    return ("+" + text) if signed else text


def _resolve(record: Any, path: str | list[str]) -> Any:
    """Chemin pointé (« metrics.points.2.macro_f1 ») ou liste de clés, pour une clé qui contient un point (« 0.7 »)."""
    node = record
    for part in (path.split(".") if isinstance(path, str) else path):
        node = node[int(part)] if isinstance(node, list) else node[part]
    return node


def check_claim_values(spans: list[tuple[str, str]], ledger: dict[str, dict[str, Any]], records: dict[str, dict[str, Any]]) -> list[str]:
    """Erreurs pour chaque chiffre balisé : clé inconnue, run introuvable ou ambigu, champ absent, valeur écrite différente de celle du registre."""
    by_slug: dict[str, list[dict[str, Any]]] = {}
    for r in records.values():
        by_slug.setdefault(str(r.get("slug")), []).append(r)
    errors = []
    for key, written in spans:
        spec = ledger.get(key)
        if spec is None:
            errors.append(f"{key} : clé inconnue de claims.json")
            continue
        run = spec["run"]
        if run in records:
            record = records[run]
        elif len(by_slug.get(run, [])) == 1:
            record = by_slug[run][0]
        elif run in by_slug:
            errors.append(f"{key} : slug {run} ambigu ({len(by_slug[run])} runs) : citer le run_id")
            continue
        else:
            errors.append(f"{key} : run {run} introuvable au registre")
            continue
        try:
            value = float(_resolve(record, spec["path"]))
        except (KeyError, IndexError, ValueError, TypeError):
            errors.append(f"{key} : champ {spec['path']} absent du run {run}")
            continue
        expected = format_fr(value * float(spec.get("scale", 1)), int(spec["decimals"]), bool(spec.get("signed", False)))
        if written != expected:
            errors.append(f"{key} : écrit « {written} », le registre donne « {expected} » ({run}, {spec['path']})")
    return errors
