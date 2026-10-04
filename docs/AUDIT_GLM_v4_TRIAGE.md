# Audit GLM v4 : triage et intégration au flux de travail

Source : `audit_GLM_v4.md` (04/10/2026, 8 axes, 40 corrections classées, 12 verdicts d'affirmations). Statuts : **fait** (preuve citée), **en file** (lot GPU ou CPU lancé), **planifié** (dans `tasks/FILE_DE_TRAVAIL_NUIT.md`), **adopté** (règle ou pratique intégrée), **dépassé** (la mesure de la nuit a changé le sujet), **écarté** (avec raison). Rien ici ne modifie le protocole gelé ; les décisions réservées restent à Cyril.

## Ce que GLM a vu juste, et ce que la mesure a ajouté
- **La défaite des LLM est une défaite de recette** (verdict n°1 « non établi », verdict n°2 « probablement vrai ») : confirmé et dépassé. CamemBERT-bio passe de 0,553 à 0,74 environ entre 6 et 10 époques ; le 0,7714 initial était un tirage favorable (rejeu 0,7362, graine 1001 0,7079). Le LoRA à 10 époques est en file (fiche hachée).
- **L'ordre des dépenses** (« ce que je ferais autrement n°2 ») : adopté dans le flux (références bon marché d'abord) et consigné en mémoire.
- **Relances qui masquent des échecs** (G3) : adopté, règle N25 au contrat de nuit.
- **Rejeu non déterministe** (G1) : adopté, déclaration de reproductibilité statistique dans le gabarit.
- **Erreur de GLM** : le plan « test de taille 31B à 2 époques, 4 h » n'avait pas de sens ; mesuré : 6 h projetées, arrêt anticipé par la règle de la fiche, remplacé par un test à recette mûre.

## Axe A (cible et métrique)
- A-c1 correction de priorité : **fait** (`prior-correction-fold0`) : conjecture de GLM (+2 à +8 points sur le 4B) non soutenue (+0,65) ; +13,8 points pour l'encodeur à 6 époques (même mécanisme que le saut de 6 à 10 époques) ; ≈ +1,0 à 10 époques.
- A-c2 F1 pondérée et micro-F1 à côté de la macro : **fait** (RESULTATS, glm_v3_cpu).
- A-c3 pondération × époques : **planifié** après le 4B à 10 époques (si le 4B rattrape l'encodeur).
- A-c4 score hiérarchique par bloc : **écarté** : les prédictions sont au niveau du chapitre ; l'analyse par familles a déjà montré que 96 % des erreurs traversent les familles.
- A-c5 gabarit : **fait** (`docs/GABARIT_RAPPORT.md`).

## Axe B (protocole de validation)
- B-c1 P1-19 cinq graines : **fait sur l'encodeur** (0,7293 ± 0,0256 ; étendue 6,4 points) ; non fait sur le LoRA (4,2 h le run).
- B-c2 RM-17 : **fait sur les graines de l'encodeur** : largeur moyenne 12,2 points contre 4,0, la règle échoue (EXPLORE).
- B-c3 leave-one-author-out : **en file** (`tfidf-loao`).
- B-c4 gabarit d'estimand : **fait**. B-c5 Brier de l'assistant : **fait** (`docs/CALIBRATION_PREDICTIONS_ASSISTANT.md` : Brier 0,23 sur 28 prédictions, à peine meilleur que 0,25).

## Axe C (réglage et équité)
- C-c1 sensibilité aux époques sur le 4B : **en file, plus fort que proposé** (10 époques au lieu de 4 et 6).
- C-c2 ADR si le gain est confirmé : **planifié** (ADR du second cycle ; Q20/Q21 déléguées).
- C-c3 planning de taux, C-c5 rang : **planifié**, après le 4B à 10 époques.
- C-c4 clause d'égalité de budget par famille dans les fiches : **adopté** (à inscrire dans chaque fiche à venir et dans l'ADR du second cycle).

