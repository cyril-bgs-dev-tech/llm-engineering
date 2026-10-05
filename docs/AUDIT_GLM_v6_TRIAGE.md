# Audit GLM v6 (30 leviers de performance) : triage, mesures et intégration

Source : `audit_GLM_v6.md` (05/10/2026, 30 leviers classés, 12 conclusions attaquées, trajectoire, obsolescence). Statuts : **fait** (preuve citée), **en file** (lot GPU ou CPU lancé), **planifié** (tâche de la feuille de route), **écarté** (avec raison), **à décider** (Cyril). Rien ici ne modifie le protocole gelé.

## 1. Ce que l'audit a apporté de plus utile
1. **Le bootstrap par blocs d'auteurs** (levier 1) : mesuré le jour même. Il rectifie une de nos phrases : la règle de puissance v2 est atteinte à 95 % (largeur 3,39) mais **pas à 98,33 % (4,24)** ; elle vaut donc pour une **question primaire unique**. Les intervalles restent positifs (ensemble moins TF-IDF : +5,20 [+3,84 ; +7,23]). Toutes les citations de « 3,78 à 98,33 % » ont été rectifiées (RESULTATS, protocole v2 brouillon, ADR-015, carte de modèle, wiki, présentation, brief v5).
2. **L'empilement appris est réfuté** (levier 4, +1 à +2,5 points annoncés) : le mélange 50/50 est quasiment optimal (poids appris 0,6 à chaque pli, +0,41 [−0,25 ; +1,13], non résolu) ; la régression logistique surajuste (−5,98). La trajectoire « par le haut » de GLM (paliers à 0,78 à 0,79) est donc abaissée : le prochain gain n'est pas dans l'assemblage.
3. **Plafond d'ambiguïté et audit d'étiquettes** (levier 3) : confirmé comme prochain domino utile (P2-06) avant le gel du système final.
4. **Variance** (levier 11) : la variance d'un run isolé est presque entièrement du « reste » (interaction pli × graine et non-déterminisme du GPU, 2,32 points), l'effet de graine est nul, l'effet de pli 0,9 : confirme la nécessité des moyennes et des prédictions regroupées.
5. **Cascade** (levier 2) : pas de désaccord ; le piège relevé (la garantie conforme change selon le système appelé) est intégré à RM-43 (couverture mesurée par région de la cascade).

