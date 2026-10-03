# Fiche préenregistrée : raccourci d'auteur sur la référence TF-IDF (RM-14)

- **question** : la macro-F1 hors pli du TF-IDF avec régression logistique sur `parhaf_cim10_chapter` est-elle gonflée par la fuite d'auteur, c'est-à-dire plus haute avec des plis par patient qu'avec des plis groupés par auteur ?
- **référence** : run P1-06 (`p1-06-tfidf-chapter`), plis par patient (clé `folds`), même fiche de modèle et de grille que `experiments/2026-10-03-p1-04-06-tfidf.md` (empreinte dans `experiments/INDEX.md`).
- **variante** : seul changement, les plis de contrôle groupés par auteur (clé `control_folds_by_author`, `StratifiedGroupKFold`), mêmes patients, même grille, même règle de réglage.
- **jeux et découpage** : développement seulement ; le test scellé n'est jamais lu ; empreinte des partitions : `data/splits/parhaf_cim10_chapter.sha256`.
- **métrique principale** : écart Δ = macro-F1(plis par patient) − macro-F1(plis par auteur) sur les prédictions hors pli regroupées, 17 chapitres. Intervalle à 95 % par bootstrap apparié (mêmes patients tirés pour les deux schémas, stratifié par chapitre, 2 000 tirages, PCG64 graine 20261003). **Secondaires** : log loss, exactitude, les deux macro-F1 séparément.
- **critère de décision** (calqué sur le seuil de PROTOCOLE section 3, écrit avant tout run) : « raccourci signalé » si Δ ≥ 0,03 et borne basse de l'IC 95 % strictement positive ; « non signalé » si la borne haute est strictement sous 0,03 ; sinon « non résolu ». Raccourci signalé ⇒ ADR et plis groupés par auteur comme métrique principale (règle de la section 3), décision à Cyril.
- **budget** : CPU seulement, au plus 1 h ; 1 run au registre plus le verdict apparié.
- **prédiction** : Δ compris entre −0,03 et +0,03 (probabilité 0,8), cohérent avec le raccourci mesuré en P0-30 (−0,86 point, non signalé).
