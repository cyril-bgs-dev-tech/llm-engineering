"""Hiérarchie CIM-10 (chapitre, bloc, catégorie à 3 caractères) lue dans le ClaML de l'ATIH (P0-27).

Le fichier source (`data/raw/cim10/cim10fr2019.xml`) est soumis aux conditions de l'ATIH : mention de l'origine,
ni modification ni usage commercial. Il n'est donc jamais versionné ni redistribué ; ce module le lit en place.
"""
from __future__ import annotations

import re
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from pathlib import Path

_XML_LANG = "{http://www.w3.org/XML/1998/namespace}lang"


@dataclass(frozen=True)
class Hierarchy:
    chapter: str  # chiffre romain, ex. "II"
    block: str  # bloc le plus fin, ex. "C30-C39"
    block_path: tuple[str, ...]  # du bloc le plus large au plus fin
    category3: str  # ex. "C34"
    label: str


@dataclass
class Claml:
    kinds: dict[str, str] = field(default_factory=dict)
    parents: dict[str, str | None] = field(default_factory=dict)
    labels: dict[str, str] = field(default_factory=dict)

    @property
    def chapters(self) -> dict[str, str]:
        return {c: self.labels.get(c, "") for c, k in self.kinds.items() if k == "chapter"}

    def lookup(self, raw_code: str) -> Hierarchy | None:
        """Renvoie la hiérarchie d'un code (3 à 6 caractères, avec ou sans point, suffixe `+n` toléré), sinon None."""
        cat = normalize3(raw_code)
        if cat is None:
            return None
        key = f"{cat[:3]}"
        node = key if self.kinds.get(key) == "category" else None
        if node is None:
            return None
        blocks: list[str] = []
        cur = self.parents.get(node)
        # Le ClaML 2019 contient des erreurs de hiérarchie connues de l'ATIH (ex. C85 rattaché à la catégorie C84) :
        # on traverse les catégories intermédiaires et `anomalies()` les signale.
        while cur is not None and self.kinds.get(cur) in ("block", "category"):
            if self.kinds.get(cur) == "block":
                blocks.append(cur)
            cur = self.parents.get(cur)
        if cur is None or self.kinds.get(cur) != "chapter" or not blocks:
            return None
        return Hierarchy(chapter=cur, block=blocks[0], block_path=tuple(reversed(blocks)), category3=key, label=self.labels.get(key, ""))

    def check_consistency(self) -> list[str]:
        """Chaque catégorie doit remonter à un bloc puis à un chapitre ; renvoie les écarts trouvés."""
        problems: list[str] = []
        for code, kind in self.kinds.items():
            if kind == "category":
                continue
            if kind == "block":
                cur: str | None = code
                seen: set[str] = set()
                while cur is not None and self.kinds.get(cur) == "block" and cur not in seen:
                    seen.add(cur)
                    cur = self.parents.get(cur)
                if cur is None or self.kinds.get(cur) != "chapter":
                    problems.append(f"bloc {code} sans chapitre")
        for code, kind in self.kinds.items():
            if kind == "category" and len(code.replace(".", "")) == 3 and self.lookup(code) is None:
                problems.append(f"catégorie {code} sans bloc ou chapitre résolu")
        return problems


    def anomalies(self) -> list[str]:
        """Catégories à 3 caractères dont le parent direct n'est pas un bloc (erreur de la source, résolue par `lookup`)."""
        return sorted(
            f"{code} a pour parent la catégorie {parent}"
            for code, kind in self.kinds.items()
            if kind == "category" and len(code) == 3 and (parent := self.parents.get(code)) and self.kinds.get(parent) == "category"
        )


def normalize3(raw_code: str) -> str | None:
    """`c341`, `C34.1`, `C341+8` donnent `C34` ; une chaîne qui n'est pas un code CIM-10 donne None."""
    m = re.match(r"^([A-Za-z])(\d{2})", raw_code.strip().replace(" ", ""))
    return (m.group(1).upper() + m.group(2)) if m else None


def load_claml(path: Path | str) -> Claml:
    root = ET.parse(path).getroot()
    out = Claml()
    for cls in root.iter("Class"):
        code = cls.get("code")
        kind = cls.get("kind")
        if not code or not kind:
            continue
        out.kinds[code] = kind
        sup = cls.find("SuperClass")
        out.parents[code] = sup.get("code") if sup is not None else None
        for rub in cls.findall("Rubric"):
            if rub.get("kind") == "preferred":
                lab = rub.find("Label")
                if lab is not None and "".join(lab.itertext()).strip():
                    out.labels.setdefault(code, "".join(lab.itertext()).strip())
                    break
    # Les blocs et chapitres peuvent être déclarés après leurs enfants : on ne résout les liens qu'ensuite.
    for cls in root.iter("Class"):
        if cls.get("kind") == "chapter" and cls.get("code"):
            out.parents.setdefault(cls.get("code", ""), None)
    return out
