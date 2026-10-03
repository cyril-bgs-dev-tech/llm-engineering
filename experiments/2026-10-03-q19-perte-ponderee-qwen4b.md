# Fiche préenregistrée : perte pondérée par classe sur le Qwen3.5-4B (exploration Q19, remplace la fiche sur le 9B)

Cite `experiments/2026-10-03-q19-perte-ponderee-qwen9b.md` (jamais exécutée, non modifiée). Raison du changement : P1-12 a retenu le Qwen3.5-4B comme élève (ADR-014) ; une exploration sur le 9B ne servirait plus le choix de recette.

- **question** : une perte d'entropie croisée pondérée par classe (poids en 1/√n, moyenne de 1 sur les exemples d'entraînement) améliore-t-elle la macro-F1 du Qwen3.5-4B au pli 0, notamment sur les chapitres rares ?
- **référence** : run `20261003-194530-p1-11-qwen3-5-4b-lr1e-4` (macro-F1 0,5867, 3 024 s, 12,9 Gio), prédictions `results/predictions/p1-11-qwen3-5-4b-lr1e-4.json`.
- **variante** : seul changement : `--class-weights inv-sqrt`. Le reste identique : LoRA r = 16 alpha 32, 4 096 tokens, lot effectif 32, micro-lot 1, 2 époques, taux 1e-4, graine 1000, pli 0.
- **jeux et découpage** : développement, pli 0 ; test scellé jamais lu.
- **métrique principale** : macro-F1 du pli 0. **Secondaires** : F1 par chapitre, F1 pondérée, exactitude, log loss, log loss équilibrée, ECE, durée.
- **critère de décision** : différence appariée (`scripts/pair_preds.py`, IC 95 %) : « amélioration suggérée » si Δ ≥ +2,0 points et borne basse > 0 ; « dégradation suggérée » si borne haute < 0 ; sinon « non résolu ». **EXPLORE : aucun verdict de gain, hors famille confirmatoire (H1 à H3)**, qui ne change pas ; une recette pondérée ne devient référence que par une nouvelle version du protocole et une ADR.
- **budget** : un run d'environ 3 100 s, `--limit-seconds 4650` (1,5 fois), probabilités et adaptateur conservés.
- **prédiction** : Δ macro-F1 entre +1 et +8 points (probabilité 0,55) ; Δ > 0 (probabilité 0,65) ; au moins un des chapitres XII, XXI, XXII quitte une F1 nulle (probabilité 0,5) ; l'exactitude baisse (probabilité 0,6).
