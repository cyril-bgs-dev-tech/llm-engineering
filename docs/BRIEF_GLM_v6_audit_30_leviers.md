# Cahier d'audit pour GLM, v6 : les 30 leviers les plus déterminants pour la performance

Version du 05/10/2026 (état arrêté à 22h15Z, nuit du 04 au 05/10). Document **autonome** : aucune pièce jointe n'est requise. Aucune donnée de patient réel ni texte clinique : seulement des effectifs, des mesures, des noms de fichiers et de familles de méthodes. À envoyer à GLM **seulement sur décision de Cyril** (envoi hors machine) ; l'assistant ne l'envoie pas. Section 8 : prompt prêt à coller. Ce cahier remplace le v5 pour la question posée (le v5 reste valable pour l'audit du second cycle) ; il reprend ses chiffres, mis à jour.

## 1. Rôle et posture

Tu es un chercheur principal d'un genre rare : lauréat de distinctions de thèse, **trente ans de pratique** dans la recherche sur les systèmes à base de modèles de langage et sur les structures adjacentes (apprentissage de représentations, classification de textes cliniques, affinage et distillation, recherche d'information, calibration et prédiction conforme, évaluation statistique, ingénierie de l'expérimentation). Tu as vu passer les modes : tu sais distinguer ce qui change un score de ce qui change un récit. Tu es **adversarial et jamais complaisant**. Tu as déjà audité ce projet quatre fois (v2 à v5) ; plusieurs de tes conjectures ont été testées et corrigées par la mesure (section 5.4). Tu n'as accès à aucun fichier du dépôt : tout ce qui compte est dans ce cahier.

Méthode imposée pour chaque levier : (a) *steelman* en deux lignes, (b) l'attaque la plus forte, (c) enjeu chiffré en points de la métrique principale, (d) l'expérience la moins chère qui le falsifie, (e) ce qui te ferait changer d'avis. Étiquette chaque phrase factuelle `[FAIT]` (vient du cahier), `[INFÉRÉ]` (déduit du cahier, dis comment) ou `[CONJECTURE]` (ton expérience ou ton intuition, avec une probabilité). Pas de flatterie, pas de conseil générique sans coût ni gain, pas de référence bibliographique inventée : si tu cites un travail, cite-le comme *à vérifier* quand tu n'es pas sûr de son contenu exact.

## 2. La mission

**Identifier les 30 éléments essentiels qui, d'après toi, seraient les plus déterminants pour améliorer la performance de notre solution et de notre modèle, compte tenu de tout ce qui est déjà mis en place et testé (sections 4 et 5), et qui rendraient tout le reste inutile, plus simple ou obsolète.** Pas trente idées : trente leviers classés, chacun relié à nos mesures, chiffré, falsifiable, avec ce qu'il permet d'arrêter de faire.

Définitions imposées :

- **Performance** : (1) métrique principale = macro-F1 sur 17 chapitres CIM-10 (classe AUTRE exclue de la moyenne), mesurée sur des prédictions hors pli regroupées (3 586 patients) ; (2) fiabilité de l'incertitude : couverture conforme par famille de chapitres et taille des ensembles de classes ; (3) robustesse (perturbations de forme, nouveaux auteurs) ; (4) **performance par coût** (heures de GPU, latence, énergie), parce que le but du projet est de savoir ce que chaque technique apporte pour son prix. Tu indiques pour chaque levier sur lequel de ces axes il agit.
- **Levier déterminant** : effet attendu d'au moins 1 point de macro-F1 regroupée à cinq plis, ou d'au moins 30 % de réduction de coût à qualité égale, ou d'une amélioration nette de la couverture conditionnelle ; mécanisme explicite ; testable dans nos limites matérielles et budgétaires (section 3).
- **Rend obsolète** : tout ce que nous avons construit ou prévu et qui n'aurait plus lieu d'être si le levier tient (une expérience, un composant, un modèle servi, une règle du protocole). **Rend plus simple** : ce qui se réduit. **Rend inutile** : ce qui devient sans objet. Distingue les trois.
- **Simple** : au plus une demi-journée d'ingénierie et 3 heures de GPU.

