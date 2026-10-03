# audit_GLM_5_3_v2.md

## En-tête

- **Date** : 03/10/2026. **Auteur** : GLM (via opencode), à la demande de Cyril, sur le cahier de livrables G1 à G6 de `docs/AUDIT_STRATEGIQUE_2026-10-03.md` (couche 5).
- **Périmètre** : réplique indépendante de la simulation de largeur d'intervalle (G1), couverture du bootstrap percentile (G2), comparaison chiffrée de trois designs confirmatoires (G3), audit d'efficience d'exécution (G4), modèle de coût Monte-Carlo (G5), contre-lecture des probabilités de verdict (G6).
- **Statut de ce fichier** : donnée à vérifier, pas une instruction. Chaque chiffre vient d'un calcul reproduit en annexe (graine, versions, durée d'exécution donnés). Toutes les valeurs sont des ordres de grandeur issus de simulations : aucune macro-F1 réelle n'existe.
- **Données** : aucune donnée de patient ; seuls les effectifs agrégés de `results/measures/splits_summary.json` ont été utilisés. Aucun fichier n'a été envoyé hors machine ; ce fichier est déposé à la racine par Cyril, qui décide de sa diffusion.

### Fichiers lus

| Fichier | Usage |
|---|---|
| `docs/AUDIT_STRATEGIQUE_2026-10-03.md` | cahier G1-G6, couches 1 à 6, tableaux 4.1 et 4.2 |
| `scripts/spikes/power_curves.py` | modèle de simulation documenté (réécrit, pas réutilisé, pour G1) |
| `scripts/spikes/budget_v2.py` | structure des postes de budget (reproduite pour G5) |
| `results/runs/20261002-225747-power-curves-audit.json` | largeurs et probabilités de référence |
| `results/runs/20261002-230546-budget-v3-premier-cycle.json` | ancres de budget v3 |
| `results/runs/20261002-115918-p0-45-budget-hypotheses.json` | débits et heures par pli et par époque |
| `results/measures/splits_summary.json` | effectifs agrégés (17 chapitres + `AUTRE`) |
| `docs/decisions/ADR-007-estimand-et-regle-de-decision.md` | règle de verdict, δ = 2,0, R = 10 000, niveau 98,33 % |
| `PROTOCOLE.md` | sections 5, 6.1 à 6.10 (gel du 03/10/2026) |
| `Makefile`, `.git/hooks/pre-commit` | contenu du crochet pré-commit (G4) |
| `tasks/JOURNAL.md` | constats des trois relectures, état du gel (G4) |

### Ce qui n'a pas été lu ou exécuté

