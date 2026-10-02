"""Découpages par patient (PROTOCOLE.md sections 2 et 3) : test scellé, plis stratifiés, plis de contrôle groupés par auteur."""
from __future__ import annotations

import hashlib
import json
from collections import Counter
from dataclasses import dataclass, field

import numpy as np
import pandas as pd
from sklearn.model_selection import StratifiedGroupKFold, StratifiedKFold, train_test_split

TEST_FRACTION = 0.15
TEST_GROUP_SPLITS = 20  # 3 plis de 20 = 15 % quand on découpe par groupes
TEST_GROUP_FOLDS = 3
N_FOLDS = 5
RARE_MIN = 20
TOLERANCE = 0.30  # écart relatif maximal de la part d'une classe de plus de 50 patients
LARGE_CLASS = 50
MIN_PER_DEV_FOLD = 2
MIN_IN_TEST = 3


@dataclass
class Splits:
    seed: int
    test: list[str]
    folds: list[list[str]]
    control_folds: list[list[str]] = field(default_factory=list)

    def to_json(self) -> str:
        payload = {
            "seed": self.seed,
            "test": sorted(self.test),
            "folds": [sorted(f) for f in self.folds],
            "control_folds_by_author": [sorted(f) for f in self.control_folds],
        }
        return json.dumps(payload, ensure_ascii=False, indent=1, sort_keys=True) + "\n"

    def sha256(self) -> str:
        return hashlib.sha256(self.to_json().encode("utf-8")).hexdigest()


def apply_rare_class_policy(labels: pd.Series, min_count: int = RARE_MIN, other: str = "AUTRE") -> pd.Series:
    """Fusionne dans `AUTRE` toute classe de moins de `min_count` exemples (PROTOCOLE.md, section 2)."""
    counts = labels.value_counts()
    rare = set(counts[counts < min_count].index)
    return labels.map(lambda x: other if x in rare else x)


def make_splits(df: pd.DataFrame, seed: int) -> Splits:
    """`df` a les colonnes `id`, `author`, `label` et, facultativement, `cluster` (groupes de quasi-doublons).

    Avec `cluster`, test et plis de développement ne séparent jamais un groupe (PROTOCOLE.md, section 4).
    """
    frame = df.set_index("id")
    if "cluster" in frame.columns:
        outer = StratifiedGroupKFold(n_splits=TEST_GROUP_SPLITS, shuffle=True, random_state=seed)
        test_parts = [val for _, val in outer.split(frame.index, frame["label"], groups=frame["cluster"])][:TEST_GROUP_FOLDS]
        test_idx = np.concatenate(test_parts)
        dev = frame.drop(index=frame.index[test_idx])
        test_ids = list(frame.index[test_idx])
        inner = StratifiedGroupKFold(n_splits=N_FOLDS, shuffle=True, random_state=seed)
        folds = [list(dev.index[val]) for _, val in inner.split(dev.index, dev["label"], groups=dev["cluster"])]
    else:
        dev_ids, test_arr = train_test_split(frame.index.to_numpy(), test_size=TEST_FRACTION, stratify=frame["label"].to_numpy(), random_state=seed)
        dev = frame.loc[dev_ids]
        test_ids = list(test_arr)
        skf = StratifiedKFold(n_splits=N_FOLDS, shuffle=True, random_state=seed)
        folds = [list(dev.index[val]) for _, val in skf.split(dev.index, dev["label"])]
    sgkf = StratifiedGroupKFold(n_splits=N_FOLDS, shuffle=True, random_state=seed)
    control = [list(dev.index[val]) for _, val in sgkf.split(dev.index, dev["label"], groups=dev["author"])]
    return Splits(seed=seed, test=test_ids, folds=folds, control_folds=control)


def check_no_overlap(s: Splits) -> list[str]:
    """Identifiants présents dans plus d'une partition (test et plis de développement)."""
    counts = Counter(i for part in [s.test, *s.folds] for i in part)
    return sorted(i for i, c in counts.items() if c > 1)


def plant_leak(s: Splits) -> tuple[Splits, str]:
    """Copie de `s` où un patient du test figure aussi dans le pli 0 : le cas piégé que `check_no_overlap` doit voir."""
    leaked = Splits(seed=s.seed, test=list(s.test), folds=[list(f) for f in s.folds], control_folds=[list(f) for f in s.control_folds])
    pid = leaked.test[0]
    leaked.folds[0].append(pid)
    return leaked, pid


def check_tolerance(df: pd.DataFrame, s: Splits) -> list[str]:
    """Écarts à la règle de déséquilibre de PROTOCOLE.md ; liste vide = conforme."""
    label = df.set_index("id")["label"]
    total = label.value_counts()
    problems: list[str] = []
    parts = {"test": s.test, **{f"pli {k}": f for k, f in enumerate(s.folds)}}
    for name, ids in parts.items():
        in_part = label[ids].value_counts()
        for cls, n_total in total.items():
            n = int(in_part.get(cls, 0))
            if n_total >= LARGE_CLASS:
                expected = n_total / len(label) * len(ids)
                if abs(n - expected) / expected > TOLERANCE:
                    problems.append(f"{name} : classe {cls} a {n} patients pour {expected:.1f} attendus")
            else:
                minimum = MIN_IN_TEST if name == "test" else MIN_PER_DEV_FOLD
                if n < minimum:
                    problems.append(f"{name} : classe {cls} a {n} patients, minimum {minimum}")
    return problems
