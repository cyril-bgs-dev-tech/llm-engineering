---
name: lora-classifier-recipe
description: Recette de référence pour affiner un LLM en classifieur avec LoRA ou QLoRA. À utiliser pour écrire ou modifier le code d'entraînement, régler les hyperparamètres, choisir tête ou verbaliseur, ou enchaîner un pré-entraînement sur tâche voisine puis la tâche cible.
---

# Recette LoRA pour classifieur

La recette commune à toutes les vagues. Elle lit le contrat `task_specs/<task_id>.yaml` (type, entrées, classes, format de sortie) et ne contient rien de propre à une tâche. Une variante (DoRA, rsLoRA, PiSSA, LoRA+) ne modifie qu'un élément de cette recette à la fois.

## Socle (S1, solution 1re de LMSYS)

- `AutoModelForSequenceClassification`, tête sur le dernier token, `pad_token` défini et cohérent avec le côté de remplissage.
- LoRA sur toutes les couches linéaires ; départ r=64, alpha=128 ; dropout consigné.
- QLoRA 4 bits NF4 pour les modèles au-delà de ce que `vram-preflight` accepte en bf16.
- Contexte 1 024 tokens au départ ; troncature par le milieu (WSDM 2025) ; la longueur est un réglage mesuré, pas une constante.
- Ordonnanceur cosinus, échauffement de 100 pas ; 2 époques au départ.

## Réglage, dans cet ordre

1. **Taux d'apprentissage d'abord** : balayage 1e-5, 2e-5, 5e-5, 1e-4 sur un pli. Toute variante est comparée à la LoRA **réglée**, jamais à une LoRA par défaut (« Learning Rate Matters », 2026).
2. Puis rang et alpha, puis longueur de contexte, puis époques.

## Tâche voisine puis tâche cible (recette Danube, 5e de LMSYS)

1. Affiner sur la tâche voisine (ex. MorFITT avant DiaMED).
2. Fusionner l'adaptateur dans le modèle de base.
3. **Jeter la tête** de classification et en initialiser une neuve pour la tâche cible.
4. Affiner sur la tâche cible avec une nouvelle LoRA.

## Tête ou verbaliseur

Les deux sont des branches de V0. Verbaliseur : probabilités des tokens du **nom en clair** de la classe tel qu'écrit dans le contrat, normalisées sur l'ensemble des classes, gabarit d'invite figé dans la configuration.

## Paires (CLISTER)

Les deux ordres de la paire dans le même pas de gradient ; prédiction symétrisée (moyenne des deux ordres) à l'inférence.

**Terminé quand** le run tourne de bout en bout sur un pli avec la configuration résolue enregistrée dans le registre, et que les tests de `leakage-guard` passent.
