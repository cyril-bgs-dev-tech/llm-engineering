# Carte de modèle provisoire (mise à jour le 04/10/2026)

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

## Mise à jour du 04/10/2026 (remplace les conclusions de la version du 03/10 là où elles divergent)

| Modèle | macro-F1 | Périmètre | Coût d'inférence (mesuré) | `run_id` |
|---|---|---|---|---|
| TF-IDF caractères 3 à 5, poids équilibrés (**service déployable**) | 0,7202 [IC bootstrap ±1,3] | 5 plis par patient | 20,4 Mo, p50 1,9 ms, p95 4,0 ms, 568 patients/s, CPU | `tfidf-variant-char-balanced`, `bench-serving-tfidf-charbal-v1` |
| CamemBERT-bio, 10 époques, 5 graines | 0,7293 ± 0,0256 (0,708 à 0,771) | pli 0 | 443 Mo, p50 191 ms, CPU 8 threads ; INT8 dynamique naïve : effondrement (0,336) | `camembert-recette-lr1e-4-ep10`, `camembert-graine-ep10-s1` à `s4`, `quantization-camembert-deploy-ep10-lr1e-4` |
| Qwen3.5-4B LoRA, 2 époques | 0,587 | pli 0, une graine | p50 117 ms, p95 290 ms, GPU, 15,5 Gio (P0-09) | `20261003-194530-p1-11-qwen3-5-4b-lr1e-4` |
| Qwen3.5-4B LoRA, 10 époques | en cours | pli 0 | | `llm-mur-qwen3-5-4b-ep10-lr1e-4` |
| TF-IDF référence v1 | 0,6844 [0,657 ; 0,709] | 5 plis | quelques minutes de CPU | `20261003-121942-p1-06-tfidf-chapter` |

**Conclusions révisées** : la recette gelée à 2 époques sous-estime fortement les modèles appris ; à recette mûre l'encodeur et le meilleur TF-IDF sont équivalents (0,73 contre 0,72) ; le TF-IDF est 100 fois plus rapide et 20 fois plus léger. Aucune comparaison n'est résolue en faveur d'un modèle appris. La variance d'une mesure est dominée par cinq chapitres de 27 à 63 patients (85 % de la variance de la macro-F1) ; la règle de puissance échoue (largeur 12,2 points contre 4,0 pour l'encodeur) : toute comparaison de ce cycle est EXPLORE.

**Incertitude** (pli 0) : encodeur 10 époques ECE 0,106 brute et 0,050 après température, exactitude 0,946 à 70 % de couverture ; TF-IDF 0,931 ; Qwen3.5-4B 0,892. Étalonner par plis d'auteurs donne 0,900 de couverture sous décalage d'auteur (0,887 sinon). Politique d'abstention (renvoi de 30 % des patients) : exactitude des cas traités autour de 0,93 pour les familles bien réglées, indistinguables entre elles ; mesurée en développement seulement.

**Limites ajoutées** : non-déterminisme GPU (à graine égale, 0,7714 puis 0,7362) ; écart patient contre auteur de 3,9 points (le leave-one-author-out et la comparaison sur partitions répétées sont en cours) ; signature d'auteur identifiable à 0,917 ; hors spécialité 0,522 ; sans accents −5,6 points pour le TF-IDF.

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

## Items TRIPOD-LLM renseignés (audit GLM, C8-A2)

| Item | Réponse du projet au 03/10/2026 | Source |
|---|---|---|
| 5a, 5c, 5e Données | PARHAF, 4 254 patients ; 4 220 avec code CIM-10 résolu ; 1 code invalide exclu ; 4 219 patients de travail ; classes très déséquilibrées (II : 1 153 contre XXII : 31 sur le développement et le test confondus) ; texte non modifié (aucun prétraitement) ; dates fictives | `results/measures/splits_summary.json` |
| 6a à 6e Modèle | Noms et versions dans le registre (`run_id`) ; LoRA r = 16, alpha 32, dropout 0,05, bf16, lot effectif 32, 4 096 tokens, 2 époques, cosinus ; graines `1000 + k` ; sortie = probabilités sur 18 sorties, argmax | registre, `PROTOCOLE.md` 6.4 |
| 7a à 7e Métriques | Macro-F1 sur 17 chapitres (`AUTRE` exclue), définie avant les runs ; log loss, ECE, couverture conforme en secondaires | `PROTOCOLE.md` 6.1, 6.2 |
| 12 Calcul | RTX 5090 32 Go ; durées par run ci-dessus ; budget B = 90 h, 4,1 h enregistrées à ce jour (`scripts/budget_alert.py`) | registre, protocole section 5 |
| 13 Éthique | Non applicable : corpus fictif, aucune donnée de patient réel ; à formuler ainsi, sans supposer | règles du projet |
| 14c à 14f Accès | Protocole préenregistré et haché (`experiments/INDEX.md`, 9 instantanés) ; code en dépôt privé (ADR-008) ; données PARHAF soumises à ses conditions | ADR-008 |
| 16a à 16d Flux | 4 254 → 4 220 → 4 219 ; test scellé 633 ; 5 plis de développement de 717 à 718 ; plis groupés par auteur de 663 à 763 ; 104 auteurs | `splits_summary.json` |
| 19b, 19d Limites, usage | Voir « Limites connues » et « Usages prévus » ci-dessus ; supervision humaine requise pour tout usage, aucun usage clinique | cette carte |
