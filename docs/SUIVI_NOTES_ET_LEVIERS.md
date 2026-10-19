# Suivi des notes par composante et des leviers

Page de synthèse du 05/10/2026 (soir). Elle ne crée aucune règle et aucun résultat : elle croise quatre documents et dit où en est chaque levier. En cas de désaccord, les sources font foi.

Sources : `docs/CHAINE_DE_DOMINOS.md` (notes, plafonds, dominos), `roadmap_unifié.md` section 4.1 et tableaux d'étapes (statuts), `docs/AUDIT_GLM_v3_TRIAGE.md` (80 actions, 10 par composante), `docs/AUDIT_GLM_v6_TRIAGE.md` et `audit_GLM_v6.md` section 7 (30 leviers, obsolescence), `docs/presentation/PREUVES.md` (notes et preuves).

**Statut des chiffres** : les notes sont des estimations de l'assistante à plus ou moins 1 point, pas des scorecards. Un chiffre sans `run_id` dans cette page renvoie à la source citée ; ce qui n'a pas de run au registre est dit.

## 1. Composantes : note, plafond, état

Moyenne estimée : **8,25 sur 10** (66 sur 8 composantes ; réévaluation du 17/10 : efficience 7 vers 8 ; réévaluation du 07/10 : efficience 6 vers 7 ; réévaluations du 06/10 : efficience 5 vers 6, puis après l'ouverture du test scellé performance 6 vers 7, rigueur 8 vers 9, incertitude 7 vers 8 ; raisons de chaque note dans `docs/presentation/PREUVES.md`, dernier paragraphe). Estimation à ±1, pas une scorecard.

**Réévaluation du 17/10/2026 (N32), aucune note ne change** : (1) *efficience* reste à 7 : la cascade E puis G est retenue par sa fiche (cascade moins G −0,10 [−0,23 ; +0,02], 82,3 % des patients sans le LoRA, run `20261017-012416-cascade-e-puis-g`), mais sa latence de 39,6 ms est **modélisée** ; la note ne bougera qu'avec la latence mesurée du service HTTP de G avec la cascade (suite de RM-60) ; (2) *reproductibilité* reste à 9 et *robustesse* à 7 : la vérification après le BIOS donne « toujours instable » (10 pannes sur 46 avant comme après, runs `20261016-230229-verification-machine-bios-avant`, `20261017-012310-verification-machine-bios-apres`) ; les preuves de ces notes (reconstruction à froid identique à 1e-9, double calcul des chiffres courts) ne sont pas touchées, mais aucun calcul long publié ne peut être ajouté tant que Q26 n'est pas traitée (RM-61, RM-62 bloquées) ; (3) *honnêteté* reste à 9 : deux résultats publiés, dont un négatif, avec leurs prédictions notées.

**Réévaluation du 17/10/2026, après la mesure du service (N32)** : *efficience 7 → 8* : la latence de la cascade n'est plus seulement modélisée ; le service HTTP de G en cascade donne une latence moyenne attendue de 38,4 ms (chemins mesurés par HTTP, part hors pli), contre 97,4 ms pour G complet dans le même service (run `20261017-015754-service-g-cascade`, `docs/presentation/PREUVES.md` ligne 68) ; pas 9 (énergie de la cascade, image GPU, charge prolongée non faites). **Moyenne estimée : 66 sur 8 = 8,25.**

**Réévaluation du 17/10/2026, après RM-61 (N32) : performance maintenue à 8**, comme écrit d'avance : G gelé transposé sur MorFITT est « dans la bande » du meilleur chiffre publié (72,30 [70,15 ; 74,35] contre 71,95, run `20261017-113948-morfitt-g-gele`) ; le plafond de 9 n'est pas atteint (moyenne 8,25).

**Réévaluation du 17/10/2026, après P5-08 et P5-11 (N32) : aucune note ne change** (moyenne 8,25) : surveillance de dérive mesurée et branchée, échantillon étiqueté dimensionné, démo locale (`docs/presentation/PREUVES.md`, lignes 70 à 72) ; l'efficience reste à 8 tant que l'image GPU (Q27) et la charge prolongée (fiche hachée, après le lot RM-61 puis RM-62) manquent.

| Composante | Note | Plafond réaliste | Ce qui a monté ou peut monter la note | État au 05/10 soir |
|---|---|---|---|---|
| Performance | **8** (était 6) | 8 (9 si un chiffre publié est dépassé) | LoRA regroupé 0,7673 ; système final G à 0,7799 en développement ; ouverture unique du test scellé ; ancrage MorFITT | G figé comme candidat, LoRA final en cours d'entraînement, test scellé non ouvert |
| Rigueur | **9** (était 8) | 10 | protocole v2 accepté (RM-37, 05/10) ; gel RM-50 ; RM-20 ; revue indépendante P5-10 | gel exécuté le 06/10 (ADR-016, prédiction chiffrée hachée) ; test scellé non ouvert, préconditions remplies |
| Données et anti-fuite | **8** (était 7) | 9 | audit d'étiquettes (P2-06) ; synthétique avec lignée (P2-10) ; ancrage public | audit fait sur 65 erreurs confiantes : ambiguïté de codage établie, bruit d'étiquette non établi ; contre-expertise par un codeur à prévoir ; P2-10 planifié |
| Incertitude | **8** (était 7) | 9 | couverture par famille (RM-33) ; lecture confirmatoire (RM-51) ; nouveaux auteurs (RM-39) | G : ECE 0,016, couverture 0,901 par famille (source : journal de nuit, 05/10 15h12Z) ; RM-51 après RM-20 |
| Erreurs et robustesse | **7** (était 6) | 9 | taxonomie, audit des 65 cas, RM-39 sur les modèles appris | TF-IDF couvert ; robustesse de l'encodeur et du LoRA à mesurer (RM-39) |
| Reproductibilité | **9** (était 8) | 10 | reconstruction à froid (P5-09), release taguée, conteneur vérifié | reconstruction à froid jamais testée sur clone neuf ; release bloquée (push réservé à Cyril) |
| Efficience et déploiement | **8** (était 7, réévaluée le 17/10) | 9 | service mesuré par profil, cascade validée hors pli, fiche de déploiement | cascade conforme : non-infériorité, 45,5 % sans LoRA ; fiche RM-48 provisoire ; élagage RM-45 fait : dégradé (−13,1 points), non retenu |
| Honnêteté et conformité | **9** (était 8) | 10 | `claim-gate` sur tout texte sortant, résultats négatifs publiés, carte de modèle, TRIPOD-LLM | résultats négatifs consignés (RM-55, RM-56, empilement, RM-44, RM-45) ; carte v4 du candidat G écrite (06/10), checklist TRIPOD-LLM à rejouer au gel ; P5-12 à faire |

## 2. Ce qui devait rendre le reste obsolète, plus simple ou inutile

Source : `audit_GLM_v6.md` section 7. La colonne « Verdict mesuré » dit ce qui s'est réellement passé.

| Hypothèse de départ | Verdict mesuré | Effet sur le plan |
|---|---|---|
| Le bootstrap par blocs d'auteurs requalifie les intervalles | Confirmé : règle v2 atteinte à 95 % (largeur 3,39), pas à 98,33 % (4,24) | une seule question primaire à 95 % (RM-29) |
| La distillation vers l'encodeur rendrait le LoRA inutile à servir | **Réfuté** : gain non préservé (−0,77 [−2,46 ; +0,96]), fuite de second ordre significative (RM-56) | C1 et C2 sortent de la liste fermée ; le LoRA reste dans G |
| L'empilement appris remplace le mélange 50/50 | **Réfuté** : +0,41 [−0,25 ; +1,13], non résolu ; la régression logistique surajuste | le 50/50 reste ; la trajectoire vers 0,78 à 0,79 est abaissée |
| La cascade rend le LoRA inutile pour 77 à 79 % des patients | **Partiel** : non-infériorité tenue ; 93 % sans LoRA avec le seuil de confiance, 45,5 % avec le routage conforme | l'économie de 50 % par routage conforme n'est pas atteinte |
| Le zéro-shot relativise l'affinage | Confirmé : 4B 0,4929, 9B 0,4725 | l'affinage apporte environ +28,8 points |
| L'audit d'étiquettes rendrait obsolète l'explication par la capacité | **Non établi** : ambiguïté de codage oui, bruit d'étiquette non | le plafond d'ambiguïté reste une hypothèse |
| Mondrian par défaut simplifie l'abstention | Fait à cinq plis ; à rejouer avec le LoRA (RM-33) | une politique au lieu de quatre tables |
| INT8 de l'encodeur inutile | **Partiel, négatif** : ONNX 32 bits identique (0,7362, latence p50 +8 %) ; INT8 statique min-max effondré à 0,0227 et plus lent (+39 %) ; les variantes par centiles n'ont pas pu être mesurées (calibration de 128 textes : plus de 40 Go de RAM, coupée par `mem_guard.sh`), run `20261006-091535-onnx-int8-statique-partiel-camembert-deploy-ep10-lr1e-4` (statut `aborted`) | la voie INT8 statique n'est pas retenue en l'état ; le service de l'encodeur reste sur GPU (règle de décision de la fiche) |
| Vote de six modèles, hiérarchie comme supervision | Mesurés sans gain ou en échec | écartés |

Reste indispensable quoi qu'il arrive : registre en ajout seul, fiches hachées, test scellé ouvert une seule fois, bootstrap hiérarchique apparié, carte de modèle et gabarit de rapport.

## 3. Les 80 actions de l'audit v3 (10 par composante)

Décompte approximatif tiré des lignes du triage (52 faites, 8 planifiées, 2 en file, 2 en cours, 1 bloquée, 3 écartées). Les non faites utiles :

- Planifiées : taux 2e-5 et 5e-5 du criblage (A2, A3), rang LoRA (A9), ensemble TF-IDF avec LLM (A10), perturbations sur le 9B (C5 A5), empreinte d'adaptateur au registre (C6 A4), `make test-gpu` (C6 A9), vLLM, débit à 4 096 tokens, quantification, latence (C7).
- Bloquée : release sur tag (C6 A6), qui exige un push décidé par Cyril.
- Écartées : ablation de troncature, cache mypy, bucketing et chargement des professeurs.

## 4. Les 30 leviers de l'audit v6

Faits : 1, 2, 3 (reste la contre-expertise), 4 (réfuté), 5 (cinq plis), 6, 7 (inclus dans le gel RM-50), 9, 10 (écarté après correction), 11, 15 (sans gain). Écartés : 12, 19, 20, 26 (le 24, poursuite du LoRA depuis un point de sauvegarde, est écarté au profit de P1-16). Planifiés : 8 (P2-10), 13 (RM-53), 14 (RM-54), 16, 17, 25 (RM-55, fait : aucun des trois ne gagne), 18 (P4-03), 22 (RM-31), 23 (P1-14), P1-16 pour les époques, 29 (RM-45), 30 (P4-01, après le test scellé). À décider après les cinq plis : 21 (graines du LoRA). En file : 28 (RM-34). Levier 27 (protocole v2) : accepté.

## 5. Séquence restante (RM-20 fait le 06/10 : G 0,8131, +7,28 [+1,55 ; +12,62], non résolu à δ = 2,0)

1. LoRA final, graine 1000 (relancé le 05/10 à 21h59Z, tokenisation passée, entraînement en cours).
2. Temps A du LoRA (prédictions sur les textes du test, sans étiquette).
3. RM-50 : **fait le 06/10/2026** (ADR-016, `results/frozen_final.json`, prédiction chiffrée hachée, répétition générale, `check` vert). Valeurs de départ du brouillon : macro-F1 du test scellé centrée sur 0,78 (intervalle à 80 % de plus ou moins 3,0), probabilité d'un « gain confirmé » à δ = 2,0 d'environ 0,47.
4. `sealed_evaluation.py check`, puis RM-20 (ouverture unique) et RM-51.
5. RM-49 (MorFITT), après RM-20 pour ne pas influencer le choix du candidat.
6. RM-21 (porte go/no-go), P4-04 à P4-10 (calibration, conforme, abstention, carte de modèle), RM-35 et RM-48.
7. P5-09 (reconstruction à froid), P5-12 (rapport via `claim-gate`), P5-10 (revue indépendante).

Réserve déclarée : un seul LoRA final entraîné (variance entre graines non mesurée) ; si G contre E ou F était rapporté, il serait « non résolu » (écart de développement de +0,78 à E).

## 6. Décisions et actes qui appartiennent à Cyril

- Release taguée et tout push, création de dépôt distant ou changement de visibilité (règle Git du projet).
- Toute location de GPU ou API payante (déclencheurs de la section 5.2 du plan, plafond de dépense validé).
- Envoi de contenu à Codex ou Gemini (`wiki-audit strong`, revue croisée) : demander à chaque fois.
- Contre-expertise de l'audit d'étiquettes par un codeur.

## 7. Incident du 05/10 : plantages du lot LoRA

- **Constat** : le LoRA final a échoué plus de dix fois de suite par un plantage du tokenizer Rust (`tokenizers` 0.23.2, tokenizer de Qwen3.5-4B), 25 fois sur 31 runs sans épinglage sur les 3 586 textes, à un indice différent à chaque fois (run `20261005-224632-tokenizers-course-threads-qwen35`, diagnostic exploratoire).
- **Écarté par mesure** : la mémoire (RAM jamais sous 61,8 Go disponibles sur 559 mesures, quatre passes de 4 Gio sans écart), le disque Windows (copie ext4 identique), un cœur défectueux (64 runs épinglés, un par cœur logique, aucun échec), un texte précis.
- **Piste** : course entre threads du processus ; aucun échec sur 78 runs épinglés sur un cœur dès le lancement, contre 8 échecs sur 34 avec un épinglage partiel ou tardif.
- **Correctif** : `build_inputs` délègue la tokenisation à un sous-processus épinglé, relancé jusqu'à 6 fois (`src/llmft/tokenizer_guard.py`, `tokenizer_child.py`, `tests/test_tokenizer_guard.py`). C'est un contournement ; le défaut reste en amont, dans `tokenizers`.
- **Statut** : mesures au registre (run ci-dessus) ; le correctif est un contournement validé par 6 tests et par un LoRA final dont la tokenisation est passée du premier coup.
- **Plantages de WSL** : cause non prouvée, aucune trace dans le noyau, mais une piste forte : la calibration par centiles de RM-44 monte à plus de 40 Go de RAM résidente et fait tomber la mémoire disponible de 29,8 à 17,6 Go en moins d'une minute (journal `results/logs/memoire.log`, ligne `GARDE` de 09:15:12Z). Le plantage précédent a eu lieu pendant ce job. Surveillance en place (`scripts/mem_watch.sh`, `results/logs/memoire.log`, aucune alerte à ce jour).
- **Lot d'élagage (RM-45)** : il a démarré par erreur sur un faux `TERMINE42` (le temps A du LoRA avait échoué faute d'adaptateur) puis a été arrêté à la main. Ses trois premiers runs sont sortis en code 2 en moins de 30 secondes, sans sortie conservée et sans run au registre. Cause non diagnostiquée : à élucider avant toute relance (`results/logs/lots/encodeur_elague.log`).
- **Test scellé** : trois lignes « inputs » (633 identifiants, textes sans étiquettes) se sont ajoutées à `data/splits/sealed_access.log` les 05/10 à 20h45, 20h47 et 21h33Z, à cause des relances du temps A du LoRA sur un adaptateur absent. Aucune ouverture d'étiquettes. Le journal compte désormais 13 entrées « inputs » et non 10 comme dit dans la ligne 47 de `docs/presentation/PREUVES.md`, à rectifier.

