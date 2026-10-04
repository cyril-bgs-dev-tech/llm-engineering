"""Briques de génération de comptes rendus synthétiques ciblés (fiche 2026-10-04-synthetique-cible-chapitres-rares) : invite, enregistrement avec lignée, filtre de qualité.
Aucun modèle n'est chargé ici : la génération elle-même est dans `scripts/gen_synthetic.py` et ne se lance qu'après le Qwen3.5-4B à 10 époques."""
from llmft import leakage

MIN_CHARS = 400
MAX_SIMILARITY = 0.6


def build_prompt(source_text: str, style_hint: str = "") -> str:
    """Invite : réécrire un cas fictif de la même nature clinique, avec d'autres détails, sans recopier l'original."""
    hint = f" Style visé : {style_hint}." if style_hint else ""
    return (
        "Tu rédiges des comptes rendus cliniques fictifs en français, pour un jeu de données d'entraînement. Voici un compte rendu fictif existant.\n\n"
        f"{source_text}\n\n"
        "Écris un NOUVEAU compte rendu fictif du même type de cas (même diagnostic principal, même type de document), avec un autre patient, d'autres valeurs, d'autres dates et une autre "
        "formulation. Ne recopie ni phrases ni noms de l'original ; n'écris aucun nom réel ; reste vraisemblable et complet." + hint + "\n\nNouveau compte rendu :\n"
    )


def make_record(source_id: str, label: str, text: str, index: int) -> dict[str, str]:
    return {"id": f"synth-{source_id}-{index}", "source_id": source_id, "label": label, "text": text}


def acceptable(candidate: str, source_text: str) -> bool:
    """Rejette un texte trop court ou quasi identique à sa source (similarité de Jaccard sur les 5-grammes de caractères)."""
    if len(candidate.strip()) < MIN_CHARS:
        return False
    pairs = leakage.near_duplicate_pairs({"c": candidate, "s": source_text}, MAX_SIMILARITY)
    return not pairs
