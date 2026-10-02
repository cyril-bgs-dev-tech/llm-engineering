#!/usr/bin/env python3
"""Génère `task_specs/*.yaml` (P0-36 à P0-39). Les noms de chapitres viennent du ClaML de l'ATIH, jamais d'une saisie à la main."""
import re
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from llmft import cim10, taskspec

OUT = ROOT / "task_specs"
INPUT_PATIENT = {"unit": "patient", "max_tokens": 4096, "truncation": "head_tail"}
METRICS = {"primary": "macro_f1", "secondary": ["accuracy", "log_loss", "ece"]}
EXCL_DOCTYPE = "Le type est celui de l'enregistrement d'origine du document, pas celui que le contenu évoque."
EXCL_SPECIALTY = "C'est la spécialité du service rédacteur, pas la spécialité qu'évoque le diagnostic ; un patient peut être pris en charge hors de la spécialité habituelle de sa maladie."
EXCL_CHAPTER = "Les diagnostics secondaires ne comptent pas : seul le diagnostic principal du scénario suggéré aux rédacteurs définit la classe."

DOCTYPES = {
    "anapath": ("ANAPATH", "Compte rendu d'anatomopathologie", "Compte rendu décrivant l'examen macroscopique et microscopique d'un prélèvement et sa conclusion anatomopathologique."),
    "crh": ("CRH", "Compte rendu d'hospitalisation", "Compte rendu de séjour hospitalier : motif d'admission, histoire de la maladie, évolution, conclusion et conduite à tenir à la sortie."),
    "crc": ("CRC", "Compte rendu de consultation", "Compte rendu d'une consultation externe : motif, examen clinique, avis et projet de suivi."),
    "cro": ("CRO", "Compte rendu opératoire", "Compte rendu d'une intervention chirurgicale : indication, technique, constatations peropératoires, suites immédiates."),
    "urgences": ("URGENCES", "Compte rendu de passage aux urgences", "Compte rendu d'un passage au service d'accueil des urgences : motif de recours, examens, orientation."),
    "accouchement": ("ACCOUCHEMENT", "Compte rendu d'accouchement", "Compte rendu de la naissance : déroulement du travail, mode d'accouchement, état du nouveau-né."),
    "maternite": ("MATERNITE", "Compte rendu de séjour en maternité", "Compte rendu du séjour de la mère et du nouveau-né en maternité après la naissance."),
}
SPECIALTIES = {  # valeur exacte de PARHAF : (libellé français, domaine)
    "ANATOMOPATHOLOGIE": ("Anatomopathologie", "examen des prélèvements et diagnostic lésionnel"),
    "CANCERO ADULTE": ("Cancérologie adulte", "prise en charge des tumeurs solides et traitements oncologiques de l'adulte"),
    "CARDIOLOGIE": ("Cardiologie", "maladies du cœur et de la circulation"),
    "CHIR ORTHO ET TRAUMATO": ("Chirurgie orthopédique et traumatologique", "chirurgie de l'appareil locomoteur et des traumatismes"),
    "CHIR.CARDIO-VASC.": ("Chirurgie cardio-vasculaire", "chirurgie du cœur et des vaisseaux"),
    "CHIRURGIE VISCERALE": ("Chirurgie viscérale", "chirurgie digestive et abdominale"),
    "GYNECOLOGIE": ("Gynécologie", "maladies de l'appareil génital féminin et du sein"),
    "HEMATOLOGIE CLINIQUE": ("Hématologie clinique", "maladies du sang et des organes hématopoïétiques"),
    "HEPATO-GASTRO-ENTERO": ("Hépato-gastro-entérologie", "maladies du tube digestif, du foie et du pancréas"),
    "MALADIES INFECTIEUSES": ("Maladies infectieuses", "diagnostic et traitement des infections"),
    "MEDECINE GERIATRIQUE": ("Médecine gériatrique", "prise en charge du sujet âgé polypathologique"),
    "MEDECINE INTER-SPECIALITES": ("Médecine inter-spécialités", "prise en charge médicale à l'interface de plusieurs spécialités"),
    "MEDECINE INTERNE": ("Médecine interne", "maladies systémiques et auto-immunes, démarche diagnostique générale"),
    "MEDECINE PEDIATRIQUE": ("Médecine pédiatrique", "maladies de l'enfant"),
    "NEPHROLOGIE": ("Néphrologie", "maladies du rein et dialyse"),
    "NEUROLOGIE": ("Neurologie", "maladies du système nerveux"),
    "OBSTETRIQUE": ("Obstétrique", "grossesse, accouchement et suites de couches"),
    "PNEUMOLOGIE": ("Pneumologie", "maladies de l'appareil respiratoire"),
    "REANIMATION": ("Réanimation", "prise en charge des défaillances d'organes aiguës"),
    "UROLOGIE": ("Urologie", "maladies de l'appareil urinaire et de l'appareil génital masculin"),
}
RARE_CHAPTERS = {"VII", "VIII", "XVI", "XVII"}  # sous le seuil de 20 patients (PROTOCOLE.md section 2)
CHAPTER_RANGE = re.compile(r"^[A-Z]\d{2}-[A-Z]\d{2}$")


