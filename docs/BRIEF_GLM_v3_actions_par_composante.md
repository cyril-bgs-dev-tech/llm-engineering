# Cahier d'audit pour GLM : les 10 actions les plus rentables par composante

Version du 03/10/2026. Ce document est **autonome** : tout ce dont GLM a besoin est dedans. Aucune pièce jointe n'est obligatoire. Aucune donnée de patient réel, aucun texte clinique : seulement des effectifs agrégés, des mesures et des noms de fichiers. À envoyer à GLM **seulement sur décision de Cyril** (envoi hors machine) ; l'assistant ne l'envoie pas.

## 1. Rôle demandé

**Format de réponse : un fichier Markdown (`.md`) unique, rien d'autre** (ni PDF, ni tableur, ni texte libre en plusieurs messages). Si tu ne peux pas joindre de fichier, réponds par **un seul bloc de code Markdown** contenant le fichier entier, que Cyril copiera dans `audit_GLM_5_3_v3.md`.

Tu es **auditeur méthodologique et ingénieur senior** indépendant. Pour **chacune des 8 composantes** du projet décrites en section 4, tu proposes **les 10 actions les plus simples à réaliser et qui apportent le plus de valeur** pour améliorer nos résultats, puis des **conseils concrets pour les intégrer avec efficience et rigueur**. Tu n'as pas à refaire les calculs déjà faits (ils sont fournis) ; on attend du **jugement**, des **priorités** et des **pièges évités**, pas une réplique de ce qui existe.

## 2. Le projet en dix lignes

- **But** : mesurer ce que chaque technique d'adaptation apporte vraiment à un classifieur de textes cliniques français : référence (LoRA réglée), distillation d'un gros professeur vers un petit élève (H1), pré-entraînement sur une tâche voisine (H2), les deux (H3).
- **Données** : PARHAF, comptes rendus cliniques **fictifs** en français (4 254 patients ; jeu de travail 4 219 ; test scellé 633 ; 5 plis de 717 à 718). Aucune donnée de patient réel.
- **Tâche principale** : prédire le **chapitre CIM-10** du diagnostic principal : 21 chapitres présents, 4 rares fusionnés dans `AUTRE`, **17 classes évaluées**, `AUTRE` exclue de la moyenne. Plus petit chapitre : 31 patients au développement, 4 au test (chapitre XXII ; autres petits : XII 6, XXI 7, IV 9, V 9).
- **Métrique primaire gelée** : macro-F1 sur 17 chapitres. Seuil utile δ = 2,0 points ; K = 5 graines (`1000 + k`) ; budget B = 90 h de GPU ; N = 4 taux d'apprentissage (1e-5, 2e-5, 5e-5, 1e-4, une graine, **grille jamais étendue**) ; **2 époques pour toutes les recettes**.
- **Matériel** : une RTX 5090 (32 Gio, plafond de sécurité 28 Gio), 32 threads, 68 Gio de RAM, disque ext4 limité ; pas de location de GPU, pas d'API payante.
- **Méthode** : tout est préenregistré (fiches `experiments/*.md` hachées par SHA-256 avant le premier run), registre de runs en écriture unique, test scellé ouvert **une seule fois** en deux temps, verdict en trois valeurs (gain confirmé, absence de gain utile, non résolu) par bootstrap hiérarchique apparié (patients stratifiés par classe, même tirage pour les deux recettes ; graines tirées indépendamment par recette ; R = 10 000 ; IC 98,33 % par Bonferroni sur 3 hypothèses).
- **Statut** : phase P1 (références et criblage). Le premier cycle est classé **EXPLORE** : à δ = 2,0 et avec la largeur d'intervalle simulée, un vrai gain de 3 points n'est confirmé que dans environ 12 % des cas et un gain exactement égal à δ jamais (1,7 %).
- **Auteur** : un seul ingénieur, aidé d'un assistant de code ; objectif secondaire : démontrer la rigueur de méthode.
- **Langue** : documentation en français, code en anglais.

## 3. Règles que toute action proposée doit respecter (sinon, dis-le et propose une variante)

