# Journal de nuit 2026-10-02 (UTC) : contrat et journal

Demande de Cyril, 2026-10-02T23:28Z : « et continues d'avancer cette nuit moi je vais me coucher donc tu dois définir un contrat de travail suffisant pour avancer sans moi en faisant les choix les plus adaptés et intelligent pour évoluer pendant une douzaine d'heures ». Contrat appliqué : `tasks/CONTRAT_NUIT.md`. HEAD au départ : 314fc71 (trois commits du lot en attente encore en cours à l'ouverture). Fenêtre visée : 2026-10-02T23:28Z → environ 11 h 30 UTC le 2026-10-03 (12 h). Heures lues par `date -u` (N7).

## Résumé pour Cyril, nuit du 03 au 04/10/2026 (mis à jour à 07 h 25 UTC, la nuit continue)
- **Résultat central** : la recette gelée (4 taux, 2 époques) sous-estimait fortement les modèles appris. À recette mûre : CamemBERT-bio à 10 époques = 0,7293 ± 0,0256 (pli 0, 5 graines), 0,7475 (pli 1) ; TF-IDF caractères + poids équilibrés = 0,7202 (5 plis, +3,65 point résolu contre la référence v1). L'encodeur moyenné bat le meilleur TF-IDF de +1,5 (pli 0, non résolu) et +6,4 (pli 1) ; l'ensemble avec le TF-IDF n'apporte rien sur l'encodeur moyenné. Le premier tirage flatteur (0,7714) était un tirage favorable : je l'avais annoncé trop tôt.
- **LLM** : Qwen3.5-4B à 2 époques = 0,587 ; **à 10 époques = 0,7795 (pli 0, une graine) : +6,4 [+2,0 ; +11,4] contre le meilleur TF-IDF, +4,9 [−0,35 ; +10,5] contre l'encodeur moyenné ; confirmation au pli 1 lancée à 07 h 19 UTC (fin vers 10 h 50 UTC)** ; le test de taille 31B à 2 époques a été annulé (projeté 6 h), remplacé.
- **Puissance** : règle RM-17 sur les 5 graines de l'encodeur : largeur 12,2 points contre 4,0 : échec, le cycle reste EXPLORE.
- **Données** : 5 plus petits chapitres = 85 % de la variance de la macro-F1 ; écart patient/auteur 5,06 points sur partitions répétées, signature d'auteur pure ≈ 2 points (leave-one-author-out 0,6185).
- **Déploiement** : service TF-IDF 20 Mo, p50 1,9 ms ; encodeur 443 Mo, 190 ms ; INT8 dynamique naïf : effondrement.
- **Livrables prêts, rien envoyé** : `docs/BRIEF_GLM_v5_audit_second_cycle.md` (à compléter avec le résultat du 4B), `docs/RAPPORT_PREMIER_CYCLE.md`, ADR-014 (élève 4B), ADR-015 (second cycle, proposée), carte de modèle, `docs/CALIBRATION_PREDICTIONS_ASSISTANT.md` (Brier 0,231), triages des audits GLM v3 et v4, surveilleur de silence (`tasks/SURVEILLEUR_SILENCE.md`, cron de session).
- **Erreurs de ma part cette nuit** : conclusions sur un seul tirage ; bug du code de sortie (`$(date)` remet `$?` à zéro) deux fois ; `find /` hors périmètre (signalé) ; pré-vol qui n'avait pas exercé le chemin complet (tête sur CPU, 28 minutes perdues) ; criblage LLM avant les références bon marché réglées.
- **À décider par toi** : promouvoir ou non des recettes plus longues en référence (ADR-015, Q20, Q21) ; changer δ ou les plis du second cycle ; poursuivre la distillation (RM-17 provisoire) ; envoyer les cahiers GLM v5 ; push des commits locaux (non fait).

## Ancien résumé (rempli à 11 h 36 UTC le 2026-10-03)
- **Fait et commité (local, rien poussé)** : protocole gelé P0-46 et G-P0 franchie ; P1-01 (harnais d'évaluation), P1-02 (comparaison appariée + couverture simulée de l'intervalle hiérarchique), P1-03 (bornes sans modèle : macro-F1 chapitre au plancher ≈ 0,06). HEAD `74fc3f0`. Détails : entrées horodatées ci-dessous.
- **Constat majeur** : à δ = 2,0 le premier cycle ne tranchera presque jamais (gain confirmé simulé 2,3 % à 2δ) ; décision C1 : EXPLORE, δ inchangé. Voir `project-risque-puissance-delta` et `experiments/ERRATA-PROTOCOLE.md`.
- **Non fait, faute de temps** : unification mathématique de la métrique (`scripts/spikes/metric_widths.py` écrit, non lancé, non commité ; Q15 reste ouverte), P1-04/P1-06 (TF-IDF), RM-14, P1-19 code, `sealed.py` à deux temps, P0-09 vLLM, ingestions wiki R-j/R-k (dont sliding-window). Aucun run GPU comparatif lancé : aucune fiche préenregistrée n'existait.
- **Erreurs de ma part** : brief GLM défaillant, skills chargés tard, test écrit après le code pour `frozen.py`, esquisse de puissance v1 à effectifs proportionnels (refaite). Corrigées, tracées.
- **Ressources** : GPU 1 497 MiB occupés par un processus étranger (laissé en place) ; B consommé inchangé (~1,5 %).
- **À décider par toi** : Q15, Q10, Q1, Q3, Q4, Q6, Q7, Q8 ; push des commits locaux ; adoption fla ; suppression des poids Gemma-4-31B (58 Go).

## Délégations en vigueur (réponses de Cyril, 2026-10-02T23:28Z)
- **Commits** : « Commits locaux, pas de push (Recommandé) » : lots thématiques, chemins nommés, après un `make check` vert ; **aucun push, aucun tag, aucune création de dépôt**.
- **Porte G-P0** : « Oui, si les planchers sont atteints (Recommandé) » : j'écris le scorecard ; si `check_scorecards` est vert et que **chaque plancher est atteint avec une preuve honnête**, je commence P1 sur CPU ; sinon arrêt à la porte, plan de rattrapage, réserve.
- **GPU** : réponse initiale « Non, pas de GPU cette nuit », **remplacée à 2026-10-02T23:29Z par Cyril** : « mais utilises le gpu si tu as besoin c'est plutôt recommandé par contre évidemment la métrique d'optimisation doit être correctement pensée ». **GPU délégué**, dans ces bornes : B = 90 h (alerte à 80 %), fiche préenregistrée hachée **avant** tout run comparatif (`experiment-preregistration`), `vram-preflight` et répétition à blanc (N8), délai d'inaction de 20 min et plafond dur de 30 Gio (N12), Ollama et tout processus étranger laissés en place, aucun téléchargement de données de patient, aucun modèle gated, aucune location, jamais le test scellé.
- **Consigne générale** (sa demande ci-dessus) : « les choix les plus adaptés et intelligents ». Acceptée **dans les bornes du contrat** : décisions de méthode et de conception rencontrées dans le périmètre, chacune inscrite ici (`Mnn`) avec ses faits et sa raison ; elle ne couvre **aucun** interdit de la section 3 (test scellé, protocole gelé, push, envoi hors machine dont GLM, location, lecture hors dossier, décision de la section 10 du plan).

## Ressources au départ
- GPU : 2 364 MiB occupés, aucun processus à moi (Ollama ou autre processus de Cyril ; **signalé, laissé en place**). Disque `/mnt/d` : 85 Go libres. B consommé : environ 1,5 % (0,9 h de runs finaux et 0,43 h perdues).

## File ordonnée (chaque élément commité avant le suivant, `make check` vert avant ; verrou nommé quand sauté)
1. **Fin du lot en cours** : attendre la fin des commits lancés avant l'ouverture, vérifier HEAD, arbre propre, `make check` vert.
2. **Scorecard G-P0** (`scorecards/G-P0.md`) : Q1 à Q12, une preuve immuable par note, notes sans gonfler ; plan de rattrapage sous plancher.
3. **Franchissement de G-P0** si les planchers sont atteints ; sinon verrou « plancher non atteint » nommé.
4. **P1-01** harnais d'évaluation (`AUTRE` verrouillé par test) ; **P1-02** outils de comparaison appariée (+ couverture simulée, mutation) ; **P1-03** bornes ; **P1-04 et P1-06** TF-IDF (CPU) ; **RM-14** raccourcis. Verrou : G-P0.
5. **P1-19, partie code** (registre étendu, prédictions par patient hachées) ; **`sealed.py` à deux temps** avec répétition générale du temps B (`leakage-guard`, TDD, `ALLOWED` arrêté sans affaiblir le garde).
6. **Réserve perpétuelle** (`CONTRAT_NUIT.md` section 6, R-a à R-h) dès que la file est vide.

**Verrous connus** : GPU : levé par Cyril, mais P1-07, P1-11 et RM-16 restent verrouillés par **G-P0** et par leur fiche préenregistrée ; test scellé ; push ; envoi à GLM (réponse de GLM absente du dépôt, Q10) ; RM-18 (A2, A3 : texte absent) ; MedGemma ; toute décision de la section 10 du plan.

## Conditions d'arrêt
Arrêt seulement si tous les éléments (file et réserve) sont faits ou verrouillés, ou si la fenêtre est écoulée ; avant : `make check` vert ou écart nommé, résumé en tête, mémoire à jour, état GPU et disque consigné.

## Journal
- 2026-10-02T23:28Z ouverture du journal ; délégations reçues ; aucun processus GPU à moi.
- 2026-10-02T23:29Z **Délégation GPU reçue** (citée ci-dessus). **Décision de méthode M1 : la métrique d'optimisation.** Faits : le protocole gelé fixe la **sélection** (taux d'apprentissage, élève) par la **macro-F1 sur 17 chapitres au pli 0, une graine**, et fige époques (2), grille (4 taux), graines ; je ne peux rien y changer. Ce que je peux et dois penser, sans toucher au gel : (1) **objectif d'entraînement** = entropie croisée standard, **sans pondération de classes** (une pondération est un levier à tester comme tel, pas un choix silencieux) ; (2) **sélection** = macro-F1 (protocole), avec **log loss, exactitude et F1 par classe publiées à côté** pour repérer un choix dû au bruit : à 717 patients et des chapitres de 5 à 6 patients au pli, un écart de macro-F1 inférieur à la largeur d'intervalle attendue n'est **pas** lu comme une supériorité (le critère « maximum de 4 tirages bruités » est dit dans le rapport) ; (3) **jamais le test scellé** pour choisir ; (4) pour les **mesures d'efficience** (P0-09, P0-10, débits), la métrique est le **débit et la latence p50 et p95 à sortie égale** (prédictions identiques à la référence Transformers), pas la qualité ; (5) tout run **préenregistre sa métrique et son critère d'arrêt avant le premier pas**. Raison : une métrique d'optimisation mal pensée ferait du GPU un générateur de gagnants apparents.
- 2026-10-02T23:29Z **Plan GPU, dans l'ordre** : (a) **P0-09 et P0-10 ré-ouverts comme spikes** (hors chemin court, mais ils donnent la preuve de Q9 et Q8 dont le plancher de G-P0 est 1) : latence p50 et p95 sur 100 requêtes, Transformers contre vLLM si l'installation isolée est possible sans toucher à l'environnement validé ; (b) **après G-P0 et P1-01** : encodeur P1-07 (4 taux, une graine) puis criblage P1-11 des trois élèves (ADR-009) ; (c) rien d'autre sans fiche.

