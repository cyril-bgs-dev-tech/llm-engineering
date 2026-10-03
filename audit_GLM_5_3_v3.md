# audit_GLM_5_3_v3.md

## 1. En-tête

- **Date** : 03/10/2026. **Modèle** : GLM 5.3 (glm-5.3-flash, via opencode), à la demande de Cyril.
- **Lu pour cette réponse** : le cahier `docs/BRIEF_GLM_v3_actions_par_composante.md` seulement ; il est autonome et aucune pièce jointe n'a été fournie. La session de travail a lu d'autres fichiers du dépôt plus tôt dans la journée (runs du registre, `PROTOCOLE.md`, ADR-007, scripts de simulation, journal) ; **aucun chiffre de cette réponse n'en provient** : chaque chiffre cité ici vient du cahier, ou est marqué « estimation » ou « conjecture ».
- **Nature** : jugement, priorités et pièges, pas une réplique des calculs existants. Rien dans ce fichier n'est une décision : les points marqués « décision de Cyril » restent siens (règle 6 de la section 3 du cahier).
- **Périmètre respecté** : aucune action proposée ne lit le test scellé, n'utilise de données de patient réel, n'exige location de GPU, API payante ou modèle à accès conditionné.

## 2. Synthèse en 10 lignes

1. **Le déficit des LLM contre TF-IDF est probablement un déficit de réglage, pas une conclusion** : le meilleur LLM (Qwen3.5-9B, macro-F1 0,565) n'a été testé qu'à 1e-5 et 1e-4 (bord supérieur de la grille), deux taux sur quatre ; conclure « LLM perdant » maintenant serait l'erreur la plus coûteuse du cycle (C1).
2. **Le déficit restant se concentre sur les chapitres rares** : F1 nulle pour XII, XXI, XXII chez le 9B, alors que l'exactitude est proche (C1) ; la perte d'entropie croisée non pondérée est le suspect numéro un (conjecture, un run pour la tester).
3. **La sauvegarde des adaptateurs est le multiplicateur d'efficience du cycle** : sans elle, chaque analyse (robustesse, calibration, quantification) coûte un réentraînement ; elle est à faire avant la prochaine vague de runs (C5, contrainte écrite dans le cahier).
4. **La règle de puissance (RM-17) décide de ~78 % du budget GPU** et elle est mesurable en quelques secondes de CPU dès que P1-19 a produit ses cinq graines ; tout ce qui la précède est du temps bien investi, tout ce qui la devance (professeur, confirmatoire) est un pari (C2).
5. **RM-14 (+3,87 points [1,27 ; 6,31] entre plis par patient et par auteur) est signalé et non tranché** : le traiter en « simple remarque » serait un piège de crédibilité ; la règle préenregistrée l'a armé exactement pour cela (C3, décision Q18).
6. **L'incertitude n'est mesurée que sur TF-IDF** (ECE 0,029, couverture conforme 0,901) ; les probabilités des LLM ne sont conservées que depuis l'après-midi du 03/10 : la politique d'abstention chiffrée ne peut pas être généralisée aux LLM avant une mesure (C4).
7. **Cinq actions n'exigent aucun GPU et débloquent tout le reste** : sauvegarde des adaptateurs, prédictions par patient avec empreinte, effectifs par pli et par classe, matrice de confusion hiérarchique, front de Pareto qualité/coût sur les runs existants.
8. **Les 5 actions les plus urgentes** : (i) finir le criblage en cours (déjà engagé, fin 19 h 50 UTC) ; (ii) compléter la grille de taux des élèves (2e-5 et 5e-5) ; (iii) sauvegarder les adaptateurs ; (iv) P1-19 (cinq graines + prédictions par patient) ; (v) RM-17 (règle de puissance) puis décision de Cyril sur le design confirmatoire.
9. **Budget** : ~85 h restantes (estimation du cahier) ; le séquencement proposé tient dans B = 90 h uniquement avec l'élève Gemma-4-E4B, ou en acceptant le repli prévu si l'élève choisi est plus gros (protocole, section 5).
10. **Trois vigilances de crédibilité** : ne pas publier une comparaison LLM/TF-IDF avant la grille complète ; ne pas régler sur un maximum de tirages bruités à une graine ; ne jamais ouvrir le test scellé pour « voir » (l'ouverture unique est un engagement, C8).

---

## 3. C1. Performance du modèle

### A. Les 10 actions

| # | Action | Effort (humain + GPU) | Gain attendu | Risque ou conflit | Preuve de fin | Dépend de |
|---|---|---|---|---|---|---|
| A1 | Finir les trois runs de criblage engagés (Gemma-4-E4B 1e-5, Qwen 9B 1e-5, Qwen 4B 1e-4) | 0,1 h + GPU déjà engagé (fin annoncée 19 h 50 UTC) | Criblage P1-11 complet : 3 élèves × 2 taux ; macro-F1 au pli 0 pour chaque cellule | Aucun | Runs `p1-11-*` au registre | Rien |
| A2 | Tester les taux intermédiaires (2e-5, 5e-5) du Qwen3.5-9B au pli 0 | 0,2 h + 2 × 1,2 h GPU (durée réelle du 9B : 4 226 s par run de 2 époques) | Conjecture : le meilleur taux du 9B est entre 1e-5 (0,193, quasi non entraîné) et 1e-4 (0,565, bord de grille) ; gain attendu de 0 à plusieurs points sur 0,565 | Aucun : les quatre taux sont dans la grille figée, c'est du remplissage, pas une extension | Runs dédiés `p1-13-*` ou équivalent, `RESULTATS.md` | A1 |
| A3 | Idem pour Qwen3.5-4B et Gemma-4-E4B (2e-5, 5e-5) | 0,2 h + 4 × 0,7 à 1,0 h GPU (2 515 s et 3 623 s réels par run) | Grille complète des trois élèves ; conjecture de gain sur les deux | Aucun | Runs dédiés | A2 |
| A4 | Analyser par chapitre l'écart TF-IDF contre 9B et classer les chapitres perdants | 0,3 h + 0 GPU (prédictions déjà produites, run `p1-23-*` cité) | Orient le levier 1 (pondération) : la part du déficit portée par XII, XXI, XXII (F1 nulle) et XVIII (F1 0,30 même au TF-IDF) | Aucun | Tableau agrégé dans `RESULTATS.md` | A1 |
| A5 | Lancer un run de référence avec perte pondérée par classe (poids 1/√n), pli 0, deux époques | 0,3 h + 0,7 à 1,2 h GPU | Conjecture : gain concentré sur les chapitres à F1 nulle ; incertitude forte (un seul run, une graine) | Aucun pour une exploration EXPLORE à un run (avis sur Q19 en section 6) ; la famille confirmatoire ne change pas | Run dédié + ligne `RESULTATS.md` | A4 |
| A6 | Diagnostiquer le sous-entraînement de CamemBERT-bio (perte encore en baisse à 0,448) | 0,2 h + 0 GPU : relire la courbe de perte du run existant avant de dépenser | Décide si un run à plus d'époques est justifié | Aucun (diagnostic) | Note au registre | Rien |
| A7 | Si le diagnostic A6 le justifie et sur avis favorable de Cyril : un run CamemBERT-bio à 4 époques | 0,2 h + ~0,5 h GPU (estimation, modèle plus petit) | Conjecture : rattrapage d'une partie des 24,9 points d'écart avec le TF-IDF | **Conflit** : époques fixées à 2 pour toutes les recettes (C6) ; exige un écart consigné (ADR-010) ou une nouvelle version, décision de Cyril | Run + ADR-010 mise à jour | A6, décision de Cyril |
| A8 | Ablation de troncature : fin seule (2 048) contre tête + fin (2 048 + 2 048), 9B au taux retenu | 0,2 h + 1,2 h GPU | Conjecture : la logique « conclusion et diagnostic en fin de document » (protocole, section 1) peut favoriser la fin seule | Aucun (EXPLORE) | Run dédié | A2 (taux retenu) |
| A9 | Sensibilité LoRA : r = 32, alpha = 64, 9B, taux retenu | 0,2 h + 1,2 h GPU | Conjecture : capacité accrue sur 17 classes ; peut aussi accroître le sur-réglage | Aucun (EXPLORE) ; le rang ne fait pas partie des valeurs gelées | Run dédié | A2 |
| A10 | Ensemble TF-IDF × 9B (moyenne de probabilités) évalué sur le pli 0 | 0,3 h + ~0,3 h GPU d'inférence (estimation) | Conjecture : les erreurs des deux familles se recouvrent peu (TF-IDF lexical, LLM sémantique) ; gain potentiel de 1 à 3 points (estimation) | Aucun (EXPLORE, aucun verdict) | Run d'évaluation dédié | A2 |

### B. Conseils d'intégration

- **Ordre** : A1 (en cours) puis A2 et A3 (grille complète) avant toute interprétation ; A4 est un analyse gratuit à faire pendant que les runs tournent ; A5 et A7 n'entrent qu'après A4.
- **Tests d'abord** : la sauvegarde d'adaptateur (voir C5-A1) et le code de pondération (poids par classe) sont du code : écrire le test qui vérifie les poids appliqués (somme des pertes pondérées reproduite à la main sur un lot jouet) avant le run.
- **Portes d'arrêt** : si après grille complète le 9B reste sous le TF-IDF de plus de 10 points, ne pas empiler les ablations (A8, A9) : les réserver à après RM-17, quand le design confirmatoire est connu.
- **Piège de rigueur** : chaque cellule de grille est un maximum de tirages bruités à une graine : traiter le « meilleur taux » comme une hypothèse de travail, pas comme un fait ; le protocole exige d'ailleurs le signalement du bord de grille (section 6.5).
- **Piège de comparaison** : TF-IDF dispose de cinq plis [0,657 ; 0,709], les LLM d'un seul pli : ne jamais écrire « inférieur de X points » sans rappeler que l'un a un intervalle et l'autre pas.
- **Économie du budget** : deux taux par élève suffisent pour le criblage (fait) ; les quatre taux ne sont nécessaires que pour l'élève retenu et la référence (règle d'égalité de budget).
- **Vérification mesurée** : une action « améliore » si la macro-F1 du pli 0 gagne et que le gain survit à un second pli de contrôle (les plis de contrôle groupés existent déjà, section 3 du protocole) ; sinon c'est une conjecture confirmée une fois, à marquer EXPLORE.