## Axe D (modèles et ordre)
- D-c1 finir les variantes TF-IDF : **fait** (0,7202 avec caractères et poids équilibrés).
- D-c2 figer l'encodeur comme deuxième référence : **dépassé** : à 6 époques il n'est plus le bon plancher ; la référence-2 est la recette mûre (10 époques), à figer après les graines.
- D-c3 zero-shot du LLM : **écarté pour l'instant** (inférence seule peu informative tant que le LoRA mûr n'est pas mesuré).
- D-c4 clause de lecture du test de taille : **dépassé** (test annulé, remplacé).
- D-c5 pilote de distillation : **planifié, après RM-17**.

## Axe E (incertitude)
- E-c1 couverture par bloc CIM-10 : **écarté** (prédictions au niveau du chapitre) ; remplacé par la couverture par familles de chapitres, **planifié**.
- E-c2 table d'abstention par modèle : **fait** (RESULTATS ; les familles bien réglées ne se distinguent pas).
- E-c3 Wilson sur « la classe jamais couverte » : **fait** (c'est `AUTRE`, 0/18 [0 ; 0,176], exclue de la macro-F1). E-c4 réserve d'échangeabilité : **fait** (gabarit). E-c5 simulation sur plis réels : **planifié**.
- Ajout (issu de la mesure) : étalonner par plis d'auteurs donne 0,900 de couverture sous décalage ; intégré dans le service d'inférence du TF-IDF (`build_bundle.py`).

## Axe F (fuite et estimand)
- F-c1 leave-one-author-out : **fait** (0,6185 ; l'effet d'auteur pur vaut environ 2 points ; le reste de l'écart des plis groupés est un rétrécissement de l'entraînement). F-c2 sur le LLM : **planifié**. F-c3 déclencheur exécutable dans la fiche Q18 : **fait** (ADR-013 : écart patient/auteur du candidat final ; ajout du leave-one-author-out comme mesure). F-c4 patient et auteur côte à côte : **adopté**. F-c5 seuil de quasi-doublons : **fait** (9, 45, 171 paires, presque toutes du même auteur).

## Axe G (ingénierie)
- G-c1 déclaration de reproductibilité : **fait** (gabarit). G-c2 relances plafonnées et consignées : **adopté** (N25). G-c3 journaux dans le dépôt : **planifié** (copie des journaux de lot sous `results/logs/`). G-c4 deuxième rejeu : **écarté** (le rejeu de l'encodeur a déjà donné un deuxième point de bruit : 0,7714 → 0,7362). G-c5 rendu hebdomadaire des écarts : **planifié**.

## Axe H (efficience et plan minimal)
- H-c1 plan minimal viable : **adopté et mis à jour** (`tasks/FILE_DE_TRAVAIL_NUIT.md` : encodeur et TF-IDF d'abord ; LLM comparé à recette mûre ; professeur sous condition).
- H-c2 deuxième répétition générale du temps B : **planifié**. H-c3 sensibilité aux époques avant P1-20 : **fait en pratique** (P1-20 non gelé). H-c4 compteur de budget en CI : **fait** (`scripts/budget_alert.py` branché au contrôle complet, voir le Makefile). H-c5 structure du rapport : **fait** (gabarit, carte de modèle).

## Verdicts des 12 affirmations (réponse de l'assistant)
1. « Aucun LLM ne bat le TF-IDF » : retirée ; remplacée par « à 2 époques, oui ; à recette mûre, non mesuré ». 2 : confirmée pour l'encodeur ; LoRA à 10 époques en file. 3 : confirmée à 2 époques ; pondération × époques planifiée. 4 : acceptée (rareté des auteurs et sous-apprentissage de la queue). 5 : confirmée (moyenne simple) ; empilement appris non testé. 6 : **établie** (composition mesurée : le tercile court contient 48 % de chapitre II contre 18 % et 16 %) : la remarque de GLM (« non établi ») venait d'une lecture du cahier avant ce chiffre. 7 : confirmée (96 % hors famille). 8 : confirmée (état exact). 9 : acceptée, reformulée « le moins coûteux faute de distinction mesurable » ; l'ADR-014 le dit. 10 : dépassée. 11 : acceptée, conditionnelle. 12 : acceptée.

## Auto-critique : points ajoutés par GLM, acceptés
(a) Grille de criblage incomplète quand les conclusions ont circulé : accepté. (b) P1-19 non commencé alors que tout l'axe B en dépend : accepté, avec la nuance que les cinq graines de l'encodeur coûtent 20 minutes, ce qui change l'arbitrage ; elles tournent.
