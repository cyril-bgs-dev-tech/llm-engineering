# Fiche préenregistrée : couverture conforme par région de la cascade à seuil de probabilité (RM-43, suite)

Écrite le 05/10/2026 avant tout run de cette fiche. Complète `2026-10-05-cascade-conforme` : la cascade à seuil (93,4 % des patients sans LoRA) est la plus économe mais sa couverture conforme par région n'a pas été mesurée.

- **question** : pour la cascade à seuil de probabilité de `2026-10-04-cascade-cinq-plis` (seuil choisi hors du pli évalué), l'ensemble de prédiction conforme par famille (niveau 0,90) a-t-il la couverture visée **dans chaque région** (cas traités par l'encodeur, cas escaladés au LoRA) et globalement ?
- **références** : couverture de la cascade conforme (`cascade-conforme-cinq-plis` : 0,9497, 0,9074, 0,9267) ; cible 0,90.
- **variante** : pour chaque pli k : seuil τ choisi sur les quatre autres plis (même grille et même tolérance de 1,0 point que la fiche de la cascade) ; routage par ce seuil ; quantiles LAC par famille calibrés **région par région** sur les cas des quatre autres plis tombant dans la région (premier modèle sur les cas qu'il garde, LoRA sur les cas escaladés), appliqués aux cas du pli k de la même région.
- **jeux et découpage** : développement, cinq plis ; test scellé jamais lu.
- **métrique principale** : couverture de l'ensemble de prédiction dans chaque région et globale, avec Wilson ; **secondaire** : taille moyenne des ensembles par région.
- **critère de décision** : aucun verdict ; rapport de chiffres. Si une région a une couverture inférieure à 0,85, la cascade à seuil n'est pas recommandée avec une garantie conforme.
- **budget** : processeur seul, quelques minutes.
- **prédiction** : couverture globale à 0,03 de 0,90 (probabilité 0,7) ; couverture de la région « encodeur » dans [0,87 ; 0,95] (probabilité 0,6) ; couverture de la région « LoRA » inférieure à 0,88 (probabilité 0,35, la région est petite : environ 6,6 % des patients, 237 cas).
