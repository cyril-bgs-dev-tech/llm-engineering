# Fiche préenregistrée : diagnostic de l'effondrement du LoRA quand la fin du texte est retirée (RM-39, suite descriptive)

Écrite le 06/10/2026 avant tout run de cette fiche. Contexte : à 30 % des mots de fin retirés, le LoRA `llm-mur2-qwen3-5-4b-ep10-lr1e-4` passe de 0,7795 à 0,1395 de macro-F1 au pli 0, alors que retirer le début ne coûte que 4,3 points (run `20261006-173250-robustesse-modeles-appris-lora`, fiche `2026-10-06-robustesse-modeles-appris`). Cause inconnue ; le script n'avait gardé que les classes prédites. Diagnostic descriptif : aucune hypothèse ne peut en sortir « confirmée » sans une expérience de plus.

- **question** : l'effondrement est-il progressif avec la part de fin retirée, et prédit-il une seule classe (collapse) ou des classes variées (perte de signal) ?
- **références** : le même modèle sur le même pli en texte propre (0,7795, mesuré dans le même script).
- **variantes** (une à la fois, texte seulement) : fin retirée à 10 %, 20 %, 30 % et 50 % des mots ; en plus, début retiré à 50 % pour comparer à rapport égal.
- **jeux et découpage** : développement, pli 0 (717 patients) ; test scellé jamais lu ; inférence seule.
- **métrique principale** : macro-F1 par variante ; **secondaires** : exactitude, probabilité maximale moyenne, histogramme des classes prédites (part de la classe la plus prédite, nombre de classes prédites), entropie moyenne.
- **critère de décision** : descriptif ; lecture écrite d'avance : « collapse » si une classe reçoit plus de 40 % des prédictions à 30 % de fin retirée ; « perte de signal » si la classe la plus prédite reçoit moins de 25 % et que la probabilité maximale moyenne tombe sous 0,6 ; sinon « mixte ». Aucune comparaison statistique : les probabilités et les prédictions sont conservées (`results/predictions/robustesse-lora-*.probs.npz`) pour une analyse apparié ultérieure.
- **budget** : inférence seule, lots de 4 triés par longueur, une quinzaine de minutes de GPU, VRAM sous 20 Go, un seul lot GPU.
- **prédiction** : effondrement progressif (macro-F1 décroissante avec la part retirée) (0,85) ; collapse sur une classe (0,5), perte de signal (0,25), mixte (0,25) ; retirer 50 % du début coûte moins que retirer 30 % de la fin (0,8).