def slug(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", text.lower()).strip("_")


def dump(name: str, spec: dict) -> None:
    taskspec.TaskSpec.model_validate(spec)  # on n'écrit jamais un contrat invalide
    header = "# Contrat de tâche généré par scripts/gen_task_contracts.py ; ne pas éditer à la main.\n"
    (OUT / f"{name}.yaml").write_text(header + yaml.safe_dump(spec, allow_unicode=True, sort_keys=False, width=110), encoding="utf-8")
    print("écrit", name)


BOUNDARY_RULES = {  # règles de départage aux frontières : la classe suit le code, pas le sens clinique
    "II": "Une séance de chimiothérapie codée Z51.1 relève du chapitre XXI, pas de II, même si la maladie sous-jacente est une tumeur.",
    "XV": "Seuls les codes O relèvent du chapitre XV ; la surveillance de grossesse et les suites de couches codées Z30 à Z39 relèvent de XXI.",
    "XVIII": "Un symptôme codé R relève de XVIII même s'il évoque une maladie d'organe : le chapitre suit le code du scénario, pas le sens clinique.",
    "XIX": "Les complications de soins codées T80 à T88 et les empoisonnements relèvent de XIX, pas du chapitre de l'organe touché.",
    "XXI": "Les codes Z (motifs de recours, séances, surveillance) relèvent de XXI, pas du chapitre de la maladie qui motive le recours.",
    "XXII": "Les codes U relèvent de XXII, dont le COVID-19 (U07.1), et non de I ni de X malgré leur sens clinique.",
}


def chapter_contract() -> dict:
    h = cim10.load_claml(ROOT / "data/raw/cim10/cim10fr2019.xml")
    import xml.etree.ElementTree as ET
    root = ET.parse(ROOT / "data/raw/cim10/cim10fr2019.xml").getroot()
    ranges = {}
    for cls in root.iter("Class"):
        if cls.get("kind") == "chapter":
            subs = [s.get("code") for s in cls.findall("SubClass") if s.get("code")]
            ranges[cls.get("code")] = f"{subs[0].split('-')[0]}-{subs[-1].split('-')[-1]}"
    classes = []
    for code, label in h.chapters.items():
        if code in RARE_CHAPTERS or code == "XX":
            continue  # XX absent du corpus, les autres rares fusionnés dans AUTRE
        classes.append({
            "id": f"ch_{code.lower()}", "name": f"Chapitre {code} : {label}",
            "definition": f"Patient dont le diagnostic principal du scénario a un code CIM-10 de la plage {ranges[code]} (chapitre {code}, {label}).",
            "exclusions": [BOUNDARY_RULES[code]] if code in BOUNDARY_RULES else [],
        })
    counts = {"VII": 2, "VIII": 2, "XVI": 4, "XVII": 10}  # effectifs mesurés au jeu de travail (results/measures/splits_summary.json)
    rare = ", ".join(f"{c} ({ranges[c]}, {counts[c]} patients)" for c in sorted(RARE_CHAPTERS, key=lambda c: list(h.chapters).index(c)))
    classes.append({
        "id": "autre", "name": "Autre chapitre",
        "definition": (
            f"Patient dont le diagnostic principal relève d'un chapitre CIM-10 qui compte moins de 20 patients dans le jeu de travail : {rare}. "
            f"Le chapitre XX ({ranges['XX']}, causes externes) n'apparaît pour aucun patient du corpus ; un tel code serait rangé ici."
        ),
        "exclusions": ["Un chapitre de 20 patients ou plus garde sa classe, même rare (XXII compte 31 patients)."],
    })
    return {
        "task_id": "parhaf_cim10_chapter", "title": "Chapitre CIM-10 du diagnostic principal (PARHAF)", "type": "multiclass",
        "input": INPUT_PATIENT, "classes": classes, "output": {"format": "{class_id}"},
        "metrics": {"primary": "macro_f1", "secondary": ["accuracy", "log_loss", "ece"]},
        "abstention": {"enabled": False},
        "source": "Noms et plages de chapitres : ATIH, CIM-10 FR à usage PMSI, ClaML 2019, reproduits tels quels (mention d'origine, voir data/cards/cim10.md).",
        "notes": [
            "L'étiquette est le chapitre du code du diagnostic principal du scénario suggéré aux rédacteurs de PARHAF, pas un codage médical ni une lecture du compte rendu. En cas de désaccord entre le texte et le scénario, le scénario fait foi.",
            "Chaque patient du scénario porte exactement un diagnostic principal ; le chapitre se lit sur les trois premiers caractères du code (la lettre seule ne suffit pas : D et H sont à cheval sur deux chapitres). Les codes à suffixe + ou étendus à 5 caractères sont ramenés à leurs trois premiers.",
            "La classe suit le code : pour les frontières entre chapitres, voir les exclusions de chaque classe.",
            "La macro-F1 principale exclut la classe `autre` ; l'exactitude, la perte logarithmique et l'ECE la comptent comme une classe ordinaire.",
            "Entrée tronquée au-delà de 4096 tokens (2048 premiers et 2048 derniers, PROTOCOLE.md section 1) : concerne 0,2 % des patients ; pas d'abstention au premier cycle.",
            "Les noms de chapitres reprennent les graphies de l'ATIH sans correction (par exemple « souscutané », « ostéoarticulaire ») : la licence interdit de modifier le texte.",
        ],
    }


def main() -> int:
    OUT.mkdir(exist_ok=True)
    dump("toy_sentiment", {
        "task_id": "toy_sentiment", "title": "Tâche jouet synthétique (deux classes)", "type": "multiclass",
        "input": {"unit": "document", "max_tokens": 128, "truncation": "head_tail"},
        "classes": [
            {"id": "positif", "name": "Positif", "definition": "Le texte exprime une satisfaction explicite.", "exclusions": ["Texte neutre ou mitigé : non généré"]},
            {"id": "negatif", "name": "Négatif", "definition": "Le texte exprime une insatisfaction explicite.", "exclusions": ["Texte neutre ou mitigé : non généré"]},
        ],
        "output": {"format": "{class_id}"}, "metrics": METRICS, "abstention": {"enabled": False},
        "source": "Données générées par src/llmft/toy.py, déterministes, aucune donnée réelle.",
    })
    dump("parhaf_doctype", {
        "task_id": "parhaf_doctype", "title": "Type de document (PARHAF, tâche de contrôle)", "type": "multiclass",
        "input": {"unit": "document", "max_tokens": 4096, "truncation": "head_tail"},
        "classes": [{"id": k, "name": f"{label} ({value})", "definition": d, "exclusions": [EXCL_DOCTYPE]} for k, (value, label, d) in DOCTYPES.items()],
        "output": {"format": "{class_id}"}, "metrics": METRICS, "abstention": {"enabled": False},
        "source": "Colonne `documents.type` de PARHAF ; signification des codes : fiche du jeu, section Controlled Vocabularies.",
    })
    dump("parhaf_specialty", {
        "task_id": "parhaf_specialty", "title": "Spécialité du service rédacteur (PARHAF, tâche de contrôle)", "type": "multiclass",
        "input": INPUT_PATIENT,
        "classes": [{"id": slug(v), "name": f"{label} ({v})", "definition": f"Patient dont le compte rendu a été rédigé dans la spécialité {label.lower()} : {dom}.", "exclusions": [EXCL_SPECIALTY]} for v, (label, dom) in SPECIALTIES.items()],
        "output": {"format": "{class_id}"}, "metrics": METRICS, "abstention": {"enabled": False},
        "source": "Colonne `specialty` de PARHAF ; liste fermée de la fiche du jeu, section Controlled Vocabularies.",
    })
    dump("parhaf_cim10_chapter", chapter_contract())
    return 0


if __name__ == "__main__":
    sys.exit(main())
