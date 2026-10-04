# Fiche préenregistrée : élève TF-IDF à étiquettes souples, professeur strictement hors pli (RM-46, EXPLORE, cinq plis)

Écrite avant les runs. L'élève garde la latence du TF-IDF (1,9 ms, 20 Mo) ; la question est de savoir ce que lui apporte un professeur plus fort.

- **question** : (a) un TF-IDF caractères (3 à 5, poids équilibrés) entraîné sur l'étiquette et sur les probabilités hors pli de l'**ensemble encodeur + TF-IDF** dépasse-t-il le même TF-IDF à étiquettes dures ? (b) bras ultérieur : même question avec le LoRA mûr comme professeur, quand ses cinq plis existeront.
- **référence** : TF-IDF caractères équilibré à étiquettes dures, mêmes plis et mêmes valeurs de C par pli (100, 10, 1000, 100, 10, choisies par la validation interne du run `tfidf-variant-char-balanced`) ; ensemble professeur ; encodeur moyenné.
- **variante** : régression logistique entraînée par réplication pondérée (`llmft.soft_labels.replicate_soft`), cible `0,5 * étiquette + 0,5 * professeur`, masse sous 0,05 abandonnée puis renormalisée ; **aucun réglage** (C par pli repris de la référence, alpha et seuil fixés ici) ; professeur du pli k = probabilités hors pli des patients des plis autres que k (`distill.oof_teacher_map`, contrôle strict). Réserve de second ordre déclarée : chaque professeur a vu le pli k (voir `2026-10-04-distillation-vers-encodeur`).
- **jeux et découpage** : développement, plis 0 à 4 ; test scellé jamais lu.
- **métrique principale** : macro-F1 sur 17 chapitres (AUTRE exclu), prédictions regroupées sur cinq plis ; différence appariée avec la référence dure (`power_rule.pooled_interval`, IC 95 %) ; secondaires : par pli, log loss, ECE, latence (inchangée).
- **critère de décision** : « gain confirmé » si la borne basse est > 0 et la différence ≥ δ = 2,0 ; « sans gain » si l'IC tient dans ±δ ; sinon « non résolu » ; rapport de l'écart au professeur.
- **budget** : calcul sur processeur seul, un thread, priorité basse, environ 15 minutes ; aucun calcul sur GPU.
- **prédiction** : l'élève souple dépasse la référence dure de 0,5 à 3 points (probabilité 0,6), IC entièrement positif (0,4), gain ≥ 2,0 (0,2) ; il reste à plus de 2 points sous le professeur (0,85).
