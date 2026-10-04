# ADR-013 : scénario de repli, plis groupés par auteur comme estimand principal (PROPOSÉE, non appliquée)

Statut : **proposée**. Préparée sur recommandation de l'audit GLM v3 (C3-A5, avis sur Q18) pour qu'une bascule éventuelle soit instruite d'avance. **Elle ne change rien au protocole gelé.** Décision déléguée du 03/10/2026 sur Q18 : garder le gel, rapporter les deux chiffres.

## Contexte
RM-14 : macro-F1 du TF-IDF 0,684 par patient contre 0,646 par auteur, écart +3,87 points [+1,27 ; +6,31], « signalé » par la règle préenregistrée. Faits ajoutés le 03/10/2026 : l'identifiant d'auteur n'est présent dans le texte que pour 1 patient sur 4 254 ; le style retrouve l'auteur à 0,917 d'exactitude (confondu avec le thème) ; 169 des 171 paires de quasi-doublons à 0,6 sont du même auteur ; les plis groupés sont plus déséquilibrés sur les petits chapitres.

## Option A (décision déléguée, appliquée) : protocole maintenu
Test scellé stratifié, non groupé : il estime la performance sur de nouveaux patients du même corpus, écrit avant les données. Les plis groupés par auteur sont rapportés à côté, avec l'écart de RM-14 (+3,87 points). Le rapport dit que les auteurs du test sont ceux du développement (`docs/GABARIT_RAPPORT.md`).

## Option B (repli préparé) : plis groupés comme estimand principal
Déclencheurs écrits d'avance, à vérifier avant l'ouverture du test scellé : (1) l'écart patient moins auteur mesuré sur le **candidat final LLM** dépasse 3 points avec borne basse positive ; (2) la lecture « fuite » est confirmée par une mesure qui élimine la lecture thématique. Si les deux sont vrais, une nouvelle version du protocole (hors gel : ADR + nouvel instantané) déclarerait l'estimand « nouveaux auteurs », avec développement groupé comme évaluation principale et test scellé rapporté comme estimand secondaire « nouveaux patients ». Coût : les partitions figées ne bougent pas (le test scellé n'est pas re-tiré, ce qui détruirait l'actif scellé) ; seule la lecture des résultats change.

## Conséquences
Rien à faire tant qu'aucun déclencheur n'est atteint. Mesure à produire d'abord : l'écart patient/auteur du candidat final LLM (pli 0 et plis de contrôle groupés existent).

## Mesure ajoutée le 04/10/2026 (audit GLM v4, F-c1)
Le leave-one-author-out sur le TF-IDF (`scripts/loao_tfidf.py`, run `tfidf-loao`) est la mesure « nouveaux auteurs » qui opérationnalise la lecture « fuite » : proche de 0,6844 (l'auteur n'aide pas), proche de 0,6457 (signature d'auteur), ou intermédiaire. Elle précède toute décision de basculement.

**Résultat (04/10/2026)** : leave-one-author-out du TF-IDF = 0,6185 (66 auteurs, 3 234 patients) ; à configuration égale, 2,2 à 2,4 points sous les plis par patient, 3 points au-dessus des plis de cinq groupes d'auteurs. Lecture : signature d'auteur d'environ 2 points ; le reste de l'écart des plis groupés est un rétrécissement de l'entraînement. Le déclencheur « écart supérieur à 3 points » se mesure désormais en leave-one-author-out sur le candidat final ; il n'est pas atteint pour le TF-IDF.
