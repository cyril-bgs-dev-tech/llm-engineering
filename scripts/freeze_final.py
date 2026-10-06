#!/usr/bin/env python3
"""Écrit `results/frozen_final.json` (RM-50, ADR-016) : composition de G, empreintes des modèles et des prédictions du temps A, paramètres de l'incertitude, prédiction chiffrée du test scellé.

Refuse d'écraser un gel existant. Ne lit aucune étiquette du test. Usage : freeze_final.py"""
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from llmft.freeze import build_frozen

OUT = ROOT / "results/frozen_final.json"
FICHE = ROOT / "experiments/2026-10-05-modeles-finaux.md"
PREDICTION = {
    "ecrite_le": "2026-10-06", "avant": "toute ouverture des étiquettes du test scellé ; valeurs centrales = valeurs de développement hors pli, intervalles élargis par l'entraînement sur tout le développement et le décalage d'auteurs",
    "macro_f1_test_systeme_final": {"centre": 0.78, "intervalle_80": [0.75, 0.81]},
    "difference_final_moins_tfidf_points": {"centre": 6.0, "intervalle_80": [3.3, 8.7]},
    "difference_final_moins_ensemble_points": {"centre": 0.8, "verdict_attendu": "non résolu", "probabilite": 0.9},
    "verdict_question_primaire": {"gain confirmé": 0.47, "non résolu": 0.50, "absence de gain utile": 0.03},
    "couverture_conforme_minimale_par_famille": {"cible": 0.90, "au_moins": 0.87, "probabilite": 0.6},
    "exactitude_a_70_pour_cent_de_couverture": {"centre": 0.95, "intervalle_80": [0.93, 0.97]},
}


def main() -> int:
    if OUT.exists():
        raise SystemExit("gel déjà écrit : aucune relance qui remplace (nouvelle ADR si le gel change)")
    frozen = build_frozen(ROOT / "results/runs", enc_seeds=(1000, 1001, 1002, 1003, 1004), lora_seeds=(1000,))
    frozen["fiche_modeles_finaux_sha256"] = hashlib.sha256(FICHE.read_bytes()).hexdigest()
    frozen["prediction_test_scelle"] = PREDICTION
    OUT.write_text(json.dumps(frozen, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    print("écrit", OUT, hashlib.sha256(OUT.read_bytes()).hexdigest())
    return 0


if __name__ == "__main__":
    sys.exit(main())
