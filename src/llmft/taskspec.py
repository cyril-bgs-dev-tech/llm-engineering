"""Contrat de tâche `task_specs/<task_id>.yaml` : tout ce qui est propre à une tâche vit là, le code ne lit que lui."""
from __future__ import annotations

from pathlib import Path
from typing import Any, Literal

import yaml
from pydantic import BaseModel, ConfigDict, Field, ValidationError, field_validator, model_validator

TaskType = Literal["multiclass", "multilabel", "pair_ordinal"]
ALLOWED_PRIMARY: dict[str, set[str]] = {
    "multiclass": {"macro_f1", "accuracy", "log_loss"},
    "multilabel": {"macro_f1", "micro_f1"},
    "pair_ordinal": {"spearman", "quadratic_kappa"},
}
SLUG = r"^[a-z][a-z0-9_]*$"


class ContractError(ValueError):
    """Contrat de tâche invalide, illisible ou introuvable ; le message nomme le champ en cause."""


class _Strict(BaseModel):
    model_config = ConfigDict(extra="forbid")


class InputSpec(_Strict):
    unit: Literal["document", "patient", "pair"]
    max_tokens: int = Field(gt=0)
    truncation: Literal["head", "tail", "head_tail"]


class ClassSpec(_Strict):
    id: str = Field(pattern=SLUG)
    name: str = Field(min_length=1)
    definition: str
    exclusions: list[str] = Field(default_factory=list)
    parent: str | None = None

    @field_validator("definition")
    @classmethod
    def _definition_not_blank(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("definition vide : chaque classe porte une définition opérationnelle")
        return value


class OutputSpec(_Strict):
    format: str

    @field_validator("format")
    @classmethod
    def _has_placeholder(cls, value: str) -> str:
        if "{class_id}" not in value and "{class_ids}" not in value:
            raise ValueError("le format de sortie doit contenir {class_id} (ou {class_ids} pour multilabel)")
        return value


class MetricsSpec(_Strict):
    primary: str
    secondary: list[str] = Field(default_factory=list)


class AbstentionSpec(_Strict):
    enabled: bool = False
    label: str | None = None


class TaskSpec(_Strict):
    task_id: str = Field(pattern=SLUG)
    title: str
    type: TaskType
    input: InputSpec
    classes: list[ClassSpec]
    output: OutputSpec
    metrics: MetricsSpec
    abstention: AbstentionSpec = Field(default_factory=AbstentionSpec)
    source: str | None = None
    notes: list[str] = Field(default_factory=list)  # règles communes à toute la tâche (départage, métriques, portée)

    @model_validator(mode="after")
    def _cross_checks(self) -> TaskSpec:
        ids = [c.id for c in self.classes]
        if len(ids) < 2:
            raise ValueError("une tâche déclare au moins 2 classes")
        dup = sorted({i for i in ids if ids.count(i) > 1})
        if dup:
            raise ValueError(f"identifiants de classe dupliqués : {dup}")
        for c in self.classes:
            if c.parent is not None and c.parent not in ids:
                raise ValueError(f"parent inconnu pour la classe {c.id} : {c.parent}")
        parents = {c.id: c.parent for c in self.classes}
        for start in ids:
            seen: set[str] = set()
            cur: str | None = start
            while cur is not None:
                if cur in seen:
                    raise ValueError(f"cycle dans la hiérarchie des classes autour de {start}")
                seen.add(cur)
                cur = parents[cur]
        if self.metrics.primary not in ALLOWED_PRIMARY[self.type]:
            raise ValueError(
                f"metrique primaire {self.metrics.primary!r} non admise pour le type {self.type} : {sorted(ALLOWED_PRIMARY[self.type])}"
            )
        if self.abstention.enabled:
            if not self.abstention.label:
                raise ValueError("abstention activée : un libellé `label` est obligatoire")
            if self.abstention.label in ids:
                raise ValueError("abstention : le libellé ne peut pas être une classe de la tâche")
        return self

    @property
    def class_ids(self) -> list[str]:
        return [c.id for c in self.classes]

    def render_output(self, class_id: str) -> str:
        if class_id not in self.class_ids:
            raise KeyError(class_id)
        return self.output.format.replace("{class_id}", class_id)

    def parent_of(self, class_id: str) -> str | None:
        return next(c.parent for c in self.classes if c.id == class_id)

    def children_of(self, class_id: str) -> list[str]:
        return [c.id for c in self.classes if c.parent == class_id]


def _format_errors(path: Path, error: ValidationError) -> str:
    lines = []
    for item in error.errors():
        where = ".".join(str(p) for p in item["loc"]) or "contrat"
        lines.append(f"{where} : {item['msg']}")
    return f"contrat invalide ({path.name}) :\n  " + "\n  ".join(lines)


def load_task_spec(path: Path | str) -> TaskSpec:
    p = Path(path)
    if not p.exists():
        raise ContractError(f"contrat introuvable : {p}")
    try:
        raw: Any = yaml.safe_load(p.read_text(encoding="utf-8"))
    except yaml.YAMLError as exc:
        raise ContractError(f"YAML illisible ({p.name}) : {exc}") from exc
    if not isinstance(raw, dict):
        raise ContractError(f"contrat invalide ({p.name}) : le fichier doit contenir un dictionnaire")
    try:
        return TaskSpec.model_validate(raw)
    except ValidationError as exc:
        raise ContractError(_format_errors(p, exc)) from exc
