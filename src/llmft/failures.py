"""Classement d'un run échoué, par le code et à partir de l'historique de perte (PROTOCOLE.md 6.4, P1-19).

Divergence : au moins une perte non finie dans l'historique (résultat de la graine, ni remplacée ni relancée).
Panne d'infrastructure : tout autre échec (mémoire, coupure, entrée-sortie) ; relance autorisée avec la même graine."""
from __future__ import annotations

import math
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

from llmft.mini_registry import register_run


def classify(loss_history: Sequence[float], error: str | None = None) -> str:
    """`divergence` si une perte n'est pas finie, sinon `infrastructure` ; le texte de l'erreur ne décide jamais."""
    return "divergence" if any(not math.isfinite(x) for x in loss_history) else "infrastructure"


def may_retry(attempts: Sequence[Mapping[str, Any]]) -> bool:
    """Relance de la même graine : seulement si aucune tentative n'a abouti ni divergé et que la dernière est une panne d'infrastructure."""
    if not attempts or any(a.get("status") == "ok" for a in attempts):
        return False
    if any(a.get("failure_class") == "divergence" for a in attempts):
        return False
    return attempts[-1].get("failure_class") == "infrastructure"


def register_failed(runs_dir: Path | str, record: dict[str, Any]) -> Path:
    """Enregistre un échec : l'historique de perte est obligatoire, le classement est posé par `classify`."""
    if "loss_history" not in record:
        raise ValueError("loss_history obligatoire pour enregistrer un échec (classement par le code)")
    full = {**record, "status": "failed", "failure_class": classify(record["loss_history"], record.get("error"))}
    return register_run(runs_dir, full)
