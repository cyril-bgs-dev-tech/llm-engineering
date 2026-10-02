"""Chaîne générique de bout en bout : contrat, chargeur, découpage, entraînement court, métriques, registre.

Rien ici ne dépend d'une tâche : tout ce qui est propre à une tâche vient du contrat et de l'adaptateur reçus en arguments.
"""
from __future__ import annotations

import hashlib
import json
import time
from pathlib import Path
from typing import Any

import numpy as np

from llmft import loader, metrics, models, registry, splits
from llmft.taskspec import TaskSpec

ROOT = Path(__file__).resolve().parents[2]


class ChainError(RuntimeError):
    """La chaîne a détecté une incohérence (fuite entre partitions, par exemple) : elle s'arrête sans rien enregistrer comme réussi."""


def run_chain(
    spec: TaskSpec,
    adapter: loader.Adapter,
    backend: str,
    steps: int,
    runs_dir: Path | str,
    seed: int = 0,
    fold: int = 0,
    hardware_profile: str = "rtx5090",
) -> dict[str, Any]:
    start = time.perf_counter()
    dataset = loader.load_dataset(spec, adapter)
    frame = dataset.frame
    part = splits.make_splits(frame[["id", "author", "label"]], seed=seed)
    leaks = splits.check_no_overlap(part)
    if leaks:
        raise ChainError(f"identifiants présents dans deux partitions : {leaks[:5]}")
    partitions = json.loads(part.to_json())
    train = loader.select(dataset, partitions, fold=fold, role="train")
    val = loader.select(dataset, partitions, fold=fold, role="validation")
    labels = spec.class_ids
    index = {c: i for i, c in enumerate(labels)}

    model = models.build_classifier(backend, num_labels=len(labels), max_tokens=min(spec.input.max_tokens, 128), seed=seed)
    model.fit(train["text"].tolist(), [index[x] for x in train["label"]], steps=steps)
    probs = model.predict_proba(val["text"].tolist())
    y_idx = np.array([index[x] for x in val["label"]])
    scores = metrics.compute([spec.metrics.primary, *spec.metrics.secondary], probs, y_idx, labels)

    vram = 0.0
    if backend == "gpu":
        import torch

        vram = round(torch.cuda.max_memory_allocated() / 2**30, 3)
    record: dict[str, Any] = {
        "kind": "chain", "slug": f"chain-{spec.task_id.replace('_', '-')}-{backend}", "status": "ok",
        "summary": f"chaîne {spec.task_id} sur {backend}, {steps} pas, pli {fold}",
        "experiment": "tests/test_transposability.py", "supersedes": None, **registry.git_state(ROOT),
        "config": {"steps": steps, "seed": seed, "fold": fold, "backend": backend, "model": models.HF_MODEL if backend == "gpu" else "hashed-bow"},
        "data": {
            "task": spec.task_id, "backend": backend, "fold": fold, "seed": seed, "n_train": len(train), "n_validation": len(val),
            "sha256": {"partitions": part.sha256(), "ids": hashlib.sha256("\n".join(sorted(frame["id"])).encode()).hexdigest()},
        },
        "env": registry.collect_env(hardware_profile=hardware_profile, location="local"),
        "preflight": {"vram_peak_gib": vram}, "metrics": scores,
        "cost": {"seconds": round(time.perf_counter() - start, 2), "vram_peak_gib": vram},
    }
    path = registry.register_run(runs_dir, record)
    record["run_id"] = path.stem
    return record
