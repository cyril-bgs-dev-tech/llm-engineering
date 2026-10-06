#!/usr/bin/env python3
"""Seul script d'évaluation du test scellé (PROTOCOLE.md 6.8, PROTOCOLE_V2.md section 5). Quatre commandes :

  inputs NOM        temps A pour un modèle final : prédictions sur les TEXTES du test (aucune étiquette), écriture unique avec empreinte ;
  rehearsal         répétition générale du temps B sur les prédictions hors pli du développement (aucune lecture du test, aucun marqueur, aucun fichier du test) ;
  check             vérifie toutes les préconditions de l'ouverture et s'arrête ;
  open --confirm-open "RAISON"   temps B réel : une seule ouverture ; refuse si une précondition manque.

Les modèles finaux sont ceux de `scripts/final_models.py` (artifacts/final). Le système final et la référence viennent du fichier de gel `results/frozen_final.json` (RM-50), jamais d'un choix fait ici.
Usage : sealed_evaluation.py {inputs NOM | rehearsal | check | open --confirm-open RAISON}"""
import hashlib
import json
import sys
import tempfile
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent))
import glm_v3_families
import p1_04_06_tfidf
import p1_finetune
from llmft import cim10, final_report, freeze, loader, sealed, splits
from llmft.mini_registry import register_run

P = ROOT / "results/predictions"
TEMPS_A = ROOT / "results/sealed_temps_a"
FINAL = ROOT / "artifacts/final"
FROZEN = ROOT / "results/frozen_final.json"
RESULT = ROOT / "results/sealed_result.json"
PART, SHA = p1_04_06_tfidf.PART, p1_04_06_tfidf.SHA
DELTA = 2.0
ENC_SEEDS, STUDENT_SEEDS, LORA_SEEDS = (1000, 1001, 1002, 1003, 1004), (1000, 1001, 1002), (1000,)
MODEL_NAMES = ["tfidf", *[f"encoder-s{s}" for s in ENC_SEEDS], *[f"student-s{s}" for s in STUDENT_SEEDS], *[f"lora-s{s}" for s in LORA_SEEDS]]
OOF = {"A TF-IDF": ["tfidf-variant-char-balanced"], "D encodeur": ["cinq-plis-ensemble-encodeur5"], "E ensemble": ["cinq-plis-ensemble-encodeur5-tfidf-charbal"], "C2 élève distillé": ["cinq-plis-distill-ens-3graines"],
       "F LoRA": ["cinq-plis-llm-mur"], "G LoRA + encodeur + TF-IDF": ["cinq-plis-llm-mur", "cinq-plis-ensemble-encodeur5", "tfidf-variant-char-balanced"]}


def load_oof(files: list[str], ids: list[str]) -> np.ndarray:
    mats = []
    for f in files:
        z = np.load(P / f"{f}.probs.npz", allow_pickle=False)
        pos = {str(i): k for k, i in enumerate(z["ids"])}
        mats.append(z["probs"].astype(np.float64)[[pos[i] for i in ids]])
    return np.mean(mats, axis=0)


def compose_test(arrays: dict[str, np.ndarray]) -> dict[str, np.ndarray]:
    """Candidats du test à partir des prédictions du temps A : mêmes compositions que le développement (D, E, C2, F, G)."""
    tf = arrays["tfidf"]
    enc = np.mean([arrays[f"encoder-s{s}"] for s in ENC_SEEDS], axis=0)
    out = {"A TF-IDF": tf, "D encodeur": enc, "E ensemble": 0.5 * enc + 0.5 * tf, "C2 élève distillé": np.mean([arrays[f"student-s{s}"] for s in STUDENT_SEEDS], axis=0)}
    if all(f"lora-s{s}" in arrays for s in LORA_SEEDS):
        lora = np.mean([arrays[f"lora-s{s}"] for s in LORA_SEEDS], axis=0)
        out["F LoRA"] = lora
        out["G LoRA + encodeur + TF-IDF"] = np.mean([lora, enc, tf], axis=0)
    return out


def family_map(labels: list[str]) -> dict[int, int]:
    names = list(glm_v3_families.FAMILIES)
    fam_of_label = {c: names.index(n) for n, cs in glm_v3_families.FAMILIES.items() for c in cs}
    return {i: fam_of_label.get(lab, len(names)) for i, lab in enumerate(labels)}


def make_compute(labels: list[str], other: str, authors: dict[str, str], ids: list[str], probs_of: dict[str, np.ndarray], cal: dict[str, tuple[np.ndarray, np.ndarray]], final: str, reference: str, secondary: list[str]) -> Any:
    def compute(y_true: list[str], _preds: list[Any]) -> dict[str, Any]:
        truth = np.array([labels.index(v) for v in y_true])
        rep = final_report.full_report(truth, probs_of, labels, other, [authors[i] for i in ids], final, reference, secondary, DELTA, family_map(labels), cal)
        rep["ids_sha256"] = hashlib.sha256("\n".join(ids).encode()).hexdigest()
        return rep
    return compute


