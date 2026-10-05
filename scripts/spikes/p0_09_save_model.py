#!/usr/bin/env python3
"""P0-09 : écrit le classifieur Qwen3.5-4B à tête neuve (graine 0, 18 sorties) dans un dossier local, pour que Transformers et
vLLM chargent EXACTEMENT les mêmes poids (une tête aléatoire différente rendrait les sorties incomparables). Usage : SORTIE_DIR"""
import sys

import torch
from transformers import AutoModelForSequenceClassification, AutoTokenizer

MODEL, OUT = "Qwen/Qwen3.5-4B", sys.argv[1]
tok = AutoTokenizer.from_pretrained(MODEL)
torch.manual_seed(0)
model = AutoModelForSequenceClassification.from_pretrained(MODEL, num_labels=18, dtype=torch.bfloat16)
model.config.pad_token_id = tok.pad_token_id
if hasattr(model.config, "text_config"):
    model.config.text_config.pad_token_id = tok.pad_token_id
model.save_pretrained(OUT)
tok.save_pretrained(OUT)
print("saved", OUT)
