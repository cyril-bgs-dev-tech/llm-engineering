"""Registre de runs complet (P0-41) : immuable, schéma obligatoire, compatible avec le mini-registre."""
import copy

import pytest

from llmft import mini_registry, registry

ENV = {"python": "3.12", "torch": "2.11.0+cu128", "cuda": "12.8", "gpu": "NVIDIA GeForce RTX 5090", "n_gpu": 1, "hardware_profile": "rtx5090", "location": "local"}
RUN = {
    "kind": "train", "slug": "lora-ref", "status": "ok", "summary": "référence",
    "experiment": "experiments/2026-10-02-ref.md", "supersedes": None,
    "git_sha": "abc123", "git_dirty": False,
    "config": {"lr": 2e-4}, "data": {"task": "toy_sentiment", "fold": 0, "seed": 1, "sha256": {"p": "00"}},
    "env": ENV, "preflight": {"vram_gib": 12.0}, "metrics": {"macro_f1": 0.5}, "cost": {"seconds": 12.0, "vram_peak_gib": 9.0},
}


def run(**changes):
    r = copy.deepcopy(RUN)
    r.update(changes)
    return r


def test_valid_run_is_written_once_and_never_overwritten(tmp_path):
    path = registry.register_run(tmp_path, run(run_id="20261002-120000-lora-ref"))
    before = path.read_bytes()
    with pytest.raises(FileExistsError):
        registry.register_run(tmp_path, run(run_id="20261002-120000-lora-ref", summary="modifié"))
    assert path.read_bytes() == before


def test_a_run_without_env_is_refused_and_nothing_is_written(tmp_path):
    bad = run()
    del bad["env"]
    with pytest.raises(registry.RegistryError, match="env"):
        registry.register_run(tmp_path, bad)
    assert list(tmp_path.iterdir()) == []


@pytest.mark.parametrize("missing", ["experiment", "git_sha", "git_dirty", "config", "data", "preflight", "metrics", "cost"])
def test_every_required_field_is_enforced(tmp_path, missing):
    bad = run()
    del bad[missing]
    with pytest.raises(registry.RegistryError, match=missing):
        registry.register_run(tmp_path, bad)


def test_env_must_carry_the_reproducibility_fields(tmp_path):
    for key in ("python", "torch", "gpu", "hardware_profile", "location"):
        env = {k: v for k, v in ENV.items() if k != key}
        with pytest.raises(registry.RegistryError, match=key):
            registry.register_run(tmp_path, run(env=env))


def test_rented_runs_must_state_their_real_cost(tmp_path):
    with pytest.raises(registry.RegistryError, match="cost"):
        registry.register_run(tmp_path, run(env={**ENV, "location": "loué"}))
    assert registry.register_run(tmp_path, run(env={**ENV, "location": "loué", "rental_cost_eur": 3.2}, run_id="20261002-130000-loue"))


def test_failed_and_aborted_runs_are_recorded_with_their_reason(tmp_path):
    with pytest.raises(registry.RegistryError, match="error"):
        registry.register_run(tmp_path, run(status="failed"))
    with pytest.raises(registry.RegistryError, match="reason"):
        registry.register_run(tmp_path, run(status="aborted"))
    assert registry.register_run(tmp_path, run(status="failed", error="OOM", run_id="20261002-140000-oom"))
    assert registry.register_run(tmp_path, run(status="aborted", reason="arrêt anticipé", run_id="20261002-150000-stop"))


def test_supersedes_must_name_an_existing_run(tmp_path):
    first = registry.register_run(tmp_path, run(run_id="20261002-120000-a"))
    with pytest.raises(registry.RegistryError, match="supersedes"):
        registry.register_run(tmp_path, run(supersedes="20990101-000000-fantome", run_id="20261002-120001-b"))
    ok = registry.register_run(tmp_path, run(supersedes="20261002-120000-a", run_id="20261002-120002-c"))
    assert first.exists() and ok.exists()


def test_mini_registry_runs_remain_readable_and_listable(tmp_path):
    mini_registry.register_run(tmp_path, {"kind": "spike", "slug": "s", "status": "ok", "summary": "x", "run_id": "20261001-100000-s"})
    registry.register_run(tmp_path, run(run_id="20261002-120000-lora-ref"))
    assert [r["run_id"] for r in registry.list_runs(tmp_path)] == ["20261001-100000-s", "20261002-120000-lora-ref"]


def test_collect_env_reports_the_real_machine():
    env = registry.collect_env(hardware_profile="rtx5090", location="local")
    assert env["python"].startswith("3.") and "torch" in env and env["location"] == "local"


def test_git_state_survives_a_machine_without_git(tmp_path, monkeypatch):
    monkeypatch.setenv("PATH", str(tmp_path))  # aucun exécutable git trouvable
    state = registry.git_state(tmp_path)
    assert state == {"git_sha": "no-git", "git_dirty": True}


def test_git_state_without_commit_is_marked_dirty(tmp_path):
    import subprocess

    subprocess.run(["git", "-C", str(tmp_path), "init", "-q"], check=True)
    assert registry.git_state(tmp_path) == {"git_sha": "no-commit", "git_dirty": True}
