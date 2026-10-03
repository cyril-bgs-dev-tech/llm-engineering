# ADR-014 : élève retenu, Qwen3.5-4B (P1-12, règle ADR-009 appliquée telle qu'écrite)

Statut : **acceptée provisoirement** (décision déléguée du 03/10/2026, réversible par Cyril). Fiche : `experiments/2026-10-03-p1-12-choix-eleve-et-plafond.md`, écrite avant la lecture des runs.

## Données (pli 0, une graine, développement ; run_id au registre)
| Candidat | meilleure macro-F1 (taux) | secondes | pic réservé |
|---|---|---|---|
| Qwen3.5-4B | **0,5867** (1e-4) ; 0,193 (1e-5) | 3 024 | 12,9 Gio |
| Qwen3.5-9B | 0,565 (1e-4) ; 0,2128 (1e-5) | 3 623 | 21,6 Gio |
| Gemma-4-E4B | 0,4558 (1e-4) ; 0,1416 (1e-5) | 4 226 | 24,8 Gio |

Runs : `20261003-194530-p1-11-qwen3-5-4b-lr1e-4`, `20261003-163427-p1-11-qwen3-5-9b-lr1e-4`, `20261003-152759-p1-11-gemma-4-e4b-lr1e-4` et les trois à 1e-5.

## Règle et résultat
Les trois candidats passent la contrainte de mémoire (≤ 28 Gio). Les deux meilleurs sont le 4B et le 9B ; l'écart apparié 4B moins 9B est **+2,16 points, IC 95 % [−1,78 ; +5,90] : non résolu** (`p1-11-qwen4b-minus-qwen9b-1e-4-fold0`). L'IC contient 0 : la règle retient **le moins coûteux, le Qwen3.5-4B** (3 024 s contre 3 623 s ; 12,9 contre 21,6 Gio).

## Ce que cela ne dit pas
- Le 4B n'est pas démontré meilleur que le 9B : un pli, une graine, deux taux sur quatre ; la prédiction de la fiche (4B ou E4B retenu, probabilité 0,6) se réalise, mais celle selon laquelle le 9B serait le meilleur n'était pas écrite comme telle.
- **Le 4B reste 11,1 points sous le TF-IDF** au pli 0, IC [−16,4 ; −4,8] (`p1-11-qwen4b-1e-4-minus-tfidf-fold0`) : aucun LLM ne bat le TF-IDF ; la question « poursuivre la distillation » (RM-17) se pose à Cyril, sans affirmation de gain.
- Le meilleur taux de chaque candidat est au bord supérieur de la grille : les taux 2e-5 et 5e-5 du 4B sont dans la file.

## Plafond de dépense (G5)
Le budget recalculé par `scripts/spikes/budget_v2.py` donne 70,4 à 83,8 h pour le 4B avec le professeur Qwen (hypothèses de P0, postes non comptés exclus). Seuil écrit d'avance : on se place dans la zone (b), entre 72 h et 90 h, par prudence : **aucun nouveau run non confirmatoire au-delà du backlog** (seules explorations autorisées : Q19, diagnostic CamemBERT à 4 et 6 époques) et question à Cyril avant P3-07. Recalcul avec les durées réelles après P1-13.

## Conséquences
La file GPU est réorientée sur le 4B : rejeu (déterminisme P1-26, probabilités, adaptateur), grille 2e-5 et 5e-5, exploration Q19 sur le 4B (nouvelle fiche), second pli pour les deux meilleurs taux, puis P1-19.
