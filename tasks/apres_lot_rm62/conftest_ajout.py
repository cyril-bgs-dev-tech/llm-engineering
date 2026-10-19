"""Ajout à tests/conftest.py après le lot RM-62 (N42) ; non collecté (hors de tests/)."""
from pathlib import Path

import pytest


@pytest.fixture
def tmp_path(tmp_path: Path) -> Path:
    """N42 : tous les tests travaillent dans un dossier à espaces, comme le dépôt (`/mnt/d/Projets persos/...`) ; un chemin non cité casse ici, pas dans un lot."""
    spaced = tmp_path / "dossier avec espaces"
    spaced.mkdir()
    return spaced
