# Fiche préenregistrée : grille complète de taux du Qwen3.5-4B (P1-13) et rejeu de déterminisme (P1-26)

Suite d'ADR-014 (élève retenu : Qwen3.5-4B). Complète les deux taux déjà mesurés (1e-5 : 0,193 ; 1e-4 : 0,5867) par les deux manquants de la grille gelée (N = 4, jamais étendue).

- **question** : quel taux de la grille {1e-5, 2e-5, 5e-5, 1e-4} donne la plus haute macro-F1 du pli 0 pour le Qwen3.5-4B ? Le rejeu à l'identique du taux 1e-4 reproduit-il le run initial (déterminisme du GPU) ?
- **référence** : runs `p1-11-qwen3-5-4b-lr1e-5` et `20261003-194530-p1-11-qwen3-5-4b-lr1e-4`.
- **variante** : seul le taux change (2e-5, 5e-5) ; le rejeu garde la configuration exacte du run à 1e-4 (graine 1000) et conserve en plus probabilités et adaptateur.
- **jeux et découpage** : développement, pli 0, une graine ; test scellé jamais lu.
- **métrique principale** : macro-F1 du pli 0. **Secondaires** : exactitude, log loss, ECE, durée, pic de mémoire. Pour le rejeu : écart maximal de la perte par pas, nombre de prédictions différentes.
- **critère de décision** : taux retenu = plus haute macro-F1 ; si le meilleur est 1e-4 (bord de la grille) il est signalé comme tel (PROTOCOLE.md 6.5), la grille ne s'étend jamais. Le rejeu est « identique » si les pertes et les prédictions coïncident, « écart borné » sinon, l'écart étant consigné ; aucun verdict de gain.
- **budget** : trois runs d'environ 3 000 s chacun (≈ 2,5 h), `--limit-seconds 4650`.
- **prédiction** : le meilleur taux est 1e-4 (probabilité 0,5) ou 5e-5 (0,4) ; macro-F1 à 5e-5 entre 0,45 et 0,60 (probabilité 0,6) ; le rejeu donne des prédictions différentes sur au moins un patient (probabilité 0,65) mais un écart de macro-F1 inférieur à 1 point (probabilité 0,85).