def dev_frame() -> tuple[pd.DataFrame, list[str], str]:
    texts, y, _, other, ids = p1_04_06_tfidf.load("chapter")
    meta = pd.read_parquet(p1_04_06_tfidf.PARQUET, columns=["id", "author"])
    author = dict(zip(meta["id"].astype(str), meta["author"], strict=True))
    frame = pd.DataFrame({"id": ids, "text": texts, "label": y, "author": [author[i] for i in ids]})
    return frame, sorted(set(y)), other or "AUTRE"


def text_frame() -> pd.DataFrame:
    """Identifiants et textes de tous les patients, SANS aucune étiquette (temps A)."""
    df = pd.read_parquet(p1_04_06_tfidf.PARQUET, columns=["id", "documents"])
    return pd.DataFrame({"id": df["id"].astype(str), "text": [p1_04_06_tfidf.patient_text(d) for d in df["documents"]]})


def full_frame() -> pd.DataFrame:
    """Tous les patients de l'ensemble de travail : texte, auteur et étiquette (politique des classes rares appliquée à l'ensemble de travail, comme make_splits)."""
    df = pd.read_parquet(p1_04_06_tfidf.PARQUET, columns=["id", "author", "suggested_scenario", "documents"])
    hierarchy = cim10.load_claml(p1_04_06_tfidf.CLAML)
    resolved = df["suggested_scenario"].map(lambda s: hierarchy.lookup(s["primary_diagnosis"]["code"][0]))
    df = df[resolved.notna()].copy()
    df["label"] = splits.apply_rare_class_policy(resolved[resolved.notna()].map(lambda r: r.chapter))
    df["id"] = df["id"].astype(str)
    df["text"] = [p1_04_06_tfidf.patient_text(d) for d in df["documents"]]
    return df[["id", "text", "label", "author"]].reset_index(drop=True)


def preconditions() -> list[str]:
    problems = []
    marker = ROOT / sealed.MARKER_PATH
    if marker.exists():
        problems.append("le test scellé est déjà ouvert")
    for n in MODEL_NAMES:
        if not (TEMPS_A / f"{n}.probs.npz").exists():
            problems.append(f"temps A manquant : {n}")
    if not FROZEN.exists():
        problems.append("fichier de gel absent : results/frozen_final.json (RM-50)")
    if not (ROOT / "docs/decisions/ADR-016-gel-du-systeme-final.md").exists():
        problems.append("ADR de gel absente : docs/decisions/ADR-016-gel-du-systeme-final.md")
    nested = ROOT / "results/measures/distill_analysis.json"
    if not nested.exists() or "nested" not in json.loads(nested.read_text(encoding="utf-8")):
        problems.append("verdict de RM-56 absent (distill_analysis.json sans bras imbriqué)")
    if FROZEN.exists() and not freeze.rehearsal_matches_freeze(ROOT / "results/runs", hashlib.sha256(FROZEN.read_bytes()).hexdigest()):
        problems.append("répétition générale du temps B absente ou antérieure au gel (empreinte du gel absente des paramètres du run)")
    return problems


