"""Adaptateur PARHAF -> colonnes du chargeur générique (id, text, label, author)."""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd


class DoctypeAdapter:
    """Un exemple par document ; l'étiquette est le type de document en minuscules (identifiant de classe du contrat)."""

    def __init__(self, parquet: Path | str, sample: int | None = None, seed: int = 0) -> None:
        self.parquet, self.sample, self.seed = Path(parquet), sample, seed

    def load(self) -> pd.DataFrame:
        df = pd.read_parquet(self.parquet, columns=["id", "author", "documents"])
        rows = [
            {"id": f"{r['id']}#{k}", "text": text, "label": str(dtype).lower(), "author": r["author"]}
            for r in df.to_dict("records")
            for k, (dtype, text) in enumerate(zip(r["documents"]["type"], r["documents"]["text"], strict=True))
        ]
        frame = pd.DataFrame(rows)
        if self.sample is None:
            return frame
        rng = np.random.default_rng(self.seed)
        per_class = max(1, self.sample // frame["label"].nunique())
        parts = [g.sample(n=min(per_class, len(g)), random_state=int(rng.integers(1 << 31))) for _, g in frame.groupby("label")]
        return pd.concat(parts).sort_values("id").reset_index(drop=True)
