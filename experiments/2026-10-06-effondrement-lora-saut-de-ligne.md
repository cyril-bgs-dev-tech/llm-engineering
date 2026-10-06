# Fiche préenregistrée : l'effondrement du LoRA sans la fin du texte vient-il du saut de ligne final ? (RM-39, suite)

Écrite le 06/10/2026 avant tout run de cette fiche ; suite de `experiments/2026-10-06-diagnostic-effondrement-lora.md` (run `robustesse-lora-diagnostic-fin-retiree`). Constats du diagnostic : retirer 10 % de la fin donne déjà 0,1436 de macro-F1, puis 0,1566, 0,1395 et 0,1250 à 20, 30 et 50 % (pas de progression : un palier) ; les 18 classes restent prédites, la classe la plus prédite pèse environ 27 % comme en texte propre, la probabilité maximale moyenne tombe de 0,97 à 0,65 (perte de signal, pas de collapse sur une classe) ; retirer 50 % du début coûte seulement 5 points (0,7282). Les 717 textes du pli 0 finissent tous par un saut de ligne, que la suppression de la fin enlève : le LoRA classe sur le dernier jeton de la séquence (tête de classification des modèles de langage causaux).

- **question** : la chute vient-elle de l'absence du saut de ligne final (position de lecture du dernier jeton) plutôt que de la perte de contenu ?
- **références** : le même modèle sur le même pli en texte propre (0,7795) et à 30 % de fin retirée (0,1395), mesurés dans le diagnostic.
- **variantes** (une à la fois) : (V1) texte propre sans son saut de ligne final ; (V2) fin retirée à 10 % puis saut de ligne final ajouté ; (V3) fin retirée à 50 % puis saut de ligne final ajouté.
- **jeux et découpage** : développement, pli 0 (717 patients) ; test scellé jamais lu ; inférence seule.
- **métrique principale** : macro-F1 par variante ; secondaires : exactitude, probabilité maximale moyenne.
- **critère de décision** : « format » si V1 tombe sous 0,68 (au moins 10 points de moins que le texte propre) **ou** si V2 atteint au moins 0,46 (récupère la moitié de la perte) ; « contenu » si V1 reste à ±0,02 du texte propre et que V2 et V3 restent sous 0,30 ; sinon « mixte ». Aucune comparaison statistique (descriptif, un pli) ; probabilités conservées pour une analyse ultérieure.
- **budget** : inférence seule, environ 25 minutes de GPU en lot de 1 (14,8 Gio de VRAM mesurés), un seul lot GPU sous `scripts/run_guarded.sh`.
- **prédiction** : V1 s'effondre (probabilité 0,55) ; V2 récupère au moins la moitié de la perte (0,5) ; verdict « format » (0,5), « mixte » (0,3), « contenu » (0,2).
