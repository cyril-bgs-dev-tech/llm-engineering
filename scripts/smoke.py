#!/usr/bin/env python3
"""RM-09 : fil synthétique de bout en bout, sur CPU, sans donnée réelle.

Contrat, chargeur, découpage, modèle trivial, métriques, registre, rejeu identique, cas de fuite piégé, rapport.
Sortie : results/smoke_report.md ; code de sortie non nul au premier maillon qui échoue.
"""
import copy
import json
import sys
import tempfile
import time
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from llmft import leakage, pipeline, registry, splits, taskspec, toy

STEPS: list[tuple[str, str]] = []


def step(name: str, detail: str) -> None:
    STEPS.append((name, detail))
    print(f"[ok] {name} : {detail}")


def main() -> int:
    t0 = time.perf_counter()
    spec = taskspec.load_task_spec(ROOT / "task_specs/toy_sentiment.yaml")
    step("contrat", f"{spec.task_id}, {len(spec.class_ids)} classes")

    raw = yaml.safe_load((ROOT / "task_specs/toy_sentiment.yaml").read_text(encoding="utf-8"))
    bad = copy.deepcopy(raw)
    bad["classes"].append(copy.deepcopy(bad["classes"][0]))
    with tempfile.TemporaryDirectory() as tmp:
        broken = Path(tmp) / "bad.yaml"
        broken.write_text(yaml.safe_dump(bad, allow_unicode=True), encoding="utf-8")
        try:
            taskspec.load_task_spec(broken)
        except taskspec.ContractError as exc:
            step("contrat invalide rejeté", str(exc).splitlines()[-1].strip())
        else:
            raise SystemExit("ECHEC : un contrat invalide a été accepté")

        runs = Path(tmp) / "runs"
        first = pipeline.run_chain(spec, toy.ToyAdapter(n=50, seed=0), backend="cpu", steps=10, runs_dir=runs, seed=3)
        step("chaîne complète", f"run {first['run_id']}, macro_f1 {first['metrics']['macro_f1']:.3f}")
        second = pipeline.run_chain(spec, toy.ToyAdapter(n=50, seed=0), backend="cpu", steps=10, runs_dir=runs, seed=3)
        if first["metrics"] != second["metrics"] or first["data"]["sha256"] != second["data"]["sha256"]:
            raise SystemExit("ECHEC : le rejeu avec la même graine ne redonne pas les mêmes résultats")
        step("rejeu identique", "mêmes partitions (SHA-256) et mêmes métriques à graine égale")
        n_runs = len(registry.list_runs(runs))

    frame = toy.make_toy(n=50, seed=0)
    s = splits.make_splits(frame[["id", "author", "label"]], seed=3)
    leaked, leaked_id = splits.plant_leak(s)
    if not splits.check_no_overlap(leaked):
        raise SystemExit("ECHEC : un patient présent dans le test et un pli n'a pas été détecté")
    step("fuite piégée détectée (partitions)", f"identifiant {leaked_id} présent dans le test et le pli 0")
    texts = {"a": "Excellent accueil lors de ma visite de mardi, je recommande vivement ce service " * 3}
    texts["b"] = texts["a"].replace("mardi", "lundi")
    pairs = leakage.near_duplicate_pairs(texts)
    if not leakage.cross_partition_pairs(pairs, {"a": "test", "b": "pli0"}):
        raise SystemExit("ECHEC : un quasi-doublon entre partitions n'a pas été détecté")
    step("fuite piégée détectée (quasi-doublon)", f"similarité {pairs[0][2]}")

    elapsed = time.perf_counter() - t0
    report = ["# Rapport du fil synthétique (make smoke)", "", f"Durée : {elapsed:.1f} s, runs enregistrés pendant le fil : {n_runs}.", "", "| Maillon | Résultat |", "|---|---|"]
    report += [f"| {n} | {d} |" for n, d in STEPS]
    report += ["", "Le « rejeu » vérifie la reproductibilité à graine égale ; la reprise d'un entraînement interrompu est prouvée à part (spike P0-13, pertes identiques sur 20 pas)."]
    (ROOT / "results/smoke_report.md").write_text("\n".join(report) + "\n", encoding="utf-8")
    print(json.dumps({"ok": True, "seconds": round(elapsed, 1)}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