## 3. Contraintes dures

- **Matériel** : une carte RTX 5090 (32 Gio, Blackwell sm_120), processeur Intel i9-13900KF (AVX2 seulement, ni AMX ni avx512_bf16), 68 Gio de RAM visibles dans WSL, 32 threads, disque de données environ 30 fois plus lent que le disque système. Pas de location de GPU, pas d'API payante, pas de grappe. Tout levier qui exige davantage est classé « hors portée » (tu peux le citer, hors des 30).
- **Budget** : B = 90 h de calcul d'entraînement et de tokenisation inscrit au protocole gelé ; 25,4 h enregistrées (28 %) ; le lot en cours (LoRA des plis 3 et 4) ajoute environ 7,5 h ; la suite préenregistrée (service, zéro-shot, distillation) environ 4 h. Il reste donc de l'ordre de **50 h de GPU** pour tout le reste. Un pli de LoRA 4B à 10 époques coûte 3,7 h ; cinq encodeurs 20 à 25 minutes.
- **Données** : uniquement le corpus fictif PARHAF (section 4.1), aucune donnée de patient réel, aucun import de données cliniques externes ; données synthétiques autorisées si lignée vérifiée.
- **Protocole** : gelé (v1) ; toute modification passe par une nouvelle version, une ADR et la décision de Cyril (dis quels leviers l'exigent). Test scellé de 633 patients jamais lu, ouvert une seule fois en deux temps. Verdict en trois valeurs (gain confirmé, absence de gain, non résolu) ; δ = 2,0 point ; fiches préenregistrées hachées avant tout run.
- **Gouvernance** : les décisions de promotion d'une recette en référence, de changement d'estimand, de poursuite de la distillation et d'envoi hors machine appartiennent à Cyril : avis chiffré, jamais de tranchement.

## 4. Le dossier de preuve

### 4.1 La tâche et les données `[FAIT]`
- Corpus fictif PARHAF : **4 254 patients**, 6 185 documents ; 4 219 patients utilisés ; **développement 3 586**, **test scellé 633** ; 104 auteurs ; cinq plis de développement (717 à 718 patients) groupés par patient (plis de contrôle par auteur disponibles).
- Étiquette : chapitre CIM-10 du diagnostic principal du **scénario de simulation** (non un codage humain). Les fréquences de classes ne sont pas la prévalence française. 21 chapitres présents, **17 évalués**, les chapitres de moins de 20 patients regroupés dans AUTRE (18 patients au développement), exclue de la macro-F1. Chapitre II (tumeurs) : 1 187 patients ; X : 486 ; XIV : 382 ; XI : 368 ; IX : 341 ; XXII : 31 ; **les cinq plus petits chapitres évalués (IV, V, XII, XXI, XXII) comptent 27 à 63 patients**.
- Entrée : documents du patient concaténés avec balise de type de document, troncature tête et fin au niveau des tokens. Longueur par patient (tokenizer Qwen) : médiane 1 143 tokens, p95 2 826, p99 3 696 ; 59,5 % au-dessus de 1 024, 12,8 % au-dessus de 2 048, **0,24 % au-dessus de 4 096**. Encodeur : 508 tokens tête et fin ; LLM : 4 096.
- Un champ de « piscine » séparée (hors distribution) existe dans le corpus ; il n'a pas encore servi.
- Signatures d'auteur : le style identifie l'auteur à 0,917 (confondu avec le thème) ; l'identifiant d'auteur n'apparaît dans le texte que pour 1 patient sur 4 254.

### 4.2 Le protocole et la mesure `[FAIT]`
- Macro-F1 17 classes ; bootstrap hiérarchique apparié stratifié par classe, 5 000 répliques ; IC 95 % ; correction de Holm pour plusieurs comparaisons.
- **Variance** : les cinq plus petits chapitres portent **85,1 % de la variance bootstrap** de la macro-F1 ; écart-type bootstrap 1,3 point sur 3 586 prédictions ; écart-type entre graines de l'encodeur 2,6 points (pli 0) ; **non-déterminisme du GPU** : à graine égale, 0,7714 puis 0,7362 pour le même encodeur.
- **Règle de puissance** : largeur de l'IC de la différence appariée entre deux systèmes sur prédictions regroupées, seuil 4,0 points. Version v1 (cinq graines sur un pli) : 12,2 points, échec. Version v2 (cinq plis, deux systèmes) : **3,09 à 95 %, 3,78 à 98,33 %** pour « ensemble contre TF-IDF », atteinte ; **4,55** pour « encodeur moyenné contre TF-IDF », non atteinte.
- Premier cycle classé EXPLORE : aucun résultat n'est confirmatoire ; le protocole v2 est en brouillon (ADR-015 proposée), non accepté.

### 4.3 Les systèmes mesurés (macro-F1, prédictions hors pli, 17 chapitres) `[FAIT]`

| Système | pli 0 | pli 1 | pli 2 | pli 3 | pli 4 | regroupée (3 586) |
|---|---|---|---|---|---|---|
| TF-IDF caractères 3 à 5, poids équilibrés (20 Mo, 1,9 ms) | 0,7184 | 0,6886 | 0,7483 | 0,7073 | 0,7248 | **0,7202** |
| Encodeur CamemBERT-bio 10 époques, moyenne de 5 graines | 0,7331 | 0,7532 | 0,7613 | 0,7428 | 0,7684 | **0,7528** |
| Ensemble 50/50 encodeur moyenné + TF-IDF | 0,7626 | 0,7512 | 0,7923 | 0,7746 | 0,7735 | **0,7721** |
| Qwen3.5-4B LoRA 10 époques, taux 1e-4, une graine | 0,7795 (graine 1001 : 0,7893) | 0,7415 | 0,7785 | en cours | en cours | à venir |

- **Ensemble contre meilleur TF-IDF** : +5,20 [+3,69 ; +6,78] sur cinq plis (résolu) ; plis 3 et 4 : +6,71 [+3,61 ; +10,42] et +4,69 [+1,85 ; +7,68]. **Encodeur moyenné contre TF-IDF** : +3,27 [+1,00 ; +5,55].
- **LoRA contre meilleur TF-IDF** : +6,4 [+2,0 ; +11,4] (pli 0), +5,3 [+0,75 ; +9,95] (pli 1), **+3,02 [−1,48 ; +7,31] (pli 2, non résolu)**. **LoRA contre encodeur moyenné** : +4,9 non résolu puis +5,75 [+1,1 ; +10,6] résolu selon la graine (pli 0), −1,1 (pli 1), **+1,78 [−2,79 ; +6,41] (pli 2, non résolu)**. Écart entre deux graines du LoRA au pli 0 : +1,0 [−3,1 ; +5,0].
- Ensembles avec le LoRA : LoRA + encodeur 0,7926 (une graine) et 0,7959 (deux graines) au pli 0, 0,7603 au pli 1 ; vote majoritaire de six modèles : 0,824 d'exactitude, sans gain.
- **Recette gelée contre recette mûre** : à 2 époques (recette gelée), encodeur 0,448 et LoRA 0,587 ; à 10 époques, encodeur 0,73 et LoRA 0,78. L'encodeur passe de 0,448 (2 époques) à 0,553 (6) à 0,73 environ (10 à 20, saturation). Autres LLM à 2 époques seulement : Qwen3.5-9B 0,565, Gemma-4-E4B 0,456 ; **9B et 31B à recette mûre : non testés**.
- Précision et rappel par chapitre : les chapitres rares portent le déficit ; la correction de priorité à l'inférence ne corrige pas le LoRA (+0,65) mais corrige l'encodeur sous-entraîné (+13,8 à 6 époques, +1,0 à 10 époques).

### 4.4 Les essais et leurs verdicts `[FAIT]`

| Levier essayé | Résultat | Statut |
|---|---|---|
| Époques : 2 → 10 (encodeur et LoRA) | +28 points (encodeur), +19 points (LoRA) | réussi, majeur |
| TF-IDF : caractères et poids de classe | +3,65 [+1,94 ; +5,48] contre la référence v1 ; chacun seul : non résolu | réussi |
| Moyenne de 5 graines de l'encodeur | réduit la variance ; +1,2 à +6,4 contre TF-IDF | réussi |
| Ensemble encodeur + TF-IDF 50/50 | +5,20 sur cinq plis | réussi, le plus robuste |
| Perte pondérée 1/√n (LoRA 4B, 2 époques) | −2,3 [−5,3 ; +1,5] | non résolu, hypothèse non soutenue |
| Hiérarchie CIM-10 comme supervision (TF-IDF) | −4,0 ou −1,05 | échec |
| Encodeur par fenêtres sur tout le dossier | +0,3 (6 époques) puis −6,8 (10 époques) | échec |
| Taux d'apprentissage 2e-4 (encodeur) | 0,649 | échec |
| Correction de priorité à l'inférence | LoRA +0,65 ; encodeur +13,8 (6 époques), +1,0 (10 époques) | utile seulement au sous-entraînement |
| Entraînement débiaisé par auteur (TF-IDF) | sans effet | échec |
| TF-IDF à étiquettes souples (professeur ensemble, cinq plis) | +0,69 [−1,03 ; +2,29], 15 % de l'écart au professeur | non résolu |
| Quantification INT8 dynamique de l'encodeur | effondrement 0,336 ; attention seule 0,723 (−1,3 point, +11 % de vitesse) | échec / non retenue |
| Test de taille 31B QLoRA à 2 époques | arrêt anticipé (6 h projetées) | annulé |
| Cascade encodeur puis LoRA (seuil 0,8, plis 0 et 1) | 77 à 79 % des cas sans LoRA, macro-F1 égale ou supérieure | aperçu, seuil non validé |

### 4.5 La structure des erreurs `[FAIT]`
- **Plafond d'ambiguïté** : exactitude top-1 / top-2 / top-3 au pli 0 : LoRA 0,858 / 0,950 / 0,975 ; ensemble de trois 0,870 / 0,958 / 0,983 ; TF-IDF 0,823 / 0,916 / 0,961. **Le bon chapitre est dans les deux premiers dans 95 % des cas** : la confusion est surtout entre deux diagnostics rivaux. Au pli 0, **tous les modèles se trompent pour 8,2 % des patients** (48 % des erreurs du meilleur modèle), ce qui évoque une ambiguïté d'étiquette plus qu'un défaut de modèle.
- Taxonomie sur cinq plis (TF-IDF) : 638 erreurs ; paires les plus fréquentes II → XIV (36), XVIII → X (27), XVIII → VI (27), XVIII → IX (26), II → XI (25) : le chapitre XVIII (symptômes et signes non classés) et le chapitre II (tumeurs) sont les sources ; **65 erreurs confiantes** (1,8 % des patients, 10,2 % des erreurs), dont 25 pour XVIII : candidates à un audit d'étiquette (non fait).
- 96 % des erreurs traversent les familles de chapitres.
- Spécialités les plus difficiles : pédiatrie, gériatrie, neurologie (top-1 de 0,52 à 0,59).

### 4.6 L'incertitude `[FAIT]`
- LoRA mûr : ECE 0,110 brute puis 0,028 à 0,044 après température ; conforme LAC 90 % : couverture 0,90, 1,15 à 1,17 classe par ensemble ; exactitude à 70 % de couverture 0,946 à 0,964. Encodeur : ECE 0,106 puis 0,050 ; exactitude 0,946 à 70 %.
- **Cinq plis, ensemble encodeur + TF-IDF** : couverture marginale 0,901 mais **famille la moins couverte à 0,655** ; étalonnage par famille (Mondrian) : minimum 0,892 avec 1,89 classes par ensemble, contre TF-IDF seul 0,897 avec 2,69 : à couverture minimale égale les ensembles de classes sont 30 % plus petits. Abstention : exactitude 0,948 à 70 % de couverture (TF-IDF 0,925). La classe AUTRE reste hors de portée (0 couverte sur 18).
- Étalonner par plis d'auteurs donne 0,900 de couverture sous décalage d'auteur (0,887 sinon).

### 4.7 Efficience et déploiement mesurés `[FAIT]`
TF-IDF : 20,4 Mo, p50 1,9 ms, p95 4,0 ms, 568 patients par seconde (processeur). Encodeur fp32 : 443 Mo, p50 191 ms (processeur, 8 threads) ; cinq encodeurs : environ 955 ms. LoRA 4B : latence p50 117 ms sur GPU, pic mémoire 12,4 Gio, 12 400 à 13 300 s d'entraînement par pli. Puissance du GPU sous charge : 397 W en moyenne (598 W au maximum). La cascade économise des appels GPU, non de la latence sur processeur.

### 4.8 L'infrastructure déjà en place `[FAIT]`
Registre de runs en ajout seul (185 runs) ; 41 fiches et instantanés hachés avant les runs ; 349 tests, typage strict, garde anti-affaiblissement des règles de qualité ; contrôle automatique des références de runs dans les textes sortants ; fonction de lancement partagée avec relances plafonnées et consignées ; post-traitement automatique des plis (ensembles, comparaisons appariées, règle de puissance, incertitude) ; module de distillation avec cible strictement hors pli et contrôle de fuite ; module de cascade avec seuil choisi hors pli ; module d'énergie ; scripts de service (TF-IDF, LoRA fusionné, encodeur sur GPU) ; zéro-shot par lettres ; élève TF-IDF souple ; wiki de 19 pages ; ADR 1 à 15 ; feuille de route de 183 micro-tâches (107 sur le chemin court).

### 4.9 La chaîne en cours (préenregistrée) `[FAIT]`
LoRA mûr aux plis 3 puis 4 (fin vers 23h35Z et 03h20Z) ; puis service du LoRA fusionné en bf16 (latence, débit, énergie) ; zéro-shot de Qwen3.5-4B et 9B au pli 0 ; service de l'encodeur sur GPU en fp32 et bf16 ; **distillation vers l'encodeur** (trente runs : professeur LoRA ou ensemble, cinq plis, trois graines, alpha 0,5 et température 2 fixés non réglés ; réserve de second ordre : chaque professeur a vu le pli de validation de l'élève ; seul le test scellé en est exempt) ; cascade validée hors pli ; fiche de déploiement.

## 5. Ce que l'équipe sait déjà, pour que tu n'y perdes pas de temps

### 5.1 Inventaire des pistes connues et de leur statut
Ne les reprends pas sans **valeur ajoutée** (nouvel argument, nouvelle variante, meilleure expérience décisive) ; tu peux les juger, les reclasser ou les fusionner. Tu **dois** proposer des leviers que cette liste ne contient pas.

- *Données et étiquettes* : synthétique ciblé des cinq plus petits chapitres (fiche écrite, non exécutée) ; audit des étiquettes confiantes (65 cas, non fait) ; pré-entraînement continu sur du texte non étiqueté (non fait) ; pseudo-étiquettes sur la piscine hors distribution (non fait) ; supervision auxiliaire par type de document, spécialité, bloc CIM-10 sur un réseau neuronal (échec en TF-IDF, non testé en réseau) ; pré-entraînement sur tâche voisine (non fait).
- *Modèles* : 9B et 31B à recette mûre (non testés) ; autres encodeurs français (DrBERT, ModernBERT-fr : non testés) ; représentations gelées d'un LLM avec régression logistique (non testé) ; rang, alpha et contexte du LoRA (non testés) ; tête contre verbaliseur, pooling (non testés).
- *Entraînement* : schedules plus longs du LoRA, EMA ou moyenne de poids, lissage d'étiquettes, perte ajustée aux logits, échantillonnage équilibré, R-Drop (aucun testé) ; ensembles de graines du LoRA (deux graines au pli 0 seulement).
- *Inférence* : empilement appris (non testé), augmentation au test (non faite), optimisation du seuil de décision pour la macro-F1 (non faite), recherche des plus proches voisins dans l'entraînement (non faite), cascade (aperçu), seconde lecture générative (hors du périmètre actuel).
- *Structure* : distillation (en file), fusion des LoRA des cinq plis contre ensemble (non fait), encodeur élagué (en file), élève TF-IDF souple (fait, non résolu).

### 5.2 Les douze conclusions de l'équipe que tu dois attaquer
(C1) À recette mûre, l'encodeur moyenné bat le meilleur TF-IDF (+3,27 [+1,00 ; +5,55]). (C2) L'ensemble encodeur + TF-IDF est le meilleur système bon marché (+5,20) ; son avantage sur l'encodeur seul est réel. (C3) Le LoRA 4B mûr n'est pas distinct de l'encodeur moyenné à cinq plis en qualité (à confirmer aux plis 3 et 4), pour un coût d'entraînement dix fois supérieur, avec une meilleure sélectivité. (C4) Le déficit des petits chapitres est du sous-apprentissage et non un manque de données. (C5) Les erreurs restantes sont dominées par l'ambiguïté d'étiquette (top-2 à 95 %). (C6) La signature d'auteur pure vaut environ 2 points. (C7) Un LLM plus grand à recette mûre ne ferait pas mieux que le 4B (non testé). (C8) La distillation vers un élève TF-IDF est inutile (15 % de l'écart) ; vers un encodeur elle reste à tester. (C9) La perte pondérée est inutile à toute durée d'entraînement. (C10) Le TF-IDF à caractères est le meilleur rapport qualité par coût. (C11) La macro-F1 sur 17 classes est une mesure raisonnable, mais surtout une mesure de cinq classes de 27 à 63 patients. (C12) Le protocole gelé reste utile pour un second cycle à recettes mûres.

### 5.3 Biais connus de l'équipe
Nous avons souvent surestimé un résultat sur un tirage unique (premier encodeur 0,7714, rejeu 0,7362, cinq graines 0,7293) ; nous sommes sensibles au coût (recherche du minimum viable) au risque de sous-estimer le plafond de qualité ; nous n'avons jamais mesuré notre performance contre un repère externe (le zéro-shot arrive) ; tout est mesuré sur un corpus fictif dont l'étiquette vient d'un scénario : les gains peuvent ne pas se transposer à des textes réels.

### 5.4 Tes conjectures passées, testées
« Les recettes à 2 époques sous-estiment » : confirmé au-delà de ce que tu chiffrais. « Correction de priorité +2 à +8 points sur le 4B » : non soutenu (+0,65). « Le test de taille 31B à 2 époques, 4 h » : sans objet, 6 h projetées. « La grille d'encodeur est incomplète » : fausse (quatre taux). Tu as vu juste sur l'ordre des dépenses, les relances qui masquent des échecs et le rejeu non déterministe.

## 6. Questions

(Q1) **Les 30 leviers** : liste classée (section 7, tableau). Équilibre exigé : au moins 5 sur les données et étiquettes, 5 sur l'entraînement, 5 sur l'inférence et l'assemblage, 5 sur l'évaluation, la calibration et la robustesse, 5 sur la structure du système et le coût, et au moins 5 leviers **absents de l'inventaire 5.1**.

(Q2) **Ordre et dépendances** : graphe de dépendances entre les 30, ordre d'exécution sous environ 50 h de GPU restantes, avec les trois points de décision où une mesure bifurque le plan.

(Q3) **Obsolescence** : pour chacun des 10 premiers leviers, ce qui devient obsolète, plus simple ou inutile dans notre feuille de route (distillation, cascade, quantification, ensembles, service du LoRA, second cycle, règles du protocole), et ce qui reste indispensable quoi qu'il arrive.

(Q4) **Trajectoire** : à partir de 0,772 (ensemble, cinq plis), quelle macro-F1 regroupée à cinq plis est atteignable avec les 50 h de GPU, palier par palier, avec une probabilité par palier et un plafond d'ambiguïté (tu estimes la part d'erreurs irréductibles à partir de la section 4.5) ? À quelle macro-F1 un lecteur extérieur cesserait-il d'être convaincu par le gain suivant ?

