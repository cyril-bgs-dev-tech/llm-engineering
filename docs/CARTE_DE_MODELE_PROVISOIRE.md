# Carte de modèle provisoire (03/10/2026)

Statut : **EXPLORE, développement seulement**. Le test scellé n'a jamais été ouvert ; aucun verdict confirmatoire n'existe. Tâche : chapitre CIM-10 du diagnostic principal, PARHAF (cas fictifs en français, 4 254 patients, 17 chapitres comparés, `AUTRE` exclue de la moyenne). Aucune donnée de patient réel. Sources des chiffres : `RESULTATS.md`.

## Modèles évalués

| Modèle | macro-F1 | Périmètre | Entraînement | Pic mémoire | `run_id` |
|---|---|---|---|---|---|
| Classe majoritaire | 0,025 | 5 plis | aucun | n/a | `p1-03-bounds` |
| TF-IDF + régression logistique | 0,684 [0,657 ; 0,709] | **5 plis par patient** | 704 à 1 158 s de CPU | n/a | `20261003-121942-p1-06-tfidf-chapter` |
| CamemBERT-bio, plein, 2 époques | 0,448 | **pli 0, 1 graine** | 43 s | 7,0 Gio | `p1-07-camembert-bio-lr1e-4` |
| Gemma-4-E4B, LoRA, 1e-4 | 0,456 | pli 0, 1 graine | 4 226 s | 24,8 Gio | `20261003-152759-p1-11-gemma-4-e4b-lr1e-4` |
| Qwen3.5-9B, LoRA, 1e-4 | 0,565 | pli 0, 1 graine | 3 623 s | 21,6 Gio | `20261003-163427-p1-11-qwen3-5-9b-lr1e-4` |
| Qwen3.5-4B, LoRA, 1e-5 | 0,193 | pli 0, 1 graine | 2 515 s | 12,9 Gio | `20261003-141041-p1-11-qwen3-5-4b-lr1e-5` |

Le TF-IDF a un intervalle sur cinq plis, les autres un seul pli : ne pas les comparer sans ce rappel. Sur le même pli 0, le TF-IDF fait 0,697 et le Qwen3.5-9B 0,565 (écart −13,2 points [−18,4 ; −7,0]).

## Front de Pareto qualité contre coût (pli 0)
Aucun modèle LLM ne domine le TF-IDF (meilleure macro-F1 et coût CPU de quelques minutes). Parmi les élèves LLM, le Qwen3.5-9B domine le Gemma-4-E4B (meilleure macro-F1, durée d'entraînement plus courte, pic plus bas). Le criblage est inachevé (deux taux sur quatre par élève) : ce front est provisoire.

## Usages prévus et hors usage
Mesure méthodologique sur textes fictifs. Hors usage : tout usage clinique ou sur patients réels, toute généralisation à d'autres corpus, tout classement final des techniques avant le verdict confirmatoire.

## Incertitude : ce qui est mesuré, et pour quel modèle
**TF-IDF seulement** (validation croisée du développement) : ECE 0,028, couverture conforme marginale 0,901, exactitude 0,931 à 70 % de couverture contre 0,818 à 100 %. Aucun de ces chiffres n'est valable pour un LLM : la mesure sur le 9B attend la conservation de ses probabilités. Sous décalage patient vers auteur, la couverture du TF-IDF tombe à 0,887 (marginale) et 0,880 (par classe).

## Limites connues
- Un pli, une graine pour les LLM ; bord de grille pour le meilleur taux ; criblage inachevé.
- Écart patient/auteur de RM-14 : +3,87 points [+1,27 ; +6,31], lecture non tranchée ; le style identifie l'auteur à 0,917 (confondu avec le thème).
- Chapitres rares (XII, XXI, XXII : 5 à 8 patients au pli 0) : F1 nulle pour le 9B, non vérifiable individuellement.
- Non mesuré : latence p50/p95, quantification, robustesse aux perturbations, calibration des LLM.
- Licences : voir `docs/LICENCES.md`.
