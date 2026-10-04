# Calibration des prédictions préenregistrées de l'assistant (audit GLM v4, B-c5)

Les prédictions ont été écrites avant les résultats dans les fiches hachées (`experiments/`) ; l'issue est 1 si la prédiction s'est réalisée, 0 sinon. Liste limitée aux prédictions chiffrées d'une probabilité que j'ai pu retrouver (les prédictions de la première fiche TF-IDF, sans probabilité explicite, sont exclues). Mise à jour du 04/10 à 03h35Z.

| Fiche | Prédiction | Probabilité | Issue | Brier |
|---|---|---|---|---|
| P1-11 | Meilleur LLM entre 0,55 et 0,85 | 0.70 | 1 | 0.090 |
| P1-11 | Un LLM dépasse le TF-IDF au pli 0 (à 2 époques) | 0.60 | 0 | 0.360 |
| P1-11 | 1e-4 meilleur que 1e-5 pour au moins deux candidats sur trois | 0.70 | 1 | 0.090 |
| P1-12 | Élève retenu : 4B ou E4B | 0.60 | 1 | 0.160 |
| P1-12 | Total nominal sous 90 h | 0.50 | 1 | 0.250 |
| P1-12 | Au moins un élève dépasse le TF-IDF au pli 0 | 0.50 | 0 | 0.250 |
| Q19 (4B) | Gain de macro-F1 entre +1 et +8 points | 0.55 | 0 | 0.303 |
| Q19 (4B) | Gain positif | 0.65 | 0 | 0.423 |
| Q19 (4B) | Un chapitre XII, XXI, XXII quitte zéro | 0.50 | 1 | 0.250 |
| Q19 (4B) | L'exactitude baisse | 0.60 | 1 | 0.160 |
| P1-13 | Meilleur taux 1e-4 | 0.50 | 1 | 0.250 |
| P1-13 | Macro-F1 à 5e-5 entre 0,45 et 0,60 | 0.60 | 1 | 0.160 |
| P1-26 | Au moins une prédiction diffère au rejeu | 0.65 | 1 | 0.122 |
| P1-26 | Écart de macro-F1 du rejeu sous 1 point | 0.85 | 1 | 0.023 |
| CamemBERT époques | 4 époques entre 0,50 et 0,62 | 0.60 | 1 | 0.160 |
| CamemBERT époques | À 6 époques l'écart au TF-IDF reste supérieur à 8 points | 0.70 | 1 | 0.090 |
| TF-IDF variantes | Variante (a) poids équilibrés : gain entre 0 et 3 points | 0.50 | 0 | 0.250 |
| TF-IDF variantes | Variante (b) caractères : gain sous 1 point ou perte | 0.60 | 1 | 0.160 |
| TF-IDF variantes | Une variante améliore de plus de δ avec borne basse positive | 0.20 | 1 | 0.640 |
| Hiérarchie | Gain entre 0 et 3 points | 0.45 | 0 | 0.203 |
| Hiérarchie | Gain d'au moins 2 points avec borne basse positive | 0.15 | 0 | 0.022 |
| Encodeur recette | Au moins un run dépasse 0,60 | 0.50 | 1 | 0.250 |
| Encodeur recette | Aucun run ne dépasse le TF-IDF du pli 0 | 0.75 | 0 | 0.562 |
| Encodeur recette | 10 époques meilleur que 6 époques à 1e-4 | 0.65 | 1 | 0.122 |
| Fenêtres | Variante (a) : gain entre +1 et +8 points | 0.55 | 0 | 0.303 |
| Fenêtres | Variante (b) dépasse 0,62 | 0.40 | 1 | 0.360 |
| Saturation | 15 époques au moins égal à 10 époques (graine 1000, premier run) | 0.55 | 0 | 0.303 |
| Saturation | Saturation avant 20 époques | 0.65 | 1 | 0.122 |
| Graines encodeur | Écart-type entre graines entre 1,5 et 6 points | 0.70 | 1 | 0.090 |
| Graines encodeur | La moyenne des 5 graines reste au-dessus du TF-IDF du pli 0 | 0.80 | 1 | 0.040 |
| Confirmation pli 1 | L'ensemble dépasse le TF-IDF au pli 1 | 0.80 | 1 | 0.040 |
| Confirmation pli 1 | IC de l'ensemble entièrement positif | 0.50 | 1 | 0.250 |
| Confirmation pli 1 | Écart au pli 1 inférieur à celui du pli 0 | 0.65 | 0 | 0.423 |
| Confirmation pli 1 | L'ensemble dépasse l'encodeur moyenné au pli 1 | 0.75 | 0 | 0.562 |

**Score de Brier moyen : 0.231** sur 34 prédictions (0,25 = toujours 0,5 ; 0 = parfait). Probabilité moyenne annoncée 0.59 contre fréquence réalisée 0.65.

| Tranche de probabilité | n | probabilité moyenne | fréquence réalisée |
|---|---|---|---|
| p≥0,7 | 9 | 0.75 | 0.78 |
| 0,5 à 0,65 | 21 | 0.57 | 0.62 |
| p<0,5 | 4 | 0.30 | 0.50 |

Lecture : le Brier proche de 0,25 dit que mes prédictions discriminent peu entre ce qui se réalise et ce qui échoue ; la calibration moyenne est correcte. Les erreurs les plus coûteuses portaient sur « le LLM bat le TF-IDF » et « l'encodeur ne bat pas le TF-IDF » (même cause : recette gelée). Méthode : chaque prédiction reçoit une probabilité avant le run ; ce tableau est mis à jour à chaque lot.
