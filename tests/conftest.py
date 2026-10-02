"""Les caches Hugging Face restent dans le projet (jamais dans le dossier personnel) ; positionné avant tout import de bibliothèque HF."""
import os
from pathlib import Path

os.environ.setdefault("HF_HOME", str(Path(__file__).resolve().parents[1] / "artifacts/hf_cache"))
