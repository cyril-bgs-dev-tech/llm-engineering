# ADR-001 : modèles à accès conditionné (micro-tâche P0-01)

## Status
Acceptée **provisoirement** le 02/10/2026 (défaut prudent, en autonomie) ; la décision sur MedGemma reste à Cyril.

## Date
2026-10-02

## Context
Le plan supposait que Gemma 4 et MedGemma étaient conditionnés par une licence à accepter sur Hugging Face. L'API du 02/10/2026 dit autre chose (`model_info`, champ `gated`) :

| Modèle | `gated` | Licence (étiquette) | Poids (safetensors) | Architecture déclarée |
|---|---|---|---|---|
| Qwen3.5-4B, 9B, 27B | non | Apache-2.0 | 8,7 ; 18,0 ; 51,7 Gio | `Qwen3_5ForConditionalGeneration` |
| Qwen3.8-27B | non | Apache-2.0 | 51,7 Gio | `Qwen3_5ForConditionalGeneration` |
| Gemma 4 E4B, 31B | non | Apache-2.0 | 14,9 ; 58,3 Gio | `Gemma4ForConditionalGeneration` |
| Mistral Small 3.2 24B | non | Apache-2.0 | 89,4 Gio | `Mistral3ForConditionalGeneration` |
| MedGemma 4B, 1.5 4B, 27B texte | **auto** (accord à accepter) | `other` (conditions Health AI Developer Foundations) | 8,0 ; 8,0 ; 50,3 Gio | `Gemma3ForConditionalGeneration`, `Gemma3ForCausalLM` |

## Decision
- **Modèles autorisés au premier cycle** : tous ceux de la liste sans accès conditionné (Qwen3.5, Qwen3.8, Gemma 4, Mistral Small 3.2).
- **MedGemma exclu** tant que Cyril n'a pas lu et accepté lui-même les conditions sur son compte Hugging Face ; un jeton éventuel se fournit par variable d'environnement, **jamais dans le dépôt** ni dans une conversation. État : **non décidé** par Cyril.
- Un seul professeur de plus de 50 Gio sur disque à la fois (`/mnt/d` : 186 Gio libres au 01/10/2026).

## Alternatives Considered
- **Accepter MedGemma à la place de Cyril** : impossible et inacceptable, l'acceptation d'une licence est un acte personnel.
- **Tout exclure sauf Qwen** : écarté, Gemma 4 est ouvert et sert de seconde famille de vocabulaire.

## Consequences
- La comparaison « modèle médical contre généraliste » (MedGemma) n'a pas lieu tant que la décision est ouverte ; le plan l'a déjà classée parmi les compléments (R12).
- La section « Statut » de cette ADR sera remplacée par une nouvelle ADR quand Cyril répond.