- 2026-10-02T23:32Z Question de Cyril « quelle est la meilleure métrique sur ce type de tâche ? » : réponse donnée en séance (entropie croisée pour entraîner ; log loss appariée pour comparer, variance plus faible attendue mais non mesurée ; macro-F1 pour la tâche réelle ; top-3 et conforme pour l'aide au codage ; ECE pour la fiabilité). **Décision laissée à Cyril** (Q15) : le protocole gelé garde la macro-F1 primaire ; la log loss est publiée en secondaire dans tous les runs. Aucune modification du gel.
- 2026-10-02T23:32Z Lancement du spike P0-09, baseline Transformers (Qwen3.5-4B, 100 requêtes synthétiques, 3 passes), délai 20 min, plafond 30 Gio ; GPU de Cyril (2,3 Go, Ollama pid 204) laissé en place. Observé : `artifacts/hf_cache` contient aussi `models--google--medgemma-4b-it` ; **non utilisé** (ADR-001, Q6).
- 2026-10-02T23:36Z P0-09 baseline Transformers terminée (rc 0) et enregistrée : p50 117 ms, p95 288-296 ms, 9,4-9,7 k tok/s ; pic 15,45 Gio ; **constat** : Qwen3.5 passe en repli PyTorch pour `causal_conv1d` et `chunk_gated_delta_rule` (flash-linear-attention absent) : les débits de P0-06 et P0-08 (donc le budget P0-45) sont probablement **conservateurs** pour les Qwen ; à tester sans toucher à `.venv` (installation `--target`).
- 2026-10-02T23:37Z Question de Cyril « une métrique composite qui se rapproche de notre besoin, excellence scientifique, papiers récents ? ». Recherche web (résumés, **non lus en entier**, donc revendications selon N14) : Edin et al. 2023 (arXiv 2304.10909, macro-F1 faussée par les codes absents), MCC multiclasse avec inférence (arXiv 2503.06450, 2025), scoring hiérarchique (arXiv 2508.04489, 2025 ; Cao et al., AISTATS 2024 ; CoPHE 2109.04853). Réponse donnée : profil de métriques plus un scalaire à poids écrits d'avance ; candidat : **log loss moyennée par chapitre** (proposition de l'auteur, variance non mesurée). **Ajouté à la réserve** : (R-i) simulation de la largeur d'intervalle de la macro-F1, de la log loss moyennée par chapitre et du MCC avec un modèle de probabilités (registre) ; (R-j) ingestion wiki des trois papiers (relecture à la source, N14). Décision de métrique : **Cyril (Q15)**, rien ne change au gel.
- 2026-10-02T23:49Z Mémoire du projet mise à jour sur demande de Cyril (13 fichiers : état courant, gel, puissance, réflexions de métrique, échanges, leçons de méthode, sources, pièges, mode nuit). Cyril confirme : « je te laisse travailler en mode je vais me coucher ».
- 2026-10-02T23:50Z Recommandation de Cyril : vérifier « Sliding-window beats linear attention ». Repéré par recherche (résumés, **non lu en entier**, N14) : arXiv 2608.28444 (Jolicoeur-Martineau, Sukthanker, Cameron, Gervais ; 28/08/2026) ; thèse : l'attention à fenêtre glissante **avec sinks** égale ou dépasse des modèles à attention linéaire **post-entraînés** (linéarisés), sans post-entraînement, et fait 2 à 10 fois mieux sur des tâches de long contexte (aiguille dans une botte de foin, BABILong). **Pertinence provisoire pour nous, à confirmer par la lecture** : (i) nos entrées font au plus 4 096 tokens (moyenne ~1 300) : le long contexte n'est pas notre goulot ; (ii) Qwen3.5 est un modèle **hybride natif** (réseau delta à porte plus attention complète), pas une linéarisation post-entraînée : le résultat ne s'applique pas directement ; (iii) piste éventuelle : coût d'inférence ou de mémoire à 4 096 tokens, et le repli lent de `chunk_gated_delta_rule` que je mesure ; changer l'architecture d'un élève est hors périmètre du premier cycle. **Ajouté à la réserve (R-k)** : ingestion wiki et note de pertinence chiffrée (relire à la source avant toute conclusion).
- 2026-10-02T23:52Z **P0-09, tentative 2 valide** (fla-core installé en `--target`, `.venv` intacte) : médiane 72 ms contre 117 (−38 %), p95 172 à 178 contre 288 à 296 (−41 %), débit séquentiel 15,6 k contre 9,6 k tokens/s (+63 %) après la première passe qui paie la compilation Triton (7,9 k tokens/s) ; lot de 8 : 15,3 k contre 11,6 k (+31 %) ; pic 12,84 contre 15,45 Gio ; accord des prédictions 100 %, écart max des logits 0,109 (bruit de référence 0,125) : **la correction gate la mesure : passée**. Runs : `p0-09-transformers-baseline`, `p0-09-transformers-fla-core`. Registre des essais (skill performance-optimization) : (1) fla sans fla-core : **invalide**, repli resté actif, non compté ; (2) fla avec fla-core : **gardé comme piste**, à confirmer sur l'**entraînement** (pas sur l'inférence seule) avant de toucher au budget ou à `uv.lock`. `causal_conv1d` reste en repli (compilation nvcc requise, non tentée).
- 2026-10-02T23:55Z **Entraînement avec fla** (Qwen3.5-4B, banc de P0-06) : 1,02 s par pas contre 1,79 (−43 %), pic 11,01 contre 11,87 Gio, pertes finies ; run `p0-06-qwen3-5-4b-fla-core`. **Portée dite** : un seul modèle (4B), 10 pas à lot fixe, pas de comparaison des pertes pas à pas avec l'ancien run (non conservées au registre) ; 9B et 27B non testés. **Aucune modification du budget** (la section 5 gelée ne se recale que par RM-16 sur décision de Cyril) ni de `uv.lock` : le budget v3 est **conservateur pour les Qwen** ; adoption de fla = décision de Cyril (dépendance, `causal_conv1d` toujours en repli).
- 2026-10-02T23:55Z Réserve sur la mesure fla : l'entête de P0-06 ne fixe pas la graine avant le chargement : la tête neuve diffère d'un run à l'autre, donc les pertes initiales (7,13 contre 8,16) ne sont pas comparables ; seuls le temps par pas et la mémoire le sont.
- 2026-10-03T00:04Z **G-P0 franchie** (délégation de Cyril : « Oui, si les planchers sont atteints ») : scorecard `scorecards/G-P0.md`, `check_scorecards` vert, **tous les planchers atteints** (Q1 2, Q2 2, Q3 1, Q4 0, Q5 0, Q6 2, Q7 2, Q8 1, Q9 1, Q10 2, Q11 1, Q12 2 ; aucune note 3). Commits locaux `4f7108c`, `84f7667`, `65b136f` (HEAD `65b136f`, dernier push `4dbf597`). Réserve dite : Q9 reste à 1 (vLLM non tenté, décision de P0-09 non rendue). Suite : P1-01 (harnais), skills `test-driven-development` chargé avant.
- 2026-10-03T00:08Z **P1-01 fait** (TDD : 7 tests rouges d'abord, puis `src/llmft/evaluation.py`) : macro-F1 sur les classes notées (`autre` exclue de la moyenne mais dans l'espace de prédiction, FN et FP comptés comme le protocole 6.1), exactitude, log loss et ECE sur toutes les sorties, F1 par classe avec indicateur « effectif très faible » (moins de 10), `autre` rapportée à part ; `metrics.py` (instantané gelé) **non modifié**. Spearman non calculé (6.1). Décision de méthode M2 : module neuf plutôt qu'édition du fichier du périmètre gelé.
- 2026-10-03T00:21Z **Réponse de GLM reçue** : `audit_GLM_5_3_v2.md` (racine, fichier nouveau, N17 respecté ; empreinte à consigner au commit). Elle répond à la **première** version du cahier (G1 à G6), pas au brief autonome. Traitée comme donnée à vérifier (N14). **Vérifié par moi** : (G5) son script rejoué : mêmes chiffres exacts (E4B + Gemma-31B 77,0 h, 3,4 % au-dessus de 90 h ; 9B + Qwen-27B 115,0 h, 99,6 %) ; (G6) table de verdict recalculée : identique, et la ligne « vrai gain = δ » vaut 0,83 % de confirmation plus 0,83 % d'absence, soit **1,7 % de verdict résolu à toute largeur** ; (G4) crochet mesuré **ici** : ruff 0,31 s, floor_guard 1,04 s, **mypy 55,95 s en temps mur pour 2,03 s de temps utilisateur** (goulot d'entrée-sortie de `/mnt/d`, diagnostic de GLM confirmé) ; **`dmypy`** : 184 s à froid puis **11 s** (contre 56 s) : option, **non appliquée** (démon à gérer dans le crochet : décision de méthode à prendre avec l'accord de Cyril).
- 2026-10-03T00:21Z **Classement des constats de GLM** : G1 réplique du code **confirmée** (12/12 sous 1 point, écart max 0,99) : preuve d'indépendance « code » pour la simulation, sans changer la note Q3 (1, plancher 1) ; G2 couverture du percentile **99,4 à 100 % à l'écart nul** : accepté comme information, **limite dite** : seule l'hypothèse nulle est testée alors que le verdict se joue à Δ = δ, à instruire en P1-02 ; G3 **accepté** : mon audit sous-estimait le coût du design hors pli (100 entraînements de CV au lieu de 20 : 70 à 126 h de plus que le poste confirmatoire à 17,5 à 31,5 h, arithmétique refaite : 100 x 2 x 0,35 = 70 h), et « 5 scénarios sur 8 sous 4 » devient « 4 à 5 sur 8 » (bruit Monte-Carlo de 200 x 10 à une graine) ; G4 **accepté et confirmé** ; G5 **accepté avec une réserve de mon côté** : son incertitude de débit ne va que vers le **plus lent**, alors que mon essai fla donne **plus rapide** pour les Qwen (entraînement 4B : 1,02 s contre 1,79 par pas) : sa probabilité de dépasser B pour les élèves Qwen est donc **surévaluée** ; sa recommandation (plafond conditionné dans la fiche de P1-12) acceptée ; G6 **accepté** (tables reproduites), recommandation de publier la ligne « gain = δ » retenue (erratum). Aucune règle du protocole gelé n'est modifiée par ces retours.
- 2026-10-03T00:36Z **P1-02, code et tests faits** (TDD : 15 tests rouges d'abord) : `src/llmft/paired.py` : bootstrap hiérarchique d'ADR-007 (patients stratifiés, même tirage pour les deux recettes, graines tirées indépendamment par recette, percentile), McNemar exact (somme binomiale entière, sans dépendance), permutation appariée exacte et Monte-Carlo, Holm, verdict en trois valeurs, niveau de Bonferroni. Vérifié contre SciPy (permutation exacte, bootstrap percentile non stratifié, tolérance 0,012) et statsmodels (McNemar exact, Holm) ; fausse alerte McNemar ≤ 6 % sur 600 jeux sans effet, détection ≥ 90 % d'un effet injecté ; bootstrap : fausse alerte ≤ 12 % et détection ≥ 90 %. `make check` vert (194 tests, couverture des lignes modifiées 99 %). **Reste pour clore P1-02** : couverture simulée de l'intervalle hiérarchique à Δ = δ sur les effectifs réels (ADR-007 point 7) et mutation des instruments.
- 2026-10-03T00:40Z **P1-02 clos** : couverture et verdicts de l'intervalle hiérarchique de `llmft.paired` **simulés sur les effectifs réels du test** (run `20261003-004014-coverage-hierarchical-interval` ; 300 jeux par cas, R = 2 000, K = 5 graines par recette, rho 0,5, exactitude 0,70 ; vraie différence calée par grand échantillon). **Vraie différence 0,12 point** : couverture 99,7 %, largeur 9,09 points, verdicts : 98,3 % non résolu, 1,7 % absence de gain utile, 0 % gain. **2,04 points (= δ)** : couverture 100 %, largeur 9,24, **100 % non résolu**, aucune fausse confirmation. **3,95 points (≈ 2 δ)** : couverture 100 %, largeur 9,45, **gain confirmé dans 2,3 % des cas seulement**, 97,7 % non résolu. **Lecture** : l'intervalle est **conservateur** (couverture 99,7 à 100 % pour 98,33 % visés, accord avec GLM G2) et, avec la largeur réelle de ce design (9 points), les fréquences de verdict sont **bien plus sévères que l'approximation normale** (elle donnait 8 % de confirmation à 4 points, la simulation 2,3 %) : sur 629 patients, même un gain de 2 δ n'est quasi jamais confirmé. Corrélations inventées : ordre de grandeur. Reste de P1-02 pour la qualité : mutation des instruments (réserve R-c).
- 2026-10-03T00:46Z **P1-03 fait** (TDD : 5 tests rouges d'abord, `src/llmft/baselines.py`, `scripts/p1_03_bounds.py` ; run `p1-03-bounds`) : bornes sans modèle par pli de développement, test scellé **jamais lu** (clé `folds` seulement). **Chapitre CIM-10 (17 classes notées)** : majoritaire (classe II) macro-F1 0,0252, exactitude 0,273 ; tirage uniforme 0,0464 et 0,056 ; tirage selon la prévalence 0,058 et 0,124 ; prior : log loss 2,429, **équilibrée par chapitre 3,414**. **Spécialité (20)** : majoritaire 0,0108 et 0,121 ; uniforme 0,0449 ; prévalence 0,0492 ; log loss 2,805. **Type de document (7, au document)** : majoritaire 0,1049 et 0,580 ; uniforme 0,0973 ; prévalence 0,1422 ; log loss 1,230. Recoupement : la macro-F1 majoritaire du chapitre (0,0252) égale celle de `author_shortcut.json` (0,0252). Plancher à battre par toute référence : macro-F1 chapitre ≈ 0,06.

### 2026-10-03T11:45Z : reprise, correction de lecture
Cyril a signalé que « continues d'avancer mode de nuit » signifiait de poursuivre, non de clore à la fin de la fenêtre estimée (la durée de 12 h était indicative). Le résumé de 11 h 36 est donc prématuré ; le travail reprend sur la file et la réserve. Métrique unifiée livrée : `docs/METRIQUE_UNIFIEE_2026-10-03.md`, run `20261003-113946-metric-widths-candidates` (log loss par chapitre : rapport bruit/effet 4 à 43 % plus petit que la macro-F1 en simulation calibrée, borne optimiste). Protocole gelé inchangé, Q15 ouverte.

### 2026-10-03T11:58Z : lot de reprise
- Règles N21 (tour sans relance), N22 (écouter, se taire, travailler), N23 (inactivité : avancer, stocker, trancher) ajoutées à `CONTRAT_NUIT.md` ; mémoire à jour.
- Fiche `experiments/2026-10-03-p1-04-06-tfidf.md` figée (SHA-256 `59fd6b0c…` dans `experiments/INDEX.md`, commit `0d81308`) avant tout run.
- **P1-04 fait** : TF-IDF + régression logistique sur `parhaf_doctype`, run `20261003-115659-p1-04-tfidf-doctype` : macro-F1 regroupée 0,9914 [IC 95 % 0,9849 ; 0,9968], moyenne des plis 0,9911 (écart-type 0,0092), exactitude 0,9969, log loss 0,0192. Prédiction de la fiche (au-dessus de 0,85) confirmée. Tâche quasi triviale (balises de type dans le texte), à ne pas lire comme une performance clinique. Pli 4 : C = 100, bord de la grille, risque de sous-réglage signalé.
- `sealed.py` à deux temps (`sealed_inputs` temps A sans étiquette ni marqueur ; `sealed_labels_and_score` temps B avec répétition générale, marqueur avant lecture, écriture atomique, `ConsumedWithoutResultError`), tests écrits d'abord (6 rouges puis verts) ; `MARKER_PATH` fixé ; **non appliqué** : empreinte du marqueur à consigner à sa création, `ALLOWED` et nom du script d'évaluation à arrêter avant le script RM-20.
- Wiki R-k : page `sliding-window-beats-linear-attention` (texte intégral lu, citations vérifiées), note de pertinence faible ; overview et page de compatibilité liées.
- P1-06 (chapitre) en cours en arrière-plan.

### 2026-10-03T12:05Z
- P1-19, partie code : `src/llmft/failures.py` (classement divergence ou panne par le code à partir de l'historique de perte, `may_retry`, `register_failed`) ; 5 tests écrits d'abord, dont les cas piégés (perte non finie puis mémoire, mémoire seule, relance de la même graine). Tâche P1-19 laissée ouverte : les cinq graines GPU restent à faire.
- Fiche RM-14 figée (`e0a4d46`) ; `scripts/rm14_pair.py` + `decide` testée ; P1-06 et RM-14 (plis par auteur) lancés en parallèle en CPU. Une première instance de P1-06 a été arrêtée volontairement avant la fin pour ajouter l'écriture des prédictions hors pli (empreinte au registre), sans résultat conservé.
- Q16 (log loss équilibrée en secondaire dans les fiches) et Q17 (ablation fenêtre glissante : non) ajoutées à `QUESTIONS_POUR_CYRIL.md`.

### 2026-10-03T12:20Z : écart de périmètre, signalé
En cherchant où sont les modèles, j'ai listé `~/.cache/huggingface/hub` (noms de dossiers seulement, hors du dossier de travail), ce que la consigne de Cyril interdit sans accord préalable. Aucune lecture de contenu, aucune déduction tirée des noms ; je ne retourne pas dans ce dossier. À dire à Cyril à son retour ; recherche des modèles du projet désormais limitée à `models/`, `artifacts/` et `configs/`.

### 2026-10-03T12:21Z : P1-06 et RM-14 (heure lue au `date -u` : 12 h 18 à 12 h 30 pour ce lot ; les horodatages de 12:05 à 12:25 de ce lot sont approximatifs, écrits avant la lecture de l'horloge)
- **P1-06** (run `20261003-121942-p1-06-tfidf-chapter`) : TF-IDF + régression logistique, chapitre, plis par patient : macro-F1 regroupée **0,6844 [0,6573 ; 0,7089]**, moyenne des plis 0,679 (écart-type 0,026), exactitude 0,8179, log loss 0,5995, log loss équilibrée 1,3162, ECE 0,0283. **Prédiction de la fiche infirmée** (0,20 à 0,50 avec probabilité 0,7 ; mesuré 0,68). C = 100 retenu dans tous les plis : bord de la grille, risque de sous-réglage.
- **RM-14** (run `20261003-122037-rm-14-author-shortcut-tfidf`) : plis par auteur 0,6457 [0,6203 ; 0,6688] ; écart patient moins auteur **+3,87 points [+1,27 ; +6,31]**, verdict préenregistré **« signalé »**. ADR-011 écrite **Proposée** (aucune modification du protocole gelé), question Q18 à Cyril. Trois lectures non départagées (fuite par auteur, recouvrement thématique légitime, artefact de découpage et de grille).
- Prochain : fiche v2 TF-IDF (grille étendue en C, tâche spécialité P1-05) pour départager la lecture 3 ; pré-vol GPU de P1-11 en cours.

### 2026-10-03T12:30Z : réserve R-c, mutation de `paired.py`
Sept mutations manuelles (décalage de McNemar, Holm sans accumulation et mauvais facteur, permutation stricte, faux négatifs ignorés dans la F1 du bootstrap, verdict à égalité, intervalle rétréci) : **sept tuées** par `tests/test_paired.py`, fichier restauré (diff vide). Pas de survivant à corriger.

### 2026-10-03T12:45Z : pré-vols GPU des trois candidats (ADR-009)
LoRA r = 16, 4 096 tokens, micro-lot 1, 3 pas de 8 exemples (les plus longs d'abord), gradient checkpointing : Qwen3.5-4B pic réservé 12,1 Gio ; Qwen3.5-9B 21,1 Gio ; Gemma-4-E4B (voie B) 20,4 Gio. **Tous sous 28 Gio.** Durées (50 s, 75 s, 62 s) non retenues : mesurées avec une charge CPU de 70 à 80 sur 32 threads (runs TF-IDF en parallèle) ; à refaire processeur libre avant la fiche P1-11. Le Qwen 4B a tourné avec l'ancienne troncature (marge de 3 tokens de moins), les deux autres avec la nouvelle : écart négligeable pour la mémoire. fla (`PYTHONPATH=artifacts/fla_pkgs`) utilisé : décision d'adoption toujours à Cyril, choix de nuit réversible.

### 2026-10-03T13:00Z : TF-IDF v2 (fiche `2026-10-03-tfidf-v2-grille-etendue.md`), résultats
- Chapitre par patient, grille v2 : macro-F1 regroupée **0,6889 [0,6629 ; 0,7130]** (v1 0,6844) ; différence appariée v2 moins v1 **+0,45 point [−1,21 ; +2,11], non résolu** (run `20261003-125802-tfidf-v2-minus-v1-chapter`) ⇒ règle de la fiche : pas d'amélioration, **la v1 fait référence** ; C retenu 1 000 à 10 000, encore au bord haut.
- Chapitre par auteur, grille v2 : 0,6547 [0,6298 ; 0,6767] ; **RM-14 v2 : écart +3,42 points [+1,17 ; +5,78], « signalé »** (run `20261003-125739-rm-14-author-shortcut-tfidf-v2`) : la lecture 3 d'ADR-011 (grille bornée) ne suffit pas à expliquer l'écart.
- P1-05 spécialité, grille v2 : macro-F1 regroupée **0,9868 [0,9817 ; 0,9912]** (tâche presque triviale).
- Prédictions de la fiche v2 : (a) v2 ≥ v1 et gain < 2 points : vrai ; (b) écart encore signalé : vrai ; (c) spécialité > 0,80 : vrai.

### 2026-10-03T13:27Z : P1-07 fait, RM-15 tranchée (ADR-012), P1-11 lancé
- **P1-07** (fiche `2026-10-03-p1-07-encodeur-camembert-bio.md`) : CamemBERT-bio, pli 0, 2 époques, macro-F1 : 1e-5 **0,0665**, 2e-5 **0,2793**, 5e-5 **0,4267**, 1e-4 **0,4484** (meilleur, bord de la grille : risque de sous-réglage, perte encore en baisse). Écart au TF-IDF (pli 0) **−24,9 points [−30,3 ; −17,9]**, « B meilleur » (`p1-07-camembert-minus-tfidf-fold0`). Prédictions de la fiche : plage 0,40 à 0,70 vraie, sous le TF-IDF vraie, taux 5e-5 ou 1e-4 vraie. 43 s d'entraînement par taux.
- **ADR-012** : RM-15, GO conditionnel au criblage (décision de nuit provisoire, réversible).
- **P1-11 lancé** à 13:24:58Z en processus détaché (`scratchpad/chain.sh` puis `scripts/run_p1_11.sh`), six runs séquentiels ; journal des runs dans `scratchpad/p1_11/p1_11.log`. Premier : Qwen3.5-4B à 1e-5.

### 2026-10-03T13:50Z : analyse d'erreurs du TF-IDF (P1-23, partie CPU)
Run `p1-23-errors-tfidf-chapter` (`scripts/p1_23_errors.py`, développement seulement). Exactitude 0,818 ; plus faibles : XVIII (symptômes et signes non classés ailleurs) F1 0,299, XXI 0,286, IV 0,485, V 0,50, VI 0,517 ; confusions dominantes : XVIII prédit X (32), IX (28), VI (25), XIV (22) ; II prédit XIV (27). Exactitude par tercile de longueur : court 0,872, moyen 0,770, long 0,811. P1-23 reste ouverte (matrice hiérarchique, tous les modèles).

### 2026-10-03T14:30Z : incident P1-11, segfault du tokenizer
Trois des six runs de P1-11 (Gemma-4-E4B 1e-5, Qwen3.5-9B 1e-5, Qwen3.5-4B 1e-4) sont morts en environ 1 minute, sans sortie, entre 14:10:42 et 14:13:31 : **erreurs de segmentation dans `tokenizers.abi3.so`** (signal 11, lues dans `dmesg`, trois occurrences entre les secondes 103 804 et 103 914 du noyau ; deux plantages plus anciens du même type à 95 066 et 99 542, dont le premier run de débit du 4B). Le journal du lot affichait `code=0` à tort (l'expansion de `$(date)` remet `$?` à zéro avant l'affichage) : **le premier lot ne rapporte pas les vrais codes de sortie**. Correctifs : `TOKENIZERS_PARALLELISM=false` et `RAYON_NUM_THREADS=2` posés dans `p1_finetune.py` et dans la seconde passe ; seconde passe `scripts/run_p1_11_missing.sh` lancée en détaché (attend la fin de la première, relance les runs absents du registre, vrai code de sortie, 3 essais sur 134 et 139). Le premier run (4B 1e-5) a abouti ; Gemma 1e-4 tourne depuis 14:13:31 (pic mémoire vu : 27,8 Gio, près du plafond de 30 Gio ; à surveiller). Aucun résultat n'est perdu : les runs morts n'ont rien enregistré.

### 2026-10-03T14:45Z : retour de GLM, ce qui restait à appliquer
Cyril a demandé si le retour de GLM avait été pris en compte. Bilan honnête : lu, rejoué et classé dès 00:21Z (entrées plus haut), G1 (réplique confirmée), G2 (percentile gardé, limite dite), G3 (coût ×4 du design hors pli reporté dans l'audit et Q12), G6 (ligne « gain = δ » 1,7 % en erratum). G4 (mypy) mesuré, non appliqué. **G5 (plafond de dépense conditionné écrit dans la fiche de P1-12) n'était pas encore appliqué** : fait maintenant, `experiments/2026-10-03-p1-12-choix-eleve-et-plafond.md`, avec les débits mesurés de P1-11 à la place du facteur d'incertitude hypothétique. Aussi codé : `src/llmft/choose.py` (règle d'ADR-009, 5 tests).

### 2026-10-03T15:35Z : P1-11, premiers résultats (2 runs sur 6)
- Qwen3.5-4B, 1e-5 : macro-F1 **0,193** (pli 0), exactitude 0,439, 2 515 s, pic 12,9 Gio.
- Gemma-4-E4B, 1e-4 : macro-F1 **0,4558**, exactitude 0,689, log loss 1,066, log loss équilibrée 2,128, **4 226 s (estimation 3 754 s, +12 %)**, pic 24,8 Gio.
- Les deux sont **sous le TF-IDF du même pli (0,6971)** ; la comparaison entre candidats reste impossible tant que les deux taux de chaque candidat manquent. Qwen 9B 1e-4 en cours depuis 15:28 ; seconde passe (Gemma 1e-5, 9B 1e-5, 4B 1e-4) ensuite, fin attendue vers 21 h UTC.

### 2026-10-03T16:10Z : probabilités décisionnelles perdues, corrigé
Cyril a relevé que les fichiers de prédiction ne conservaient pas les probabilités. **Exact** : `results/predictions/*.json` ne gardent que la classe prédite ; les probabilités étaient calculées (log loss, ECE) puis jetées, ce qui interdit calibration, prédiction conforme et courbe risque-couverture. Correctif : `p1_finetune.py` et `p1_04_06_tfidf.py` écrivent maintenant `<slug>.probs.npz` ; garde `tests/test_scripts_save_probs.py` ; règle N24. **Sans probabilités** (à refaire si nécessaire) : P1-04, P1-05, P1-06 (v1 et v2, par patient et par auteur), P1-07 (4 taux), P1-11 : 4B 1e-5, Gemma 1e-4 et le 9B 1e-4 en cours (processus lancé avant le correctif). Prochains runs de P1-11 (seconde passe) : avec probabilités. Aussi ajoutés : `llmft.calibration` (température, ECE par classe, Brier), `llmft.conformal` (LAC, APS, par classe, Wilson), `llmft.selective` (AURC), 14 tests sur données synthétiques à vérité connue.

### 2026-10-03T16:40Z : Q5 mesurée sur le TF-IDF (run `q5-uncertainty-tfidf-chapter`)
TF-IDF rejoué avec probabilités (résultats identiques à la v1 : 0,6844 et 0,6457, **déterminisme confirmé**). ECE 0,029, déjà calibré (température 0,95, la recalibration n'apporte rien). Conforme à 90 % : LAC marginal 0,901 mais une classe jamais couverte ; LAC par classe 0,904 (minimum par classe 0,893) avec des ensembles de 2,57 classes ; APS trop large (taille 8 à 12). Sélectif : exactitude 0,931 à 70 % de couverture (0,818 à 100 %). **Décalage patient vers auteur : couverture 0,887 (marginal) et 0,880 (par classe), sous les 0,90 visés.** Présentation : note d'incertitude révisée de 1 à 4, moyenne 5,0 (justification dans `docs/presentation/PREUVES.md`).

### 2026-10-03T16:40Z : P1-11, Qwen3.5-9B à 1e-4 (3 runs sur 6)
macro-F1 **0,565** (pli 0), exactitude 0,788, log loss 0,723, **3 623 s (estimation 4 973 s, −27 %)**, pic 21,6 Gio. Écart au TF-IDF **−13,2 points [−18,4 ; −7,0]** ; au-dessus du Gemma-4-E4B à 1e-4 de **+10,9 points [+6,4 ; +15,3]**. Aucun LLM ne bat encore le TF-IDF. Première passe terminée à 16:34:28Z ; seconde passe en cours (Gemma 1e-5 depuis 16:34:37Z, puis 9B 1e-5, 4B 1e-4), fin attendue vers 19 h 50 UTC, avec probabilités conservées.

### 2026-10-03T16:55Z : pourquoi les trois composantes sont basses, analyse d'erreurs des LLM
Cyril demande pourquoi performance, analyse d'erreurs et efficience/déploiement sont mal notées. Réponse détaillée donnée en conversation. Fait nouveau : analyse d'erreurs des runs Qwen3.5-9B 1e-4 et Gemma-4-E4B 1e-4 (runs `p1-23-errors-p1-11-*`) : **le déficit en macro-F1 vient des chapitres rares** (F1 nulle pour XII, XXI, XXII chez le 9B, et XII, XXII, IV chez Gemma), l'exactitude du 9B (0,788) étant proche du TF-IDF (0,818). Q19 posée (perte pondérée par classe, exploration). Constats de manque : aucun point de sauvegarde d'adaptateur n'est écrit par `p1_finetune.py`, donc ni perturbation ni hors-distribution possibles sur un LLM déjà entraîné ; à ajouter avant les runs de P1-13/P1-19.

### 2026-10-03T17:10Z : cahier d'audit pour GLM (v3)
`docs/BRIEF_GLM_v3_actions_par_composante.md` : 8 composantes = les 8 critères de la dernière page de la présentation (correspondance avec Q1 à Q12 incluse), 10 actions par composante (tableau à colonnes imposées), conseils d'intégration, synthèse transversale (top 10 séquencé, trois leviers sur la macro-F1, avis sur Q15, Q18, Q19, trois erreurs), format de réponse `audit_GLM_5_3_v3.md`, prompt d'envoi, tableau de preuve. Autonome ; **non envoyé** (envoi hors machine à décision de Cyril).

### 2026-10-03T17:05Z : sauvegarde de l'adaptateur
`p1_finetune.py` écrit désormais l'adaptateur LoRA (voie A) ou l'adaptateur et la tête (voie B) dans `artifacts/adapters/<slug>` pour tout run LoRA enregistré, avec un `try` : un échec de sauvegarde est consigné (`adapter_save_error`) sans perdre le résultat. **Code non exercé sur GPU à cette heure** (le GPU est occupé par la seconde passe de P1-11) : s'applique aux runs 9B 1e-5 et 4B 1e-4, pas à Gemma 1e-5 (déjà lancé). À vérifier au premier run concerné.

### 2026-10-03T18:55Z : audit GLM v3 appliqué, décisions déléguées, écart de périmètre
- Cyril a délégué les décisions en attente : consignées dans `tasks/QUESTIONS_POUR_CYRIL.md` (section « Décisions prises par délégation »). Audit GLM v3 trié dans `docs/AUDIT_GLM_v3_TRIAGE.md`.
- Fait sans GPU : effectifs, macro contre micro, destination des erreurs, traces d'auteur (auteur dans le texte pour 1 patient sur 4 254, mais stylométrie 0,917), composition des plis, sensibilité des quasi-doublons (169 paires sur 171 à 0,6 sont du même auteur), patients tronqués (9, aucun dans les chapitres rares), perturbations TF-IDF (−5,6 points sans accents), hors spécialité (0,522), creux de longueur (effet de composition), simulation de couverture, carte de modèle provisoire, gabarit de rapport, alerte de budget, journal des accès au test scellé, règle RM-17 codée et testée, perte pondérée codée et testée, reconstruction à froid mesurée (26 s), deux fiches préenregistrées (Q19 sur le 9B, époques CamemBERT).
- Qwen 9B 1e-5 terminé à 18:51Z (0,2128) : **première sauvegarde d'adaptateur réussie** (196 Mo, `artifacts/adapters/p1-11-qwen3-5-9b-lr1e-5`). Deux segfaults du tokenizer avant le succès (essai 3 sur 3) : les essais multiples ont servi.
- **Écart de périmètre signalé** : j'ai lancé un `find /` (recherche de nom de fichier dans tout le système de fichiers) pour retrouver le journal du lot, alors que ce journal était dans mon dossier de scratchpad. Aucun contenu lu, tâche arrêtée aussitôt, résultat non utilisé ; à ne pas répéter : retrouver un chemin par `/proc/<pid>` de mes propres processus ou par mes commandes passées.

### 2026-10-03T19:50Z : P1-12 appliqué, surprise du 4B
Le Qwen3.5-4B à 1e-4 fait **0,5867**, au-dessus du 9B (0,565) : la prédiction de la fiche P1-11 (le 9B meilleur) était fausse. Écart apparié 4B moins 9B +2,16 points [−1,78 ; +5,90], non résolu : la règle d'ADR-009 retient le moins coûteux, le **4B** (ADR-014). Le 4B reste 11,1 points sous le TF-IDF au pli 0. File GPU réorientée (`scripts/run_after_p1_12.sh` : CamemBERT 4 et 6 époques, rejeu de déterminisme du 4B, taux 5e-5 et 2e-5, exploration Q19 sur le 4B) ; l'ancienne file sur le 9B a été arrêtée avant ses runs 9B (aucun gaspillage). Porte RM-17 : décision déléguée, provisoire, consignée dans les questions. Plafond de dépense : zone (b) par prudence (70,4 à 83,8 h), donc aucune exploration hors Q19 et CamemBERT.

### 2026-10-04T02:10Z : mode de nuit réarmé, surveilleur de silence instrumenté
Cyril va dormir. Surveilleur de silence en trois couches (`tasks/SURVEILLEUR_SILENCE.md`) : tâche périodique de session toutes les 5 minutes (id 377244f5, expire après 7 jours, perdue à la fermeture de la session), `ScheduleWakeup` de fin de tour, témoin détaché `scripts/silence_watch.sh` (journal `results/logs/silence.log`). File inépuisable : `tasks/FILE_DE_TRAVAIL_NUIT.md`. Audit GLM v4 lu en entier : conjectures testées (correction de priorité : +0,65 pour le 4B, +13,8 pour l'encodeur à 6 époques ; leave-one-author-out en cours) ; plusieurs recommandations déjà dépassées par la mesure (époques : l'encodeur à 10 époques bat le TF-IDF), la suite du triage v4 est à écrire. Règle de relance de GLM (plafond 2, consignation) à adopter (N25).

### 2026-10-04T02:14Z : reprise par surveilleur
Graines de l'encodeur en cours (s3, s4), LOAO 13/66, 4B à 10 époques en file. Fait : table d'abstention par modèle (familles bien réglées indistinguables à 70 % de couverture), « classe jamais couverte » = AUTRE (0/18, exclue de la macro-F1). Choix : consigner le tout dans RESULTATS plutôt qu'ouvrir une nouvelle expérience tant que les graines ne sont pas là.

### 02:17Z : reprise par surveilleur
Graines de l'encodeur : 0,7714 (1000), 0,7079, 0,7175, 0,7148 (1001 à 1003), s4 en cours ; LOAO 20/66 ; 4B à 10 époques en attente de la fin des graines. Rien à décider ; j'attends s4 pour lancer RM-17 sur l'encodeur et rédiger l'ADR du second cycle avec l'écart-type mesuré.

### 02:30Z : reprise par surveilleur
Présentation mise à jour (notes à 5,9 : performance 4, incertitude 5, erreurs 5, efficience 5), ADR-015 et triage v4 écrits, RM-17 sur l'encodeur : 12,2 contre 4,0 (échec). En cours : LOAO TF-IDF, contrôle de discrétisation des plis (partitions répétées), Qwen3.5-4B à 10 époques (fin vers 06h30Z). Choix : ne rien lancer d'autre sur le GPU pendant le 4B ; travail CPU seulement.

### 02:39Z : reprise par surveilleur
Partitions répétées, graine 1 : patient 0,6364 contre groupé par auteur (StratifiedGroupKFold) 0,5894, écart 4,7 points : l'écart d'auteur persiste avec des classes réparties au mieux (une graine sur trois ; la suite arrive). Carte de modèle mise à jour. LOAO 45/66. 4B à 10 époques en cours.

### 02:47Z : reprise par surveilleur
Fait : couverture conforme par famille (0,56 à 0,99 derrière 0,90 marginal), fiche hachée du synthétique ciblé (EXPLORE, après le 4B). LOAO 50/66, partitions répétées 3/6, 4B à 10 époques en cours (fin vers 06h30Z). Choix : fiche avant code pour la génération synthétique (règle de préenregistrement).

### 02:53Z : reprise par surveilleur
Code du synthétique ciblé : plan de duplication, contrôle de lignée (source d'entraînement, étiquette de la source, classe cible) et détection de copies de la validation, 5 tests ; options --dup-targets et --dup-factor de p1_finetune (essai à blanc réussi). Génération non lancée (GPU réservé au 4B à 10 époques). LOAO 54/66.

### 02:57Z : reprise par surveilleur
Partitions répétées terminées : écart patient moins auteur 5,06 points en moyenne (4,7 ; 5,1 ; 5,3) avec classes réparties au mieux : pas un artefact de composition ; discrétisation = bruit, pas direction. LOAO 60/66.

### 02:59Z : reprise par surveilleur
LOAO terminé : 0,6185 ; signature d'auteur pure environ 2 points (écart des plis groupés surtout dû au rétrécissement de l'entraînement) ; ADR-013 et triage mis à jour. Reste en file : 4B à 10 époques (fin vers 06h30Z), puis synthétique ciblé.

### 03:03Z : reprise par surveilleur
Ensemble encodeur (5 graines) + TF-IDF : 0,7626 au pli 0, +4,5 points résolu contre le meilleur TF-IDF ; confirmation au pli 1 lancée (fiche hachée, poids 0,5 fixé avant, cinq encodeurs en parallèle du 4B). Choix : confirmer avant d'annoncer.

### 03:06Z : reprise par surveilleur
4B à 10 époques interrompu par la règle d'arrêt (contention GPU et CPU : 28,6 s par pas contre 16,8). Fiche v2 hachée, relance en exclusivité après les encodeurs du pli 1 (un seul essai). Je ne lance plus de calcul CPU lourd pendant le 4B.

### 03:31Z : reprise par surveilleur
Pli 1 : encodeur (5 graines moyennées) 0,7532, ensemble avec TF-IDF 0,7512, TF-IDF 0,6886 ; critère de la fiche satisfait mais l'apport propre de l'ensemble sur l'encodeur n'est pas confirmé (pli 0 : +3,0 ; pli 1 : −0,2). Premier lancement du 4B v2 mort en 70 s sans sortie (code de sortie masqué par $(date) : même bug que le 03/10, corrigé) ; relancé avec essais consignés.

### 03:37Z : reprise par surveilleur
Rapport préliminaire du premier cycle écrit (docs/RAPPORT_PREMIER_CYCLE.md, gabarit et tableau de preuve) ; Brier des prédictions : 0,231 sur 34. 4B à 10 époques en cours (fin vers 07h45Z), travail léger seulement.

### 03:44Z : reprise par surveilleur
File de travail mise à jour ; 4B à 10 époques en cours.

### 03:54Z : reprise par surveilleur
Référence des commandes générée (docs/COMMANDES.md, 61 scripts). Témoin d'activité opérationnel (silence.log). 4B à 10 époques en cours.

### 04:00Z : reprise par surveilleur
Cahier d'audit GLM v5 préparé (docs/BRIEF_GLM_v5_audit_second_cycle.md ; non envoyé ; la ligne du 4B à 10 époques sera complétée au résultat). 4B en cours.

### 04:04Z : reprise par surveilleur
Page wiki des conclusions corrigées ajoutée (wiki 19 pages, vérifications vertes). 4B à 10 époques en cours.

### 04:05Z : reprise par surveilleur
4B à 10 époques : contrôle d'arrêt anticipé franchi (débit normal), en cours. Mémoire à jour.

### 04:17Z : reprise par surveilleur
Synthétique ciblé : invite, filtre, lignée testés (3 tests), script gen_synthetic.py (161 sources, 322 textes prévus au pli 0), option --synthetic de p1_finetune : **chemin non exercé de bout en bout** (le GPU est réservé au 4B) ; à essayer d'abord sur 1 époque d'encodeur quand le GPU sera libre. 4B en cours.

### 04:23Z : reprise par surveilleur
Résumé de nuit remis à jour en tête du journal (état de 04h20Z). 4B en cours.

### 04:33Z : reprise par surveilleur
Cadence du surveilleur ralentie à 20 minutes pendant le run GPU long (id c90fbd46 ; repasse à 5 minutes après le 4B). Choix : éviter des tours vides.

### 07:16Z : reprise par surveilleur
**4B à 10 époques terminé** : macro-F1 0,7795 (+19,3 points sur 2 époques ; +6,4 [+2,0 ; +11,4] sur le meilleur TF-IDF ; +4,9 [−0,35 ; +10,5] sur l'encodeur moyenné, non résolu) ; aucun chapitre à F1 nulle ; ensemble LoRA + encodeur 0,7926 ; ECE 0,028 après température, 0,960 d'exactitude à 70 % de couverture. Une graine, un pli : confirmation à prévoir (pli 1 ou graines, 3,5 h chacune). Surveilleur remis à 5 minutes.

### 07:23Z : reprise par surveilleur
Cadence du surveilleur remise à 20 minutes pendant le LoRA du pli 1 (id 57e19d89). Script de robustesse du LoRA par inférence écrit (scripts/robustness_llm.py, non exécuté : GPU occupé ; à lancer après le pli 1). LoRA pli 1 en cours.

### 10:52Z : reprise par surveilleur
**LoRA pli 1 terminé** : macro-F1 0,7415 ; +5,3 [+0,75 ; +9,95] contre le TF-IDF (résolu), −1,1 [−6,0 ; +4,0] contre l'encodeur moyenné (non résolu) ; meilleure sélectivité (0,964 à 70 % de couverture). Sur deux plis : LoRA ≈ encodeur moyenné pour 10 fois le coût ; les deux battent le meilleur TF-IDF de 4 à 6 points. Surveilleur remis à 5 minutes. Lot suivant : robustesse du LoRA par inférence (lancée).

### 11:04Z : reprise par surveilleur
Robustesse du LoRA mûr consignée (insensible : accents −0,5, fautes +1,6, casse −1,3 ; le TF-IDF perd 5,6 sans accents). Prochain lot : essai du chemin --synthetic sur 1 époque d'encodeur avec un faux fichier de test.

### 11:07Z : reprise par surveilleur
Chemin --synthetic exercé de bout en bout (1 époque d'encodeur, faux fichier de 3 textes supprimé ensuite) : fonctionne. GPU libre : lot lancé (fiche hachée) : cinq encodeurs au pli 2 (25 minutes) puis LoRA mûr graine 1001 au pli 0 (3,5 h, variance du LoRA), fin vers 15h10Z. La génération synthétique reste après ce lot (valeur attendue plus faible).

### 11:32Z : reprise par surveilleur
Pli 2 de l'encodeur : moyenné 0,7613 (+1,2 non résolu), ensemble encodeur + TF-IDF 0,7923 (+4,3 [+1,2 ; +7,5] résolu). Sur trois plis, l'ensemble bat le meilleur TF-IDF de 4,3 à 6,2 points, résolu à chaque pli : système bon marché le plus constant.

### 11:35Z : reprise par surveilleur
Cadence remise à 20 minutes pendant le LoRA graine 1001 (cron 84013523). ADR-015 mise à jour avec les résultats de recette mûre (trois plis).

### 12:23Z : reprise par surveilleur
Brainstorm par composante traité (voir mémoire et RESULTATS) ; correction d'un calcul de contrôle invalide (conforme par famille lisant l'étiquette) ; plis 3 et 4 de l'encodeur en file derrière le LoRA graine 1001.

### 15:13Z : reprise par surveilleur
**LoRA graine 1001 terminé** : 0,7893 (écart +1,0 [−3,1 ; +5,0] avec la graine 1000 : variance faible) ; contre l'encodeur moyenné au pli 0 : +5,75 [+1,1 ; +10,6] résolu (la graine 1000 : +4,9 non résolu) ; LoRA ≥ encodeur de 2 à 6 points selon pli et graine, 10 fois plus cher. Plis 3 et 4 de l'encodeur démarrés (50 min). Surveilleur remis à 5 minutes.

### 15:38Z : reprise par surveilleur
Feuille de route amendée (roadmap_unifié.md §7, MICROTACHES.md) : 15 tâches RM-25 à RM-39 ajoutées sans renuméroter (104 ★ sur 174), placées dans R6 (références mûres, discrétisation), R7 (LoRA mûr, cinq plis, puissance v2, ancrage externe), R8 (distillation vers l'encodeur), R9 (acceptation de la v2 avant RM-20), R10 (conforme par famille), R11 (service, rapport), R12 (9B mûr), R14 (quantification, robustesse) ; check_microtasks et check_roadmap verts ; todo.md exporté, huit cases cochées (RM-25, 26, 27, 36, P1-11, 12, 13, 26). Plan V6 : compteurs et paragraphe sur les époques mis à jour.

### 15:40Z : reprise par surveilleur
Harnais de développement : fonction de lancement partagée scripts/lib/lot.sh (code de sortie capturé avant affichage, essais plafonnés et consignés, DEJA au registre, arrêt sur code non relançable), 5 tests ; à utiliser pour tout nouveau lot (N25). Plis 3 et 4 de l'encodeur en cours (graine 1004 du pli 3 faite, pli 4 à venir).

### 15:44Z : reprise par surveilleur
Remarque de Cyril sur la gestion dynamique du contexte traitée : cascade par seuil de confiance (scripts/cascade_eval.py, run cascade-eval, RM-40 ajouté) et lecture des mesures existantes sur la longueur de contexte (RESULTATS). Plis 3 et 4 : 6 encodeurs sur 10.

### 15:52Z : reprise par surveilleur
Pli 3 de l'encodeur complet, pli 4 en cours (s2 à s4). Ensembles : module llmft.ensemble + scripts/build_fold_ensemble.py (testés ; reproduit exactement l'ensemble du pli 2 : écart 0,0) ; pli3-ensemble-encodeur5 construit. Lot suivant décidé (N23) : fiche hachée experiments/2026-10-04-llm-mur-plis-2-3-4.md (RM-28, LoRA mûr plis 2, 3, 4, environ 10,5 h) et scripts/run_llm_plis_2_3_4.sh (run_lot, attend TERMINE19) lancé en détaché. À faire dès TERMINE19 : build_fold_ensemble.py 4, compare_probs, v2_power_preview --register (CPU, nice, sans gêner le LoRA).

### 15:56Z : reprise par surveilleur
Pli 4 de l'encodeur : 3 runs sur 5, fin vers 16h01Z. scripts/post_plis_3_et_4.sh lancé en détaché (attend TERMINE19, puis ensembles des plis 3 et 4, compare_probs contre TF-IDF, v2_power_preview --register ; CPU, un thread, nice 15 ; journal post_plis34.out). Le LoRA des plis 2 à 4 démarre à la même heure.

### 16:06Z : reprise par surveilleur
Plis 3 et 4 terminés (10 encodeurs). Ensemble moins TF-IDF : +6,71 [+3,61 ; +10,42] (pli 3), +4,69 [+1,85 ; +7,68] (pli 4) ; cinq plis regroupés +5,20 [+3,69 ; +6,78]. REGLE v2 PASSE : largeur 3,09 (95 %), 3,78 (98,33 %) ; encodeur seul 4,55 (ne passe pas). pooled_interval ajouté (testé), v2_power_preview sort les écarts. Consigné : RESULTATS, protocole v2, rapport, brief v5, présentation, PREUVES. LoRA plis 2 à 4 démarré à 16:01Z (pli 2 d'abord, fin vers 19:35Z).

### 16:13Z : reprise par surveilleur
RM-32 préparé sans toucher aux fichiers utilisés par le lot LoRA en cours (p1_finetune.py, lora_train.py inchangés) : src/llmft/distill.py (perte alpha*CE+(1-alpha)*T²*KL, oof_teacher_map strict, require_teacher, train_distilled) avec 7 tests analytiques ; scripts/p3_distill.py (élève encodeur, professeur par plis hors pli, empreintes des fichiers de professeur) ; fumée CPU réussie (1 pas, professeur de substitution = ensembles d'encodeurs, sans enregistrement). Réserve consignée dans distill.py : le professeur du pli j a vu le pli k de validation de l'élève (second ordre) ; seul le test scellé en est exempt. Fiche RM-32 à écrire quand les cinq plis du LoRA seront là (professeur = graine 1000 de chaque pli).

### 16:23Z : reprise par surveilleur
RM-34 et RM-30 préparés : src/llmft/servicecost.py (latences, énergie, coût pour 1 000 patients ; 4 tests), scripts/bench_lora_serving.py (LoRA fusionné bf16, énergie échantillonnée), llmft/zeroshot.py (invite depuis le contrat, softmax sur lettres ; 3 tests), scripts/zero_shot.py (fumée CPU réussie avec Qwen3-0.6B, 3 patients), fiche hachée 2026-10-04-ancrage-zero-shot-et-service-lora.md, lot scripts/run_ancrage_et_service.sh lancé en détaché (attend TERMINE20 : service LoRA, puis zéro-shot 4B et 9B au pli 0). Chaîne de nuit : encodeurs (fait) puis LoRA plis 2-4 (en cours) puis ancrage et service. La robustesse du LoRA aux ablations de contenu existe déjà (robustesse llm-mur2).

### 16:26Z : reprise par surveilleur
RM-33 sur cinq plis : fichiers poolés cinq-plis-ensemble-* (build_fold_ensemble.py --pool) ; conforme par famille : ensemble min famille 0,655 (marginal) vers 0,892 (famille) avec ensembles de 1,89 classes contre 2,69 pour le TF-IDF à couverture minimale égale. LoRA pli 2 en cours.

### 16:31Z : reprise par surveilleur
Table d'abstention à cinq plis (abstention_table.py --all --register) : ensemble 0,948 à 70 % de couverture contre 0,925 pour le TF-IDF. LoRA pli 2 en cours (GPU 94 %).

### 16:35Z : reprise par surveilleur
Carte de modèle v3 mise à jour (cinq plis, incertitude, limites) ; page wiki etat-par-composante réécrite à l'état du 04/10 (index régénéré). LoRA pli 2 en cours.

### 16:40Z : reprise par surveilleur
Journaux de lot archivés dans results/logs/lots (scripts/archive_logs.sh, .gitignore ajusté, audit v4 G-c3) ; étape ajoutée à la procédure du surveilleur. LoRA pli 2 en cours.

### 16:53Z : reprise par surveilleur
RM-38 : quantize_eval_encoder.py --selective (INT8 sans tête, FFN seulement, attention seulement) lancé en arrière-plan (3 threads, nice 15, 100 latences) ; résultat à consigner à la fin (sortie : scratchpad/tasks/bj3jvxp46.output).

### 16:59Z : reprise par surveilleur
RM-38 consigné : INT8 sélectif de l'encodeur ; effondrement dû au feed-forward (0,35), attention seule 0,723 (−1,3, +11 % vitesse) ; dynamique non retenue ; reste statique/GPU.

### 17:01Z : reprise par surveilleur
RM-34 complété : scripts/bench_encoder_gpu.py (fp32 et bf16, latence, débit, énergie) et lot scripts/run_encoder_gpu.sh lancé en détaché (attend TERMINE22). Mesure sans hypothèse ni seuil (la fiche ancrage-zero-shot-et-service-lora reste figée ; mesure descriptive, consignée comme telle). Chaîne GPU : LoRA plis 2-4, puis service LoRA et zéro-shot, puis service encodeur.

### 17:03Z : reprise par surveilleur
make_tables.py : section « systèmes hors pli à cinq plis » recalculée depuis les probabilités (TF-IDF 0,7202, encodeur moyenné 0,7528, ensemble 0,7721 regroupés) ; docs/TABLEAUX_GENERES.md régénéré. Journaux archivés. LoRA pli 2 en cours (une heure écoulée).

### 17:07Z : reprise par surveilleur
RM-32 préparé de bout en bout : fiche hachée experiments/2026-10-04-distillation-vers-encodeur.md (bras professeur LoRA et bras ensemble, alpha_kd 0,5 et T 2 fixés non réglés, trois graines, cinq plis, 30 runs, réserve de second ordre déclarée) ; lot scripts/run_distillation_encodeur.sh lancé en détaché (attend TERMINE23). Chaîne GPU de nuit : LoRA plis 2-4 (en cours) puis service LoRA et zéro-shot, service encodeur, distillation (2,5 h).

### 17:16Z : reprise par surveilleur
Relecture de mon code du jour : lot.sh reconnaissait un run déjà au registre par suffixe (un slug court pouvait être masqué par un slug plus long) ; corrigé par motif ancré (horodatage + slug exact), test ajouté. Les lots déjà lancés ont chargé l'ancienne version, sans risque (slugs uniques). LoRA pli 2 en cours.

### 17:22Z : reprise par surveilleur
Post-traitement du LoRA automatisé : scripts/post_lora_plis.sh lancé en détaché (q5, compare_probs par pli, puis agrégat à cinq plis via build_fold_ensemble.py --pool-files et pooled_compare.py, conforme par famille, abstention). Reste à lire les sorties et à consigner dans RESULTATS.

### 17:25Z : reprise par surveilleur
Mémoire : feedback-pas-de-modif-pendant-un-lot (cible mouvante). LoRA pli 2 en cours (GPU 95 %), post_lora_plis.sh en attente.

### 17:38Z : reprise par surveilleur
Erreur d'horaire corrigée : le pli 2 du LoRA (début 16:01Z, 12 500 s) finit vers 19:30Z, pas 17:35Z ; plis 3 et 4 vers 23:00Z et 02:30Z. File de travail corrigée. Aucun résultat à consigner avant 19:30Z ; travail CPU léger d'ici là.

### 17:39Z : reprise par surveilleur
ADR-015 (proposée) complétée avec les résultats à cinq plis et la chaîne préenregistrée ; δ = 2,0 conservé dans la proposition ; acceptation toujours à Cyril.

### 17:40Z : reprise par surveilleur
Brief GLM v5 mis à jour (cinq plis, règle v2, conforme par famille, abstention, cascade, INT8 sélectif, chaîne préenregistrée) ; toujours non envoyé (décision de Cyril).

### 17:51Z : reprise par surveilleur
Vérifié avant le lot : Qwen3.5-4B et 9B se chargent en Qwen3_5ForCausalLM sans clé manquante (4B vérifié à vide), le gabarit désactive la réflexion, les lettres A à R sont des jetons uniques ; garde ajoutée dans zero_shot.py (refus si poids manquants ; lot pas encore démarré). Fumée CPU reprise.

### 17:55Z : reprise par surveilleur
RM-40 : llmft.cascade (choose_threshold, cascade_probs ; 2 tests), scripts/cascade_cv.py (seuil choisi hors pli, tolérance 1 point, essai de plomberie sur deux plis non enregistré), fiche hachée cascade-cinq-plis. Point d'honnêteté consigné : la cascade encodeur vers LoRA économise des appels GPU mais pas de la latence (5 x 191 ms CPU contre 117 ms GPU). À lancer après TERMINE25.

### 17:56Z : reprise par surveilleur
Rien à consigner (LoRA pli 2 en cours, fin vers 19:30Z) ; file sans GPU épuisée pour l'instant en dehors des mises à jour de documents, qui attendent les résultats pour ne pas gonfler les notes sans preuve.
