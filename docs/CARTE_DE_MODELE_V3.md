# Carte de modèle v3 (04/10/2026) : classifieur du chapitre CIM-10, comptes rendus cliniques fictifs français

Remplace `docs/CARTE_DE_MODELE_PROVISOIRE.md`. Statut : **EXPLORE, développement seulement** ; test scellé jamais ouvert ; aucun verdict confirmatoire. Chaque chiffre renvoie à un `run_id` de `RESULTATS.md` (tableaux regénérables : `docs/TABLEAUX_GENERES.md`).

## Usage prévu et hors usage
**Prévu** : mesure méthodologique de l'apport de techniques d'adaptation (TF-IDF, encodeur affiné, LoRA d'un LLM, ensembles) sur un corpus **fictif**, comme démonstration de méthode d'évaluation. **Hors usage** : tout usage clinique, toute décision sur des patients réels, toute généralisation à un autre corpus ou à des textes réels, tout classement définitif des techniques avant verdict confirmatoire. Supervision humaine requise pour tout usage.

## Données
PARHAF (4 254 comptes rendus fictifs, 4 219 utilisés, 104 auteurs, 17 chapitres évalués) ; fiche : `docs/FICHE_DE_DONNEES_PARHAF.md`. Aucune donnée de patient réel.

## Systèmes évalués (macro-F1 sur les plis du développement, prédictions hors pli)
| Système | macro-F1 | Périmètre | Coût d'inférence | Taille |
|---|---|---|---|---|
| TF-IDF caractères 3 à 5, poids équilibrés (service) | 0,7202 | 5 plis | p50 1,9 ms, p95 4,0 ms (CPU) | 20,4 Mo |
| Encodeur CamemBERT-bio, 10 époques, moyenne de 5 graines | 0,7331 ; 0,7532 ; 0,7613 | plis 0, 1, 2 | 191 ms par modèle (CPU 8 threads) | 443 Mo par modèle |
| Ensemble 50/50 encodeur (5) + TF-IDF | 0,7626 ; 0,7512 ; 0,7923 | plis 0, 1, 2 | environ 1 s (CPU) | environ 2,2 Go |
| Qwen3.5-4B LoRA, 10 époques (pli 0 : deux graines 0,7795 et 0,7893 ; pli 1 : une graine) | 0,7844 (moyenne) ; 0,7415 | plis 0, 1 | p50 117 ms (GPU) | adaptateur 196 Mo |
Écarts contre le meilleur TF-IDF : ensemble +4,5, +6,2, +4,3 (résolu aux trois plis) ; LoRA +6,4, +5,3 (résolu aux deux plis) ; encodeur moyenné seul +1,5, +6,4, +1,2 (non résolu à deux plis). LoRA et encodeur moyenné : +4,9 (graine 1000, non résolu), +5,75 (graine 1001, résolu) au pli 0, −1,1 au pli 1 : le LoRA est au moins équivalent et plutôt meilleur. La recette gelée (2 époques) sous-estimait fortement les modèles appris (encodeur 0,448 ; LoRA 0,587).

## Incertitude (pli 0 et 1 ; étalonnage croisé ; jamais sur le test)
LoRA mûr : ECE 0,110 brute et 0,028 (pli 0) / 0,034 (pli 1) après température ; ensemble conforme LAC 90 % : couverture 0,909 / 0,9025 avec 1,15 / 1,17 classe par ensemble ; exactitude à 70 % de couverture 0,960 / 0,964. Encodeur : 0,946 ; TF-IDF : 0,931 à 0,940. **La couverture marginale cache des familles de chapitres sous-couvertes (minimum 0,56 à 0,68)** ; l'étalonnage conditionnel par famille relève ce minimum à 0,80–0,90 mais multiplie la taille des ensembles par 1,6 à 3. Étalonner par plis d'auteurs donne 0,900 de couverture sous décalage d'auteur.

## Robustesse
TF-IDF à caractères : insensible aux perturbations de forme (±1 point) et aux ablations de contenu (fin retirée −0,1 ; début retiré −0,6). TF-IDF à mots : −5,6 points sans accents. LoRA mûr : accents −0,5, fautes +1,6, casse −1,3 (bruit). Hors spécialité (TF-IDF à mots) : exactitude 0,522. Non mesuré : robustesse de l'encodeur, ablations de contenu du LoRA, nouveaux auteurs pour les modèles appris.

## Limites connues et ce que nous ne savons pas
Un à trois plis, une graine pour le LoRA ; non-déterminisme GPU (écart de 3,5 points pour une même graine de l'encodeur) ; cinq chapitres de 27 à 63 patients portent 85 % de la variance de la macro-F1 ; règle de puissance v1 échouée (12,2 contre 4,0) ; signature d'auteur d'environ 2 points ; erreurs surtout entre diagnostics rivaux (le bon chapitre est dans les deux premiers dans 95 % des cas, mauvaise précision dans les spécialités à diagnostics multiples : pédiatrie 0,52, gériatrie 0,54) ; 65 erreurs confiantes (1,8 % des patients) à auditer ; quantification INT8 naïve inutilisable (effondrement) ; apport de la distillation, du pré-entraînement voisin et des données synthétiques non mesuré.

## Éthique et conformité
Corpus fictif, aucun comité d'éthique requis (à formuler ainsi) ; licences des modèles : `docs/LICENCES.md` (Apache-2.0 pour Qwen3.5 et Gemma 4, MIT pour CamemBERT-bio) ; checklist TRIPOD-LLM renseignée dans `docs/CARTE_DE_MODELE_PROVISOIRE.md` ; aucune sortie du dépôt sans claim-gate (`scripts/check_claims.py`, tableau de preuve du rapport).
