---
title: Compatibilité de classification des modèles candidats (P0-06 et P0-08)
category: Expériences
summary: Quelle classe de chargement fonctionne pour chaque modèle candidat, mémoire de pointe et temps par pas mesurés sur la RTX 5090 le 02/10/2026, y compris le banc du plus gros professeur en QLoRA 4 bits
tags: [compatibilite, classification, qlora, spike, p0-06, p0-08]
sources: [spike-p0-06-qwen3-5-4b, spike-p0-06-qwen3-5-9b, spike-p0-06-gemma-4-e4b, spike-p0-06-qwen3-8-27b, spike-p0-06-gemma-4-31b]
created: 2026-10-02
updated: 2026-10-03
---

# Compatibilité de classification des modèles candidats (P0-06 et P0-08)

Mesures faites le 02/10/2026 sur la RTX 5090 (WSL2, torch 2.11.0+cu128, transformers 5.18.0, peft 0.21.2, bitsandbytes 0.50.2, voir [[env-blackwell](pages/env-blackwell.md)]) par `scripts/spikes/p0_06_compat.py` (élèves, bf16) et `scripts/spikes/p0_06_08_teacher.py` (professeurs, QLoRA NF4). Chaque modèle est chargé avec ses vrais poids, reçoit une LoRA de rang 16 sur toutes les couches linéaires, le gradient checkpointing, et fait 10 pas sur des tokens tirés au hasard (4 × 1 024 tokens, 18 classes). **Ce banc valide le chargement, le passage avant et arrière et la mémoire. Il ne mesure aucun apprentissage utile** : les pertes tombent vers 0 parce que le lot est fixe.

## Tableau de compatibilité

| Modèle | Précision | Voie | Classe de chargement | Pic alloué (réservé) | Temps par micro-pas de 4 × 1 024 |
|---|---|---|---|---|---|
| Qwen3.5-4B | bf16 | A | `Qwen3_5ForSequenceClassification` | 11,87 Gio (12,42)[^1] | 1,79 s[^1] |
| Qwen3.5-9B | bf16 | A | `Qwen3_5ForSequenceClassification` | 19,87 Gio (20,31)[^2] | 2,47 s[^2] |
| Gemma-4-E4B | bf16 | B | `Gemma4ForConditionalGeneration` + tête maison | 17,74 Gio (18,45)[^3] | 1,40 s[^3] |
| Qwen3.8-27B | NF4 4 bits | A | `Qwen3_5ForSequenceClassification` | 21,94 Gio (23,45)[^4] | 7,50 s[^4] |
| Gemma-4-31B | NF4 4 bits | B | `Gemma4ForConditionalGeneration` + tête maison | 24,44 Gio (25,89)[^5] | 6,96 s[^5] |

**Voie A** : `AutoModelForSequenceClassification` existe pour l'architecture. **Voie B** : repli sur `AutoModelForCausalLM` et une tête linéaire maison lue sur l'état caché du dernier token réel (padding à droite).

## Ce qui a été trouvé

**Les Qwen3.5 et Qwen3.8 ont une classe de classification utilisable**, à une condition : écrire l'identifiant du token de remplissage aussi dans la configuration du texte (`text_config`). Le premier essai du 4B a échoué avec « Cannot handle batch sizes > 1 if no padding token is defined » parce que le correctif n'était pas encore dans le script ; après correction, le 4B, le 9B et le 27B passent.[^6]

**Gemma 4 n'a pas de classe de classification** : transformers répond « Unrecognized configuration class » pour `Gemma4Config`, donc la voie B est nécessaire.[^7] Elle fonctionne pour le E4B et pour le 31B. Le **repli « verbaliseur » n'a pas été nécessaire** : il reste en réserve et n'est consigné ici que comme solution si la tête maison posait un jour problème.

**Le plus gros professeur candidat tient sur la carte (P0-08).** Gemma-4-31B en QLoRA 4 bits, 10 pas d'optimiseur au batch effectif 64 (16 micro-lots de 4 × 1 024 tokens) : 102,2 s par pas, pic alloué 24,86 Gio, **réservé 26,41 Gio, sous les 30 Gio visés**.[^8] Avec un lot de 1 × 4 096 tokens, longueur maximale du protocole : 9,7 s, pic réservé 25,99 Gio.[^9] Pour Qwen3.8-27B : 112,0 s par pas, pic réservé 23,54 Gio ;[^10] 1 × 4 096 tokens : 11,4 s, pic réservé 23,54 Gio.[^11] Les deux restent sous la limite, **le plan B de P0-08 (professeur plus petit ou location) n'est pas déclenché**.

