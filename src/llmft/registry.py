"""Registre de runs complet (skill run-registry) : un fichier JSON par run, écrit une fois, schéma obligatoire.

Il complète `mini_registry` (bibliothèque standard, utilisé par les spikes) : le format est un sur-ensemble, les deux sortes
de runs se listent ensemble.
"""
from __future__ import annotations

import platform
import subprocess
from importlib import metadata
from pathlib import Path
from typing import Any

from llmft import mini_registry

REQUIRED = ("experiment", "git_sha", "git_dirty", "config", "data", "env", "preflight", "metrics", "cost")
REQUIRED_ENV = ("python", "torch", "gpu", "hardware_profile", "location")
RENTED = "loué"


class RegistryError(ValueError):
    """Run incomplet ou incohérent ; le message nomme le champ en cause. Rien n'est écrit."""


def _validate(record: dict[str, Any], runs_dir: Path) -> None:
    for field in REQUIRED:
        if field not in record:
            raise RegistryError(f"champ obligatoire manquant : {field}")
    env = record["env"]
    if not isinstance(env, dict):
        raise RegistryError("env doit être un dictionnaire")
    for key in REQUIRED_ENV:
        if key not in env:
            raise RegistryError(f"env : champ manquant : {key}")
    if env["location"] == RENTED and "rental_cost_eur" not in env:
        raise RegistryError("run loué : env.rental_cost_eur est obligatoire (le coût réel fait partie du run) ; cost incomplet")
    status = record.get("status")
    if status == "failed" and not record.get("error"):
        raise RegistryError("status failed : le champ error est obligatoire")
    if status == "aborted" and not record.get("reason"):
        raise RegistryError("status aborted : le champ reason est obligatoire")
    sup = record.get("supersedes")
    if sup is not None and not (runs_dir / f"{sup}.json").exists():
        raise RegistryError(f"supersedes : le run {sup} n'existe pas dans le registre")


def register_run(runs_dir: Path | str, record: dict[str, Any]) -> Path:
    """Valide le schéma complet puis écrit le run avec le mini-registre (mode « x » : jamais d'écrasement)."""
    directory = Path(runs_dir)
    _validate(record, directory)
    return mini_registry.register_run(directory, record)


def list_runs(runs_dir: Path | str) -> list[dict[str, Any]]:
    return mini_registry.list_runs(runs_dir)


def git_state(root: Path | str) -> dict[str, Any]:
    """Commit courant et arbre modifié ; sans commit `no-commit`, sans binaire git `no-git` ; dans les deux cas l'arbre compte comme modifié."""

    def run(*args: str) -> str:
        return subprocess.run(["git", "-C", str(root), *args], capture_output=True, text=True, check=False).stdout.strip()

    try:
        sha = run("rev-parse", "--verify", "HEAD")
        dirty = bool(run("status", "--porcelain")) or not sha
    except FileNotFoundError:
        return {"git_sha": "no-git", "git_dirty": True}
    return {"git_sha": sha or "no-commit", "git_dirty": dirty}


def collect_env(hardware_profile: str, location: str = "local", libs: tuple[str, ...] = ("transformers", "peft", "trl", "accelerate", "bitsandbytes")) -> dict[str, Any]:
    """Versions et matériel réellement présents au moment du run."""
    env: dict[str, Any] = {"python": platform.python_version(), "hardware_profile": hardware_profile, "location": location}
    try:
        import torch

        env["torch"] = torch.__version__
        env["cuda"] = torch.version.cuda
        env["n_gpu"] = torch.cuda.device_count()
        env["gpu"] = torch.cuda.get_device_name(0) if torch.cuda.is_available() else "aucun"
    except ImportError:
        env.update({"torch": "absent", "cuda": None, "n_gpu": 0, "gpu": "aucun"})
    for lib in libs:
        try:
            env[lib] = metadata.version(lib)
        except metadata.PackageNotFoundError:
            env[lib] = "absent"
    return env