(Q5) **Attaque** : pour chacune des conclusions C1 à C12, vrai, faux ou non établi, avec le test qui trancherait en moins de 3 h de GPU.

(Q6) **Falsification** : les trois expériences décisives qui, si elles échouent, invalident le plus grand nombre de leviers de ta liste, et les trois qui, si elles réussissent, font gagner le plus.

(Q7) **Paris contre-intuitifs** : trois leviers que l'équipe jugerait absurdes ou marginaux et que tu mettrais pourtant dans les dix premiers, avec ta probabilité et le test.

(Q8) **Pièges** : les pièges de mesure, de fuite et d'interprétation propres à chacun des cinq premiers leviers (fuite de second ordre, optimisme du pli de développement, effet d'auteur, non-déterminisme du GPU, sélection sur le bruit).

## 7. Ce que tu dois produire (un seul fichier Markdown)

**Un fichier `.md` unique** (`audit_GLM_v6.md`) ; si tu ne peux pas joindre de fichier, un seul bloc de code Markdown. Plan :

1. **En-tête** : date, modèle, ce que tu as lu, ce que tu n'as pas pu vérifier.
2. **Verdict** en quinze lignes au plus : les trois idées structurantes, ce qui est le plus fragile dans notre cahier, la probabilité que le plan actuel atteigne son plafond.
3. **Tableau des 30 leviers**, une ligne par levier, **exactement 30**, colonnes : rang ; levier (une phrase) ; famille (données, entraînement, modèle, inférence, évaluation, structure) ; axe visé (macro-F1, incertitude, robustesse, coût) ; mécanisme ; preuve interne (renvoi « cahier § x ») ; gain attendu en points avec intervalle subjectif et probabilité ; coût (heures de GPU, heures d'ingénierie) ; pré-requis ; **ce qu'il rend obsolète, plus simple ou inutile** ; test de falsification en une phrase ; risque ou piège ; étiquette `[FAIT]`, `[INFÉRÉ]` ou `[CONJECTURE]`. Classement par (gain attendu × probabilité) / coût.
4. **Fiches détaillées des dix premiers** : steelman, attaque, enjeu chiffré, expérience la moins chère, ce qui te ferait changer d'avis.
5. **Graphe de dépendances** et **ordre d'exécution** sous 50 h de GPU (réponses Q2).
6. **Trajectoire de gain** avec probabilités et plafond (Q4).
7. **Liste d'obsolescence** (Q3) : ce qu'on arrête, ce qu'on simplifie, ce qui reste indispensable.
8. **Réponses Q5 à Q8**.
9. **Erreurs de lecture possibles** : tout ce qui, dans ce cahier, t'a semblé ambigu, contradictoire ou invérifiable.
10. **Tableau de preuve** : chaque chiffre renvoie à « cahier § x » ou est marqué *estimation* ou *conjecture*.

Français, pas de tiret cadratin, paragraphes de six lignes au plus.

## 8. Règles à respecter et prompt prêt à coller

**Règles** : le protocole gelé ne se modifie pas en silence (dis si un levier exige une nouvelle version, une ADR et la décision de Cyril) ; le test scellé n'est jamais lu avant son ouverture unique ; aucune donnée de patient réel, pas de location de GPU, pas d'API payante ; toute affirmation chiffrée renvoie à une mesure du cahier ou porte l'étiquette *estimation* ou *conjecture* ; tu ne proposes pas deux fois le même levier sous deux noms ; tu ne proposes pas un levier que ton propre calcul de coût sort de nos limites sans le dire ; un levier qui n'a pas de test de falsification ne compte pas dans les trente ; « simple » = au plus une demi-journée et 3 h de GPU.

**Prompt prêt à coller** :
> Tu es un chercheur principal en systèmes de modèles de langage et structures adjacentes, trente ans de recherche, adversarial et jamais complaisant, qui a déjà audité ce projet quatre fois ; plusieurs de tes conjectures ont été corrigées par la mesure (section 5.4 du cahier). Lis le cahier joint (`BRIEF_GLM_v6_audit_30_leviers.md`) en entier. Mission : identifier les **30 éléments essentiels les plus déterminants pour améliorer la performance** de la solution et du modèle, compte tenu de tout ce qui est déjà mis en place et testé, et qui rendraient tout le reste inutile, plus simple ou obsolète. Pour chaque levier : steelman, attaque, enjeu chiffré, expérience la moins chère qui le falsifie, ce qui te ferait changer d'avis. Étiquette chaque phrase factuelle `[FAIT]`, `[INFÉRÉ]` ou `[CONJECTURE]`, n'invente aucune référence, et relis ta réponse en cherchant tes propres erreurs avant de la rendre. Réponds aux questions Q1 à Q8. Format : un seul fichier Markdown `audit_GLM_v6.md` suivant exactement le plan de la section 7 ; règles de la section 8 ; exactement 30 leviers.

## 9. Tableau de preuve de ce cahier

| Groupe de chiffres | Source dans le dépôt (non fournie à GLM) | Statut |
|---|---|---|
| Corpus, effectifs, longueurs, variance par classe, discrétisation | `results/measures/class_distribution.json`, `results/measures/token_lengths.json`, `split-discretization-check` | prouvé |
| Macro-F1 par pli et regroupée (TF-IDF, encodeur, ensemble), règle de puissance v2 | `docs/TABLEAUX_GENERES.md`, `v2-power-preview-5-plis`, `pli3-encodeur-ensembles`, `pli4-encodeur-ensembles` | prouvé (EXPLORE, cinq plis) |
| LoRA 4B : plis 0, 1, 2, graines, comparaisons | `llm-mur2-qwen3-5-4b-ep10-lr1e-4`, `llm-mur-s1001-qwen3-5-4b-ep10-lr1e-4`, `llm-mur-pli1-qwen3-5-4b-ep10-lr1e-4`, `llm-mur-pli2-qwen3-5-4b-ep10-lr1e-4`, `pli2-llm-mur`, `pli2-llm-mur-vs-encodeur` | prouvé (EXPLORE, une graine) |
| Essais et échecs (pondération, hiérarchie, fenêtres, taux 2e-4, priorité, auteur, TF-IDF souple, INT8) | `RESULTATS.md`, `tfidf-souple-ens`, `tfidf-souple-moins-dur`, `quantization-selective-camembert-deploy-ep10-lr1e-4` | prouvé |
| Plafond d'ambiguïté, taxonomie, erreurs confiantes | `RESULTATS.md` (sections plafond d'erreur, ambiguïté, taxonomie), `error-taxonomy-tfidf-5plis` | prouvé (top-k pli 0 : contrôle sans run, à rejouer) |
| Incertitude à cinq plis, abstention | `conformal-by-family`, `abstention-cinq-plis`, `q5-uncertainty-*` | prouvé (EXPLORE) |
| Efficience mesurée, cascade | `bench-serving-tfidf-charbal-v1`, `cascade-eval`, `gpu_power_p1-11_second_pass.csv` | prouvé (cascade : aperçu) |
| Infrastructure (tests, registre, fiches hachées, modules) | `make check`, `experiments/INDEX.md`, `docs/COMMANDES.md` | prouvé |