**Réévaluation du 07/10 (matin, estimation, ±1 ; raison de ne pas changer la note, N32)** : **Analyse d'erreurs et robustesse reste à 7.** Preuve nouvelle : LoRA entraîné avec fin de texte aléatoire, verdict de la fiche « corrigé » au pli 0 (macro-F1 0,794 à 10 % de fin retirée contre 0,1436 ; `PREUVES.md` ligne 59). Elle ne suffit pas à monter la note : une graine, un pli, aucun intervalle ; la variante n'est pas dans le système gelé G, dont le LoRA reste fragile ; la perte logarithmique de la variante est plus élevée (0,99 contre 0,82) ; le LoRA n'a toujours pas été mesuré sur de nouveaux auteurs. Passage à 8 si la variante est répliquée sur une seconde graine ou en plis d'auteurs et que sa calibration est mesurée.

**Réévaluation du 07/10 (matin, estimation, ±1)** : **Efficience et déploiement 6 → 7** : G mesuré d'un seul tenant (p50 91,6 ms, 10,3 Gio, 10,5 Wh ; `PREUVES.md` ligne 61), fiche de déploiement finale et frontière coût-qualité (ligne 62), image de service du TF-IDF construite, durcie et testée (ligne 63). Pas 8 : compression jamais réussie, G servi par un banc seulement, démarrage à froid de 153 s, file sous quatre clients (p95 0,8 s). Passage à 8 : service HTTP de G dans une image GPU, charge prolongée, et un gain de compression ou de cascade qui batte E.