1. **Le protocole gelé ne se modifie pas en silence** : toute règle changée = nouvelle version du protocole + ADR + décision de Cyril. Dis explicitement si une action l'exige.
2. **Le test scellé n'est jamais lu** avant son ouverture unique (aucune action ne peut s'appuyer dessus).
3. **Pas de donnée de patient réel**, pas de location de GPU, pas d'API payante, pas de modèle à accès conditionné non accepté.
4. **Toute affirmation chiffrée renvoie à un run du registre** ; les résultats négatifs sont publiés.
5. **Simple** = au plus **une demi-journée de travail humain ou assistant et au plus 3 h de GPU** par action ; sinon, découpe-la.
6. Les décisions de la section 6 appartiennent à Cyril : donne un avis, ne tranche pas.

## 4. Les 8 composantes : état actuel et preuves

Notes sur 10 de l'auto-évaluation (estimation de l'assistant, non confirmée indépendamment ; à plus ou moins 1 point) : **projet 5,0 en moyenne**, contre 7,6 pour le meilleur du libre et 9,4 pour le meilleur absolu, estimés par composante. Tu peux **contester ces notes** si une preuve ci-dessous les contredit.

**Ces 8 composantes sont exactement les 8 critères de notation de la dernière page de la présentation du projet** (mêmes noms, mêmes notes). Correspondance avec les douze catégories de qualité Q1 à Q12 de la spécification interne, au cas où tu les croises : C1 Performance (hors Q, ajoutée pour juger les résultats) ; C2 = Q2 (protocole) + Q3 (validité statistique) ; C3 = Q1 (données) ; C4 = Q5 (incertitude) ; C5 = Q4 (erreurs et robustesse) ; C6 = Q6 (reproductibilité) + Q7 (ingénierie) ; C7 = Q8 (efficience) + Q9 (déploiement) ; C8 = Q10 (sûreté et éthique) + Q11 (documentation) + Q12 (honnêteté scientifique).

### C1. Performance du modèle (note 3 ; libre 8 ; absolu 9)

| Mesure (pli 0 sauf mention) | macro-F1 | Remarque |
|---|---|---|
| Classe majoritaire / tirage selon prévalence | 0,025 / 0,058 | planchers |
| **TF-IDF + régression logistique** (5 plis) | **0,684** [0,657 ; 0,709] | C = 100, bord de grille ; grille étendue : 0,689 (différence non résolue) |
| CamemBERT-bio affiné, 2 époques | 0,448 (taux 1e-4, bord de grille) ; 0,067 ; 0,279 ; 0,427 aux taux plus bas | **24,9 points sous le TF-IDF** [−30,3 ; −17,9], sous-entraîné (perte encore en baisse) |
| Qwen3.5-4B LoRA 1e-5 | 0,193 | taux le plus bas |
| Gemma-4-E4B LoRA 1e-4 | 0,456 | non distinct du CamemBERT-bio (+0,7 point [−3,2 ; +4,4]) |
| **Qwen3.5-9B LoRA 1e-4** | **0,565** | exactitude 0,788 (TF-IDF 0,818) ; 13,2 points sous le TF-IDF [−18,4 ; −7,0] |

Faits utiles : (a) **le déficit des LLM est concentré sur les chapitres rares** : F1 nulle pour XII (6 patients au pli 0), XXI (8), XXII (5) chez le 9B, alors que l'exactitude est proche ; (b) recette actuelle : LoRA r = 16, alpha 32, dropout 0,05, bf16, lot effectif 32, 4 096 tokens (tête 2 048 + fin 2 048), 2 époques, échauffement 20 pas puis cosinus, perte d'entropie croisée **non pondérée**, une graine, deux taux seulement (1e-5 et 1e-4) ; (c) chapitre le plus difficile pour tous : XVIII (symptômes non classés ailleurs), F1 0,30 au TF-IDF ; (d) trois runs de criblage restent (Gemma 1e-5, Qwen 9B 1e-5, Qwen 4B 1e-4), fin vers 19 h 50 UTC.

### C2. Rigueur statistique et protocole (note 7 ; libre 8 ; absolu 9)