## 2. Erreurs ou limites de l'audit, et erreurs de notre cahier
- **Notre erreur (levier 10 et 12)** : le cahier v6 présentait le champ `pool` comme une « piscine hors distribution » séparée. C'est faux : ce sont les **sous-ensembles d'usage annotés** (général 3 048, codage CIM-10 245, infectiologie 110, oncologie 92 et 91 au développement), **tous dans les plis de développement**. Les leviers 10 (garde de dérive) et 12 (pseudo-étiquettes sur la piscine) reposent sur cette erreur : **écartés**. Mesure utile en remplacement (faite) : exactitude par sous-ensemble : codage 0,918 [0,877 ; 0,947] au-dessus du général 0,844 ; oncologie à 1,000 (un seul chapitre) ; la difficulté est entièrement dans le sous-ensemble général.
- **Coûts sous-estimés** : leviers 16, 17 et 25 (lissage, EMA, curriculum) chiffrés à 0,1 h : c'est le coût d'un run ; pour un verdict (trois graines, cinq plis) il faut environ 1,2 h par facteur (RM-55 les corrige).
- **Levier 30 (fusion des cinq LoRA)** : **non mesurable sur le développement** : chaque pli est vu à l'entraînement par quatre des cinq adaptateurs ; la fusion ne peut s'évaluer que sur le test scellé (RM-20) ou par plis imbriqués. Reporté à P4-01, après RM-20, avec cette réserve.
- **Levier 19 (métadonnées de scénario)** : inspection des champs : le scénario ne contient que le diagnostic principal (et âge, sexe, modes d'admission et de sortie) ; aucun diagnostic rival : **écarté**.
- **Levier 20 (version dé-stylée)** : le générateur du corpus n'est pas disponible ; une normalisation textuelle serait un nouveau prétraitement sans valeur démonstrative : **écarté** (le leave-one-author-out couvre la question).
- **Levier 24 (poursuivre le LoRA depuis un point de sauvegarde)** : l'adaptateur n'est sauvegardé qu'à la fin, avec un calendrier d'apprentissage terminé : la poursuite change le calendrier ; **écarté** au profit de P1-16 (époques), avec un nouveau run.
- **Levier 26 (plus proches voisins)** : redondant avec le TF-IDF linéaire sur les mêmes n-grammes ; probabilité de gain faible reconnue par GLM : **écarté** (gardé comme piste si les représentations de l'encodeur sont exploitées, hors des 30).
- **Autres remarques** : la définition des familles de Mondrian a été fixée avant les mesures à cinq plis (`glm_v3_families.py`) ; l'incertitude de la cascade avec « 77 à 79 % » reste un aperçu non validé (fiche `cascade-cinq-plis`).

## 3. Les 30 leviers : décision

| # | Levier | Décision | Où |
|---|---|---|---|
| 1 | Bootstrap par blocs d'auteurs | **fait** | run `glm-v6-blocs-auteurs` ; protocole v2 : règle par blocs, question primaire unique à 95 % (RM-29) |
| 2 | Cascade validée hors pli | **fait** : encodeur puis LoRA non-inférieur (+0,12 [−1,74 ; +1,90]), 93 % sans LoRA ; TF-IDF puis LoRA non-inférieur non atteint | RM-40, `cascade_cv.py` |
| 3 | Audit des 65 erreurs confiantes | **fait sur les 65 cas** (30 préenregistrés : E 27 %, R 67 %, M 7 % ; 65 : E 28 %, R 69 %, M 3 % : ambiguïté de codage établie, bruit d'étiquette non établi) ; reste la contre-expertise par un codeur | P2-06, fiche `2026-10-05-audit-erreurs-confiantes`, run `sensibilite-xviii-xxi` |
| 4 | Empilement appris par chapitre | **fait, réfuté** | run `glm-v6-empilement` |
| 5 | Mondrian par défaut | fait à cinq plis ; à rejouer avec le LoRA | RM-33, post-traitement du LoRA |
| 6 | Zéro-shot 4B et 9B | **fait** : 4B 0,4929, 9B 0,4725 (l'affinage apporte +28,8 points) | RM-30 |
| 7 | Figer la référence-2 | inclus dans le gel | RM-50 (candidat D) |
| 8 | Synthétique ciblé | planifié | P2-10, domino 4 |
| 9 | LoRA aux plis 3 et 4 et comparaison regroupée | **fait** : LoRA regroupé 0,7673, +4,71 contre le TF-IDF, +1,45 non résolu contre l'encodeur, −0,49 contre l'ensemble | RM-28 |
| 10 | Piscine hors distribution | **écarté** (champ mal décrit) ; remplacé par la mesure par sous-ensemble, faite | run `glm-v6-par-pool` |
| 11 | Décomposition de variance | **fait** | run `glm-v6-variance` |
| 12 | Pseudo-étiquettes sur la piscine | **écarté** (pas de piscine) | : |
| 13 | Encodeurs alternatifs | planifié | RM-53 |
| 14 | Représentations gelées d'un LLM | planifié | RM-54 |
| 15 | Optimisation du seuil de décision | **fait, sans gain** (S4 −0,51 [−1,58 ; +1,14]) | run `glm-v6-empilement` |
| 16 | Lissage d'étiquettes | planifié | RM-55 |
| 17 | Moyenne de poids (EMA) | planifié | RM-55 |
| 18 | Augmentation au test (ordre des documents) | planifié (EXPLORE, ordre gelé) | P4-03 |
| 19 | Métadonnées de scénario | **écarté** (aucun rival dans le scénario) | : |
| 20 | Version dé-stylée | **écarté** | leave-one-author-out |
| 21 | Trois graines du LoRA | à décider après les cinq plis | règle : si la variance entre graines du LoRA dépasse l'écart LoRA contre ensemble, la comparaison est dite invérifiable à ce budget |
| 22 | 9B à recette mûre | planifié (non ★) | RM-31 |
| 23 | Rang et alpha | planifié (chemin complet) | P1-14 |
| 24 | Époques du LoRA | planifié (nouveau run, pas de poursuite) | P1-16 |
| 25 | Curriculum | planifié | RM-55 |
| 26 | Plus proches voisins | **écarté** | : |
| 27 | Protocole v2 (ADR-015) | **à décider** (Cyril) ; ADR complétée | RM-37 |
| 28 | Service de l'encodeur sur GPU | en file | RM-34 |
| 29 | Encodeur élagué | planifié | RM-45 |
| 30 | Fusion des cinq LoRA | planifié, **après le test scellé** (non mesurable en développement) | P4-01 |

## 4. Conséquences sur la chaîne de dominos
- Domino 7 (RM-20) : la largeur à vérifier est celle **par blocs d'auteurs** ; la comparaison primaire est unique (ensemble contre TF-IDF), à 95 %.
- Domino 4 (P2-06, P2-10) : l'audit d'étiquettes précède le synthétique ; il est le prochain objectif sans GPU.
- La trajectoire de gain : l'assemblage est épuisé (S1 +0,4) ; les gains restants sont dans les étiquettes, les données de la queue (synthétique) et le coût ; GLM situe un lecteur extérieur « convaincu jusqu'à environ 0,80 » (conjecture).
- L'audit n'a pas fait changer le système final candidat (ensemble 50/50), ce qui est lui-même un résultat.
