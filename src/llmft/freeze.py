"""Fichier de gel du système final (RM-50, `results/frozen_final.json`) : composition, runs et empreintes des modèles et des prédictions du temps A, paramètres de l'incertitude.

Il ne choisit rien : le système (G) vient de la règle de sélection écrite d'avance (run `selection-systeme-final-apres-rm56`). Il refuse un run absent ou ambigu (deux runs du même nom)."""
import json
from pathlib import Path
from typing import Any

DELTA = 2.0
CONFORMAL_LEVEL = 0.90
ABSTENTION_COVERAGES = (1.0, 0.9, 0.8, 0.7, 0.5)


def _run(runs_dir: Path, slug: str) -> dict[str, Any]:
    files = sorted(runs_dir.glob(f"*-{slug}.json"))
    if not files:
        raise FileNotFoundError(f"run absent : {slug}")
    if len(files) > 1:
        raise ValueError(f"plusieurs runs pour {slug} : {[f.name for f in files]}")
    record: dict[str, Any] = json.loads(files[0].read_text(encoding="utf-8"))
    if record.get("status") != "ok":
        raise ValueError(f"run {slug} non abouti : {record.get('status')}")
    return record


def build_frozen(runs_dir: Path, *, enc_seeds: tuple[int, ...], lora_seeds: tuple[int, ...]) -> dict[str, Any]:
    if not enc_seeds or not lora_seeds:
        raise ValueError("le système final annonce LoRA + encodeur + TF-IDF : au moins une graine d'encodeur et une de LoRA")
    names = ["tfidf", *[f"encoder-s{s}" for s in enc_seeds], *[f"lora-s{s}" for s in lora_seeds]]
    models: dict[str, dict[str, str]] = {}
    for name in names:
        train, preds = _run(runs_dir, f"final-{name}"), _run(runs_dir, f"temps-a-{name}")
        models[name] = {"run_entrainement": train["run_id"], "sha256_modele": train["metrics"]["sha256"], "run_temps_a": preds["run_id"], "sha256_temps_a": preds["metrics"]["sha256"]}
    return {
        "final": "G LoRA + encodeur + TF-IDF", "reference": "A TF-IDF", "secondaires": ["E ensemble", "F LoRA"], "delta": DELTA,
        "composition": {"lora": [f"lora-s{s}" for s in lora_seeds], "encodeur": [f"encoder-s{s}" for s in enc_seeds], "tfidf": "tfidf",
                        "poids": "un tiers LoRA, un tiers encodeur (moyenne de ses graines), un tiers TF-IDF"},
        "modeles": models,
        "incertitude": {"temperature": "aucune : ECE 0,016 avant et 0,020 après (run cinq-plis-ensemble-g), la calibration brute est conservée",
                        "niveau_conforme": CONFORMAL_LEVEL, "methode": "LAC marginal et LAC par famille (Mondrian), familles de scripts/glm_v3_families.py, quantiles calibrés sur les prédictions hors pli du développement seulement",
                        "abstention_couvertures": list(ABSTENTION_COVERAGES), "echangeabilite": "patients tirés du même corpus que le développement, mêmes auteurs possibles ; aucune garantie sous nouveaux auteurs"},
    }


def rehearsal_matches_freeze(runs_dir: Path, frozen_sha256: str) -> bool:
    """Vrai si une répétition générale du temps B a été faite avec ce gel (empreinte du fichier de gel dans ses paramètres) : une répétition antérieure au gel ne compte pas."""
    for path in runs_dir.glob("*-repetition-generale-temps-b.json"):
        record = json.loads(path.read_text(encoding="utf-8"))
        if record.get("status") == "ok" and record.get("params", {}).get("frozen_sha256") == frozen_sha256:
            return True
    return False
