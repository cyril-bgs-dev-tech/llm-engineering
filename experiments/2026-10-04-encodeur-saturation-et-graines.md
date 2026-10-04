# Fiche préenregistrée : saturation de la durée et variance entre graines de l'encodeur CamemBERT-bio (EXPLORE)

Écrite avant tout résultat de ces runs, après lecture de la recette mûre (10 époques 1e-4 : 0,7714 ; 6 époques 1e-4 : 0,5527 ; 6 époques 2e-4 : 0,6291 ; le saut vient des chapitres rares, IV, V, XII, XXI, XXII passant de 0 ou presque à 0,55 à 1,0 sur 5 à 11 patients chacun).

- **question** : la macro-F1 de l'encodeur sature-t-elle au-delà de 10 époques ? Quelle est la variance entre graines de la meilleure recette ?
- **référence** : `camembert-recette-lr1e-4-ep10` (0,7714, pli 0, graine 1000).
- **variantes** : (a) taux 1e-4, 15 puis 20 époques, graine 1000 ; (b) la recette de plus haute macro-F1 parmi 10, 15 et 20 époques à 1e-4 (égalité : moins d'époques) avec les graines 1001 à 1004 (`1000 + k`, protocole 6.4). Les autres paramètres sont identiques (508 tokens tête et fin, lot effectif 32, micro-lot 16, pli 0).
- **jeux et découpage** : développement, pli 0 ; test scellé jamais lu.
- **métrique principale** : macro-F1 du pli 0 ; secondaires : exactitude, log loss, ECE, F1 par chapitre.
- **critère de décision** : saturation = gain de moins de δ = 2,0 points entre deux durées consécutives ; variance = écart-type des cinq graines (1000 à 1004) de la recette retenue ; EXPLORE, aucun verdict de gain, la référence confirmatoire reste inchangée ; toute recette plus longue ne devient référence que par nouvelle version du protocole et ADR.
- **budget** : 15 et 20 époques : environ 5 et 7 minutes ; quatre graines : environ 15 à 25 minutes ; au plus 45 minutes de GPU.
- **prédiction** : 15 époques ≥ 10 époques (probabilité 0,55) ; saturation avant 20 époques (probabilité 0,65) ; écart-type entre graines compris entre 1,5 et 6 points (probabilité 0,7) ; la moyenne des cinq graines reste au-dessus du TF-IDF du pli 0, 0,6971 (probabilité 0,8).
