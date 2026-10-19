"""Tampon de santé de la machine autour d'un calcul (RM-59, Q26) : identifiant de démarrage, segfaults du journal du noyau, temps de fonctionnement.

Motif : le 07/10/2026, la machine a produit des pannes impossibles en Python correct et un résultat silencieusement différent sur 120 ;
un run qui a traversé un segfault du noyau ou un redémarrage ne peut pas être cru sur sa seule sortie. Le verdict ne prouve pas qu'un
calcul est juste (une erreur sans segfault reste possible : d'où `resilience.agree_twice`) ; il dit seulement quand il ne faut pas le croire.
Bibliothèque standard seule."""
from __future__ import annotations

import subprocess
from collections.abc import Callable
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class Snapshot:
    boot_id: str | None
    kernel_segfaults: int | None
    uptime_s: float | None


@dataclass(frozen=True)
class Verdict:
    status: str  # "ok", "suspect" ou "inconnu"
    reasons: tuple[str, ...]


def count_kernel_segfaults(dmesg_text: str) -> int:
    return sum(1 for line in dmesg_text.splitlines() if "segfault at" in line)


def _read_boot_id() -> str:
    return Path("/proc/sys/kernel/random/boot_id").read_text(encoding="ascii")


def _read_uptime() -> str:
    return Path("/proc/uptime").read_text(encoding="ascii")


def _read_dmesg() -> str:
    proc = subprocess.run(["dmesg"], capture_output=True, text=True, check=False, timeout=30)
    if proc.returncode != 0:
        raise PermissionError(proc.stderr.strip() or f"dmesg : code {proc.returncode}")
    return proc.stdout


def snapshot(read_boot_id: Callable[[], str] = _read_boot_id, read_uptime: Callable[[], str] = _read_uptime,
             read_dmesg: Callable[[], str] = _read_dmesg) -> Snapshot:
    """Photo de l'état de la machine ; une source illisible donne None, jamais une valeur inventée."""
    try:
        boot: str | None = read_boot_id().strip()[:8]
    except OSError:
        boot = None
    try:
        uptime: float | None = float(read_uptime().split()[0])
    except (OSError, ValueError, IndexError):
        uptime = None
    try:
        segv: int | None = count_kernel_segfaults(read_dmesg())
    except (OSError, subprocess.SubprocessError):
        segv = None
    return Snapshot(boot_id=boot, kernel_segfaults=segv, uptime_s=uptime)


def verdict(start: Snapshot, end: Snapshot) -> Verdict:
    """« suspect » si la machine a redémarré ou si le noyau a consigné un segfault entre les deux photos ; « inconnu » si le journal du noyau est illisible."""
    reasons = []
    if start.boot_id and end.boot_id and start.boot_id != end.boot_id:
        reasons.append(f"identifiant de démarrage changé ({start.boot_id} puis {end.boot_id}) : la machine a redémarré")
    elif start.uptime_s is not None and end.uptime_s is not None and end.uptime_s < start.uptime_s:
        reasons.append("temps de fonctionnement en recul : la machine a redémarré")
    if start.kernel_segfaults is not None and end.kernel_segfaults is not None and end.kernel_segfaults > start.kernel_segfaults:
        reasons.append(f"{end.kernel_segfaults - start.kernel_segfaults} segfault(s) du noyau pendant le calcul")
    if reasons:
        return Verdict("suspect", tuple(reasons))
    if start.kernel_segfaults is None or end.kernel_segfaults is None:
        return Verdict("inconnu", ("journal du noyau illisible : santé non vérifiable",))
    return Verdict("ok", ())


def stamp(start: Snapshot, end: Snapshot | None = None) -> dict[str, Any]:
    """Champ `machine_health` d'un run : photo de départ, photo de fin (prise maintenant si absente), verdict et raisons."""
    end = end if end is not None else snapshot()
    v = verdict(start, end)
    return {"start": asdict(start), "end": asdict(end), "verdict": v.status, "reasons": list(v.reasons)}


HEALTH_REQUIRED_SINCE = "2026-10-16T22:00:00Z"  # entrée en vigueur (RM-59, début de la séance du 17/10 heure de Paris) : les runs antérieurs n'avaient pas de tampon


def unhealthy_runs(records: list[dict[str, Any]], since: str = HEALTH_REQUIRED_SINCE) -> list[tuple[str, str]]:
    """Runs « ok » créés depuis `since` sans tampon, ou dont le tampon n'est pas « ok », sauf dérogation écrite (`health_waiver`)
    ou remplacement par un run sain qui les cite dans `supersedes` (convention du registre : une correction est un nouveau run)."""
    problems: dict[str, str] = {}
    for r in records:
        if r.get("status") != "ok" or str(r.get("created_at", "")) < since or str(r.get("health_waiver", "")).strip():
            continue
        health = r.get("machine_health")
        if not isinstance(health, dict):
            problems[r["run_id"]] = "sans tampon de santé de la machine"
        elif health.get("verdict") != "ok":
            problems[r["run_id"]] = f"verdict {health.get('verdict')} : {'; '.join(health.get('reasons') or [])}"
    covered = {str(r["supersedes"]) for r in records if r.get("supersedes") and r.get("status") == "ok" and r["run_id"] not in problems
               and (isinstance(r.get("machine_health"), dict) or str(r.get("health_waiver", "")).strip())}
    return [(run_id, reason) for run_id, reason in problems.items() if run_id not in covered]
