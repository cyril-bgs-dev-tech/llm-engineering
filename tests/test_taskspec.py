"""Contrat de tâche (P0-35) : un contrat invalide est rejeté avec un message clair, le code ne lit que le contrat."""
import copy
from pathlib import Path

import pytest
import yaml

from llmft import taskspec

VALID = {
    "task_id": "toy_sentiment",
    "title": "Sentiment jouet",
    "type": "multiclass",
    "input": {"unit": "document", "max_tokens": 128, "truncation": "head_tail"},
    "classes": [
        {"id": "pos", "name": "Positif", "definition": "Le texte exprime une satisfaction.", "exclusions": ["Texte neutre"]},
        {"id": "neg", "name": "Négatif", "definition": "Le texte exprime une insatisfaction."},
    ],
    "output": {"format": "{class_id}"},
    "metrics": {"primary": "macro_f1", "secondary": ["accuracy", "log_loss", "ece"]},
    "abstention": {"enabled": False},
}


def write(tmp_path, spec, name="t.yaml"):
    p = tmp_path / name
    p.write_text(yaml.safe_dump(spec, allow_unicode=True), encoding="utf-8")
    return p


def mutate(**changes):
    spec = copy.deepcopy(VALID)
    for key, value in changes.items():
        spec[key] = value
    return spec


def test_valid_contract_loads_and_exposes_closed_class_list(tmp_path):
    spec = taskspec.load_task_spec(write(tmp_path, VALID))
    assert spec.task_id == "toy_sentiment"
    assert spec.class_ids == ["pos", "neg"]
    assert spec.render_output("neg") == "neg"


@pytest.mark.parametrize(
    "bad, message",
    [
        (mutate(classes=[VALID["classes"][0], {**VALID["classes"][0]}]), "dupliqu"),
        (mutate(classes=[VALID["classes"][0]]), "au moins 2 classes"),
        (mutate(classes=[{**VALID["classes"][0], "definition": "  "}, VALID["classes"][1]]), "definition"),
        (mutate(classes=[{**VALID["classes"][0], "parent": "inconnu"}, VALID["classes"][1]]), "parent"),
        (mutate(metrics={"primary": "spearman", "secondary": []}), "metrique primaire"),
        (mutate(output={"format": "toujours positif"}), "{class_id}"),
        (mutate(type="regression"), "type"),
        (mutate(task_id="Nom Avec Espaces"), "task_id"),
        (mutate(extra_field=1), "extra_field"),
    ],
)
def test_invalid_contract_is_rejected_with_a_clear_message(tmp_path, bad, message):
    with pytest.raises(taskspec.ContractError) as err:
        taskspec.load_task_spec(write(tmp_path, bad))
    assert message in str(err.value)


def test_parent_cycle_is_rejected(tmp_path):
    classes = [
        {"id": "a", "name": "A", "definition": "a", "parent": "b"},
        {"id": "b", "name": "B", "definition": "b", "parent": "a"},
    ]
    with pytest.raises(taskspec.ContractError, match="cycle"):
        taskspec.load_task_spec(write(tmp_path, mutate(classes=classes)))


def test_abstention_enabled_requires_a_label_and_it_is_not_a_class(tmp_path):
    ok = mutate(abstention={"enabled": True, "label": "abstention"})
    assert taskspec.load_task_spec(write(tmp_path, ok)).abstention.label == "abstention"
    for bad in ({"enabled": True}, {"enabled": True, "label": "pos"}):
        with pytest.raises(taskspec.ContractError, match="abstention"):
            taskspec.load_task_spec(write(tmp_path, mutate(abstention=bad), "b.yaml"))


def test_missing_file_is_reported_clearly(tmp_path):
    with pytest.raises(taskspec.ContractError, match="introuvable"):
        taskspec.load_task_spec(tmp_path / "absent.yaml")


def test_hierarchy_helpers(tmp_path):
    classes = [
        {"id": "root", "name": "R", "definition": "r"},
        {"id": "kid", "name": "K", "definition": "k", "parent": "root"},
        {"id": "kid2", "name": "K2", "definition": "k2", "parent": "root"},
    ]
    spec = taskspec.load_task_spec(write(tmp_path, mutate(classes=classes)))
    assert spec.children_of("root") == ["kid", "kid2"]
    assert spec.parent_of("kid") == "root"
    assert spec.parent_of("root") is None


REAL = sorted((Path(__file__).resolve().parents[1] / "task_specs").glob("*.yaml"))


@pytest.mark.parametrize("path", REAL, ids=[p.stem for p in REAL])
def test_every_committed_contract_is_valid_and_named_after_its_file(path):
    assert taskspec.load_task_spec(path).task_id == path.stem
