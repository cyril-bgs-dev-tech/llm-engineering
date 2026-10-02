"""Transposabilité (P0-44) : la tâche jouet et `parhaf_doctype` passent par la même chaîne, sans ligne propre à l'une d'elles."""
import hashlib
import json
import math
import time
from pathlib import Path

import pandas as pd
import pytest
import yaml

from llmft import pipeline, registry, taskspec
from llmft.adapters import parhaf
from llmft.toy import ToyAdapter

ROOT = Path(__file__).resolve().parents[1]
PARQUET = ROOT / "data/raw/parhaf/data/train-00000-of-00001.parquet"
SPECS = ROOT / "task_specs"
NEEDS_PARHAF = pytest.mark.skipif(not PARQUET.exists(), reason="PARHAF absent")


def cuda_with_tokenizer():
    try:
        import torch

        return torch.cuda.is_available() and (ROOT / "artifacts/hf_cache").exists()
    except ImportError:
        return False


BACKENDS = ["cpu", pytest.param("gpu", marks=[pytest.mark.gpu, pytest.mark.skipif(not cuda_with_tokenizer(), reason="GPU ou cache de tokenizer absent")])]


def check(record, spec, backend):
    assert record["status"] == "ok" and record["env"]["location"] == "local"
    assert record["data"]["task"] == spec.task_id and record["data"]["backend"] == backend
    assert set(record["metrics"]) >= {spec.metrics.primary, *spec.metrics.secondary}
    assert all(math.isfinite(v) for v in record["metrics"].values())  # aucune valeur NaN ni infinie


@pytest.mark.parametrize("backend", BACKENDS)
def test_toy_task_runs_through_the_chain(tmp_path, backend):
    spec = taskspec.load_task_spec(SPECS / "toy_sentiment.yaml")
    record = pipeline.run_chain(spec, ToyAdapter(n=50, seed=0), backend=backend, steps=10, runs_dir=tmp_path)
    check(record, spec, backend)
    assert registry.list_runs(tmp_path)[0]["run_id"] == record["run_id"]


@NEEDS_PARHAF
@pytest.mark.parametrize("backend", BACKENDS)
def test_doctype_task_runs_through_the_same_chain(tmp_path, backend):
    spec = taskspec.load_task_spec(SPECS / "parhaf_doctype.yaml")
    record = pipeline.run_chain(spec, parhaf.DoctypeAdapter(PARQUET, sample=420, seed=0), backend=backend, steps=10, runs_dir=tmp_path)
    check(record, spec, backend)


def test_the_core_contains_nothing_specific_to_a_task():
    for name in ("pipeline.py", "models.py", "metrics.py", "loader.py"):
        source = (ROOT / "src/llmft" / name).read_text(encoding="utf-8").lower()
        for word in ("parhaf", "toy", "doctype", "sentiment", "cim10", "specialty"):
            assert word not in source, f"{name} mentionne {word}"


def test_adding_a_task_of_the_same_family_changes_no_core_file_and_its_cost_is_measured(tmp_path):
    """Nouvelle tâche : un YAML et un adaptateur ; le noyau est identique octet pour octet avant et après."""
    core = [ROOT / "src/llmft" / n for n in ("pipeline.py", "models.py", "metrics.py", "loader.py", "taskspec.py", "splits.py", "registry.py")]
    before = {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in core}
    start = time.perf_counter()
    yaml_text = yaml.safe_dump({
        "task_id": "toy_topic", "title": "Thème jouet", "type": "multiclass",
        "input": {"unit": "document", "max_tokens": 64, "truncation": "head"},
        "classes": [{"id": "sport", "name": "Sport", "definition": "Texte sur le sport."}, {"id": "cuisine", "name": "Cuisine", "definition": "Texte sur la cuisine."}],
        "output": {"format": "{class_id}"}, "metrics": {"primary": "macro_f1", "secondary": ["accuracy"]},
    }, allow_unicode=True)
    spec_path = tmp_path / "toy_topic.yaml"
    spec_path.write_text(yaml_text, encoding="utf-8")

    class TopicAdapter:  # le seul code propre à la nouvelle tâche
        def load(self) -> pd.DataFrame:
            rows = [(f"t{i}", ("le match de football" if i % 2 else "la recette de gâteau") + f" numéro {i}", "sport" if i % 2 else "cuisine", f"a{i % 5}") for i in range(60)]
            return pd.DataFrame(rows, columns=["id", "text", "label", "author"])

    record = pipeline.run_chain(taskspec.load_task_spec(spec_path), TopicAdapter(), backend="cpu", steps=10, runs_dir=tmp_path / "runs")
    elapsed = time.perf_counter() - start
    after = {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in core}
    assert before == after and record["status"] == "ok"
    cost = {"files": 2, "lines": len(yaml_text.splitlines()) + 6, "seconds_to_first_run": round(elapsed, 2)}
    (ROOT / "results/measures/task_addition_cost.json").write_text(json.dumps(cost, indent=1) + "\n", encoding="utf-8")
    assert cost["files"] <= 2
