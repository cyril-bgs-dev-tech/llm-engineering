# ADR-016 : gel du système final G et prédiction chiffrée du test scellé (RM-50), ACCEPTÉE le 06/10/2026

Statut : **acceptée** par la validation de Cyril du 06/10/2026 (question Q22 de `tasks/QUESTIONS_POUR_CYRIL.md`, section « Décisions validées le 06/10/2026 », à la demande « valides toutes les questions qui attendent une décision utilisateur avec la réponse la plus intelligemment adaptée »). **Ce gel n'ouvre aucune étiquette du test scellé et n'autorise pas son ouverture (RM-20), qui reste une décision séparée de Cyril.** Brouillon d'origine : `docs/BROUILLON_GEL_SYSTEME_FINAL.md`.

## Décision
Le système final est **G : moyenne à parts égales de trois sorties de probabilité**, le LoRA Qwen3.5-4B (graine 1000), l'encodeur CamemBERT-bio moyenné sur cinq graines (1000 à 1004) et le TF-IDF caractères 3 à 5 à poids équilibrés, tous entraînés sur les 3 586 patients du développement. Référence de la question primaire : le meilleur TF-IDF (A). Comparaisons secondaires sans verdict : G moins l'ensemble encodeur + TF-IDF (E), G moins le LoRA seul (F).

## Pourquoi G (règle écrite avant lecture)
Règle de sélection de `docs/BROUILLON_GEL_SYSTEME_FINAL.md` section 2, appliquée aux prédictions hors pli des cinq plis : run `20261005-145138-selection-systeme-final-apres-rm56`. G est le seul candidat admissible (E : borne basse −2,79, F : −2,47, sous le seuil −2,0) ; les élèves distillés sont sortis après le contrôle de fuite RM-56 (gain non préservé). Macro-F1 de développement : 0,7799 ; écart à E : +0,78 (non résolu), à A : +5,98.

## Ce qui est figé
`results/frozen_final.json` (empreinte SHA-256 `8cb2382c75b9a11481c2a95aac2fef833e2c96e63affd5a15749c526e3ce7116`) : composition, runs et empreintes des sept modèles et de leurs prédictions du temps A (écrites sans étiquette), δ = 2,0, incertitude (aucune température : ECE 0,016 avant, 0,020 après ; conforme LAC à 90 %, marginal et par famille de Mondrian, familles de `scripts/glm_v3_families.py`, quantiles calibrés sur les prédictions hors pli du développement seulement ; table d'abstention à 100, 90, 80, 70 et 50 % de couverture), hypothèse d'échangeabilité, empreinte de la fiche `experiments/2026-10-05-modeles-finaux.md`, et la **prédiction chiffrée du test scellé** : macro-F1 de G centrée sur 0,78 [0,75 ; 0,81] à 80 % ; différence avec le TF-IDF +6,0 [+3,3 ; +8,7] ; verdict de la question primaire « gain confirmé » 0,47, « non résolu » 0,50, « absence de gain utile » 0,03 ; G moins E « non résolu » (0,9) ; couverture conforme minimale par famille au moins 0,87 (0,6) ; exactitude à 70 % de couverture 0,95 [0,93 ; 0,97].

## Ce qui n'est pas fait, et pourquoi (réserves déclarées)
- **Pas de seconde graine du LoRA** : la règle a été appliquée à des prédictions hors pli avec une graine par pli ; une seconde graine finale changerait le système sans estimation hors pli. La variance entre graines du LoRA n'est pas mesurée (deux graines au pli 0 : 0,7795 et 0,7893).
- **Pas de synthétique ciblé ni de contre-expertise des étiquettes** avant le gel : ils ne s'évaluent pas avant lui et ne changent pas G.
- **Fragilité du LoRA à la fin du texte** (runs `20261006-173250-robustesse-modeles-appris-lora`, `20261006-181026-robustesse-lora-diagnostic-fin-retiree`, `20261006-182233-robustesse-lora-saut-de-ligne`) : elle ne touche pas le test (tous les textes, développement et test, ont la même fin, un saut de ligne) mais borne tout usage : la limite est déclarée dans la carte de modèle v4.
- La différence G moins E (+0,78) et G moins F (+1,27) sera rapportée « non résolue » si elle l'est.

## Procédure et arrêts
Aucune recette n'est modifiée ni ajoutée entre ce gel et RM-20. Avant l'ouverture : `scripts/sealed_evaluation.py rehearsal` (répétition générale sur le développement, avec G et la référence du gel) puis `check` ; l'ouverture est unique (`open --confirm-open`), journalisée, suivie de RM-51 sur la même ouverture. Si la règle de puissance échoue pour la paire choisie, ou si une précondition manque, l'évaluation se fait sans verdict (PROTOCOLE_V2.md).
