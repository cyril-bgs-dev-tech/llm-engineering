---
title: Environnement Blackwell (RTX 5090, sm_120)
category: Expériences
summary: Ce qui fonctionne sur la RTX 5090 le 01/10/2026 (PyTorch cu128, bf16, attention fusionnée, LoRA sur modèle NF4), mesures des spikes P0-04, P0-05 et RM-06 (débit disque, RAM visible)
tags: [environnement, blackwell, sm120, spike]
sources: [spike-p0-04-torch-blackwell, spike-p0-05-lora-nf4, rm06-machine-wsl]
created: 2026-10-01
updated: 2026-10-02
---

# Environnement Blackwell (RTX 5090, sm_120)

Mesures faites sur la machine de Cyril (WSL2, Python 3.12, pilote 610.47) par les spikes `scripts/spikes/p0_04_torch_blackwell.py` et `scripts/spikes/p0_05_lora_nf4.py`. **Elles valent pour ces versions et ce jour** ; une autre version de bibliothèque se revérifie avec `vram-preflight`.

## Versions installées (résultat)

| Bibliothèque | Version | sm_120 |
|---|---|---|
| torch | 2.11.0+cu128 (runtime CUDA 12.8) | oui : `sm_120` figure dans `get_arch_list()`[^1] |
| transformers | 5.18.0 | oui (chargement NF4 et 10 pas réussis)[^2] |
| peft | 0.21.2 | oui (LoRA `all-linear`, 10 092 544 paramètres entraînables)[^2] |
| bitsandbytes | 0.50.2 | oui (quantification NF4 à double quantification)[^2] |
| trl, accelerate, datasets | 1.14.1, 1.15.0, 5.0.1 | installés ; pas encore exercés (la distillation viendra avec P0-06 et RM-19) |

## P0-04 : PyTorch voit la carte

La carte est détectée comme `NVIDIA GeForce RTX 5090`, capacité `sm_120`, 31,84 Gio de mémoire.[^3] Un produit matriciel bf16 4096 x 4096 est fini et `scaled_dot_product_attention` causal s'exécute ; son écart maximal à un calcul naïf en float32 vaut 0,008, cohérent avec bf16.[^4] La roue cu128 suffit : **cu130 n'a pas été essayée**, faute de besoin.

## P0-05 : LoRA sur modèle 4 bits

Qwen3-0.6B chargé en NF4 occupe 0,502 Gio ; 10 pas LoRA (lot de 4 textes de 256 tokens, texte synthétique répété) prennent 3,5 secondes, pic de mémoire 2,212 Gio, toutes pertes finies.[^5] La perte décroît de 0,659 à 0,035 : **cela ne prouve aucun apprentissage utile**, le texte étant répété ; seule la pile est validée.

## RM-06 : la machine telle que WSL la voit

| Mesure | Valeur |
|---|---|
| RAM visible dans WSL | 68,7 Gio ; **l'hypothèse « environ 96 Go » de `CLAUDE.md` n'est pas confirmée** (l'hôte Windows peut en avoir davantage ; le plafond WSL n'a pas été lu)[^6] |
| Threads CPU | 32[^6] |
| Disque libre | `/mnt/d` 186 Gio ; ext4 de WSL 33 Gio[^6] |
| Écriture puis lecture de 1 Gio | ext4 : 6 031 puis 8 160 Mo/s ; `/mnt/d` : 209 puis 272 Mo/s, soit environ 30 fois plus lent[^6] |
| Pilote et GPU | 610.47 ; 32 607 Mio au total ; 3 088 Mio occupés avant tout spike[^6] |

Conséquences : les poids de modèle de 20 Gio et plus (professeurs de 27 à 31 milliards de paramètres) ne tiennent pas sur le disque ext4 (33 Gio libres) et se chargent depuis `/mnt/d` à environ 270 Mo/s, soit plus de trois minutes par chargement ; les petits élèves (4 à 9 milliards, 8 à 18 Gio) et les points de sauvegarde actifs vont sur ext4. La lecture sur ext4 est une borne haute, le cache de page ayant pu en servir une partie malgré l'invalidation demandée ; le rapport de l'ordre de 30 reste net.

## Limites

- Le dimensionnement de mémoire des modèles de 4 à 31 milliards de paramètres est mesuré le 02/10/2026 dans [[compatibilite-modeles-p0-06](pages/compatibilite-modeles-p0-06.md)] ; le budget de calcul par vague reste à écrire (P0-45).
- 3,1 Gio de mémoire GPU étaient déjà occupés avant les spikes par un processus que je n'ai pas lancé : non touché, à signaler à Cyril.
- FlashAttention, vLLM, FP8 et NVFP4 ne sont pas testés ici.

[^1]: raw/spike-p0-04-torch-blackwell.json L2-L12 [synthesis] — version de torch, runtime CUDA et liste des architectures compilées, `sm_120` en dernière position
[^2]: raw/spike-p0-05-lora-nf4.json L3-L5,L19-L22 [synthesis] — chargement 4 bits réussi, nombre de paramètres entraînables, pertes finies, durée et pic de mémoire
[^3]: raw/spike-p0-04-torch-blackwell.json L13-L16 — "device": "NVIDIA GeForce RTX 5090", "capability": "sm_120"
[^4]: raw/spike-p0-04-torch-blackwell.json L17-L19 — "matmul_bf16_ok": true, "sdpa_ok": true, "sdpa_max_abs_diff_vs_fp32": 0.00804
[^5]: raw/spike-p0-05-lora-nf4.json L3-L5,L19-L22 [synthesis] — 0,502 Gio après chargement, 10 pas en 3,5 s, pic 2,212 Gio
[^6]: raw/rm06-machine-wsl.json L2-L16 [synthesis] — débits d'écriture et de lecture, threads, RAM visible, disque libre, pilote et mémoire GPU
