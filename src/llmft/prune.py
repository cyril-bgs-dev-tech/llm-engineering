"""Élagage de couches d'un encodeur de type BERT (RM-45) : garde une couche sur `every` ; la moyenne des représentations et la tête de classification restent celles du modèle."""
from typing import Any


def layers_to_keep(n_layers: int, every: int) -> list[int]:
    """Indices des couches conservées : 0, every, 2 * every... (au moins une couche)."""
    if every < 1:
        raise ValueError("every >= 1")
    keep = list(range(0, n_layers, every))
    return keep or [0]


def prune_encoder(model: Any, every: int) -> list[int]:
    """Remplace la liste des couches de l'encodeur du modèle de classification (`model.roberta.encoder.layer` ou `model.bert.encoder.layer`) ; renvoie les indices gardés."""
    base = getattr(model, "roberta", None) or getattr(model, "bert", None)
    if base is None:
        raise ValueError("encodeur de type BERT ou RoBERTa attendu")
    layers = base.encoder.layer
    keep = layers_to_keep(len(layers), every)
    base.encoder.layer = type(layers)([layers[i] for i in keep])
    model.config.num_hidden_layers = len(keep)
    return keep
