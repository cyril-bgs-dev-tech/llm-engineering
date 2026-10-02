---
name: model-card-calibration
description: Calibre un modèle, ajoute la prédiction conforme avec abstention et rédige sa carte de modèle. À utiliser avant de présenter, servir ou quantifier un modèle comme candidat final, et quand on parle de fiabilité, d'abstention ou de passage à l'humain.
---

# Calibration, abstention et carte de modèle

Dans un hôpital, la question n'est pas seulement « quel score ? » mais « quand le modèle doit-il se taire ? ». Un modèle candidat sort de cette étape calibré, capable de s'abstenir, et documenté.

## Étapes

1. **Calibration** : mise à l'échelle par température apprise sur une partition de calibration distincte du test scellé ; ECE et diagramme de fiabilité avant et après.
2. **Prédiction conforme** (split conformal, méthode APS ou équivalente) sur la même partition de calibration : pour un niveau `1 - α` fixé d'avance (90 % par défaut), mesurer sur le test la couverture réelle et la taille moyenne des ensembles.
3. **Abstention** : politique « une seule classe dans l'ensemble → décision automatique, sinon → renvoi à l'humain ». Mesurer le taux d'automatisation et l'exactitude sur la part automatisée.
4. **Après quantification** (GPTQ, INT8, FP8, NVFP4) : refaire 1 à 3 sur le modèle quantifié ; une calibration ne se transfère pas d'une précision à l'autre.
5. **Carte de modèle** `model_cards/<modele>.md` : usage prévu et usages exclus (aide à la décision, jamais décision clinique autonome), données d'entraînement (fiches `dataset-intake`), métriques avec intervalles et `run_id`, calibration, couverture conforme, taux d'automatisation, coûts d'inférence mesurés, limites connues (cas cliniques publiés et non comptes rendus réels), biais observés par classe.

**Terminé quand** la carte existe, chaque chiffre y cite un `run_id`, et la couverture conforme mesurée sur le test est rapportée à côté du niveau visé.