def main() -> int:
    cmd = sys.argv[1]
    split = loader.load_partitions(PART, SHA)
    if cmd == "inputs":
        name = sys.argv[2]
        target = TEMPS_A / f"{name}.probs.npz"
        if target.exists():
            raise SystemExit(f"temps A déjà écrit pour {name} : aucune relance qui remplace")
        frame = text_frame()
        inputs = sealed.sealed_inputs(split, frame, "text", journal=ROOT / sealed.JOURNAL_PATH)
        ids = inputs["id"].tolist()
        texts = inputs["text"].tolist()
        probs = predict_final(name, texts)
        TEMPS_A.mkdir(parents=True, exist_ok=True)
        np.savez_compressed(target, ids=np.array(ids), probs=probs.astype(np.float32))
        sha = hashlib.sha256(target.read_bytes()).hexdigest()
        print(register_run(ROOT / "results/runs", {"kind": "measure", "slug": f"temps-a-{name}", "status": "ok", "summary": f"Temps A : prédictions du modèle final {name} sur les textes du test (aucune étiquette), empreinte {sha[:12]}", "params": {"n": len(ids)}, "metrics": {"sha256": sha}}))
        return 0
    frame_dev, labels, other = dev_frame()
    if cmd == "rehearsal":
        ids = frame_dev["id"].tolist()
        probs_of = {n: load_oof(f, ids) for n, f in OOF.items()}
        cal = {n: (p, np.array([labels.index(v) for v in frame_dev["label"]])) for n, p in probs_of.items()}
        authors = dict(zip(frame_dev["id"], frame_dev["author"], strict=True))
        fake_split = {"test": ids}  # répétition : tout le développement joue le rôle du test
        frozen = json.loads(FROZEN.read_text(encoding="utf-8"))  # la répétition utilise le système, la référence et les comparaisons du gel (RM-50), comme l'ouverture
        compute = make_compute(labels, other, authors, ids, probs_of, cal, frozen["final"], frozen["reference"], frozen["secondaires"])
        with tempfile.TemporaryDirectory() as tmp:
            rep = sealed.sealed_labels_and_score(fake_split, frame_dev, "label", {i: None for i in ids}, compute, marker=Path(tmp) / "m", reason="répétition générale du temps B sur le développement", out_path=Path(tmp) / "r.json", rehearsal=True)
        print(json.dumps({k: rep[k] for k in ("n", "question_primaire", "sensibilite")}, ensure_ascii=False, indent=1)[:1800])
        print(register_run(ROOT / "results/runs", {"kind": "measure", "slug": "repetition-generale-temps-b", "status": "ok", "params": {"n": rep["n"], "final": frozen["final"], "reference": frozen["reference"], "frozen_sha256": hashlib.sha256(FROZEN.read_bytes()).hexdigest()}, "summary": "Répétition générale du temps B réussie sur les prédictions hors pli du développement (aucune écriture de marqueur)", 
                                                    "metrics": {"verdict_question_primaire": rep["question_primaire"]["verdict"], "ids_sha256": rep["ids_sha256"]}}))
        return 0
    if cmd == "check":
        problems = preconditions()
        print("préconditions : " + ("toutes remplies" if not problems else "\n  - " + "\n  - ".join(problems)))
        return 0 if not problems else 1
    if cmd == "open":
        if "--confirm-open" not in sys.argv:
            raise SystemExit("--confirm-open RAISON obligatoire")
        reason = sys.argv[sys.argv.index("--confirm-open") + 1]
        problems = preconditions()
        if problems:
            raise SystemExit("ouverture refusée :\n  - " + "\n  - ".join(problems))
        frozen = json.loads(FROZEN.read_text(encoding="utf-8"))
        arrays = {}
        for n in MODEL_NAMES:
            z = np.load(TEMPS_A / f"{n}.probs.npz", allow_pickle=False)
            arrays[n] = (np.array([str(i) for i in z["ids"]]), z["probs"].astype(np.float64))
        test_ids = [str(i) for i in split["test"]]
        for n, (zid, _) in arrays.items():
            if list(zid) != test_ids:
                raise SystemExit(f"identifiants du temps A différents de ceux du test pour {n}")
        probs_of = compose_test({n: p for n, (_, p) in arrays.items()})
        dev_ids = frame_dev["id"].tolist()
        cal = {n: (load_oof(f, dev_ids), np.array([labels.index(v) for v in frame_dev["label"]])) for n, f in OOF.items() if n in probs_of}
        frame = full_frame()
        check_dev = frame.set_index("id").loc[dev_ids, "label"].tolist()
        if check_dev != frame_dev["label"].tolist():
            raise SystemExit("étiquettes du développement différentes selon la politique des classes rares : ouverture refusée avant tout accès")
        authors = dict(zip(frame["id"], frame["author"], strict=True))
        compute = make_compute(labels, other, authors, test_ids, probs_of, cal, frozen["final"], frozen["reference"], frozen["secondaires"])
        result = sealed.sealed_labels_and_score(split, frame, "label", {i: None for i in test_ids}, compute, marker=ROOT / sealed.MARKER_PATH, reason=reason, out_path=RESULT, journal=ROOT / sealed.JOURNAL_PATH)
        print(json.dumps({k: result[k] for k in ("n", "question_primaire")}, ensure_ascii=False, indent=1))
        return 0
    raise SystemExit("commande inconnue")


def predict_final(name: str, texts: list[str]) -> np.ndarray:
    """Prédictions d'un modèle final sur des textes ; probabilités alignées sur les classes du développement."""
    _, labels, _ = dev_frame()
    if name == "tfidf":
        import joblib

        from llmft import tfidf

        d = joblib.load(FINAL / "tfidf.joblib")
        return tfidf.predict_aligned(d["vec"], d["model"], texts, labels)
    import torch
    from transformers import AutoModelForSequenceClassification, AutoTokenizer

    if name.startswith(("encoder-s", "student-s")):
        path = FINAL / ("final-" + name)
        tok = AutoTokenizer.from_pretrained(path)
        model = AutoModelForSequenceClassification.from_pretrained(path, torch_dtype=torch.float32).to("cuda").eval()
        x = p1_finetune.build_inputs(tok, texts, 508)
        return p1_finetune.predict(model, x, tok.pad_token_id, "cuda", 16, len(labels))
    if name.startswith("lora-s"):
        from peft import PeftModel

        base_name = "Qwen/Qwen3.5-4B"
        tok = AutoTokenizer.from_pretrained(base_name)
        pad_id = tok.pad_token_id if tok.pad_token_id is not None else tok.eos_token_id
        base = AutoModelForSequenceClassification.from_pretrained(base_name, num_labels=len(labels), torch_dtype=torch.bfloat16)
        base.config.pad_token_id = pad_id
        if hasattr(base.config, "text_config"):
            base.config.text_config.pad_token_id = pad_id
        model = PeftModel.from_pretrained(base, FINAL / ("final-" + name)).to("cuda").eval()
        x = p1_finetune.build_inputs(tok, texts, 4096)
        return p1_finetune.predict(model, x, pad_id, "cuda", 1, len(labels))
    raise SystemExit(f"modèle inconnu : {name}")


if __name__ == "__main__":
    sys.exit(main())
