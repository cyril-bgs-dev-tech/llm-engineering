# Revue indépendante (P5-10) : synthèse, actions et suites (06/10/2026)

**Nature de la revue, à dire sans l'enjoliver** : trois sous-agents locaux (code-reviewer, security-auditor, test-engineer), du même modèle que l'assistant qui a écrit le code, lecture seule, sans accès aux étiquettes du test scellé, sans envoi hors machine. L'indépendance de **code** et de **contexte** est réelle (aucun n'a vu mon raisonnement) ; l'indépendance de **personne** et de **modèle** n'existe pas : cette revue ne remplace pas une relecture humaine, qui reste à faire. Rapports : `CODE_REVIEWER_2026-10-06.md`, `SECURITY_AUDITOR_2026-10-06.md`, `TEST_ENGINEER_2026-10-06.md`.

## Ce que les rapports concluent
- **Code** : 0 bloquant, 6 importants, 11 mineurs ; les chiffres du test scellé passent par un chemin de calcul correct (bootstrap par blocs d'auteurs avec le même tirage pour les deux systèmes, appariement d'identifiants, aucune fuite du test vers le gel).
- **Sécurité et données** : 0 bloquant, 6 importants, 9 mineurs ; aucun secret ni donnée de patient réel dans le dépôt ni son historique ; ouverture du test scellé cohérente (marqueur, journal, empreintes, une seule ouverture).
- **Tests** : sur 132 mutations écrites à la main, 52 tuées par la suite, **72 survivantes**, 8 équivalentes ; **20 mutations sur 21 survivaient dans `final_report.py`, le module qui écrit le verdict publié** (final et référence inversés, δ publié à 0, calibration conforme sur le test…). La suite était verte sans être probante sur ce chemin. Le rapport ne dit pas qu'un défaut a touché G 0,8131 : il n'a recalculé aucun résultat.

## Actions faites le 06/10/2026
| Constat | Action | Preuve |
|---|---|---|
| 72 mutations survivantes (dont `final_report`, `conformal`, niveaux d'intervalle, `power_rule`, `sealed`) | 88 tests de durcissement adoptés depuis les esquisses du test-engineer (`tests/test_durcissement_*.py`) ; 12 défauts que les sondes avaient mis en évidence corrigés dans le code avec le test d'abord (puis le marqueur xfail retiré, car le plancher le refuse) | `make check` : 485 tests, couverture des lignes modifiées 100 % |
| Défauts réels prouvés par sondes | budget : durées NaN, infinies ou négatives ignorées ; bootstrap d'auteurs : au moins deux auteurs ; conforme : alpha dans ]0, 1[ et probabilités finies ; gel : au moins une graine d'encodeur et de LoRA ; fuite : textes identiques courts signalés ; permutation : vecteur vide refusé ; cache : entrée de mauvaise longueur recalculée | tests de durcissement |
| `sealed.py` consomme le test pour une erreur récupérable (identifiant absent, colonne absente, identifiants dupliqués détectés après le marqueur) | vérification de structure avant tout marqueur, sans lire de valeur d'étiquette | trois tests de durcissement |
| Précondition « répétition générale enregistrée » : un simple glob, satisfait par une répétition périmée | `freeze.rehearsal_matches_freeze` : la répétition doit porter l'empreinte du gel ; répétition refaite avec G (`20261006-220542-repetition-generale-temps-b`) | 3 tests |
| `run_guarded.sh` ne tue que le premier processus : les petits-fils survivent | commande lancée dans son propre groupe, arrêt du groupe ; test discriminant (rouge d'abord : il avait d'abord passé à tort, car le tube capturé retenait le retour) | `tests/test_run_guarded.py` |
| `cold_rebuild.sh` : `rm -rf` sur un argument non contrôlé | nom de dossier imposé (`llmft-cold*` ou `cold*`) | essai d'un chemin refusé |
| MorFITT sans manifeste, révision, fiche ni contrat | `data/scripts/download_morfitt.py`, manifeste (identique octet pour octet à un téléchargement propre de la révision épinglée), fiche (licence : trois déclarations divergentes, la plus restrictive retenue), contrat de tâche | `data/cards/morfitt.md` |
| ADR-016 : hypothèse « tous les textes, test compris, finissent par un saut de ligne » ; Q24 « aucun run passé n'est touché » | erratum daté (l'ADR est figée) ; mesure de 16 passes non épinglées : 16 identiques, 0 plantage ; saut de ligne vérifié sur 3 586 textes de développement, pas sur le test | `ADR-016-erratum-2026-10-06.md` |

## Constats non corrigés, et pourquoi
- **Garde du test scellé contournable par un appel volontaire** (marqueur supprimable, `rehearsal=True` sur la vraie partition, étiquettes déductibles du parquet brut) : la protection est procédurale ; la rendre technique change le protocole gelé. Déclaré, pas corrigé.
- **`full_frame()` lit les étiquettes avant l'écriture du marqueur** dans le script d'ouverture : aucune fuite effective constatée ; à restructurer au prochain cycle.
- **Cache de tokenisation en pickle**, clé sans empreinte des fichiers du tokenizer : risque d'exécution faible (écriture dans le projet requise), risque d'intégrité moyen ; passage à un format sans pickle et empreinte du tokenizer dans la clé : à faire.
- **Mineurs** (`bash -c` avec variables interpolées, images non figées, `revision` absente sur les modèles Hugging Face, `FICHE_DE_DONNEES_PARHAF.md` disant « jamais lu » : à mettre à jour, textes sous licence dans `knowledge/raw` : à vérifier) : listés dans les rapports, non traités ce soir.
- **Cause du plantage du tokenizer** : le taux de 25 plantages sur 31 du 05/10 ne se reproduit pas (0 sur 18 le 06/10) ; l'explication par une course entre threads reste une piste.
