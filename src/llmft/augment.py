"""Sur-échantillonnage et données synthétiques ciblées (fiche 2026-10-04-synthetique-cible-chapitres-rares) : plan de duplication, contrôle de lignée, détection de copies de la validation.
Les contrôles complètent `llmft.leakage` (cinq contrôles de `leakage-guard`) ; aucun texte synthétique n'est jamais admis dans la validation."""
import random
from collections.abc import Mapping, Sequence
from typing import Any

from llmft import leakage


def duplication_plan(ids: Sequence[str], labels: Mapping[str, str], targets: set[str], factor: int) -> list[str]:
    """Identifiants d'entraînement, chaque patient d'une classe ciblée apparaissant `factor` fois en tout."""
    if factor < 1:
        raise ValueError("facteur de duplication inférieur à 1")
    plan: list[str] = []
    for i in ids:
        plan.extend([i] * (factor if labels[i] in targets else 1))
    return plan


def validated_synthetic(
    records: Sequence[Mapping[str, Any]], train_ids: set[str], targets: set[str], label_of: Mapping[str, str] | None = None
) -> list[Mapping[str, Any]]:
    """Lève ValueError si un texte n'a pas de source d'entraînement, une étiquette différente de celle de sa source, ou une classe non ciblée."""
    problems = leakage.check_synthetic_sources(records, train_ids)
    if problems:
        raise ValueError("lignée invalide : " + " ; ".join(problems))
    for r in records:
        if r["label"] not in targets:
            raise ValueError(f"{r['id']} : classe {r['label']} non cible")
        if label_of is not None and label_of[r["source_id"]] != r["label"]:
            raise ValueError(f"{r['id']} : étiquette {r['label']} différente de celle de sa source ({label_of[r['source_id']]})")
    return list(records)


def copies_of_validation(synthetic: Mapping[str, str], validation: Mapping[str, str], threshold: float = leakage.NEAR_DUPLICATE_THRESHOLD) -> list[str]:
    """Identifiants synthétiques quasi identiques à un texte de validation (copie ou paraphrase trop proche)."""
    pairs = leakage.near_duplicate_pairs({**synthetic, **validation}, threshold)
    flagged = {a for a, b, _ in pairs if a in synthetic and b in validation} | {b for a, b, _ in pairs if b in synthetic and a in validation}
    return sorted(flagged)


def random_tail_cut(text: str, rng: random.Random, probability: float, max_fraction: float) -> str:
    """Augmentation de robustesse à la fin du texte (RM-39, fiche 2026-10-07-lora-fin-aleatoire) : avec la `probabilité` donnée, retire entre 5 % et `max_fraction` des mots de la fin
    (séparés par des espaces), au moins un mot gardé ; sinon rend le texte inchangé. N'ajoute jamais le saut de ligne final : c'est le défaut de fin que le modèle doit apprendre à tolérer."""
    if rng.random() >= probability:
        return text
    words = text.split(" ")
    if len(words) < 2:
        return text
    fraction = rng.uniform(0.05, max_fraction)
    keep = max(1, round((1 - fraction) * len(words)))
    return " ".join(words[:keep]) if keep < len(words) else text