Protocole gelé en 9 instantanés SHA-256, 3 relectures adversariales, bootstrap hiérarchique codé et testé (7 mutations manuelles sur 7 détectées), couverture de l'intervalle simulée sur les effectifs réels (99,4 à 100 % sous l'hypothèse nulle), puissance simulée (largeur d'IC 98,33 % de 7,4 à 14,3 points sur le test, 3,8 à 6,7 sur les plis 1 à 4). **Faiblesses** : une seule graine au développement, un seul pli pour le réglage, premier cycle non confirmatoire, règle de puissance à RM-17, aucune mesure de variance entre graines encore (P1-19 à venir).

### C3. Données et anti-fuite (note 6 ; libre 8 ; absolu 10)

Découpage stratifié par patient, quasi-doublons (seuil 0,8, 9 paires toutes du même auteur gardées dans la même partition), test scellé à porte unique. **Constat nouveau (RM-14)** : macro-F1 du TF-IDF **0,684 avec plis par patient contre 0,646 avec plis groupés par auteur** : écart **+3,87 points [+1,27 ; +6,31]**, « signalé » par la règle préenregistrée (v2 avec grille étendue : +3,42 [+1,17 ; +5,78]). Trois lectures non tranchées : fuite par auteur, recouvrement thématique légitime (l'auteur seul prédit le chapitre aussi bien que la spécialité seule : 0,377 contre 0,385), artefact de découpage. Le test scellé est stratifié par patient, **jamais groupé**.

### C4. Fiabilité de l'incertitude (note 4 ; libre 7 ; absolu 9)

Mesuré sur le TF-IDF seulement, validation croisée par pli, développement : ECE 0,029 (déjà calibré, température 0,95, la recalibration n'améliore rien) ; conforme LAC à 90 % : couverture marginale 0,901 mais **une classe jamais couverte**, par classe 0,904 (minimum 0,893) avec 2,57 classes par ensemble ; APS trop large (8 à 12 classes) ; prédiction sélective : exactitude 0,931 à 70 % de couverture (0,818 à 100 %) ; **sous décalage patient vers auteur, couverture 0,887 (marginal) et 0,880 (par classe)**, sous le niveau visé. Code testé sur données synthétiques (14 tests). **Manque** : mesure sur les LLM (leurs probabilités n'ont été conservées qu'à partir du 03/10 après-midi), politique d'abstention chiffrée, hors-distribution, couverture sur le test (prévue dans l'ouverture unique, avec Wilson).

### C5. Analyse d'erreurs et robustesse (note 3 ; libre 7 ; absolu 9)

Fait : erreurs par classe, confusions principales, spécialité et tercile de longueur pour le TF-IDF et deux LLM (exactitude par longueur : court 0,86, moyen 0,69, long 0,81 pour le 9B). **Manque** : perturbations (fautes, abréviations, bruit, troncature), hors-distribution par spécialité exclue, matrice de confusion hiérarchique, relecture d'échantillons. **Contrainte technique** : aucun point de sauvegarde d'adaptateur n'est écrit par le script d'entraînement, donc aucune évaluation sur un LLM déjà entraîné sans le réentraîner.

### C6. Reproductibilité et ingénierie (note 7 ; libre 8 ; absolu 9)

245 tests, typage strict, analyse statique, détection de secrets à chaque commit, garde contre l'affaiblissement des règles de qualité, registre append-only (58 runs), 12 ADR, wiki de 15 pages à citations vérifiées, environnement verrouillé, TF-IDF rejoué à l'identique (déterminisme confirmé). **Faiblesses** : reconstruction à froid jamais testée, déterminisme des runs GPU non mesuré (P1-26 à venir), crochet de commit lent (environ 1 min, mypy domine, entrée-sortie du disque NTFS), un incident de plantage du tokenizer sur 3 runs de 6 (cause trouvée au journal du noyau, corrigée).

### C7. Efficience et déploiement (note 3 ; libre 8 ; absolu 10)

Mesuré : pic de mémoire réservé à 4 096 tokens en LoRA (Qwen3.5-4B 11,5 Gio ; Qwen3.5-9B 19,7 à 21,6 ; Gemma-4-E4B 19,8 à 24,8 ; Gemma-4-31B QLoRA 26,4), débit moyen 0,54 / 0,87 / 0,65 s par exemple (durées réelles de 2 515 s, 3 623 s, 4 226 s pour 2 époques sur 2 869 patients, de 0 à 27 % sous ou +12 % par rapport aux projections), flash-linear-attention accélère les Qwen3.5 hybrides. **Manque** : latence p50 et p95, effet de la quantification sur le score, énergie ou coût, front de Pareto qualité contre coût, service testé en charge (spike vLLM écrit, jamais lancé), surveillance de dérive.

### C8. Sûreté, conformité, honnêteté (note 7 ; libre 7 ; absolu 9)

Aucune donnée réelle, checklist TRIPOD-LLM partiellement remplie, porte « claim-gate » (tableau de preuve avant toute sortie), résultats négatifs consignés dans `RESULTATS.md`, trois prédictions de fiches fausses consignées. **Manque** : carte de modèle, revue indépendante du code et des statistiques, sous-groupes rapportés au-delà de la spécialité.

## 5. Ce qui est demandé, composante par composante

Pour **chacune des 8 composantes** C1 à C8, rends :

**A. Les 10 actions**, dans un tableau avec exactement ces colonnes :

| # | Action (une phrase, verbe d'action) | Effort (heures humain + heures GPU) | Gain attendu (quelle mesure, de combien, avec quelle incertitude) | Risque ou conflit avec le protocole gelé (aucun, ou lequel) | Preuve de fin (commande, fichier ou run qui montre que c'est fait) | Dépend de |

Ordonne par **valeur divisée par effort**, décroissant. Chaque action doit être exécutable seule. Si un gain est une conjecture, écris « conjecture » et pourquoi.

**B. Les conseils d'intégration** (5 à 8 puces par composante) : dans quel **ordre**, avec quels **tests écrits d'abord**, quelles **portes d'arrêt**, quels **pièges de rigueur** (fuite de test, sélection sur le test, comparaisons multiples, comparaison de budgets inégaux, optimisme d'un maximum de plusieurs tirages bruités), comment **éviter de gaspiller les 90 h** de GPU, comment **vérifier qu'une action a vraiment amélioré** (critère mesuré, pas ressenti).

**C. Un point de vigilance** par composante : la chose qui, mal faite, ferait perdre le plus de crédibilité.

## 6. Synthèse transversale demandée à la fin

1. **Top 10 global** (toutes composantes confondues) des actions à faire en premier, avec **séquencement** sur le budget restant : environ 85 h de GPU et quelques jours de travail. Montre les dépendances (par exemple : enregistrer les adaptateurs avant toute analyse de robustesse).
2. **Les trois leviers** qui, à effort égal, améliorent le plus la macro-F1 des LLM (hypothèses causales à tester, pas des promesses), en tenant compte du fait que le déficit est concentré sur les chapitres rares.
3. **Avis sur trois décisions ouvertes** (ce sont celles de Cyril, tu donnes un avis argumenté, pas une décision) :
   - Q15 : ajouter la différence appariée de log loss équilibrée par chapitre comme co-critère à la macro-F1 confirmatoire, ou la garder en secondaire ?
   - Q18 : après l'écart patient contre auteur, garder le protocole gelé (en rapportant les deux chiffres) ou passer à des plis groupés par auteur au prix d'un test scellé non groupé ?
   - Q19 : une perte pondérée par classe (poids en 1/√n) est-elle une modification de la référence qui exige une nouvelle version du protocole, ou une exploration légitime à un run ?
4. **Trois erreurs que tu ferais à notre place** : les décisions de méthode les plus risquées parmi celles déjà prises.

## 7. Format de réponse imposé : un seul fichier Markdown

Réponds par **un fichier `.md` unique nommé `audit_GLM_5_3_v3.md`**, que Cyril déposera à la racine du dépôt. Structure :

1. **En-tête** : date, version de modèle, ce que tu as lu (ici : ce cahier seulement, sauf pièces jointes que tu cites par nom).
2. **Synthèse en 10 lignes** : les 5 constats les plus importants et les 5 actions les plus urgentes.
3. **Sections C1 à C8**, chacune avec A (tableau de 10 actions), B (conseils), C (point de vigilance).
4. **Synthèse transversale** (section 6).
5. **Ce que tu n'as pas pu vérifier** : section obligatoire, même vide.
6. **Tableau de preuve de ta propre réponse** : pour chaque chiffre que tu cites ou calcules, la source dans ce cahier, ou « estimation » si c'en est une.

**Règles de rédaction** : français, sans tiret cadratin ; chaque chiffre vient de ce cahier ou est marqué « estimation » ; ne propose pas d'action qui lit le test scellé ou qui exige des données réelles ; si une action n'est pas « simple » au sens de la section 3, découpe-la ; ne conclus pas par une question.

## 8. Prompt d'envoi, prêt à coller (avec ce fichier)

> **Réponds uniquement par un fichier Markdown (.md) unique** (ou, à défaut, un seul bloc de code Markdown contenant tout le fichier). Tu es auditeur méthodologique et ingénieur senior indépendant. Lis le cahier `BRIEF_GLM_v3_actions_par_composante.md` (autonome, aucune autre pièce n'est nécessaire). Pour chacune des 8 composantes décrites en section 4, donne les 10 actions les plus simples et de plus forte valeur, puis des conseils d'intégration rigoureux, et la synthèse transversale de la section 6. Respecte strictement les règles de la section 3 et le format de la section 7 : un unique fichier `audit_GLM_5_3_v3.md`, en français, sans tiret cadratin, avec la section « Ce que tu n'as pas pu vérifier » et le tableau de preuve de ta propre réponse. Ne refais pas les calculs fournis ; apporte du jugement, des priorités et des pièges évités.

## 9. Tableau de preuve de ce cahier (claim-gate)

| Affirmation du cahier | Preuve (dans le dépôt) | Statut |
|---|---|---|
| Effectifs : 4 254, 4 219, 633, plis 717 à 718, 17 classes, petits chapitres | `results/measures/splits_summary.json`, ADR-005, ADR-006 | prouvé |
| TF-IDF 0,684 [0,657 ; 0,709] ; v2 0,689 ; bornes 0,025 et 0,058 | runs `p1-06-tfidf-chapter`, `…-v2`, `p1-03-bounds`, `tfidf-v2-minus-v1-chapter` | prouvé |
| CamemBERT-bio 0,448 et taux plus bas ; écart −24,9 | runs `p1-07-camembert-bio-lr*`, `p1-07-camembert-minus-tfidf-fold0` | prouvé |
| Qwen 4B 0,193 ; Gemma 0,456 ; Qwen 9B 0,565 ; écarts | runs `p1-11-*`, `p1-11-*-minus-*-fold0` | prouvé |
| Déficit sur chapitres rares (F1 nulle XII, XXI, XXII) | runs `p1-23-errors-p1-11-*` | prouvé |
| RM-14 : +3,87 [+1,27 ; +6,31] ; v2 +3,42 [+1,17 ; +5,78] ; auteur seul 0,377 contre 0,385 | runs `rm-14-author-shortcut-tfidf`, `…-v2`, `p0-30-author-shortcut-v2`, ADR-011 | prouvé ; lectures non tranchées |
| Q5 : ECE 0,029, conforme, sélectif, décalage | run `q5-uncertainty-tfidf-chapter`, `RESULTATS.md` | prouvé (TF-IDF seulement) |
| Mémoire et débits, durées réelles | runs `debit-*`, `preflight-*`, `p1-11-*` | prouvé |
| 245 tests, 58 runs, 12 ADR, 7 mutations sur 7 | `pytest --collect-only`, `ls results/runs`, `ls docs/decisions`, journal de nuit | prouvé (comptes du 03/10/2026) |
| Puissance : 12 % à gain 3, 1,7 % à gain égal à δ | `audit_GLM_5_3_v2.md` G6, erratum 6.3, run `power-curves-audit` | prouvé (approximation normale) |
| Notes 5,0 / 7,6 / 9,4 | `docs/presentation/PREUVES.md` | **estimation** |
| Budget restant d'environ 85 h | B = 90 h moins environ 5 à 8 h consommées (runs et pré-vols) | estimation |
