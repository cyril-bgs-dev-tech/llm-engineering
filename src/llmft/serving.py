"""Service d'inférence minimal et déployable du classifieur de chapitre (audit : efficience et déploiement).

Un « bundle » = TF-IDF + régression logistique ajustés sur le développement, température, quantile conforme LAC et seuil d'abstention (couverture cible),
ces trois derniers calculés sur des prédictions hors pli. Sauvegarde : modèle (joblib) + métadonnées avec l'empreinte du fichier ; le chargement refuse un fichier modifié.
Entrée : texte brut. Sortie : étiquette, probabilité calibrée, ensemble conforme, indicateur d'abstention (passage à l'humain). Aucune donnée n'est conservée."""
import hashlib
import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, cast

import joblib
import numpy as np
from numpy.typing import NDArray

from llmft import calibration, conformal, tfidf

_joblib: Any = cast(Any, joblib)  # joblib n'a pas de stubs : le typage strict porte sur notre code


@dataclass
class Bundle:
    vec: Any
    model: Any
    labels: list[str]
    temperature: float
    qhat: float
    abstain_threshold: float
    alpha: float
    group_of_class: dict[int, int] | None = None
    qhat_group: dict[int, float] | None = None
    meta: dict[str, Any] = field(default_factory=dict)


def train_bundle(
    texts: list[str], y: list[str], labels: list[str], c: float, ngram: tuple[int, int], oof_probs: NDArray[np.float64], oof_y: NDArray[np.int_],
    alpha: float = 0.10, coverage_target: float = 0.70, meta: dict[str, Any] | None = None, class_weight: str | None = None, analyzer: str = "word",
    group_of_class: dict[int, int] | None = None,
) -> Bundle:
    vec, model = tfidf.fit_model(texts, y, c, ngram, class_weight, analyzer)
    temperature = calibration.fit_temperature(oof_probs, oof_y)
    cal = calibration.apply_temperature(oof_probs, temperature)
    qhat = conformal.fit(cal, oof_y, alpha, "lac")
    conf = np.sort(cal.max(1))[::-1]
    threshold = float(conf[max(0, round(coverage_target * len(conf)) - 1)])
    qgroup = conformal.fit_by_group(cal, oof_y, group_of_class, alpha, "lac") if group_of_class is not None else None
    return Bundle(vec, model, list(labels), float(temperature), float(qhat), threshold, alpha, group_of_class, qgroup, dict(meta or {}, c=c, ngram=list(ngram), coverage_target=coverage_target, class_weight=class_weight, analyzer=analyzer))


def predict_probs(bundle: Bundle, texts: list[str]) -> NDArray[np.float64]:
    return calibration.apply_temperature(tfidf.predict_aligned(bundle.vec, bundle.model, texts, bundle.labels), bundle.temperature)


def predict(bundle: Bundle, texts: list[str], mode: str = "marginal") -> list[dict[str, Any]]:
    """`mode` : « marginal » (ensembles courts) ou « famille » (couverture visée par famille de chapitres, ensembles plus grands)."""
    probs = predict_probs(bundle, texts)
    if mode == "famille":
        if bundle.group_of_class is None or bundle.qhat_group is None:
            raise ValueError("ce bundle n'a pas de quantiles par famille")
        sets = conformal.predict_sets_by_group(probs, bundle.qhat_group, bundle.group_of_class, "lac")
    else:
        sets = conformal.predict_sets(probs, bundle.qhat, "lac")
    out = []
    for row, s in zip(probs, sets, strict=True):
        top = int(row.argmax())
        out.append({"label": bundle.labels[top], "probability": float(row[top]), "set": sorted(bundle.labels[k] for k in s), "abstain": bool(row[top] < bundle.abstain_threshold)})
    return out


def save_bundle(bundle: Bundle, directory: Path | str) -> None:
    d = Path(directory)
    d.mkdir(parents=True, exist_ok=True)
    _joblib.dump({"vec": bundle.vec, "model": bundle.model}, d / "model.joblib", compress=3)
    sha = hashlib.sha256((d / "model.joblib").read_bytes()).hexdigest()
    meta = {"labels": bundle.labels, "temperature": bundle.temperature, "qhat": bundle.qhat, "abstain_threshold": bundle.abstain_threshold, "alpha": bundle.alpha, "model_sha256": sha,
            "group_of_class": None if bundle.group_of_class is None else {str(k): v for k, v in bundle.group_of_class.items()}, "qhat_group": None if bundle.qhat_group is None else {str(k): v for k, v in bundle.qhat_group.items()}, "meta": bundle.meta}
    (d / "meta.json").write_text(json.dumps(meta, ensure_ascii=False, indent=1), encoding="utf-8")


def load_bundle(directory: Path | str) -> Bundle:
    d = Path(directory)
    meta = json.loads((d / "meta.json").read_text(encoding="utf-8"))
    if hashlib.sha256((d / "model.joblib").read_bytes()).hexdigest() != meta["model_sha256"]:
        raise ValueError("empreinte du modèle différente de celle des métadonnées : fichier modifié")
    obj = _joblib.load(d / "model.joblib")
    groups = None if meta.get("group_of_class") is None else {int(k): v for k, v in meta["group_of_class"].items()}
    qgroups = None if meta.get("qhat_group") is None else {int(k): v for k, v in meta["qhat_group"].items()}
    return Bundle(obj["vec"], obj["model"], meta["labels"], meta["temperature"], meta["qhat"], meta["abstain_threshold"], meta["alpha"], groups, qgroups, dict(meta["meta"], model_sha256=meta["model_sha256"]))
