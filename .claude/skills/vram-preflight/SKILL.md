---
name: vram-preflight
description: Vérifie qu'un entraînement ou une inférence tient sur la RTX 5090 avant de le lancer. À utiliser avant tout run long, en changeant de modèle, de rang LoRA, de longueur de contexte, de batch ou de quantification, ou après une erreur CUDA out of memory.
---

# Pré-vol VRAM (RTX 5090, 32 Go, Blackwell sm_120)

Un run qui meurt en mémoire après deux heures coûte deux heures. Le pré-vol coûte deux minutes : on **mesure**, on n'estime pas.

## Étapes

1. **Environnement** : consigner `nvidia-smi`, versions de PyTorch, CUDA, transformers, peft, bitsandbytes, et le support Blackwell de chaque bibliothèque utilisée (FlashAttention, GPTQ, FP8). Une bibliothèque sans support sm_120 vérifié est signalée avant le run, pas découverte pendant.
2. **Libérer le GPU** : vérifier qu'aucun autre processus n'occupe la carte (Ollama, un autre entraînement). Ne jamais tuer un processus que tu n'as pas lancé : le signaler à Cyril.
3. **Banc de 10 pas** avec la configuration exacte du run (modèle, quantification, rang, `max_len` au maximum du jeu, batch, gradient checkpointing) : mesurer `torch.cuda.max_memory_allocated`, `max_memory_reserved` et le temps par pas.
4. **Marge** : la mémoire réservée de pointe doit rester sous 30 Go (2 Go de marge pour la fragmentation et l'affichage). Au-delà, réduire dans cet ordre : batch par pas (en gardant le batch effectif par accumulation), longueur de contexte, rang LoRA, puis passer en QLoRA.
5. **Projection** : temps par pas × nombre de pas = durée prévue ; la comparer au budget de la fiche préenregistrée (`experiment-preregistration`).
6. **Consigner** les mesures dans le registre (`run-registry`, champ `preflight`).

## Machine louée

Même procédure avec le profil `hardware/<carte>.yaml` de la machine louée, avant le run complet : une heure louée perdue en erreur mémoire est une dépense, pas seulement du temps. La marge se recalcule sur la mémoire de la carte louée.

**Terminé quand** le banc de 10 pas est passé sans erreur, la pointe est sous 30 Go et la durée projetée tient dans le budget.

## Repères

Les ordres de grandeur du plan (QLoRA 4 bits 24-27B : 20 à 28 Go ; LoRA bf16 7-9B : 24 à 30 Go) sont des hypothèses. La mesure du banc les remplace dès qu'elle existe, et la page wiki du modèle reçoit le chiffre mesuré.