- ADR-004, ADR-009, ADR-010, ADR-006, 008 : non lues (les valeurs qu'elles portent ont été prises via `PROTOCOLE.md` et les runs).
- `knowledge/` (wiki et `knowledge/raw/*`), `data/` (parquet et partitions), `src/llmft/` : non lus.
- `experiments/INDEX.md` et la conformité des neuf instantanés de `experiments/frozen/` aux empreintes : non vérifiés (`scripts/check_frozen.py` non exécuté).
- Le run `20261002-221006-power-sketch-ic-width-v2.json` : non relu (ses résultats sont cités par la source, pas recalculés ici).
- Les jetons et durées des trois relectures (§ 2.2 de la source) : non vérifiables (notifications de session, hors registre).
- Aucun run GPU ; tout est calcul de simulation en CPU.

---

## G1. Réplique indépendante de la simulation de largeur

**Résultat** : les 12 scénarios (3 évaluations × 2 exactitudes × 2 corrélations) sont reproduits à moins de 1 point sur chacun des trois indicateurs (macro-F1 17 chapitres, exactitude, macro-F1 12 grands chapitres). Écart maximal : 0,99 point (macro-F1 17, test 629, exactitude 0,6, corrélation 0,5 : 14,3 dans la source, 13,31 dans la réplique à paramètres identiques). À paramètres convergés (2 000 répliques × 30 jeux, écart Monte-Carlo mesuré ≤ 0,49 point), l'écart va de +0,01 à +0,76 point, avec un léger excès systématique sur les scénarios du test (direction conservatrice : la réplique trouve des intervalles un peu plus larges).

**Méthode** : modèle réécrit à partir du texte documenté (docstring de `power_curves.py` et couche 4 de l'audit), sans réutiliser leur code : difficulté latente par patient, masque `ok = (rho × latent + (1 − rho) × bruit) < exactitude`, erreur vers une classe tirée selon la prévalence, bootstrap apparié stratifié par classe avec remise sur les patients seuls, largeur = percentile [0,8333 ; 99,1667] moyenne sur les jeux. Différences d'implémentation assumées : tirage stratifié par comptes multinomiaux par strate (équivalent mathématique au tirage d'indices avec remise), macro-F1 par matrice de poids, pas par boucles de masques. Aucune étiquette réelle : effectifs agrégés seulement.

**Chiffres** (largeur en points de macro-F1 17 ; réplique convergée = moyenne des graines 3 et 4, R = 2 000, 30 jeux ; source = run `20261002-225747-power-curves-audit`) :

| Évaluation | n | Exactitude ; corrélation | Source | Réplique (200×10, graine 3) | Réplique convergée | Écart |
|---|---|---|---|---|---|---|
| Test scellé | 629 | 0,6 ; 0,5 | 14,3 | 13,31 | 14,72 | +0,42 |
| Test scellé | 629 | 0,6 ; 0,8 | 8,2 | 8,71 | 8,96 | +0,76 |
| Test scellé | 629 | 0,8 ; 0,5 | 8,4 | 8,86 | 8,83 | +0,43 |
| Test scellé | 629 | 0,8 ; 0,8 | 7,4 | 7,79 | 8,06 | +0,66 |
| Plis 1 à 4 | 2 871 | 0,6 ; 0,5 | 6,7 | 6,53 | 6,79 | +0,09 |
| Plis 1 à 4 | 2 871 | 0,6 ; 0,8 | 3,8 | 3,95 | 4,38 | +0,58 |
| Plis 1 à 4 | 2 871 | 0,8 ; 0,5 | 4,0 | 3,80 | 4,05 | +0,05 |
| Plis 1 à 4 | 2 871 | 0,8 ; 0,8 | 3,9 | 3,75 | 3,81 | −0,09 |
| Développement | 3 572 | 0,6 ; 0,5 | 6,1 | 5,64 | 6,14 | +0,04 |
| Développement | 3 572 | 0,6 ; 0,8 | 3,8 | 3,90 | 3,87 | +0,07 |
| Développement | 3 572 | 0,8 ; 0,5 | 3,7 | 3,84 | 3,71 | +0,01 |
| Développement | 3 572 | 0,8 ; 0,8 | 3,3 | 3,45 | 3,41 | +0,11 |

Unité : points de macro-F1 (échelle 0 à 100). Intervalle de l'écart : +0,01 à +0,76 point en convergé ; +0,15 à +0,99 point à paramètres identiques (200×10). Les indicateurs exactitude et macro-F1 12 grands chapitres sont reproduits au même niveau (écart maximal mesuré : 0,29 et 0,35 point en convergé).

**Écart avec le document source** : **confirmé** — critère d'acceptation du cahier (écart < 1 point sur chacun des 12 scénarios) atteint : 12/12 à paramètres identiques, 12/12 en convergé. Deux constats chiffrés au passage : (a) la variation de la largeur entre graines Monte-Carlo à 200×10 atteint 1,15 point sur le scénario le plus large (mesuré sur les graines 3 à 6) : la source à une seule graine porte donc elle-même une incertitude de cet ordre ; (b) l'excès systématique de la réplique converge sur les scénarios du test (0,42 à 0,76 point), ce qui renforce plutôt la lecture 1 du tableau 4.1 (les largeurs du test sont sous-estimées, pas surestimées).

**Limites** : corrélations inventées (0,5 et 0,8) ; effectifs des plis 1 à 4 proportionnels aux chapitres (les effectifs par pli et par classe n'existent pas dans `splits_summary.json`) ; deux modèles de même niveau ; la réplique partage le modèle statistique de la source : elle vérifie le code, pas les hypothèses.

**Recommandation** : utiliser la réplique comme preuve d'indépendance « code » pour la note Q3 du scorecard G-P0 ; le critère d'acceptation est atteint sans explication ad hoc. Coût : nul (calculs faits). Réversible : oui.

---

## G2. Couverture du bootstrap percentile à 98,33 %

**Résultat** : sur les effectifs réels du test (633 patients, strates de 4 à 174 plus `AUTRE` 4), la couverture de l'intervalle percentile à 98,33 % est de **99,7 à 100 %** pour une cible de 98,33 % (1 000 jeux, R = 10 000). L'intervalle est donc **conservateur** : il contient la vraie différence nulle plus souvent que son niveau nominal, jamais en dessous du seuil de fiabilité de 97 % posé par la source (§ 4.5). BCa (jackknife delete-un-patient, graines fixes) donne la même couverture (99,4 à 100 %) sans gain. Les strates fusionnées (pool de 39) raccourcissent à peine la largeur (9,50 contre 9,61 points) sans changer la couverture. R = 2 000 donne une couverture de 99,8 % et une largeur de 9,56 contre 9,61 à R = 10 000 : la sensibilité à R est faible.

**Méthode** : schéma hiérarchique simulé : vraie différence nulle, difficulté latente par patient (comme la couche 4), corrélations d'erreurs 0,5 ou 0,8 entre toutes les prédictions d'un même jeu ; estimateur = moyenne des macro-F1 (17 chapitres) sur K = 5 graines par recette, différence des deux recettes ; bootstrap = tirage stratifié par strate avec remise (mêmes patients pour les deux recettes) puis K graines tirées avec remise indépendamment par recette ; intervalle percentile à 98,33 % ; couverture = part de 1 000 jeux contenant 0. BCa par jackknife sur les 633 patients, graines traitées comme fixes (hypothèse déclarée).

**Chiffres** (couverture en part des 1 000 jeux contenant la vraie différence 0 ; largeur moyenne en points de macro-F1 17) :

| Exactitude ; corrélation | Couverture percentile | Couverture BCa | Largeur percentile | Largeur BCa |
|---|---|---|---|---|
| 0,6 ; 0,5 | 99,9 % | 99,9 % | 9,61 | 9,62 |
| 0,6 ; 0,8 | 99,7 % | 99,4 % | 5,98 | 6,00 |
| 0,8 ; 0,5 | 100 % | 100 % | 5,83 | 5,83 |
| 0,8 ; 0,8 | 100 % | 99,7 % | 5,34 | 5,36 |

Sensibilité (exactitude 0,6, corrélation 0,5) : strates fusionnées 100 % (largeur 9,50) ; R = 2 000 : 99,8 % (largeur 9,56).

**Écart avec le document source** : la source ne calculait pas la couverture (elle la renvoyait à P1-02, § 4.5 et ADR-007 point 7) : résultat **nouveau**, aucune contradiction. Deux éclairages pour le design : (a) le sur-couvrement s'explique par la discrétisation des strates minuscules (4 à 9 patients) et par l'estimation de queues à 0,83 % ; (b) la largeur du schéma hiérarchique (5,3 à 9,6 points) est **plus petite** que la largeur d'une paire unique de modèles (7,4 à 14,3, tableau 4.1) parce que la moyenne sur cinq graines réduit la variance : les largeurs de la couche 4 sont donc une borne haute raisonnable pour la comparaison confirmatoire telle que réglée, sous l'hypothèse (inventée) d'indépendance des graines.

**Limites** : corrélations inventées et uniformes entre recettes et graines (la corrélation réelle entre deux graines d'une même recette, qui décide de tout, reste non mesurée) ; jackknife BCa fait à graines fixes, donc incomplet face au schéma hiérarchique complet ; l'intervalle du taux de couverture à 1 000 jeux est d'environ ±1,1 point (95 %).

**Recommandation** : garder l'intervalle percentile tel qu'écrit dans ADR-007 (R = 10 000, stratifié, apparié) et inscrire la couverture mesurée (99,4 à 100 %) comme propriété conservatrice du design ; aucun passage à BCa ni fusion de strates, dont le gain mesuré est nul ou négatif (−0,11 à +0,03 point de largeur). Coût : nul. Réversible : oui (aucune règle ne change ; le protocole étant gelé, un changement passerait par une nouvelle version, règle 4 de 6.10).

---

## G3. Comparaison chiffrée de trois designs confirmatoires

**Résultat** : le design « test scellé 633 » est le moins cher mais ne peut pas délivrer de verdict résolu pour un gain utile réel de 3 points (probabilité 2,3 à 3,7 % selon le scénario). Le design hors pli multiplie la puissance mais son coût d'entraînement a été sous-estimé par la source : en validation croisée complète (5 plis × 4 recettes × 5 graines = 100 entraînements de 2 868 patients au lieu de 20 sur le développement entier), le poste confirmatoire passe d'environ 17,5 à 31,5 h à environ 70 à 126 h selon l'élève : **B = 90 h est dépassé pour tout choix d'élève dans cette arithmétique**. Le compromis qui tient dans B est un hors-pli limité (2 recettes × 5 graines × 5 plis), qui laisse H2 et H3 sans comparaison hors pli.

**Méthode** : largeurs attendues issues de la réplique convergée de G1 (macro-F1 17, patients seuls) ; probabilités de verdict résolu par l'approximation normale de la source (σ = largeur/(2z), z = 2,394) ; coûts par arithmétique explicite à partir des heures par pli et par époque du run `p0-45-budget-hypotheses` (élèves 0,35 à 0,63 h ; facteur développement/pli 1,2503 ; deux époques).

**Chiffres**. Largeurs (points, min-max sur les 4 scénarios) et P(verdict résolu, δ = 2,0) :

| Design | n évalué | Largeur | P(résolu), vrai gain 2 | 3 | 4 | 5 |
|---|---|---|---|---|---|---|
| A. Test scellé (protocole actuel) | 629 | 8,06 à 14,72 | 0,017 à 0,017 | 0,023 à 0,037 | 0,042 à 0,114 | 0,078 à 0,270 |
| B. Hors pli, plis 1 à 4 | 2 871 | 3,81 à 6,79 | 0,017 à 0,017 | 0,047 à 0,128 | 0,163 à 0,548 | 0,390 à 0,916 |
| C. Hors pli, développement entier | 3 572 | 3,41 à 6,14 | 0,017 à 0,017 | 0,054 à 0,161 | 0,202 à 0,661 | 0,478 à 0,965 |

Coûts en heures de GPU (entraînement, élèves ; professeurs inchangés ; hypothèse : les 100 entraînements du CV remplacent les 20 de P3-07) :

| Poste | A (actuel) | B et C (CV complet) |
|---|---|---|
| Entraînement confirmatoire, élève Gemma-4-E4B | 17,5 | 70 |
| Idem, élève Qwen3.5-4B | 23,0 | 92 |
| Idem, élève Qwen3.5-9B | 31,5 | 126 |
| Δ par rapport au plan v3 (57,6 à 86,3 h) | 0 | +52,5 à +40 (E4B) ; +69 à +40 (4B) ; +94 à +40 (9B) |
| Total cycle avec E4B et professeur Gemma-4-31B | 57,6 | 110,1 |

Détail du calcul de la ligne E4B : 100 runs × 2 époques × (2 868 patients / 2 868 par pli) × 0,35 h = 100 × 0,7 = 70 h ; contre 20 runs × 2 × 1,2503 × 0,35 = 17,5 h. Détail du total B : 57,6 − 17,5 + 70 = 110,1 h.

**Écart avec le document source** : **partiel** — (a) les largeurs confirment le tableau 4.1 (lignes plis 1 à 4 et développement) à moins de 0,1 point près ; (b) la lecture 5 du tableau 4.1 (« cinq scénarios sur huit strictement sous 4, six en comptant 4,0 ») est **infirmée dans la réplique convergée** : quatre scénarios sur huit strictement sous 4 (3,41 ; 3,71 ; 3,81 et 4,05 compté à la limite), le scénario défavorable restant à 6,14 à 6,79 ; (c) le coût « moyen » de l'idée I3 (tableau de la couche 3, ligne I3, colonne Coût) est **infirmé** : l'arithmétique du CV complet multiplie le poste confirmatoire par 4 (70 à 126 h), chiffre absent de la source, qui ne budgétait que la fuite des professeurs imbriqués (§ 4.4, point 1, « environ cinq fois plus de heures de professeur : non budgété »).

**Limites** : le poste « inference hors pli » (évaluation de 4 recettes × 5 graines sur 2 871 à 3 572 patients) n'est budgété nulle part dans la source ni ici faute de débit mesuré en inférence ; le biais de sélection du taux (choisi sur le pli 0) reste faible dans le design B (un hyperparamètre parmi quatre sur un pli distinct) mais s'ajoute dans le design C (le pli 0 fait partie de l'évaluation) ; la fuite de distillation de la source (§ 4.4, point 1) est structurelle et non chiffrable sans vraies prédictions ; les professeurs imbriqués coûtent environ 79 à 89 h de plus (5 × 15,8 à 17,8), non budgétés.

**Recommandation** : si la mesure de RM-17 (arbre de décision de la couche 4.3 de la source) désigne le design hors pli, faire figurer l'arithmétique d'entraînement (70 à 126 h) et le choix des recettes couvertes (H1 seule, ou H1 à H3) dans la nouvelle version du protocole **avant** tout run confirmatoire, car B = 90 h ne couvre pas le CV complet. Coût : une version du protocole et une ADR (quelques heures hors GPU). Réversible : oui tant qu'aucun run confirmatoire n'est lancé.

---

## G4. Audit d'efficience d'exécution (suite du v1)

**Résultat** : le crochet pré-commit (`exec make check-fast`) mesure **84 s en cumul nominal** sur la machine de calcul de ce fichier (montage bind docker-desktop, pas la machine de l'audit) : ruff 0,4 s ; mypy 80,9 s (premier run) puis 102,0 s (second run avec cache) ; floor_guard 1,4 s ; gitleaks via Docker 1,6 s. mypy représente environ 96 % du temps mur et son temps utilisateur n'est que de 1,9 à 2,6 s : le goulot est l'entrée-sortie du système de fichiers, pas le calcul. La cadence des relectures confirme la lecture de la source : le coût par constat est plat (8 178, 8 038 et 8 160 jetons par constat) tandis que le texte grossit ; les bloquants baissent (4, 3, 2) et sont désormais tous traités.

**Méthode** : chronométrage de chaque étape de `make check-fast` (`time` shell, deux passes mypy) sur cette machine ; lecture de `Makefile` et de `.git/hooks/pre-commit` ; arithmétique sur le tableau 2.2 de la source (jetons et durées : non vérifiables, pris comme donnés) ; comptage des commits et des tâches du backlog.

**Chiffres** :

| Mesure | Valeur | Contexte |
|---|---|---|
| ruff check | 0,43 s | cette machine |
| mypy src (1re passe, cache froid) | 80,9 s (utilisateur 2,6 s) | cette machine |
| mypy src (2e passe, cache présent) | 102,0 s (utilisateur 1,9 s) | cette machine |
| floor_guard | 1,37 s | cette machine |
| gitleaks (Docker, image en cache) | 1,63 s | cette machine |
| Jetons par constat de relecture (1/2/3) | 8 178 ; 8 038 ; 8 160 | arithmétique sur 130 850/16 ; 144 688/18 ; 163 208/20 |
| Bloquants par tour (1/2/3) | 4 ; 3 ; 2 | source § 2.2 |
| Croissance du protocole | 73 lignes → 190 lignes (source) ; 203 lignes aujourd'hui | source § 2.2 ; mesure actuelle |
| Commits au dépôt | 32 (source : 27) | comptage au moment de la mesure |
| Tâches cochées / ouvertes | 51 / 114 (source : 50 / 115) | comptage au moment de la mesure |

**Écart avec le document source** : **partiel** — (a) le constat B de la source (« crochet : environ une minute par commit ; cause non mesurée : à isoler avant toute optimisation ») est affiné : l'étape dominante est mypy (80,9 à 102,0 s), et son écart temps mur/temps utilisateur (80 contre 2,6 s) pointe l'entrée-sortie, non le calcul ; mais la mesure vient d'une machine et d'un système de fichiers différents de ceux de l'audit (§ 1.2, B) : elle doit être refaite sur la machine cible avant décision ; (b) les effectifs du dépôt ont dérivé depuis la source (§ 2.3 : 27 commits, 50 tâches) : 32 commits et 51 tâches cochées au moment de la mesure ; (c) la lecture « les relectures ne convergent pas aussi vite qu'elles coûtent » (lecture rapide 4 de la source) est **confirmée** par l'arithmétique : coût par constat plat (écart ≤ 1,8 % entre les trois tours), textes en croissance.

**Limites** : une seule machine, deux passes mypy, pas de mesure du crochet en situation réelle de commit ; gitleaks mesuré avec une image en cache local ; les jetons des relectures ne sont pas revérifiables.

**Recommandation** : avant toute modification du crochet, refaire la mesure sur la machine cible (`time .venv/bin/python -m mypy src` avec cache chaud sur disque natif) et seulement ensuite choisir l'atténuation (par exemple déplacer le cache mypy sur disque rapide) sans affaiblir aucun contrôle de `CONSTRAINTS.md`. Coût de la mesure : quelques minutes. Réversible : oui (aucun contrôle modifié par la mesure).

---

## G5. Modèle de coût avec incertitude (Monte-Carlo)

**Résultat** : avec un facteur d'incertitude de débit Uniforme(1,0 ; 1,65) par modèle (borne donnée par les rapports de débit mesurés 1 024 → 4 096 tokens : 1,52 et 1,63) et les chargements de professeurs ajoutés (5 à 7 min × 6), la probabilité de dépasser B = 90 h vaut **3,4 %** pour la meilleure combinaison (Gemma-4-E4B + Gemma-4-31B, sans relances), **10,9 %** pour E4B + Qwen3.8-27B, **52 à 64 %** pour les élèves de 4B et 9B, **98 à 100 %** pour le 9B. Une relance moyenne de +10 % porte la meilleure combinaison à 28,3 % ; l'ajout forfaitaire de 10 h de postes non comptés la porte à 36,3 %. L'alerte à 80 % de B (72 h) est dépassée dans 72 à 100 % des tirages pour toutes les combinaisons sauf aucune.

**Méthode** : structure des postes de `budget_v2.py` reconstruite et validée contre les ancres du run `20261002-230546-budget-v3-premier-cycle` (à facteur 1,0, les six combinaisons retombent exactement sur 57,6/67,5 ; 60,0/73,5 ; 68,0/77,8 ; 70,4/83,8 ; 83,9/93,8 ; 86,3/99,8) ; incertitude appliquée par modèle et par tirage ; 100 000 tirages par scénario ; trois scénarios (nominal ; relances +10 % ; +10 h de postes non comptés).

**Chiffres** (heures de GPU ; 100 000 tirages par cellule) :

| Élève + professeur | Scénario | Moyenne | p5 | p95 | P(> 90 h) | P(> 72 h) |
|---|---|---|---|---|---|---|
| E4B + Gemma-4-31B | nominal | 77,0 | 64,8 | 89,1 | 3,4 % | 72,2 % |
| E4B + Gemma-4-31B | relances +10 % | 84,7 | 71,4 | 98,0 | 28,3 % | 93,9 % |
| E4B + Gemma-4-31B | +10 h non comptés | 86,9 | 74,9 | 99,0 | 36,3 % | 99,0 % |
| E4B + Qwen3.8-27B | nominal | 80,1 | 67,6 | 92,7 | 10,9 % | 83,8 % |
| E4B + Qwen3.8-27B | relances +10 % | 88,1 | 74,3 | 101,9 | 42,4 % | 98,0 % |
| E4B + Qwen3.8-27B | +10 h non comptés | 90,1 | 77,6 | 102,7 | 50,5 % | 100 % |
| Qwen3.5-4B + Gemma-4-31B | nominal | 90,6 | 75,9 | 105,4 | 52,2 % | 99,3 % |
| Qwen3.5-4B + Qwen3.8-27B | nominal | 93,8 | 78,6 | 109,1 | 63,0 % | 100 % |
| Qwen3.5-9B + Gemma-4-31B | nominal | 111,8 | 92,6 | 130,9 | 98,0 % | 100 % |
| Qwen3.5-9B + Qwen3.8-27B | nominal | 115,0 | 95,4 | 134,6 | 99,6 % | 100 % |

(Toutes les cellules des scénarios « relances » et « non comptés » existent dans la sortie complète, annexe ; seules les lignes citées par la question du cahier sont reproduites ici.) Unité : heures de GPU. Ces nombres sont des conséquences mécaniques des hypothèses ; ce ne sont pas des durées annoncées (RM-16 recale).

**Écart avec le document source** : **confirmé et quantifié** — la ligne 81 de la source (« seul l'E4B tient avec marge sous 90 h ») est vraie uniquement sous les hypothèses du protocole (débit 1 024 tokens pour les élèves, aucun surcoût) : dès que l'incertitude de débit mesurée sur les professeurs est appliquée aux élèves (hypothèse déclarée du Monte-Carlo), même l'E4B dépasse B dans plus d'un cas sur quatre en cas de relances. La lecture de la source sur le repli (C7) reste valable ; le chiffre nouveau est la sensibilité : P(> 90 h) varie de 3,4 % à 99,6 % selon la combinaison, et l'alerte à 72 h est quasi certaine dans tous les cas sauf le meilleur.

**Limites** : le facteur Uniforme(1,0 ; 1,65) est une hypothèse, pas une mesure (aucun débit élève à 4 096 tokens n'existe, § 2.5 de la source) ; les 10 h de postes non comptés sont un forfait de sensibilité, pas une estimation (la vraie liste est en section 5 du protocole : P2-07, RM-19, P1-07, relances, calibration, inférence hors pli, chargements, vagues V2 à V5) ; indépendance supposée entre postes.

**Recommandation** : consigner dans la pré-enregistrement de P1-12 (choix de l'élève) le plafond de dépense conditionné à la combinaison retenue (par exemple : E4B + Gemma-4-31B seul à ne dépasser B qu'en cas de relance), pour que l'alerte à 80 % de B ait un seuil d'action écrit d'avance. Coût : rédactionnel. Réversible : oui (nouvelle fiche, aucune règle du protocole modifiée).

---

## G6. Contre-lecture des probabilités de verdict et du choix de δ

**Résultat** : le tableau 4.2 de la source est reproduit à l'identique (écart nul sur les 16 valeurs croisées du tableau : 50 %, 21,2 %, 11,6 %, 7,5 % pour l'absence à vrai gain nul ; 11,6 %, 5,5 %, 3,6 %, 2,8 % pour la confirmation d'un vrai gain de 3 ; 88,4 %, 50 %, 27,5 %, 16,9 % pour la confirmation d'un vrai gain de 5). Les tables nouvelles montrent que : (a) un vrai gain égal à δ n'est quasiment jamais résolu (1,7 % dans tous les cas de largeur 3 à 10) ; (b) à largeur 4, la règle d'absence ne conclut l'absence de gain utile que si l'écart observé est **négatif** (seuil δ − w/2 = 0) — c'est structurel dès que w > 2δ ; (c) le niveau de δ déplace le verdict : à largeur 4 et vrai gain 3, P(gain confirmé) passe de 27,5 % (δ = 1,5) à 11,6 % (δ = 2,0), 0,8 % (δ = 3,0) et 0 % (δ = 4,0), tandis que P(absence de gain utile à vrai gain nul) passe de 27,5 % à 50 %, 88,4 % et 99,2 %.

**Méthode** : approximation normale de la source (σ = w/(2z), z = 2,394) ; verdicts selon ADR-007 (gain confirmé si L > δ, absence si U < δ, non résolu sinon) ; L = Δ̂ − w/2, U = Δ̂ + w/2, Δ̂ ~ N(gain réel, σ²) ; calcul analytique, aucune simulation.

**Chiffres** (P(verdict résolu) ; δ = 2,0 ; selon la largeur et le vrai gain) :

| Largeur | Seuil d'absence (Δ̂ < …) | Gain 2 | Gain 3 | Gain 4 | Gain 5 |
|---|---|---|---|---|---|
| 3 | 0,5 | 0,017 | 0,212 | 0,788 | 0,992 |
| 4 | 0,0 | 0,017 | 0,116 | 0,500 | 0,884 |
| 5 | −0,5 | 0,017 | 0,076 | 0,316 | 0,684 |
| 6 | −1,0 | 0,017 | 0,056 | 0,212 | 0,500 |
| 8 | −2,0 | 0,017 | 0,038 | 0,116 | 0,275 |
| 10 | −3,0 | 0,017 | 0,030 | 0,076 | 0,169 |

Et pour les autres δ (largeur 4) : P(gain confirmé à vrai gain 3) : 27,5 % (δ = 1,5) ; 11,6 % (2,0) ; 0,8 % (3,0) ; 0 % (4,0). P(absence de gain utile à vrai gain 0) : 27,5 % ; 50 % ; 88,4 % ; 99,2 %. Table complète pour δ de 1,5 à 4,0 et largeurs de 3 à 10 : sortie du script en annexe (24 lignes × 5 gains).

**Écart avec le document source** : **confirmé** (reproduction exacte du tableau 4.2 et de la note « moins de 1 % pour un vrai gain égal à δ », § 4.2 lecture 1 et protocole 6.3 point 5). Deux précisions chiffrées nouvelles : le seuil d'absence δ − w/2 est négatif dès que la largeur dépasse 2δ, donc « absence de gain utile » exige alors un écart observé négatif, et non merely « pas de gain » ; et la ligne « gain 2 » est plate à 0,017 pour toute largeur : un vrai gain exactement égal à δ est inséparable de l'absence de gain par cette règle, à toute largeur simulée.

**Limites** : approximation normale (les vraies distributions de Δ sont discrètes, strates de 4 patients) ; la largeur y est un paramètre, pas une mesure ; le choix de δ est un jugement de valeur qui appartient à Cyril (ADR-007 point 5), et le protocole est gelé : toute modification passe par une nouvelle version (règle 4 de 6.10).

**Recommandation** : publier, à côté de la règle, la ligne « gain 2 » de ce tableau (0,017 à toute largeur) : elle dit, avant tout run, que la comparaison ne peut trancher un gain de l'ampleur exacte du seuil, et évite qu'un « non résolu » soit lu plus tard comme un échec d'exécution. Coût : nul (table déjà calculée). Réversible : oui.

---

## Table de synthèse

| Livrable | Verdict | Confiance | Action proposée |
|---|---|---|---|
| G1 réplique de la simulation | confirmé (12/12 < 1 point ; max 0,99) | élevée (code) | preuve d'indépendance « code » pour Q3 du scorecard |
| G2 couverture du bootstrap | non évalué dans la source ; résultat nouveau : conservateur (99,4 à 100 %) | moyenne (corrélations inventées) | garder percentile R = 10 000, pas de BCa, consigner la couverture |
| G3 trois designs confirmatoires | partiel : largeurs confirmées ; « 5 scénarios sur 8 » affaibli (4/8 en convergé) ; coût I3 infirmé (×4 : 70 à 126 h) | élevée pour l'arithmétique, moyenne pour les largeurs | si design hors pli retenu : nouvelle version du protocole avant tout run |
| G4 efficience d'exécution | partiel : mypy = 96 % du crochet (80,9 à 102,0 s, I/O dominante, autre machine) ; dérive des compteurs du dépôt (32 commits, 51 tâches) | moyenne (un seul environnement mesuré) | refaire la mesure sur la machine cible avant toute modification du crochet |
| G5 coût Monte-Carlo | confirmé et quantifié : P(> 90 h) de 3,4 % (E4B + 31B nominal) à 99,6 % (9B + 27B) | moyenne (facteurs hypothétiques, ancres validées) | plafond conditionné écrit dans la fiche de P1-12 avant le choix de l'élève |
| G6 contre-lecture des verdicts | confirmé (tableau 4.2 exact) ; règles nouvelles : absence impossible à w > 2δ sans écart observé négatif ; « gain = δ » jamais résolu (0,017) | élevée pour l'arithmétique (calcul analytique) | publier la ligne « gain 2 » avec la règle |

---

## Ce que GLM n'a pas pu vérifier

- Les jetons et durées des trois relectures adversariales (130 850, 144 688, 163 208 ; 354, 472, 525 s) : ils viennent de notifications de session, pas du registre ; le présent audit les a pris comme donnés et n'a fait que l'arithmétique dérivée.
- La corrélation réelle des erreurs entre deux graines d'une même LoRA et entre deux recettes : aucune prédiction réelle n'existe ; toutes les corrélations (0,5 ; 0,8 ; indépendance des graines) sont inventées et la conclusion « borne haute des largeurs de la couche 4 » en dépend.
- Le débit des élèves à 4 096 tokens et le surcoût de remplissage : non mesurés (§ 2.5 de la source) ; le facteur Uniforme(1,0 ; 1,65) de G5 est extrapolé des professeurs.
- Les effectifs par pli et par classe du découpage : absents de `splits_summary.json` (seuls les totaux par pli y sont) ; les scénarios « plis 1 à 4 » de G1 et G3 restent à effectifs proportionnels, même limite que la source (couche 4, champ Limites).
- Le temps réel du crochet pré-commit sur la machine de travail de l'audit : mesuré ici sur un montage différent (bind docker-desktop de WSL) ; la cause exacte sur `/mnt/d` reste à isoler.
- La conformité des neuf instantanés de `experiments/frozen/` aux empreintes de `experiments/INDEX.md` : non vérifiée (`check_frozen.py` non exécuté).
- Toute valeur de macro-F1 de quelque modèle que ce soit : aucune n'existe ; rien de ce que ce fichier contient ne préjuge du signe ni de l'ampleur d'un effet de distillation.

---

## Annexe de code

Environnement d'exécution : Python 3.12.13, numpy 2.4.6, Linux (WSL2), 32 fils d'exécution. Toutes les graines sont données dans le code ou la configuration. Durées d'exécution : G1 0,6 s (200×10), 35,5 s (2 000×30, deux graines) ; G2 11,0 min (quatre scénarios × R = 10 000 × 1 000 jeux, bootstrap) + 1,6 min (sensibilités à 500 jeux) ; G5 0,1 s ; G6 instantané. Les commandes de l'audit source ont été lancées depuis la racine du dépôt avec le Python système (pas `.venv`), hors du registre (sorties JSON conservées en dehors du dépôt ; ce fichier en porte les valeurs).

### G1 — `/tmp/opencode/glm/g1_replica.py` (graines 3, 4, 5, 6 ; config `{"replicas": 200, "datasets": 10, "seeds": [3]}` puis `{"replicas": 2000, "datasets": 30, "seeds": [3, 4]}`)

```python
#!/usr/bin/env python3
"""G1 - replique independante de la simulation de largeur d'intervalle.

Modele (documente dans docs/AUDIT_STRATEGIQUE_2026-10-03.md couche 4 et le docstring
de scripts/spikes/power_curves.py, reecrit ici sans reutiliser leur code) :
- deux modeles de meme niveau (ecart reel nul) ; erreur vers une classe tiree selon la prevalence ;
- masque de bonne reponse : ok = (rho * latent_partage + (1 - rho) * bruit_propre) < exactitude ;
- bootstrap apparie stratifie par classe, avec remise, sur les patients seuls ;
- largeur = percentile [0.8333 ; 99.1667] de la difference, moyennee sur les jeux ;
- effectifs : test reel (629), plis 1 a 4 proportionnels avec plancher 3 (somme 2871),
  developpement reel (3572).

Difference d'implementation assumee : le tirage stratifie est fait par comptes
multinomiaux par strate (equivalent mathematique au tirage d'indices avec remise),
et le F1 est calcule par matrices de poids, pas par boucles de masques.
"""
import json
import time
from pathlib import Path

import numpy as np

ROOT = Path("/mnt/wsl/docker-desktop-bind-mounts/Ubuntu/f5f9e8476e8d13b5f5b3d181fec59f383c00f25d2cf43a1d4f16ba998a6da6a7")
summary = json.loads((ROOT / "results/measures/splits_summary.json").read_text())
total = {k: v for k, v in summary["classes"].items() if k != "AUTRE"}
test = {k: v for k, v in summary["test_class_counts"].items() if k != "AUTRE"}
dev = {k: total[k] - test[k] for k in total}
names = list(total)
BIG = np.array([test[k] >= 16 for k in names])

SIZES = {
    "test_629": np.array([test[k] for k in names]),
    "plis_1_a_4": np.array([max(3, round(dev[k] * 2869 / sum(dev.values()))) for k in names]),
    "dev_reel": np.array([dev[k] for k in names]),
}


def macro_f1_matrix(tp, fp, fn, keep):
    denom = 2 * tp + fp + fn
    f1 = np.where(denom > 0, 2 * tp / np.maximum(denom, 1), 0.0)
    return f1[:, keep].mean(axis=1)


def scenario(counts, acc, rho, seed, n_datasets, n_rep):
    rng = np.random.default_rng(seed)
    n_classes = len(counts)
    y = np.repeat(np.arange(n_classes), counts)
    start = np.concatenate([[0], np.cumsum(counts)[:-1]])
    prev = counts / counts.sum()
    cum_prev = np.cumsum(prev)
    n = counts.sum()
    res = {"macro": [], "acc": [], "big": []}
    for _ in range(n_datasets):
        shared = rng.random(n)
        preds = {}
        for tag in ("a", "b"):
            ok = (rho * shared + (1 - rho) * rng.random(n)) < acc
            u = rng.random(n)
            wrong = np.searchsorted(cum_prev, u, side="right").clip(0, n_classes - 1)
            wrong = np.where(wrong == y, (wrong + 1) % n_classes, wrong)
            preds[tag] = np.where(ok, y, wrong)
        # poids de prediction par strate : W[c][v, i] = 1 si le patient i de la strate c est predit c
        W = {}
        for c in range(n_classes):
            sl = slice(start[c], start[c] + counts[c])
            W[c] = np.stack([np.eye(n_classes)[preds[t][sl]] for t in ("a", "b")], axis=1)
        tp = np.zeros((n_rep, n_classes, 2))
        fp = np.zeros((n_rep, n_classes, 2))
        for c in range(n_classes):
            idx = rng.integers(0, counts[c], size=(n_rep, counts[c]))
            m = np.bincount((idx + np.arange(n_rep)[:, None] * counts[c]).ravel(),
                            minlength=n_rep * counts[c]).reshape(n_rep, counts[c])
            for v in range(2):
                contrib = m @ W[c][:, v, :]  # (n_rep, n_classes) : patient predit v -> compte
                tp[:, :, v] += contrib * np.eye(n_classes)[c]
                fp[:, :, v] += contrib * (1 - np.eye(n_classes)[c])
        fn = counts[None, :, None] - tp
        d_macro = macro_f1_matrix(tp[:, :, 0], fp[:, :, 0], fn[:, :, 0], np.ones(n_classes, bool)) - \
                  macro_f1_matrix(tp[:, :, 1], fp[:, :, 1], fn[:, :, 1], np.ones(n_classes, bool))
        d_acc = tp[:, :, 0].sum(1) / n - tp[:, :, 1].sum(1) / n
        d_big = macro_f1_matrix(tp[:, :, 0], fp[:, :, 0], fn[:, :, 0], BIG) - \
                macro_f1_matrix(tp[:, :, 1], fp[:, :, 1], fn[:, :, 1], BIG)
        for key, d in (("macro", d_macro), ("acc", d_acc), ("big", d_big)):
            lo, hi = np.percentile(d, [0.8333, 99.1667])
            res[key].append(100 * (hi - lo))
    return {k: float(np.mean(v)) for k, v in res.items()}


def main():
    t0 = time.time()
    out = []
    cfg = json.loads(Path(__file__).with_suffix(".cfg.json").read_text())
    n_rep, n_datasets, seeds = cfg["replicas"], cfg["datasets"], cfg["seeds"]
    for size_name, counts in SIZES.items():
        for acc in (0.6, 0.8):
            for rho in (0.5, 0.8):
                runs = [scenario(counts, acc, rho, s, n_datasets, n_rep) for s in seeds]
                mean_over_seeds = {k: round(float(np.mean([r[k] for r in runs])), 2) for k in runs[0]}
                spread = {k: round(float(np.max([r[k] for r in runs]) - np.min([r[k] for r in runs])), 2) for k in runs[0]}
                out.append({"evaluation": size_name, "patients": int(counts.sum()), "acc": acc, "rho": rho,
                            "widths": mean_over_seeds, "spread_over_seeds": spread})
                print(out[-1], flush=True)
    print(json.dumps({"runtime_s": round(time.time() - t0, 1), "params": cfg, "results": out}, indent=1))


if __name__ == "__main__":
    main()
```

### G2 — `/tmp/opencode/glm/g2_coverage.py` (graine 20261002 ; config principale `{"accs": [0.6, 0.8], "rhos": [0.5, 0.8], "variants": ["percentile"], "n_outer": 1000, "R": 10000, "seed": 20261002}` ; sensibilités `["merged", "percentile2000"]` à 500 jeux)

```python
#!/usr/bin/env python3
"""G2 - couverture de l'intervalle percentile a 98,33 % (ADR-007, PROTOCOLE.md 6.2).

Schema hierarchique simule sur les effectifs reels du test scelle (633 patients :
17 chapitres evalues de 4 a 174, strate AUTRE de 4, tiree mais exclue de la macro-F1).
- vraie difference nulle entre deux recettes ;
- difficulte latente par patient (comme la couche 4 de l'audit) : correct si rho*g_i + (1-rho)*eps < acc,
  g_i latent partage par toutes les predictions du jeu courant (hypothese inventee, dite) ;
- erreur -> chapitre tire selon la prevalence des strates du test (AUTRE possible comme prediction) ;
- estimateur : moyenne des macro-F1 (17 chapitres) sur K = 5 graines par recette, difference ;
- bootstrap : tirage stratifie par strate avec remise (memes patients pour les deux recettes),
  puis K graines tirees avec remise, independamment par recette ; intervalle percentile a 98,33 % ;
- variantes : BCa (jackknife delete-un-patient, graines fixes) ; strates fusionnees
  (5 strates evaluees < 10 + AUTRE en un pool de 39) ; R = 2000 en sensibilite.
Couverture : part de N jeux ou l'intervalle contient la vraie difference (0).
"""
import json
import pathlib
import time
from math import erf, sqrt

import numpy as np

ROOT = pathlib.Path("/mnt/wsl/docker-desktop-bind-mounts/Ubuntu/f5f9e8476e8d13b5f5b3d181fec59f383c00f25d2cf43a1d4f16ba998a6da6a7")
summary = json.loads((ROOT / "results/measures/splits_summary.json").read_text())
eval_classes = [k for k in summary["classes"] if k != "AUTRE"]
n_eval = len(eval_classes)
test_counts = {k: v for k, v in summary["test_class_counts"].items()}
strata = [test_counts[k] for k in eval_classes] + [test_counts["AUTRE"]]  # 18 strates
N_PAT = sum(strata)
AUTRE = n_eval
K = 5
ALPHA = 0.05 / 3
SIZES_EVAL = np.array(strata[:n_eval])


def probit(p):
    lo, hi = -12.0, 12.0
    for _ in range(100):
        mid = (lo + hi) / 2
        if 0.5 * (1 + erf(mid / sqrt(2))) < p:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2


def macro_from_tpfp(tp, fp):
    """tp, fp : (..., n_eval) -> macro-F1 sur les 17 chapitres."""
    fn = SIZES_EVAL - tp
    denom = 2 * tp + fp + fn
    f1 = np.where(denom > 0, 2 * tp / np.maximum(denom, 1), 0.0)
    return f1.mean(axis=-1)


def one_scenario(acc, rho, n_outer, R, seed, variant):
    rng = np.random.default_rng(seed)
    if variant == "merged":
        small = [i for i in range(n_eval) if strata[i] < 10]
        big = [i for i in range(n_eval) if strata[i] >= 10]
        groups = [[i] for i in big] + [small + [AUTRE]]
    else:
        groups = [[i] for i in range(len(strata))]
    sizes = [sum(strata[i] for i in g) for g in groups]
    starts, off = [], 0
    for g, gs in zip(groups, sizes):
        starts.append(list(range(off, off + gs)))
        off += gs
    y_of_start = np.concatenate([[i if i < n_eval else -1] * strata[i] for i in range(len(strata))])
    y_lab = y_of_start
    y_rep = np.where(y_lab >= 0, y_lab, AUTRE)
    prev = np.array(strata) / N_PAT
    cum = np.cumsum(prev)
    cov_p, cov_b = [], []
    w_p, w_b = [], []
    t_jk, t_bs = 0.0, 0.0
    for it in range(n_outer):
        g = rng.random(N_PAT)  # difficulte latente par patient (comme la couche 4)
        ok = (rho * g[None, None, :] + (1 - rho) * rng.random((2, K, N_PAT))) < acc
        preds = np.empty((2 * K, N_PAT), dtype=int)
        row = 0
        for v in range(2):
            for j in range(K):
                wrong = np.searchsorted(cum, rng.random(N_PAT), side="right")
                pred = np.where(ok[row], y_rep, wrong)
                pred = np.where((~ok[row]) & (pred == y_rep), (pred + 1) % len(strata), pred)
                preds[row] = pred
                row += 1
        # comptes de base (jeu complet)
        tp0 = np.zeros((2 * K, n_eval))
        fp0 = np.zeros((2 * K, n_eval))
        for c in range(n_eval):
            sel_y = y_lab == c
            for k in range(2 * K):
                tp0[k, c] = (preds[k, sel_y] == c).sum()
                fp0[k, c] = ((preds[k] == c) & ~sel_y).sum()
        macro0 = macro_from_tpfp(tp0, fp0)
        d_hat = macro0[:K].mean() - macro0[K:].mean()
        # jackknife delete-un-patient (graines fixes), vectorise
        t0 = time.time()
        eq = (y_lab[:, None] == np.arange(n_eval)[None, :]).astype(float)  # (N, 17)
        corr = ((preds == y_rep[None, :]) & (y_lab >= 0)[None, :]).astype(float)  # (M, N)
        onehot = (preds[:, :, None] == np.arange(n_eval + 1)[None, None, :]).astype(float)[:, :, :n_eval]
        eff_tp = np.einsum("mn,nc->mnc", corr, eq)  # retrait du tp de sa classe
        eff_fp = onehot - eff_tp  # retrait d'un faux positif de la classe predite
        tp_d = tp0[None, :, :] - eff_tp.transpose(1, 0, 2)
        fp_d = fp0[None, :, :] - eff_fp.transpose(1, 0, 2)
        macro_d = macro_from_tpfp(tp_d, fp_d)  # (N, M)
        d_jack = macro_d[:, :K].mean(axis=1) - macro_d[:, K:].mean(axis=1)
        t_jk += time.time() - t0
        d_bar = d_jack.mean()
        dev = d_bar - d_jack
        den = (dev ** 2).sum()
        a_hat = float((dev ** 3).sum() / (6 * den ** 1.5)) if den > 0 else 0.0
        # bootstrap : meme tirage de patients pour les deux recettes
        t0 = time.time()
        tp_b = np.zeros((R, n_eval, 2 * K))
        fp_b = np.zeros((R, n_eval, 2 * K))
        for gi, (gs, st) in enumerate(zip(sizes, starts)):
            idx = rng.integers(0, gs, size=(R, gs))
            m = np.bincount((idx + np.arange(R)[:, None] * gs).ravel(),
                            minlength=R * gs).reshape(R, gs)
            cells = preds[:, st]  # (M, gs)
            labs = np.array([y_of_start[st[t]] for t in range(gs)])
            uniform_lab = len(set(labs.tolist())) == 1
            for k in range(2 * K):
                ck = cells[k]
                if uniform_lab:
                    lab_t = labs[0]
                    sel_ok = ck == lab_t if lab_t >= 0 else np.zeros(gs, bool)
                    if sel_ok.any():
                        tp_b[:, lab_t, k] += m[:, sel_ok].sum(axis=1)
                    for c in range(n_eval):
                        if c == lab_t:
                            continue
                        sel = ck == c
                        if sel.any():
                            fp_b[:, c, k] += m[:, sel].sum(axis=1)
                else:  # groupe fusionne : patients de chapitres differents
                    for t in range(gs):
                        lab_t, p_t = labs[t], ck[t]
                        if lab_t >= 0 and p_t == lab_t:
                            tp_b[:, lab_t, k] += m[:, t]
                        elif p_t < n_eval:
                            fp_b[:, p_t, k] += m[:, t]
        t_bs += time.time() - t0
        fn_b = SIZES_EVAL[None, :, None] - tp_b
        denom = 2 * tp_b + fp_b + fn_b
        f1_b = np.where(denom > 0, 2 * tp_b / np.maximum(denom, 1), 0.0)
        macro_b = f1_b.mean(axis=1)  # (R, 2K)
        sel_a = rng.integers(0, K, size=(R, K))
        sel_b = rng.integers(0, K, size=(R, K))
        ma = macro_b[:, :K][np.arange(R)[:, None], sel_a].mean(axis=1)
        mb = macro_b[:, K:][np.arange(R)[:, None], sel_b].mean(axis=1)
        d_star = ma - mb
        lo, hi = np.percentile(d_star, [100 * ALPHA, 100 * (1 - ALPHA)])
        cov_p.append(bool(lo <= 0 <= hi))
        w_p.append(float(hi - lo))
        # BCa
        less = float((d_star < d_hat).mean())
        z0 = probit(min(max(less, 1e-9), 1 - 1e-9))
        za = probit(ALPHA)
        lo_z, hi_z = z0 + za, z0 - za
        a1 = z0 + lo_z / max(1 - a_hat * lo_z, 1e-6)
        a2 = z0 + hi_z / max(1 - a_hat * hi_z, 1e-6)
        al1 = max(0.5 * (1 + erf(min(max(a1, -8), 8) / sqrt(2))), 0.5 / R)
        al2 = min(0.5 * (1 + erf(min(max(a2, -8), 8) / sqrt(2))), 1 - 0.5 / R)
        lo_b2, hi_b2 = np.percentile(d_star, [100 * al1, 100 * al2])
        cov_b.append(bool(lo_b2 <= 0 <= hi_b2))
        w_b.append(float(hi_b2 - lo_b2))
    return {"acc": acc, "rho": rho, "variant": variant, "R": R, "n_outer": n_outer,
            "coverage_percentile": round(float(np.mean(cov_p)), 4),
            "coverage_bca": round(float(np.mean(cov_b)), 4),
            "mean_width_points": round(100 * float(np.mean(w_p)), 2),
            "mean_width_bca_points": round(100 * float(np.mean(w_b)), 2),
            "jackknife_s": round(t_jk, 1), "bootstrap_s": round(t_bs, 1)}


def main():
    t_all = time.time()
    cfg = json.loads(pathlib.Path("/tmp/opencode/glm/g2.cfg.json").read_text())
    rows = []
    for acc in cfg["accs"]:
        for rho in cfg["rhos"]:
            for variant in cfg["variants"]:
                if variant == "merged":
                    R, var = cfg["R_merged"], "merged"
                elif variant == "percentile2000":
                    R, var = 2000, "percentile"
                else:
                    R, var = cfg["R"], "percentile"
                rows.append(one_scenario(acc, rho, cfg["n_outer"], R, cfg["seed"], var))
                print(rows[-1], flush=True)
    print(json.dumps({"runtime_s": round(time.time() - t_all, 1), "params": cfg, "results": rows}, indent=1))


if __name__ == "__main__":
    main()
```

### G5 — `/tmp/opencode/glm/g5_cost.py` (graine 20261002 ; 100 000 tirages par scénario)

```python
#!/usr/bin/env python3
"""G5 - modele de cout du premier cycle avec incertitude (Monte-Carlo).

Entrees mesurees : heures par pli et par epoque (run 20261002-115918-p0-45-budget-hypotheses,
eleves 0,35/0,46/0,63 h ; professeurs 1,58/2,40 et 1,78/2,90 h optimiste/pessimiste) ;
structure des postes de scripts/spikes/budget_v2.py (run 20261002-230546-budget-v3-premier-cycle).

Hypotheses du Monte-Carlo (dites, arbitraires mais bornees par les mesures) :
- facteur de debit f : la mesure a 1 024 tokens surestime le debit sur patients reels ;
  le rapport mesure 1 024 -> 4 096 vaut 1,52 (Gemma-4-31B) et 1,63 (Qwen3.8-27B) ;
  f ~ Uniforme(1,0 ; 1,65) par modele et par iteration, applique a chaque poste du modele ;
- chargements professeurs : 5 a 7 min par chargement (section 5 du protocole), 6 chargements ;
- chargements eleves : non mesures, hors du calcul de base (scenario) ;
- relances : scenario +10 % uniforme ;
- postes non comptes (P2-07, RM-19, P1-07, calibration, inference hors pli...) : scenario constant +10 h.
Sorties par combinaison eleve-professeur : moyenne, p5, p50, p95 du total, P(total > 90 h), P(total > 72 h).
100 000 tirages par scenario. Aucune duree annoncee : distributions et probabilites seulement (RM-16 recale).
"""
import json
import pathlib
import time

import numpy as np

ROOT = pathlib.Path("/mnt/wsl/docker-desktop-bind-mounts/Ubuntu/f5f9e8476e8d13b5f5b3d181fec59f383c00f25d2cf43a1d4f16ba998a6da6a7")
hs = {"Gemma-4-E4B": 0.35, "Qwen3.5-4B": 0.46, "Qwen3.5-9B": 0.63}
ht = {"Gemma-4-31B": 1.58, "Qwen3.8-27B": 1.78}
EPOCHS, DEV_OVER_FOLD, N_MC = 2, 1.2503, 100_000
FOLD_RUNS = 4 + 5 + 1 + 12  # P1-13 + P1-19 + P1-26 + variantes
CONF_RUNS = 20  # 4 recettes x 5 graines


def combo(student, teacher, rng, scenario):
    f_students = {s: 1.0 + 0.65 * rng.random((N_MC, 1)) for s in hs}  # Uniforme(1,0 ; 1,65)
    f_teacher = 1.0 + 0.65 * rng.random((N_MC, 1))
    total = np.zeros((N_MC, 1))
    # criblage : 3 eleves x 2 taux x 2 epoques, un pli
    for s in hs:
        total = total + 2 * 2 * hs[s] * f_students[s]
    # postes eleve de l'eleve choisi
    fs = f_students[student]
    total = total + (FOLD_RUNS * EPOCHS * hs[student]) * fs
    total = total + (CONF_RUNS * EPOCHS * DEV_OVER_FOLD * hs[student]) * fs
    # postes professeur
    total = total + ((1 + 5) * EPOCHS * ht[teacher]) * f_teacher
    # chargements professeurs : 6 x U(5,7) min
    total = total + 6 * (5 + 2 * rng.random((N_MC, 1))) / 60
    if scenario == "relances":
        total *= 1.10
    elif scenario == "non_comptes":
        total = total + 10.0
    return total


def main():
    t0 = time.time()
    rng = np.random.default_rng(20261002)
    out = {}
    for student in hs:
        for teacher in ht:
            for scenario in ("nominal", "relances", "non_comptes"):
                x = combo(student, teacher, rng, scenario).ravel()
                out[f"{student} + {teacher} [{scenario}]"] = {
                    "mean_h": round(float(x.mean()), 1),
                    "p5_h": round(float(np.percentile(x, 5)), 1),
                    "p50_h": round(float(np.percentile(x, 50)), 1),
                    "p95_h": round(float(np.percentile(x, 95)), 1),
                    "p_over_90h": round(float((x > 90).mean()), 3),
                    "p_over_72h": round(float((x > 72).mean()), 3),
                }
    # point de controle : facteurs a 1,0 exactement reproduisent les ancres v3
    anchor = {}
    for student in hs:
        for teacher in ht:
            base = 5.76 + (FOLD_RUNS + CONF_RUNS * DEV_OVER_FOLD) * EPOCHS * hs[student]
            anchor[f"{student} + {teacher}"] = [round(base + 6 * EPOCHS * ht[teacher], 1),
                                                round(base + 6 * EPOCHS * {"Gemma-4-31B": 2.4, "Qwen3.8-27B": 2.9}[teacher], 1)]
    print(json.dumps({"runtime_s": round(time.time() - t0, 1), "anchors": anchor, "results": out}, indent=1))


if __name__ == "__main__":
    main()
```

### G6 — `/tmp/opencode/glm/g6_verdicts.py` (calcul analytique, aucune graine)

```python
#!/usr/bin/env python3
"""G6 - contre-lecture des probabilites de verdict (regle d'ADR-007) et du choix de delta.

Approximation normale identique a celle de l'audit (couche 4.2) et de
scripts/spikes/power_curves.py : sigma = largeur / (2 z), z = 2,3940.
Regles : gain confirme si L > delta (L = d_hat - w/2) ; absence de gain utile si U < delta ;
non resolu sinon. Probabilites sous d_hat ~ N(vrai gain, sigma^2).
"""
import json
from math import erf, sqrt

Z = 2.3940


def cdf(x):
    return 0.5 * (1 + erf(x / sqrt(2)))


rows = []
for delta in (1.5, 2.0, 3.0, 4.0):
    for width in (3.0, 4.0, 5.0, 6.0, 8.0, 10.0):
        sigma = width / (2 * Z)
        row = {"delta": delta, "width": width,
               "seuil_absence_d_hat": round(delta - width / 2, 2)}
        for gain in (0.0, 2.0, 3.0, 4.0, 5.0):
            pc = 1 - cdf((delta + width / 2 - gain) / sigma)
            pa = cdf((delta - width / 2 - gain) / sigma)
            row[f"p_resolu_g{int(gain)}"] = round(pc + pa, 3)
            row[f"p_confirm_g{int(gain)}"] = round(pc, 3)
            row[f"p_absence_g{int(gain)}"] = round(pa, 3)
        rows.append(row)
json.dump(rows, open("/tmp/opencode/glm/g6_rows.json", "w"), indent=1)
```