**Chargement et RAM hôte.** Le chargement des 27 et 31 milliards prend 301 s et 388 s ; la RAM de l'hôte atteint 49,8 et 49,6 Gio au pic, sur 68 Gio visibles.[^12]

## Limites, dites explicitement

- **Le padding n'est pas exercé.** Les lots du banc ont tous la même longueur et un masque d'attention tout à 1 ; les tokens tirés ne valent jamais l'identifiant de remplissage. Le chemin « longueurs variables avec remplissage » est à tester dans le code d'entraînement réel (`lora-classifier-recipe`, tests d'abord).
- **Qualité de classification : non mesurée.** Rien ici ne dit qu'un modèle classe mieux qu'un autre.
- **Non testés** : MedGemma (exclu tant que Cyril n'a pas accepté ses conditions, ADR-001) et Mistral Small 3.2 24B (autorisé, hors liste de P0-06).
- **Incident de méthode** : un premier run de Gemma-4-E4B a saturé la VRAM (32 Go) pendant des minutes parce que, en voie B, l'activation du gradient checkpointing était sautée sans bruit ; le script l'active désormais sur le modèle de base, consigne son état, et impose un plafond dur de 30 Gio. La part du calcul réduit des logits (`logits_to_keep=1`), appliqué en même temps, n'est pas isolée.
- Les mesures valent pour ces versions de bibliothèques et ce jour (`vram-preflight`).
- Les Qwen3.5 sont des hybrides à attention linéaire à porte ; l'étude [[sliding-window-beats-linear-attention](pages/sliding-window-beats-linear-attention.md)] écarte explicitement les hybrides, ses conclusions ne s'y appliquent donc pas telles quelles.
- Le temps, les machines et la mémoire mesurés ici alimentent l'item de rapport « calcul requis » de [[tripod-llm-reporting-guideline](pages/tripod-llm-reporting-guideline.md)].

[^1]: raw/spike-p0-06-qwen3-5-4b.json L6-L12,L26-L29 [synthesis] — classe de chargement, pad, mémoire après chargement, temps par pas, pics alloué et réservé
[^2]: raw/spike-p0-06-qwen3-5-9b.json L6-L12,L26-L29 [synthesis] — même banc pour le 9B
[^3]: raw/spike-p0-06-gemma-4-e4b.json L6-L13,L27-L30 [synthesis] — voie B, classe de chargement, checkpointing actif, temps par pas, pics de mémoire
[^4]: raw/spike-p0-06-qwen3-8-27b.json L3-L14,L33-L36 [synthesis] — chargement NF4, voie A, mémoire, étape de compatibilité
[^5]: raw/spike-p0-06-gemma-4-31b.json L3-L14,L33-L36 [synthesis] — chargement NF4, voie B, mémoire, étape de compatibilité
[^6]: raw/spike-p0-06-qwen3-5-4b.json L9 — "pad_set_in_text_config": true
[^7]: raw/spike-p0-06-gemma-4-e4b.json L7 — "Unrecognized configuration class"
[^8]: raw/spike-p0-06-gemma-4-31b.json L57-L60 [synthesis] — 102,23 s par pas d'optimiseur, 24,86 Gio alloués, 26,41 Gio réservés
[^9]: raw/spike-p0-06-gemma-4-31b.json L73-L76 [synthesis] — lot de 1 × 4 096 tokens : 9,69 s, 24,46 Gio alloués, 25,99 Gio réservés
[^10]: raw/spike-p0-06-qwen3-8-27b.json L57-L60 [synthesis] — 111,95 s par pas d'optimiseur, 22,45 Gio alloués, 23,54 Gio réservés
[^11]: raw/spike-p0-06-qwen3-8-27b.json L73-L76 [synthesis] — lot de 1 × 4 096 tokens : 11,38 s, 21,97 Gio alloués, 23,54 Gio réservés
[^12]: raw/spike-p0-06-qwen3-8-27b.json L9,L14 [synthesis] — 301,1 s de chargement et 49,8 Gio de RAM hôte au pic pour le 27B ; le 31B donne 387,5 s et 49,6 Gio dans raw/spike-p0-06-gemma-4-31b.json L9,L14