### C. Point de vigilance

La chose qui coûterait le plus de crédibilité : publier « les LLM perdent contre TF-IDF » sur la base d'une grille à moitié remplie, avec le meilleur taux au bord supérieur et trois chapitres à F1 nulle non diagnostiqués. La note 3/10 de C1 se corrige par des runs, pas par des phrases.

---

## 4. C2. Rigueur statistique et protocole

### A. Les 10 actions

| # | Action | Effort (humain + GPU) | Gain attendu | Risque ou conflit | Preuve de fin | Dépend de |
|---|---|---|---|---|---|---|
| A1 | Produire les cinq graines de P1-19 avec prédictions par patient et empreinte | 0,5 h + 5 × 0,7 à 1,2 h GPU (≈ 3,5 à 6,3 h, au-dessus du plafond « simple » : découper en 3 graines puis 2) | Variance entre graines de la référence ; la pièce qui manque à toute la suite (RM-17, corrélation d'erreurs, K < 5) | Aucun : P1-19 est préenregistré, l'extension « prédictions par patient » est prévue au protocole (6.3, point 2) | Runs `p1-19-s0` à `s4` + fichiers de prédictions hachés | Rien |
| A2 | Exécuter la règle de puissance RM-17 (10 paires de graines, bootstrap dans le pool du pli 0 aux effectifs du test) | 0,2 h + 0 GPU (CPU, secondes) | Largeur moyenne non arrondie ; verdict réussite ou échec ; conditionne ~78 % des heures de GPU restantes (estimation cohérente avec la structure du budget) | Aucun : la règle 6.3 est écrite et confirmée (C1 de Cyril) | Run au registre + ligne datée de `experiments/INDEX.md` | A1 |
| A3 | Mesurer les effectifs réels par pli et par classe (17 chapitres × 5 plis) | 0,2 h + 0 GPU | Remplace les effectifs proportionnels des simulations de puissance (limite dite dans l'audit v2) ; rend les scénarios RM-17 honnêtes | Aucun (mesure d'agrégats, pas de lecture d'étiquette de test) | JSON dans `results/measures/` | Rien |
| A4 | Ajouter le code de classement automatique des échecs au registre (divergence contre panne, à partir de l'historique de perte) | 0,5 h + 0 GPU | Classement sans jugement après coup ; prévu et non fait (6.4) | Aucun | Code + tests sur cas piégés (perte non finie, mémoire, relance) | Rien |
| A5 | Publier macro-F1 pondérée par chapitre et micro-F1 côte à côte pour chaque run publié | 0,3 h + 0 GPU | Rend visible la sensibilité aux cinq petits chapitres (4 à 9 patients de test) | Aucun (secondaire rapporté) | `RESULTATS.md` | Rien |
| A6 | Pré-enregistrer le gabarit du rapport « non résolu » (ce que le lecteur doit comprendre, avant tout chiffre) | 0,2 h + 0 GPU | Protège contre la réinterprétation après coup d'un « non résolu » en « échec » ou en « victoire » | Aucun | Gabarit dans `experiments/` | Rien |
| A7 | Répliquer la règle de puissance par une deuxième implémentation avant de l'exécuter | 0,3 h + 0 GPU | Le calcul de 6.3 est entièrement spécifié : une réplique indépendante évite un verdict de 78 % du budget sur un bug d'implémentation | Aucun | Script de réplique + écarts consignés | A1 |
| A8 | Analyse bayésienne complémentaire (probabilité postérieure que Δ dépasse δ), étiquetée EXPLORE | 0,5 h + 0 GPU | Lisibilité pour un lecteur non statisticien, en complément, jamais décisionnelle | Aucun (EXPLORE) | Script + run | A1 |
| A9 | Scorecard G-P0 avec preuves immuables (runs, instantanés) | 0,5 h + 0 GPU | Clôture propre de la porte G-P0 | Aucun (après gel, fait) | `scorecards/` suivant le gabarit RM-12 | Gel (fait) |
| A10 | Script d'alerte à 80 % de B (somme des runs du registre contre 72 h) | 0,3 h + 0 GPU | L'alerte prévue (section 5 du protocole) devient automatique au lieu de manuelle | Aucun | Script + test | Rien |

### B. Conseils d'intégration

- **Ordre strict** : A1 avant tout ; A2 et A7 le jour où A1 est complet ; rien du poste professeur (P2-01, P2-02) avant le verdict de RM-17 : c'est la porte la plus rentable du cycle.
- **Tests d'abord** : le code de classement des échecs (A4) exige ses cas piégés écrits avant l'implémentation (le journal des relectures a déjà sanctionné des règles sans test).
- **Portes d'arrêt** : si A1 révèle qu'une graine a divergé, ne pas la remplacer (6.4) : la règle prévoit la présentation « non combiné » ; c'est un résultat, pas un accident à réparer.
- **Piège de rigueur** : la réplique A7 doit être écrite sans lire l'implémentation principale, sinon elle ne prouve rien ; les deux graine-flux doivent être indépendants.
- **Piège de comparaisons multiples** : tout ce qui n'est pas H1 à H3 est EXPLORE (C5 de Cyril) : les trois comparaisons confirmatoires sont figées, n'y ajoute jamais une quatrième après avoir vu des résultats.
- **Économie du budget** : A2 et A7 ne coûtent rien en GPU mais décident de 44,9 à 68,0 h : ils précèdent tout le reste du séquencement.
- **Vérification mesurée** : l'action « améliore la rigueur » si un défaut est trouvé ou si un chiffre cité devient traçable par `run_id` ; une action qui ne trouve rien n'est pas un échec (elle est une preuve).

### C. Point de vigilance

Le piège de crédibilité maximal de C2 : exécuter la règle de puissance sur une implémentation non répliquée et la consigner comme verdict. Une erreur de graine, de paires ou d'effectifs de strate y invalide 78 % du budget en silence.

---

## 5. C3. Données et anti-fuite

### A. Les 10 actions

| # | Action | Effort (humain + GPU) | Gain attendu | Risque ou conflit | Preuve de fin | Dépend de |
|---|---|---|---|---|---|---|
| A1 | Instruire la lecture « fuite dans le texte » de RM-14 : rejouer la comparaison patient/auteur avec les identifiants d'auteur retirés des textes (TF-IDF hors pli, CPU) | 0,3 h + 0 GPU | Si l'écart +3,87 points tombe : la fuite vit dans le texte ; sinon : homogénéité thématique légitime ; tranchera la lecture 1 des trois | Aucun (contrôle sur le développement, jamais le test) | Run de contrôle dédié + `RESULTATS.md` | Rien |
| A2 | Publier la table agrégée auteurs × chapitres (effectifs par cellule, sans identifiant) | 0,2 h + 0 GPU | Explique la concentration du déficit : si les chapitres rares n'ont que 1 à 2 auteurs, la difficulté est structurelle | Aucun (agrégats) | JSON dans `results/measures/` | Rien |
| A3 | Rapporter la sensibilité du contrôle de quasi-doublons au seuil 0,7 (44 paires) sans changer le seuil figé 0,8 | 0,3 h + 0 GPU | Montre que le contrôle ne dépend pas d'un seuil ajusté | Aucun (le seuil gelé ne bouge pas) | JSON de mesure | Rien |
| A4 | Corréler spécialité et chapitre par auteur (la lecture 2 de RM-14 : spécialité seule 0,385 contre auteur seul 0,377) | 0,3 h + 0 GPU | Arbitre l'une des trois lectures avec un chiffre | Aucun | JSON | Rien |
| A5 | Préparer les fiches des deux scénarios Q18 (protocole maintenu avec les deux chiffres rapportés ; plis groupés principaux avec le test non groupé assumé) | 0,5 h + 0 GPU | Décision éclairée, préparée avant que le déficit ne soit observé sur les LLM | Aucun (préparation, aucune règle changée) | Deux fiches préenregistrées hachées | RM-14 (fait) |
| A6 | Lister les patients tronqués (0,2 % du jeu) et leur chapitre | 0,2 h + 0 GPU | Sait si la troncature touche les chapitres rares (XXII : 31 patients au développement) | Aucun (agrégats) | JSON | Rien |
| A7 | Contrôler la cohérence des empreintes du test scellé et des plis depuis le gel (sans aucune lecture du contenu) | 0,2 h + 0 GPU | Prouve qu'aucune partition n'a dérivé depuis le gel | Aucun | Sortie du contrôle existant (`make check`) | Rien |
| A8 | Comparer la composition par classe des plis de contrôle groupés (663 à 763) et des plis stratifiés (717 à 718) | 0,3 h + 0 GPU | Interprète correctement RM-14 (l'écart peut venir des effectifs de plis, pas du groupement) | Aucun | JSON | Rien |
| A9 | Documenter l'estimand du test scellé (« nouveaux patients du même corpus », jamais groupé) dans le gabarit de rapport | 0,2 h + 0 GPU | Évite la surinterprétation d'un chiffre confirmatoire | Aucun | Gabarit | Rien |
| A10 | Étiqueter chaque lecture de RM-14 comme « non tranchée » partout où elle est citée (wiki, RESULTATS) | 0,2 h + 0 GPU | Empêche qu'une des trois lectures ne devienne une affirmation par répétition | Aucun | Pages wiki mises à jour | Rien |

### B. Conseils d'intégration

- **Ordre** : A1, A4 et A8 d'abord (ils fabriquent les faits) ; A5 ensuite (elle consigne les scénarios de décision) ; le reste est du reporting.
- **Tests d'abord** : toute transformation de texte (A1 : retrait d'identifiants) doit avoir un test qui prouve que seuls les identifiants changent (diff contrôlé sur des échantillons fictifs).
- **Portes d'arrêt** : si A1 montre que la fuite vit dans le texte, ne « nettoie » pas le corpus pour faire baisser l'écart : le protocole fige le prétraitement (section 1 : aucune modification du texte) ; l'action produit un chiffre, la décision (Q18) reste celle de Cyril.
- **Piège de rigueur** : RM-14 a été mesuré sur TF-IDF ; l'écart patient/auteur des LLM peut différer (les LLM peuvent mémoriser différemment) : ne transpose pas le +3,87 aux LLM sans mesure.
- **Piège de fuite** : le retrait d'identifiants d'auteur (A1) est une expérience d'analyse, pas un nouveau prétraitement du corpus : les runs officiels gardent le texte intégral gelé.
- **Économie du budget** : aucune action C3 ne consomme de GPU ; elles sont toutes à faire en attendant les runs.
- **Vérification mesurée** : une lecture de RM-14 « tranchée » = un chiffre avec intervalle qui élimine au moins une des trois lectures ; tant que ce n'est pas le cas, elle reste ouverte.

### C. Point de vigilance

La chose la plus dangereuse : laisser traîner RM-14 « signalé mais non interprété » jusqu'à l'ouverture du test scellé. Si le test (jamais groupé) donne des scores alignés sur les plis par patient, et que RM-14 vient contredire cette lecture après coup, c'est toute la chaîne confirmatoire qui paraît optimiste ; instruire maintenant (A1, A4, A8) est la seule protection.

---

## 6. C4. Fiabilité de l'incertitude

### A. Les 10 actions

| # | Action | Effort (humain + GPU) | Gain attendu | Risque ou conflit | Preuve de fin | Dépend de |
|---|---|---|---|---|---|---|
| A1 | Réévaluer ECE et courbes de fiabilité du Qwen3.5-9B sur ses prédictions hors pli (pli 0) | 0,2 h + ~0,3 h GPU d'inférence si nécessaire (estimation) | Premier chiffre de calibration d'un LLM du projet ; comparé au 0,029 du TF-IDF | Aucun (secondaire) | Run d'évaluation dédié | Sauvegarde d'adaptateurs (C5-A1) |
| A2 | Piloter la prédiction conforme LAC sur le 9B hors pli | 0,3 h + ~0,3 h GPU (estimation) | Couverture marginale et par classe du LLM vs 0,901 / 0,904 (min 0,893) du TF-IDF ; conjecture : les chapitres rares du LLM donneront une couverture par classe très inégale | Aucun (P4-04/05 restent les tâches officielles ; ceci est un pilote EXPLORE) | Run + `RESULTATS.md` | A1 |
| A3 | Régler APS pour viser des ensembles de 2 à 3 classes (au lieu de 8 à 12) sur le développement, jamais sur le test | 0,3 h + 0 GPU | Ensembles conformes réellement utiles au passage humain | Aucun (réglage sur développement) | Run de réglage | A2 |
| A4 | Publier la table de politique d'abstention (couverture contre exactitude) pour le LLM | 0,2 h + 0 GPU | Politique de passage à l'humain chiffrée (le TF-IDF donne 0,931 d'exactitude à 70 % de couverture) | Aucun | `RESULTATS.md` | A1 |
| A5 | Mesurer la couverture du LLM sous décalage patient vers auteur (plis groupés) | 0,2 h + ~0,3 h GPU (estimation) | Couverture du LLM sous décalage vs 0,887 / 0,880 du TF-IDF (sous le niveau visé) ; conjecture : le LLM décrochera pareil ou pire | Aucun | Run | A1 |
| A6 | Ajouter les intervalles de Wilson à 95 % par classe et par spécialité à chaque couverture publiée | 0,2 h + 0 GPU | Une couverture par classe avec 4 à 9 patients n'est lisible qu'avec son intervalle | Aucun (le protocole 6.6 exige déjà Wilson) | Code + tests + sorties | Rien |
| A7 | Rendre obligatoire la conservation des probabilités par un test de conformité (les LLM n'ont été conservés qu'à partir du 03/10 après-midi) | 0,2 h + 0 GPU | Aucune mesure perdue à l'avenir ; les analyses C4 deviennent rejouables | Aucun | Test de conformité au registre des contrôles | Rien |
| A8 | Simuler la couverture par classe attendue sur les effectifs du test (17 chapitres, 4 à 174) avant l'ouverture unique | 0,3 h + 0 GPU | Attente chiffrée : quelles classes ne peuvent pas être vérifiées sur le test (4 à 9 patients) ; protège la lecture de RM-20 | Aucun (simulation, aucune étiquette) | Simulation enregistrée au registre | Rien |
| A9 | Courbes de fiabilité par chapitre pour les chapitres d'au moins 16 patients | 0,2 h + 0 GPU | Localise la miscalibration au niveau où l'effectif la permet | Aucun | JSON | A1 |
| A10 | Documenter l'écart d'échangeabilité du test (modèle entraîné sur 100 % du développement, calibration sur 80 %) dans le gabarit de rapport | 0,2 h + 0 GPU | Le protocole 6.6 le dit déjà : le rapport doit le dire aussi | Aucun | Gabarit mis à jour | Rien |

### B. Conseils d'intégration

- **Ordre** : A1 d'abord (tout dépend d'un LLM mesuré) ; A2, A4, A5 ensuite ; A6 et A7 sont transversaux et précèdent tout rapport.
- **Tests d'abord** : le code de Wilson (A6) et la conservation des probabilités (A7) sont du code testé sur cas connus ; le code conforme a déjà ses 14 tests synthétiques : le réutiliser, pas le réécrire.
- **Portes d'arrêt** : si la couverture par classe du LLM est catastrophique sur les chapitres rares, ne pas « réparer » en réglant la fonction de score sur le test : tout le réglage reste sur le développement (protocole 6.6).
- **Piège de rigueur** : l'ECE 0,029 du TF-IDF (« déjà calibré ») ne se transpose pas aux LLM : les probabilités d'une tête de classification LoRA sur 17 classes sous entraîné n'ont aucune raison d'être calibrées ; c'est une mesure à faire, pas un héritage.
- **Piège de sélection** : régler APS (A3) sur le développement et le documenter ; un APS réglé sur le test serait une fuite de l'ouverture unique.
- **Économie du budget** : ces actions coûtent de l'inférence (minutes par évaluation), pas de l'entraînement : elles peuvent s'enchaîner dans une seule session d'inférence du modèle sauvegardé.
- **Vérification mesurée** : une action C4 réussit si un chiffre de couverture ou de calibration existe avec son intervalle et son `run_id` ; « ça semble bien calibré » n'est pas un résultat.

### C. Point de vigilance

La crédibilité se perd ici si la politique d'abstention est chiffrée sur TF-IDF puis présentée comme celle du système : le cahier le dit (les probabilités LLM n'existaient pas avant le 03/10) ; une carte de modèle qui mélangerait les deux serait une affirmation non prouvée au sens du claim-gate.

---

## 7. C5. Analyse d'erreurs et robustesse

### A. Les 10 actions

| # | Action | Effort (humain + GPU) | Gain attendu | Risque ou conflit | Preuve de fin | Dépend de |
|---|---|---|---|---|---|---|
| A1 | Écrire la sauvegarde des adaptateurs dans le script d'entraînement (un point de contrôle par run, empreinte au registre) | 0,5 h + 0 GPU (disque : ~100 à 400 Mo par adaptateur, estimation) | Rend toutes les analyses (C4, C5, C7) possibles sans réentraînement ; lève la contrainte écrite du cahier | Aucun | Test + un run de vérification qui écrit et relit un adaptateur | Rien |
| A2 | Construire la matrice de confusion hiérarchique (17 chapitres regroupés en 13 blocs CIM-10) pour TF-IDF et le 9B | 0,3 h + 0 GPU | Les erreurs deviennent lisibles au niveau où les effectifs existent (les blocs ont des effectifs décents) | Aucun (rapport, pas une métrique primaire) | JSON + page wiki | Prédictions existantes |
| A3 | Localiser les prédictions des chapitres à F1 nulle (XII, XXI, XXII du 9B) : vers quels chapitres vont les erreurs | 0,2 h + 0 GPU | Dirige le levier de pondération (C1-A5) avec un fait, pas une intuition | Aucun | JSON | Prédictions existantes |
| A4 | Perturbations synthétiques (fautes d'orthographe, abréviations) évaluées sur TF-IDF hors pli | 0,5 h + 0 GPU | Première baseline de robustesse, gratuite en GPU | Aucun (EXPLORE) | Run + `RESULTATS.md` | Rien |
| A5 | Idem sur le 9B par inférence seule (adaptateur sauvegardé) | 0,3 h + ~0,5 h GPU (estimation) | Compare la robustesse LLM au TF-IDF | Aucun | Run | A1, A4 (protocole de perturbation) |
| A6 | Relecture de 30 erreurs du 9B au pli 0 (textes fictifs du dépôt, agrégats publiés seulement) | 0,5 h + 0 GPU | Typologie qualifiée des erreurs (chapitres voisins, format, longueur) | Aucun | Note dans `RESULTATS.md` | Prédictions du 9B |
| A7 | Creuser le creux d'exactitude des longueurs moyennes du 9B (0,86 court ; 0,69 moyen ; 0,81 long) par relecture de 20 cas | 0,3 h + 0 GPU | Un creux de 17 points entre court et moyen est suspect (effet de troncature ou de préparation) | Aucun | Note | Rien |
| A8 | Hors-distribution par spécialité exclue (leave-one-specialty-out) sur TF-IDF | 0,5 h + 0 GPU | Fragilité hors distribution mesurée sans GPU | Aucun | Run | Rien |
| A9 | Publier le tableau croisé erreurs × spécialité × longueur (agrégats) | 0,2 h + 0 GPU | Traçabilité de l'analyse d'erreurs | Aucun | Page wiki | A2 à A8 |
| A10 | Gabarit d'analyse d'erreurs réutilisable (script + structure de sortie) pour chaque futur run | 0,3 h + 0 GPU | Chaque run nouveau produit son analyse sans effort refait | Aucun | Script + gabarit | Rien |

### B. Conseils d'intégration

- **Ordre** : A1 est le prérequis de tout le reste (il est écrit noir sur blanc dans le cahier qu'aucune évaluation d'un LLM déjà entraîné n'est possible sans lui) ; A2, A3, A6, A7 ne demandent que des prédictions existantes et peuvent se faire immédiatement.
- **Tests d'abord** : le code de perturbation (A4, A5) doit avoir ses cas de test (perturbation contrôlée, non perturbation des étiquettes) ; une perturbation qui change l'étiquette créerait une fausse baisse.
- **Portes d'arrêt** : ne pas transformer l'analyse d'erreurs en boucle sans fin : A2, A3 et A6 suffisent pour orienter les leviers ; le reste (A7, A8) attend la fin du criblage.
- **Piège de rigueur** : les textes sont fictifs mais le dépôt les traite comme sensibles (règles d'envoi) : les relectures d'échantillons citent des fragments dans les notes internes seulement, jamais dans une sortie hors machine.
- **Piège de comparaison** : la robustesse se compare à budget égal (même perturbation, même échantillon, même partition) : une comparaison TF-IDF/LLM sur des perturbations différentes ne prouve rien.
- **Économie du budget** : toutes les actions GPU de C5 sont de l'inférence (0,5 h au total, estimation) : elles tiennent dans une fenêtre creuse entre deux runs d'entraînement.
- **Vérification mesurée** : chaque action produit un agrégat daté et haché ; l'analyse « améliore » si elle change une décision de design (choix de pondération, choix d'élève) ou révèle un défaut reproductible.

### C. Point de vigilance

Sans la sauvegarde des adaptateurs (A1), toute l'analyse de robustesse des LLM coûtera des réentraînements complets : c'est le seul point de C5 qui, mal fait, gaspille des heures de GPU et rend la comparaison de budgets inégale (un LLM réentraîné pour être réévalué n'est plus la même recette).

---

## 8. C6. Reproductibilité et ingénierie

### A. Les 10 actions

| # | Action | Effort (humain + GPU) | Gain attendu | Risque ou conflit | Preuve de fin | Dépend de |
|---|---|---|---|---|---|---|
| A1 | Scripter et rejouer la reconstruction à froid depuis un clone neuf (clone, `uv sync --frozen`, `make check`, `make smoke`) | 0,5 h + 0 GPU | Le seul test qui prouve le partage du dépôt (P5-09) ; le cahier le liste comme jamais testé | Aucun | Script + mesure consignée (temps, sorties vertes) | Rien |
| A2 | Mesurer le déterminisme GPU (P1-26 : rejeu de la référence, courbes de perte comparées) | 0,2 h + 0,7 h GPU | Le rejeu à l'identique du TF-IDF existe ; celui du GPU non : sans lui, aucun run n'est réellement reproductible | Aucun (prévu) | Run + comparaison chiffrée des pertes | Rien |
| A3 | Mesurer le crochet de commit par étape sur la machine cible, puis déplacer le cache mypy sur un disque rapide | 0,3 h + 0 GPU | ~1 min par commit visée sous ~20 s (estimation) ; le goulot mesuré (audit v2) est mypy à 96 %, entrée-sortie dominante | Aucun : aucun contrôle affaibli, seul l'emplacement du cache change | Mesure avant/après consignée au registre | Rien |
| A4 | Consigner l'empreinte de chaque adaptateur sauvegardé au registre | 0,2 h + 0 GPU | Chaîne complète : run, code, poids | Aucun | Registre | C5-A1 |
| A5 | Créer les pages wiki par composante (C1 à C8) avec preuves à lignes | 0,5 h + 0 GPU | L'état de chaque composante est traçable, ce que le cahier fait à la main aujourd'hui | Aucun | Pages + `check_wiki` vert | Rien |
| A6 | Tester la release sur tag en conditions réelles (tag `v0.1.x`, job de release, artefact vérifié) | 0,3 h + 0 GPU | ADR-008 vérifiée avant d'en dépendre pour un partage réel | Aucun | Tag + release + artefact | Rien |
| A7 | Consigner l'incident tokenizer (3 runs sur 6, cause au journal du noyau, correctif) dans une page wiki d'incidents | 0,2 h + 0 GPU | Mémoire d'incidents réutilisable ; le cahier dit « corrigée », la trace reste à écrire | Aucun | Page wiki | Rien |
| A8 | Programmer l'audit pip-audit en hebdomadaire (Dependabot ne couvre que les actions) | 0,2 h + 0 GPU | Détection des vulnérabilités sans intervention | Aucun | Workflow CI | Rien |
| A9 | Rejouer les tests GPU marqués (`make test-gpu`) sur la RTX 5090 avant le lancement de P2 | 0,2 h + ~0,5 h GPU (estimation) | Le matériel cible est vérifié avant les gros runs (les professeurs QLoRA y passent) | Aucun | Sortie pytest GPU verte | Rien |
| A10 | Documenter les contrats des modules du chemin court (registre, sealed, métriques) dans le wiki | 0,3 h + 0 GPU | Les modules critiques sont lisibles par un relecteur externe | Aucun | Pages wiki | Rien |

### B. Conseils d'intégration

- **Ordre** : A1 et A2 avant P2 (ce sont les deux seuls « jamais testés » listés) ; A3 en parallèle des runs (il ne touche pas au GPU) ; le reste est du reporting de fond de roulement.
- **Tests d'abord** : le script de reconstruction (A1) est lui-même un test : il doit échouer proprement si une dépendance manque (le verrouillage de l'environnement est déjà en place : le vérifier, c'est le but).
- **Portes d'arrêt** : si la reconstruction à froid échoue, ne pas partager le dépôt avant correction (c'est exactement son rôle) ; si le déterminisme GPU échoue, le consigner comme une limite connue (les runs restent traçables, pas bit-à-bit reproductibles).
- **Piège de rigueur** : accélérer le crochet ne doit jamais passer par sauter gitleaks ou réduire le périmètre mypy : la règle du dépôt interdit l'affaiblissement des contrôles ; le cache rapide est la voie sans conflit.
- **Piège de fuite** : la reconstruction à froid utilise le dépôt, jamais les données brutes (elles ne sont pas suivies) : le script doit le prouver.
- **Économie du budget** : A2 est le seul coût GPU de C6 (0,7 h) et il est déjà préenregistré (P1-26).
- **Vérification mesurée** : chaque action C6 produit une mesure avant/après ou un artefact vérifiable ; « plus propre » n'est pas une preuve.

### C. Point de vigilance

Le déterminisme GPU (A2) non mesuré avant P2 créerait le pire scénario : un professeur entraîné en 18 à 29 h de GPU (estimation sur les durées du cahier) dont le rejeu donnerait des poids différents sans explication ; mesuré à l'avance, c'est une limite connue et documentée ; découvert après, c'est une crédibilité perdue.

---

## 9. C7. Efficience et déploiement

### A. Les 10 actions

| # | Action | Effort (humain + GPU) | Gain attendu | Risque ou conflit | Preuve de fin | Dépend de |
|---|---|---|---|---|---|---|
| A1 | Lancer le spike vLLM écrit mais jamais lancé (service en charge sur données synthétiques) | 0,3 h + 1 à 2 h GPU (estimation) | Latence p50/p95 et débit de service mesurés au lieu de manquants | Aucun (EXPLORE, données synthétiques) | Run + mesures | Rien |
| A2 | Mesurer le débit des élèves à 4 096 tokens (mesure manquante explicitée dans le cahier) | 0,2 h + ~0,3 h GPU (estimation) | Borne le cas pessimiste des élèves : le modèle de coût Monte-Carlo n'a aujourd'hui qu'une extrapolation des professeurs | Aucun | Run au registre | Rien |
| A3 | Construire le front de Pareto macro-F1 contre heures GPU à partir des runs existants | 0,3 h + 0 GPU | Rend visible l'arbitrage élève (E4B 0,456, 4B 0,193 à 1e-5, 9B 0,565) contre coûts (2 515 à 4 226 s par run de pli) | Aucun | Figure ou table dans `RESULTATS.md` | A1 de C1 (criblage fini) |
| A4 | Mesurer l'effet de la quantification (NF4 ou INT8) sur le score de l'élève sauvegardé | 0,3 h + ~0,5 h GPU (estimation) | Conjecture : la quantification fait perdre 0 à 2 points de macro-F1 (estimation, littérature générale) ; décide du coût de déploiement | Aucun (EXPLORE) | Run | C5-A1 |
| A5 | Implémenter le regroupement par longueurs (bucketing) pour réduire le remplissage | 0,5 h + 0 GPU de code ; gain mesuré à la volée | Conjecture : +10 à +30 % de débit réel (estimation) ; les patients font ~1 300 tokens pour une fenêtre de 4 096 | Aucun (code, pas une règle du protocole) | Test + mesure avant/après | Rien |
| A6 | Échantillonner la puissance consommée (nvidia-smi) pendant un run de référence | 0,2 h + 0 GPU (mesure passive) | Coût énergétique documenté par run | Aucun | JSON | Rien |
| A7 | Script de surveillance de dérive à l'entrée (prévalence des chapitres, longueurs, signal d'auteur) | 0,5 h + 0 GPU | Alerte future si une nouvelle vague de données dérive | Aucun | Script + test | Rien |
| A8 | Mesurer la latence de bout en bout par patient (préparation + prédiction) | 0,2 h + 0 GPU (lors d'une inférence déjà prévue) | Chiffre de service honnête | Aucun | JSON | A1 |
| A9 | Documenter la politique mémoire des runs P2 (plafond dur 28 Gio du cahier, chargements de 5 à 7 min par professeur) | 0,2 h + 0 GPU | Évite un incident OOM pendant le poste le plus cher | Aucun | Page wiki | Rien |
| A10 | Réduire le temps de chargement des professeurs (chargement paresseux, cache disque local) | 0,3 h + 0 GPU de code | Conjecture : les 5 à 7 min par chargement × 6 chargements ≈ 0,5 à 0,7 h récupérables | Aucun | Mesure avant/après | Rien |

### B. Conseils d'intégration

- **Ordre** : A2 avant RM-16 (la mesure pilote en profitera) ; A1 quand une fenêtre GPU creuse se présente ; A3 dès que le criblage est fini ; le reste en tâche de fond.
- **Tests d'abord** : le bucketing (A5) doit être testé sur lots jouets (mêmes lots, ordres différents, mêmes résultats de perte par pas) avant d'être activé pour un run réel ; une modification de batch subvertit silencieusement la comparaison de budgets.
- **Portes d'arrêt** : le service vLLM (A1) est un spike : il s'arrête après sa mesure et ne tourne pas en continu (la 5090 est déjà partagée avec Ollama, 1,4 Gio signalés au journal).
- **Piège de rigueur** : tout gain de débit mesuré (A5, A10) doit être mesuré sur le même workload avant/après ; un débit mesuré sur un workload différent est une conjecture habillée.
- **Piège de comparaison** : le front de Pareto (A3) mélange des modèles évalués sur des effectifs différents (5 plis pour TF-IDF, pli 0 pour les LLM) : marquer chaque point avec son périmètre d'évaluation.
- **Économie du budget** : C7 ne consomme que ~2 à 3 h de GPU au total (estimation) ; c'est la composante au meilleur ratio preuve/heure de GPU.
- **Vérification mesurée** : chaque chiffre de C7 a son unité, son workload et son `run_id` ; « plus rapide » sans ces trois là ne se publie pas.

### C. Point de vigilance

Le spike vLLM jamais lancé (A1) est le point qui ferait perdre le plus de crédibilité en démo : annoncer un service sans l'avoir jamais démarré serait exactement le type d'affirmation que le claim-gate est écrit pour bloquer.

---

## 10. C8. Sûreté, conformité, honnêteté

### A. Les 10 actions

| # | Action | Effort (humain + GPU) | Gain attendu | Risque ou conflit | Preuve de fin | Dépend de |
|---|---|---|---|---|---|---|
| A1 | Rédiger la carte de modèle provisoire (TF-IDF, CamemBERT-bio, élèves) avec les chiffres du registre, les périmètres d'évaluation et le statut EXPLORE | 0,5 h + 0 GPU | Le document d'honnêteté central ; son absence est listée dans le cahier | Aucun | Carte + passage claim-gate | Rien |
| A2 | Compléter les items TRIPOD-LLM restants (flux des données, effectifs par partition, disponibilité du code) | 0,3 h + 0 GPU | La checklist n'est que partiellement remplie ; les items restants sont descriptifs | Aucun | Page wiki mise à jour | Rien |
| A3 | Publier les sous-groupes au-delà de la spécialité : longueur, auteur (agrégat), chapitre | 0,3 h + 0 GPU | Détection d'iniquité entre sous-groupes dès le premier cycle | Aucun (agrégats) | JSON + wiki | Rien |
| A4 | Consigner les audits indépendants (v2 et v3, ce fichier) dans le wiki avec leurs écarts classés | 0,2 h + 0 GPU | La revue indépendante du cahier (« manque » listé) devient traçable | Aucun (autorisé par Cyril) | Page wiki | Ce fichier |
| A5 | Faire tourner la routine claim-gate (tableau de preuve) avant chaque communication externe, y compris les pages wiki | 0,2 h + 0 GPU par usage | Aucune affirmation non prouvée ne sort | Aucun | Gabarit rempli par communication | Rien |
| A6 | Étiqueter les trois lectures non tranchées de RM-14 dans tout document qui les cite | 0,2 h + 0 GPU | Aucune lecture ne devient une affirmation par répétition | Aucun | Wiki + `RESULTATS.md` | Rien |
| A7 | Tenir un journal des accès au test scellé (qui, quand, quelle fonction) | 0,2 h + 0 GPU | La porte unique devient prouvée par journal, pas seulement par test | Aucun | Journal daté | Rien |
| A8 | Publier d'avance l'attente « non résolu probable » dans `RESULTATS.md` (≈ 12 % de verdict résolu à gain réel de 3 points) | 0,2 h + 0 GPU | Le verdict négatif attendu ne surprendra personne et ne sera pas lu comme un échec | Aucun (déjà écrit au protocole 6.3, point 5) | `RESULTATS.md` | Rien |
| A9 | Vérifier la page des licences pour chaque modèle ajouté au chemin court | 0,2 h + 0 GPU | Conformité suivie au fur et à mesure | Aucun | `docs/LICENCES.md` à jour | Rien |
| A10 | Ajouter une section « ce que nous ne savons pas » au gabarit de chaque rapport public | 0,2 h + 0 GPU | L'honnêteté devient structurelle, pas circonstancielle | Aucun | Gabarit | Rien |

### B. Conseils d'intégration

- **Ordre** : A1 et A2 d'abord (ce sont les deux manques explicitement listés par le cahier) ; A4 dès que ce fichier est déposé ; le reste suit le rythme des communications.
- **Tests d'abord** : aucun code nouveau exigé ; le claim-gate (A5) est un gabarit à remplir, avec preuve par ligne.
- **Portes d'arrêt** : toute communication externe (portfolio, LinkedIn, lettre) passe par le claim-gate ; c'est la seule porte d'arrêt de C8 et elle existe déjà.
- **Piège de rigueur** : la carte de modèle provisoire (A1) doit séparer explicitement ce qui est mesuré sur cinq plis (TF-IDF : intervalle [0,657 ; 0,709]) de ce qui est mesuré sur le pli 0 à une graine (les LLM) : mélanger les deux niveaux de preuve serait l'affirmation la plus fragile du dossier.
- **Piège de fuite** : le journal des accès au test (A7) ne journalise jamais le contenu, seulement l'opération.
- **Économie du budget** : C8 ne consomme aucun GPU ; son coût total est une demi-journée d'écriture.
- **Vérification mesurée** : chaque page C8 vérifiée par les contrôles existants (`check_wiki`, `check_wiki_quotes`, `check_scorecards`) verts.

### C. Point de vigilance

La crédibilité de tout le projet repose sur la frontière EXPLORE/confirmatoire : si une carte de modèle ou une communication présente une moyenne sur le pli 0 à une graine avec l'aura d'un résultat confirmatoire, tout le travail de protocole (9 instantanés, 3 relectures) sera lu comme une coquille décorative.

---

## 11. Synthèse transversale

### 1. Top 10 global et séquencement sur ~85 h de GPU restantes (estimation du cahier)

| Ordre | Action | Composante | GPU | Dépend de |
|---|---|---|---|---|
| 1 | Finir le criblage engagé (3 runs) | C1 | déjà engagé | rien |
| 2 | Sauvegarder les adaptateurs + prédictions par patient avec empreinte (code et tests) | C5, C2 | 0 (disque seulement) | rien |
| 3 | Compléter la grille de taux des élèves (2e-5, 5e-5, trois élèves) | C1 | 5,6 à 7,6 h (estimation, 6 runs) | ordre 1 |
| 4 | P1-19 : cinq graines de la référence + classement automatique des échecs | C2, C6 | 3,5 à 6,3 h | ordre 3 (référence réglée) |
| 5 | Effectifs par pli et par classe + réplique de la règle de puissance | C2 | 0 | rien (en parallèle) |
| 6 | RM-17 : règle de puissance, puis décision de Cyril (design confirmatoire ou EXPLORE) | C2 | 0 (CPU) | ordres 4 et 5 |
| 7 | Leviers sur la référence : perte pondérée (si avis Q19 favorable), ablation de troncature, sensibilité LoRA | C1 | 3 à 5 h (estimation) | ordre 3 |
| 8 | Mesures pilotes : débit élèves à 4 096 tokens, déterminisme GPU (P1-26), recale du budget (RM-16) | C7, C6 | ~1,5 h (estimation) | ordre 2 |
| 9 | Professeur : réglage (P2-01) puis cinq plis (P2-02), 6 chargements compris | C1, C7 | 18,9 à 32,6 h (estimation : 15,8 à 29,0 + chargements) | ordre 6 (verdict de la règle de puissance) |
| 10 | Confirmatoire P3-07 (si la règle réussit) ou bascule EXPLORE consignée ; ouverture unique RM-20 seulement à la fin | C2, C8 | 17,5 à 31,5 h | ordre 9 |

Total de la séquence : ~49 à 90 h de GPU (estimation) ; tient dans B = 90 h avec l'élève Gemma-4-E4B, sous réserve du verdict RM-17 (le protocole prévoit le repli sinon, section 5).

### 2. Les trois leviers, à effort égal, pour la macro-F1 des LLM

1. **Pondération de la perte par classe (1/√n)** : cible directe du déficit concentré (F1 nulle sur XII, XXI, XXII) ; un run au pli 0 pour la tester (conjecture : le gain vient surtout de ces trois chapitres et de XVIII ; risque : dégrader les chapitres dominants).
2. **Grille de taux complète** : le meilleur LLM n'a vu que les deux bords de la grille (0,193 à 1e-5, quasi non entraîné ; 0,565 à 1e-4, bord supérieur) ; les deux taux intermédiaires manquent et sont dans la grille figée ; c'est le levier le plus certain (les runs sont déjà chiffrés : 1,0 à 1,2 h chacun).
3. **Durée d'entraînement (époques)** : la perte de CamemBERT-bio est encore en baisse à 2 époques ; le même signe de sous-entraînement peut toucher les élèves au taux bas ; **conflit assumé** : les époques sont gelées à 2 (C6) ; le levier exige un écart consigné (ADR-010) ou une nouvelle version, à trancher par Cyril avant P1-20, pas après un résultat.

### 3. Avis sur les trois décisions ouvertes

- **Q15 (log loss équilibrée par chapitre comme co-critère confirmatoire)** : avis favorable au **maintien en secondaire**. Trois raisons chiffrées : (a) la log loss sur des chapitres de 4 à 9 patients de test est dominée par ces effectifs, sa variance dépasse celle de la macro-F1 que la simulation place déjà à 7,4 à 14,3 points de large ; un co-critère doublerait la famille (m = 6) et ferait passer le niveau Bonferroni de 98,33 à 99,17 %, aggravant le « non résolu » ; (b) le verdict confirmatoire est déjà en trois valeurs et apparié : un second critère créerait des verdicts divergents difficiles à publier ; (c) la sensibilité aux chapitres rares est déjà rendue visible par les recommandations C2-A5 (macro pondérée contre micro) et C1-A4 (analyse par chapitre), sans toucher à la famille. Le changer après avoir vu des résultats serait exactement le piège de latitude après coup que le protocole interdit.
- **Q18 (protocole gelé avec les deux chiffres rapportés, contre plis groupés principaux)** : avis favorable au **protocole maintenu pour le premier cycle, avec les deux chiffres rapportés et une ADR préparée** (C3-A5). Raisons : (a) le test scellé, jamais groupé, estime « de nouveaux patients du même corpus » : c'est un estimand défendable, écrit avant les données ; le basculer maintenant produirait un test groupé incohérent (les patients du test partagent leurs auteurs avec le développement) ou un re-tirage qui détruit l'actif scellé ; (b) RM-14 est signalé sur TF-IDF seul (+3,87 [1,27 ; 6,31]) : la transposition aux LLM n'est pas mesurée ; l'ADR mérite d'attendre cette mesure (elle est peu coûteuse : pli 0 et plis de contrôle existent) ; (c) la règle préenregistrée (section 3 du protocole) prévoyait le basculement si le raccourci est signalé : l'outiller en ADR préparée (C3-A5) honore la règle sans brûler le cycle.
- **Q19 (perte pondérée 1/√n : modification de la référence ou exploration légitime)** : avis favorable à l'**exploration légitime à un run, étiquetée EXPLORE** (C1-A5), sous deux conditions : (a) la famille confirmatoire (H1, H2, H3) ne change pas : si un jour une recette pondérée entre en comparaison confirmatoire, c'est une nouvelle famille ou une nouvelle référence, donc une nouvelle version du protocole et une ADR (règle 5 de 6.10) ; (b) la règle d'égalité de budget de réglage s'applique dès que deux recettes sont comparées, même en EXPLORE. Le protocole gelé ne décrit la perte de la référence que par sa configuration de réglage (section 6.5) ; un run d'exploration pondérée n'y touche pas tant qu'aucun verdict n'en est tiré et que le run est enregistré.

### 4. Trois erreurs que l'auditeur ferait à votre place

1. **Conclure « les LLM perdent contre TF-IDF » sur l'état actuel du criblage** : deux taux sur quatre, le meilleur au bord supérieur, une graine, un pli ; cette phrase, publiée maintenant, serait à dédire dans quinze jours et coûterait la crédibilité exacte que le projet cherche à prouver. La bonne formulation actuelle : « sous-réglé et non diagnostiqué » (voir C1).
2. **Confier la décision d'élève (P1-12) au seul maximum de la grille à une graine et un pli** : c'est le maximum de quatre tirages bruités ; le piège associé est de le traiter ensuite comme un fait. L'atténuation est peu coûteuse : rejouer les deux meilleurs taux sur un second pli (2 runs, ~2 h, estimation) avant P1-20 ; si le classement s'inverse, le choix au bord de grille signalé l'est pour une bonne raison.
3. **Généraliser au LLM les chiffres d'incertitude mesurés sur TF-IDF** (ECE 0,029, couverture conforme 0,901, sélectivité 0,931 à 70 %) : les probabilités des LLM n'existaient même pas au registre avant le 03/10 après-midi ; une carte de modèle ou une politique d'abstention qui hériterait implicitement de ces chiffres serait une affirmation sans preuve au sens du claim-gate. La mesure LLM (C4-A1) coûte moins d'une heure de GPU (estimation) et il faut la faire avant toute politique.

---

## 12. Ce que je n'ai pas pu vérifier

- Les notes d'auto-évaluation (projet 5,0 ; libre 7,6 ; absolu 9,4) : le cahier les marque déjà « estimation, non confirmée indépendamment » ; je n'ai pas contesté les notes faibles (C1, C5, C7), que les preuves citées rendent plausibles, mais je n'ai pas de base pour les valider à plus ou moins 1 point.
- Les trois runs de criblage en cours : leurs résultats n'existaient pas au moment de la lecture (fin annoncée 19 h 50 UTC) ; l'action C1-A1 suppose qu'ils finissent.
- Le budget restant (~85 h) : estimation du cahier, dépendante des heures déjà consommées que je n'ai pas recomptées.
- L'état exact de la sauvegarde des probabilités LLM « depuis l'après-midi du 03/10 » : je n'ai pas vu le mécanisme ; l'action C4-A7 suppose qu'il existe et a besoin d'un test.
- La cause précise du creux d'exactitude des longueurs moyennes (0,69) du 9B : le chiffre vient du cahier, l'explication est à instruire (C5-A7).
- Les effectifs réels par pli et par classe : absents du cahier (les simulations citées les supposent proportionnels) ; l'action C2-A3 existe pour cela.
- La dénomination exacte des runs du registre cités par le cahier dans son tableau de preuve (par exemple `p1-23-errors-p1-11-*`) : je reprends les noms du cahier sans avoir vérifié chaque `run_id`.

## 13. Tableau de preuve de ma réponse

| Chiffre ou affirmation de ce fichier | Source |
|---|---|
| Effectifs (4 254, 4 219, 633, plis 717 à 718, 17 classes, petits chapitres 4 à 9 au test, 31 au développement) | cahier, § 2 et § 4 (C1) |
| TF-IDF 0,684 [0,657 ; 0,709] ; v2 0,689 ; planchers 0,025 / 0,058 | cahier, § 4 (C1, tableau) |
| CamemBERT-bio 0,448 (taux 1e-4, bord) ; écart −24,9 [−30,3 ; −17,9] ; perte en baisse | cahier, § 4 (C1) |
| Qwen3.5-4B 0,193 ; E4B 0,456 (+0,7 [−3,2 ; +4,4] vs CamemBERT) ; 9B 0,565 (exactitude 0,788 ; TF-IDF 0,818) ; écart 9B vs TF-IDF −13,2 [−18,4 ; −7,0] | cahier, § 4 (C1) |
| F1 nulle XII, XXI, XXII chez le 9B ; XVIII 0,30 au TF-IDF | cahier, § 4 (C1, faits a et c) |
| Recette actuelle (r = 16, alpha 32, dropout 0,05, bf16, lot 32, 4 096 tokens, 2 époques, CE non pondérée, une graine, 2 taux testés) | cahier, § 4 (C1, fait b) |
| Trois runs de criblage restants, fin 19 h 50 UTC | cahier, § 4 (C1, fait d) |
| Protocole gelé, 9 instantanés, 3 relectures, bootstrap testé (7 mutations sur 7), couverture 99,4 à 100 %, largeurs 7,4 à 14,3 (test) et 3,8 à 6,7 (plis) | cahier, § 4 (C2) |
| RM-14 : +3,87 [1,27 ; 6,31] ; groupé 0,646 ; auteur seul 0,377 contre spécialité 0,385 | cahier, § 4 (C3) |
| ECE 0,029 ; LAC 0,901 marginal, une classe jamais couverte, 0,904 par classe (min 0,893), 2,57 classes par ensemble ; APS 8 à 12 classes ; sélectif 0,931 à 70 % (0,818 à 100 %) ; décalage 0,887 / 0,880 | cahier, § 4 (C4) |
| Exactitude par longueur 0,86 / 0,69 / 0,81 (9B) | cahier, § 4 (C5) |
| Aucun point de sauvegarde d'adaptateur écrit par le script d'entraînement | cahier, § 4 (C5, contrainte technique) |
| 245 tests, 58 runs, 12 ADR, wiki de 15 pages, TF-IDF déterministe ; reconstruction à froid jamais testée ; P1-26 à venir ; crochet ~1 min (mypy, NTFS) ; incident tokenizer 3/6 | cahier, § 4 (C6) |
| Pics mémoire (11,5 à 26,4 Gio) ; durées réelles 2 515 / 3 623 / 4 226 s (2 époques, 2 869 patients) ; de 0 à 27 % sous ou +12 % des projections ; flash-linear-attention ; vLLM écrit jamais lancé | cahier, § 4 (C7) |
| TRIPOD-LLM partiel ; claim-gate ; négatifs publiés ; trois prédictions fausses consignées ; carte de modèle, revue indépendante, sous-groupes : manquants | cahier, § 4 (C8) |
| δ = 2,0 ; K = 5 ; B = 90 h ; N = 4 ; 2 époques ; R = 10 000 ; IC 98,33 % ; 12 % de verdict résolu à gain réel de 3 ; 1,7 % à gain égal à δ | cahier, § 2 et tableau de preuve |
| Durées par run converties en heures (0,7 / 1,0 / 1,2 h) | arithmétique sur les durées du cahier (2 515 / 3 623 / 4 226 s) |
| Coûts GPU des actions non mesurées ci-dessus (grille, P1-19, professeur, confirmatoire, ablations, quantification, vLLM, énergie) | estimation (dérivée des durées réelles citées ou de la littérature d'usage, marquées dans les tableaux) |
| Gains attendus des actions marquées « conjecture » | conjecture (raison donnée dans la cellule) |
| Notes 5,0 / 7,6 / 9,4 ; budget restant ~85 h | cahier, § 4 et tableau de preuve (marqués estimation) |
| Le crochet de commit : mypy ~96 % du temps mur, entrée-sortie dominante | session de ce jour (audit `audit_GLM_5_3_v2.md`, G4, déposé au dépôt) |
