"""Arguments de chargement pour la quantification 4 bits NF4 des gros élèves ou professeurs (QLoRA, vram-preflight)."""
from typing import Any, cast


def load_kwargs(quant: str) -> dict[str, Any]:
    if quant == "none":
        return {}
    if quant != "nf4":
        raise ValueError(f"quantification inconnue : {quant}")
    import torch
    from transformers import BitsAndBytesConfig

    cfg = cast(Any, BitsAndBytesConfig)(load_in_4bit=True, bnb_4bit_quant_type="nf4", bnb_4bit_compute_dtype=torch.bfloat16, bnb_4bit_use_double_quant=True)
    return {"quantization_config": cfg, "device_map": {"": 0}}
