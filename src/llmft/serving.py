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
    meta: dict[str, Any] = field(default_factory=dict)


def train_bundle(
    texts: list[str], y: list[str], labels: list[str], c: float, ngram: tuple[int, int], oof_probs: NDArray[np.float64], oof_y: NDArray[np.int_],
    alpha: float = 0.10, coverage_target: float = 0.70, meta: dict[str, Any] | None = None, class_weight: str | None = None, analyzer: str = "word",
) -> Bundle:
    vec, model = tfidf.fit_model(texts, y, c, ngram, class_weight, analyzer)
    temperature = calibration.fit_temperature(oof_probs, oof_y)
    cal = calibration.apply_temperature(oof_probs, temperature)
    qhat = conformal.fit(cal, oof_y, alpha, "lac")
    conf = np.sort(cal.max(1))[::-1]
    threshold = float(conf[max(0, round(coverage_target * len(conf)) - 1)])
    return Bundle(vec, model, list(labels), float(temperature), float(qhat), threshold, alpha, dict(meta or {}, c=c, ngram=list(ngram), coverage_target=coverage_target, class_weight=class_weight, analyzer=analyzer))


def predict_probs(bundle: Bundle, texts: list[str]) -> NDArray[np.float64]:
    return calibration.apply_temperature(tfidf.predict_aligned(bundle.vec, bundle.model, texts, bundle.labels), bundle.temperature)


def predict(bundle: Bundle, texts: list[str]) -> list[dict[str, Any]]:
    probs = predict_probs(bundle, texts)
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
    meta = {"labels": bundle.labels, "temperature": bundle.temperature, "qhat": bundle.qhat, "abstain_threshold": bundle.abstain_threshold, "alpha": bundle.alpha, "model_sha256": sha, "meta": bundle.meta}
    (d / "meta.json").write_text(json.dumps(meta, ensure_ascii=False, indent=1), encoding="utf-8")


def load_bundle(directory: Path | str) -> Bundle:
    d = Path(directory)
    meta = json.loads((d / "meta.json").read_text(encoding="utf-8"))
    if hashlib.sha256((d / "model.joblib").read_bytes()).hexdigest() != meta["model_sha256"]:
        raise ValueError("empreinte du modèle différente de celle des métadonnées : fichier modifié")
    obj = _joblib.load(d / "model.joblib")
    return Bundle(obj["vec"], obj["model"], meta["labels"], meta["temperature"], meta["qhat"], meta["abstain_threshold"], meta["alpha"], meta["meta"])
