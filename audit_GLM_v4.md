# audit_GLM_v4.md

## 1. En-tête

- **Date** : 04/10/2026. **Modèle** : GLM 5.3 (glm-5.3-flash, via opencode).
- **Lu pour cette réponse** : le cahier `docs/BRIEF_GLM_v4_audit_efficacite_methodes.md` seulement. Aucune pièce jointe n'a été fournie ; la source « dans le dépôt, non fournie à GLM » du tableau de preuve du cahier n'a pas été vue.
- **Ce que je n'ai pas pu vérifier** : le contenu des runs cités (`RESULTATS.md`, registre), les fiches hachées du test de taille, la dette d'orchestration décrite en G4, l'état réel des 290 tests, et les chiffres « en cours » de la section 3.8 du cahier (ils n'existaient pas au moment de l'écriture). Chaque chiffre de ma réponse renvoie à « cahier § x », ou est marqué *estimation* ou *conjecture*.
- **Posture** : steelman, attaque, enjeu chiffré, correction la moins chère, ce qui me ferait changer d'avis. Les décisions (promotion en référence, estimand, poursuite de la distillation, envoi hors machine) restent à Cyril : avis chiffré, jamais de tranchement.

## 2. Verdict en 12 lignes

Le projet est sur la bonne voie pour la **validité** : protocole gelé, registre en écriture unique, résultats négatifs publiés, prédictions préenregistrées ratées et consignées ; c'est rare et cela se défend. [FAIT, cahier § 3 et § 5]

Le risque actuel n'est plus la validité, c'est l'**efficacité perçue** : environ 9 h de GPU d'entraînement enregistrées, aucune recette LLM ne bat une référence lexicale quasi gratuite (0,587 contre 0,6971 au pli 0), et le plan complet reste 70 à 84 h sur 90. [FAIT, cahier § 3.2 et § 3.7]

Mais cette « défaite des LLM » est mesurée sur des recettes **prouvablement sous-réglées** : taux toujours au bord supérieur, 4B strictement croissant sur la grille, et CamemBERT-bio gagne +10,5 points rien qu'en passant de 2 à 6 époques (0,448 à 0,553) pour 0,08 h de GPU. [FAIT, cahier § 3.2 et § 3.3] [INFÉRÉ] La comparaison gelée sous-estime donc probablement les LLM de plusieurs points ; la phrase « aucun LLM ne bat le TF-IDF » n'est pas démontrée.

La règle de puissance échouera presque sûrement (largeur simulée 7,8 à 13,7 contre 4,0 admis) : environ 78 % du budget dépend d'une règle qui n'a pas de chance. [FAIT, cahier § 2] [INFÉRÉ] La décision la plus urgente est donc de **ne pas engager le professeur ni le confirmatoire** avant trois mesures peu coûteuses : cinq graines de la référence (P1-19), la règle de puissance RM-17 (gratuite en GPU), et un run de sensibilité aux époques sur le 4B.

La crédibilité se gagnera en publiant d'avance que le premier cycle est EXPLORE et « non résolu par construction », pas en espérant un verdict confirmatoire. [INFÉRÉ]

## 3. Tableau de notes par axe

| Axe | Efficacité /10 | Validité /10 | Preuve | Principale faiblesse | Correction la moins chère |
|---|---|---|---|---|---|
| A cible et métrique | 4 | 6 | E2 | Verdict dominé par 5 chapitres de 4 à 9 patients (écart macro-F1 13 points, écart F1 pondérée 4 points) | Correction de priorité à l'inférence sur les prédictions existantes (0 GPU) |
| B protocole de validation | 5 | 7 | E3 | Pli 0 à une graine sert à choisir et à rapporter ; IC de 7,7 points sur la comparaison d'élèves | P1-19 (cinq graines) puis RM-17 |
| C réglage et équité | 3 | 5 | E3 (époques), E2 (taux) | 2 époques gelées pour tous contre l'évidence des +10,5 points de CamemBERT | Un run de sensibilité aux époques sur le 4B |
| D modèles et ordre | 4 | 6 | E2 | Criblage LLM (9 h) avant la fin du réglage des références à 0,04 à 0,1 h | Finir les variantes TF-IDF et figer CamemBERT 6 époques comme référence-2 |
| E incertitude et abstention | 5 | 6 | E3 (TF-IDF), E2 (LLM) | Garantie de couverture non transférable (deux moitiés d'un pli, modèle du test entraîné sur 100 % du développement) | Wilson par classe et réserve d'échangeabilité déjà écrite, appliquées à chaque rapport |
| F fuite et estimand | 4 | 6 | E3 | Signature d'auteur à 0,917 confondue avec le thème, jamais départagée | Leave-one-author-out sur le TF-IDF (CPU, 0 GPU) |
| G ingénierie et structure | 6 | 7 | E3 | Déterminisme GPU non géré (40 prédictions sur 717 changent à même graine) et relances qui peuvent masquer des échecs | Déclaration de reproductibilité statistique, plafond de relances |
| H efficience globale | 2 | 5 | E2 | 78 % du budget derrière une règle sans puissance ; explorations sans gain consommées | Plan minimal viable (section 6) |

## 4. Axe A : choix du problème, de la cible et de la métrique

**Steelman** [FAIT, cahier § 2 et § 4] : la métrique primaire est gelée avant toute mesure, l'exclusion d'`AUTRE` est définie, les effectifs par classe sont publiés, et le choix de la macro-F1 pèse chaque chapitre également, ce qui est le bon choix si l'objectif est de ne pas laisser la classe dominante (174 patients) cacher le reste. La tâche a un plancher (0,025) et une borne (0,025 / 0,058) publiés, donc l'échelle des gains est connue.

**(A1) La macro-F1 à 17 classes est-elle évaluable ?** [INFÉRÉ] Oui comme mesure d'ensemble, non comme instrument de verdict à ce niveau de bruit. [FAIT] L'écart de macro-F1 entre le TF-IDF et le 9B est de 13 points, celui de la F1 pondérée de 4 points : la plus grande partie de l'écart vient des petits chapitres. [FAIT] La simulation du cahier (§ 3.5) donne à un chapitre de 5 patients un intervalle de Wilson de [0,38 ; 0,96], et 9 chapitres sur 17 auront moins de 30 patients au test. [INFÉRÉ] Le verdict porte donc pour moitié sur des chapitres dont la F1 individuelle est presque une pièce de monnaie. Ce qui me ferait changer d'avis : une mesure réelle montrant que la macro-F1 sur 17 classes a une variance comparable à celle de la F1 pondérée.

**(A2) δ = 2,0 est-il cohérent avec un bruit d'un point ?** [FAIT] Le rejeu de même graine du 4B donne 0,5807 contre 0,5867, soit 0,6 point [−1,85 ; +0,69] de bruit pur de non-déterminisme. [INFÉRÉ] δ = 2,0 vaut donc environ 2 à 3 fois le bruit d'un seul run, avant même la variance entre graines ; c'est serré mais cohérent, à condition que l'intervalle apparié tienne compte du bruit (c'est le rôle du bootstrap hiérarchique). [INFÉRÉ] Le vrai risque n'est pas δ mais la largeur d'IC (7,8 à 13,7 simulés contre 4,0 admis) ; δ est un mètre correct dans une pièce trop petite. Ce qui me ferait changer d'avis : une corrélation d'erreurs entre graines mesurée forte (elle rétrécit la largeur).

**(A3) Le plafond de la tâche rend-il le classement peu informatif ?** [FAIT] Les erreurs traversent les familles (4,8 % du TF-IDF et 3,9 % du 9B restent dans la même famille), la spécialité détermine en grande partie le chapitre (hors distribution par spécialité : 0,522 contre 0,818), et le diagnostic principal est ambigu. [INFÉRÉ] Le plafond limite les gains absolus de toutes les recettes de la même façon : il rend le **classement des techniques** plus, pas moins, informatif, puisque tout le monde court sur la même piste plafonnée. L'informativité chute seulement si le plafond varie par technique ; rien ne l'indique ici.

**(A4) Décalage perte/métrique : quel levier en premier ?** [INFÉRÉ] La correction la moins chère est à l'inférence : sur les probabilités déjà conservées du 4B (règle écrite, cahier § 4, axe E), appliquer une correction de priorité au niveau des logits (p′ ∝ p / q^τ, q prévalence d'entraînement, τ de 0 à 1), τ choisi sur une moitié du pli 0, macro-F1 mesurée sur l'autre moitié ; zéro GPU, quelques minutes de CPU. [FAIT] La perte pondérée a déjà été testée au niveau de la perte : −2,3 [−5,3 ; +1,5], non résolu ; elle ne teste pas le même mécanisme (rééquilibrage des logits après coup contre rééquilibrage du gradient) et coûte un run. En premier : la correction de priorité. Deuxième : la pondération relancée à plus d'époques (l'interaction n'a jamais été mesurée). Troisième : la sélection du point de décision sur la macro-F1, qui exige des données de calibration propres.

**5 corrections classées** (effort humain ; GPU ; gain attendu ; risque ; preuve de fin) :

| # | Correction | Effort | GPU | Gain attendu | Risque ou conflit | Preuve de fin |
|---|---|---|---|---|---|---|
| A-c1 | Correction de priorité à l'inférence, τ choisi sur une moitié du pli 0, mesuré sur l'autre | 0,3 h | 0 | Conjecture : +2 à +8 points de macro-F1 sur le 4B (les erreurs vont vers des chapitres majoritaires, la priorité force la sortie des rares) ; incertitude forte | Aucun (EXPLORE, jamais sur le test) | Run d'analyse au registre |
| A-c2 | Publier la F1 pondérée et la micro-F1 à côté de la macro-F1 dans chaque résultat | 0,2 h | 0 | Rend visible la part des petits chapitres dans tout écart | Aucun (secondaire) | `RESULTATS.md` |
| A-c3 | Pondération de perte relancée à 4 ou 6 époques (interaction époques × poids, jamais mesurée) | 0,3 h | 0,8 à 1,2 h | Conjecture : l'échec de la pondération à 2 époques peut être un artefact de sous-entraînement | Aucun (EXPLORE) | Run dédié |
| A-c4 | Score hiérarchique (macro-F1 par bloc CIM-10) calculé sur les prédictions existantes | 0,3 h | 0 | Chiffre gratuit qui vérifie l'affirmation 7 (score hiérarchique inutile) | Aucun | JSON au registre |
| A-c5 | Gabarit de rapport qui marque « cible : macro-F1 17 classes, bruit de petits chapitres quantifié » | 0,2 h | 0 | Empêche la surinterprétation d'un écart | Aucun | Gabarit |

**Expérience décisive minimale** : A-c1 (correction de priorité, 0 GPU). Elle départage en un après-midi si le déficit des petits chapitres est un problème de seuil de décision ou un problème d'apprentissage ; les deux suites d'actions ne sont pas les mêmes selon la réponse.

## 5. Axe B : protocole de validation

**Steelman** [FAIT, cahier § 2] : tout est préenregistré et haché, le test scellé a une porte unique et une ouverture unique en deux temps, le bootstrap est apparié et hiérarchique, la règle de puissance a un repli écrit et confirmé par Cyril, et le registre en écriture unique a déjà attrapé des erreurs de chiffres. C'est un dispositif de protection contre les trois façons classiques de se tromper : fuite, sélection après coup, comparaisons multiples.

**(B1) Biais du pli 0 qui choisit et rapporte.** [INFÉRÉ] Le meilleur taux est un maximum de tirages bruités : avec un bruit de rejeu de 0,6 point et une variance entre graines inconnue, le maximum de 4 essais surcharge le gagnant d'environ 0,5 à 1,5 point (estimation, borne supérieure d'ordre de grandeur dérivée du bruit de rejeu ; pas de mesure directe dans le cahier). [FAIT] L'effet porte précisément sur la comparaison 4B moins 9B (+2,16 [−1,78 ; +5,90]), qui est dans la zone du biais ; l'écart de 11,1 points contre le TF-IDF, lui, dépasse largement ce biais et reste solide en ordre de grandeur. Correction : rapporter le choix du taux avec son biais de sélection annoncé (le protocole 6.5 le dit déjà) et ne retenir un classement d'élèves qu'après cinq graines.

**(B2) Un criblage à un pli et une graine est-il décisionnel pour un écart de 2 points ?** [FAIT] Non : l'IC du rejeu seul ([−1,85 ; +0,69]) couvre presque la moitié de δ ; l'IC du choix d'élève ([−1,78 ; +5,90]) le couvre tout entier. [INFÉRÉ] Le criblage est décisionnel pour l'**ordre de grandeur** (qui est un élève plausible, qui est hors course à 0,193), pas pour des écarts de 2 points. C'est acceptable si le rapport le dit ; le risque est de publier « le 4B est le meilleur élève » comme un fait mesuré.

**(B3) La règle « le moins coûteux si l'IC contient 0 » est-elle saine ?** [INFÉRÉ] Oui, comme règle de budget : préenregistrée (ADR-009), elle évite la sélection après coup et elle est réversible (un changement d'élève passe par une nouvelle version si une mesure future l'exige). [INFÉRÉ] Son artefact est réel : un « non résolu » peut cacher un vrai écart de 3 points ; la règle paye alors le prix en performance plutôt qu'en GPU. Pour un projet dont le but déclaré est de **mesurer** les techniques, cette règle est cohérente (le coût fait partie de la mesure) ; pour un projet de production, elle ne le serait pas. Je la garderais, en l'étiquetant « règle de budget, pas un résultat de performance ».

**(B4) L'estimand du test scellé est-il honnête ?** [FAIT] Le TF-IDF retrouve l'auteur à 0,917, les plis par auteur perdent 3,87 points [1,27 ; 6,31], et le déficit du 9B est de −7,6 points d'exactitude sur les auteurs peu représentés. [INFÉRÉ] L'estimand « nouveaux patients du même corpus » est honnête **s'il est lu comme** : nouveaux patients de la même population d'auteurs (104), pas de nouveaux auteurs. [INFÉRÉ] Le score du test scellé sera donc vraisemblablement plus proche de l'estimation par patient (0,6844) que de l'estimation par auteur (0,6457), et cette lecture doit être écrite avant l'ouverture, sinon elle ressemblera à un aveu après coup. Ce qui me ferait changer d'avis : un leave-one-author-out montrant que le TF-IDF ne perd rien à ne jamais voir l'auteur.

**(B5) Le protocole est-il une coquille si la règle de puissance échoue ?** [FAIT] Le repli est écrit : bascule EXPLORE, test réservé au candidat final, aucune modification de δ. [INFÉRÉ] Ce n'est pas une coquille, c'est un instrument dont la fonction confirmatoire est prouvée inutile par construction, et dont les fonctions de protection (fuite, sélection, comparaisons multiples) restent toutes actives. [INFÉRÉ] Ce qui doit changer **avant** de dépenser le budget confirmatoire : rien dans le protocole ; c'est le plan de dépense qui doit changer (voir H1 et H2) : ne pas engager le professeur tant que la règle n'a pas produit son verdict, et traiter le confirmatoire comme conditionnel. Le protocole lui-même prévoit ce scénario ; l'erreur serait de le traverser en espérant.

**(B6) Les prédictions préenregistrées sont-elles calibrées ?** [FAIT] Plusieurs étaient fausses (TF-IDF estimé 0,20 à 0,50 contre 0,6844 mesuré ; « le 9B sera le meilleur » ; « la perte pondérée aidera »). [INFÉRÉ] La calibration des prédictions de l'assistant est mauvaise mais la pratique est excellente : les ratés sont publiés. Correction : tenir un score Brier par prédiction (déjà mesuré pour le modèle, le faire pour l'assistant) et noter chaque prédiction avec une probabilité explicite ; coût nul.

**5 corrections classées** :

| # | Correction | Effort | GPU | Gain attendu | Risque ou conflit | Preuve de fin |
|---|---|---|---|---|---|---|
| B-c1 | P1-19 : cinq graines de la référence au pli 0, prédictions par patient avec empreinte | 0,5 h | 3,5 à 6,3 h (découper : 3 graines puis 2) | La variance entre graines et la corrélation d'erreurs : la pièce qui manque à RM-17 et à tout le reste | Aucun (préenregistré) | Runs `p1-19-*` |
| B-c2 | RM-17 : règle de puissance sur les dix paires | 0,2 h | 0 | Verdict écrit de la règle ; conditionne le reste du budget | Aucun (règle 6.3) | Run + ligne `INDEX.md` |
| B-c3 | Leave-one-author-out TF-IDF (définition opérationnelle de la lecture « fuite ») | 0,3 h | 0 | Départage fuite contre thème de RM-14 | Aucun (développement) | Run de contrôle |
| B-c4 | Gabarit « estimand du test » écrit avant l'ouverture (lecture par patient attendue, réserve d'auteur) | 0,2 h | 0 | Protège la lecture de RM-20 | Aucun | Gabarit |
| B-c5 | Brier de l'assistant : chaque prédiction préenregistrée reçoit une probabilité et un score | 0,2 h | 0 | Calibre le jugement de l'assistant | Aucun | Table de scores |

**Expérience décisive minimale** : B-c1 + B-c2 (P1-19 puis RM-17). Tout le reste de l'axe en dépend ; c'est aussi la porte des 78 % du budget.

## 6. Axe C : stratégie de réglage et équité des comparaisons

**Steelman** [FAIT, cahier § 4] : la grille de 4 taux est gelée avant les runs, le critère de choix est écrit (macro-F1 la plus élevée, égalité au taux le plus bas), le bord de grille est signalé par une règle, et la règle d'égalité de budget (ADR-004) existe : le dispositif évite l'accumulation post hoc d'essais.

**(C1) Le gel compare-t-il des LLM mal réglés à un TF-IDF bien réglé ?** [FAIT] Oui, en partie : le meilleur taux est toujours au bord supérieur, le 4B est strictement croissant en taux, et CamemBERT-bio gagne +10,5 points de 2 à 6 époques ; le TF-IDF a eu une grille de C puis une version étendue. [INFÉRÉ] Quantification de la sous-estimation des LLM : l'analogue d'époques donne +10,5 points à l'encodeur ; le comportement monotone en taux suggère un optimum au-delà de 1e-4 ou un palier non atteint ; une sous-estimation de l'ordre de 5 à 15 points de macro-F1 est plausible (conjecture bornée par ces deux indices, pas de mesure LoRA directe). [INFÉRÉ] L'underestimate n'invalide pas l'ordre de grandeur actuel (11,1 points d'écart) mais interdit la phrase « aucun LLM ne bat le TF-IDF ». Ce qui me ferait changer d'avis : un run LoRA à plus d'époques qui ne dépasse pas la version à 2 époques.

**(C2) Quel protocole de réglage à budget égal correct ?** [INFÉRÉ] Trois clauses suffisent : (1) même nombre de runs de réglage par famille (par exemple 4), (2) même heures de GPU allouées par famille, (3) même critère et même pli et même graine de sélection ; la grille elle-même peut différer par famille (taux pour les LLM, C pour le TF-IDF, époques pour les encodeurs) à condition qu'elle soit **préenregistrée avant les runs de la famille**. [INFÉRÉ] Description honnête malgré le gel : le rapport publie, par famille, le budget de réglage dépensé et la grille préenregistrée ; le gel d'ADR-004 reste tenu si le nombre d'essais et les heures sont égaux, même si les dimensions diffèrent. La différence actuelle : le TF-IDF a eu un effort de réglage réel (grille de C), les LLM ont eu 4 taux à 2 époques, une seule dimension ; l'égalité de budget est en déficit côté LLM.

**(C3) Rang LoRA, époques, planning de taux : lequel rapporte le plus par heure ?** [FAIT] Époques : +10,5 points pour 0,08 h de GPU (CamemBERT 2 à 6 époques, 128 s à 6 époques) : c'est le meilleur rapport mesure du projet. [FAIT] Taux : +39,4 points de 1e-5 à 1e-4 sur le 4B, mais le levier est déjà poussé au bord ; un planning (échauffement puis palier) peut débloquer au-delà du bord (conjecture). [CONJECTURE] Rang : probablement le moindre rapport (pas de mesure dans le cahier) ; à tester en dernier. Ordre : époques, planning de taux, rang.

**5 corrections classées** :

| # | Correction | Effort | GPU | Gain attendu | Risque ou conflit | Preuve de fin |
|---|---|---|---|---|---|---|
| C-c1 | Sensibilité aux époques sur le 4B (4 puis 6 époques, taux 1e-4) | 0,3 h | 1,7 à 2,5 h (estimation : 0,84 h par run de 2 époques, donc ~1,7 h pour 4 et ~2,5 h pour 6) | Conjecture : +5 à +10 points si le comportement suit CamemBERT ; quantifie la sous-estimation de C1 | Aucun (EXPLORE) ; ne change rien au gel | Runs dédiés + `RESULTATS.md` |
| C-c2 | Si C-c1 gagne : écart consigné (ADR-010) puis décision de Cyril sur les époques du cycle | 0,3 h | 0 | Évite que la recette gelée soit comparée sous-réglée | **Conflit assumé** : époques gelées à 2 (C6), toute valeur différente exige ADR et décision | ADR-010 mise à jour |
| C-c3 | Planning de taux (échauffement puis palier) sur le 4B | 0,2 h | 0,8 h | Conjecture : débloque le bord supérieur ; incertitude forte | Aucun (EXPLORE) | Run dédié |
| C-c4 | Clause d'égalité de budget explicite par famille dans les fiches (essais, heures, critère) | 0,3 h | 0 | Équité auditable des comparaisons à venir | Aucun (renforce ADR-004) | Fiches hachées |
| C-c5 | Rang 32 / alpha 64 sur le 4B, une fois époques et taux réglés | 0,2 h | 0,8 h | Conjecture : 0 à +3 points | Aucun (EXPLORE) | Run dédié |

**Expérience décisive minimale** : C-c1 (époques sur le 4B). C'est la mesure qui quantifie la sous-estimation des LLM et qui décide si la phrase de la section 6, affirmation 1, tombe.

## 7. Axe D : choix des modèles et ordre des expériences

**Steelman** [FAIT, cahier § 3.7 et § 3.8] : le criblage a produit les mesures de mémoire, de débit et de compatibilité qui fondent le test de taille en cours ; le test de taille est préenregistré avec une règle d'arrêt à trois branches, et la référence lexicale est elle-même en cours d'enrichissement (variantes de poids, n-grammes).

**(D1) L'ordre inversé aurait-il changé les décisions ?** [FAIT] CamemBERT-bio à 6 époques (0,553) coûte 0,04 h et est non distinct du 4B (−3,4 [−8,2 ; +2,1]) ; le 4B coûte 0,84 h par run. [INFÉRÉ] Si les références bon marché avaient été réglées à fond d'abord, la grille de lecture aurait été : référence lexicale 0,6844, référence encodeur ~0,55, puis la question du LLM posée avec un plafond à +13 points ; la décision de lancer 9 h de criblage LLM aurait été plus difficile à justifier ; le coût d'opportunité de l'ordre suivi est de l'ordre de 5 à 8 h de GPU passées avant des mesures accessibles pour moins de 0,5 h (estimation ; les mesures de mémoire et de compatibilité du criblage restent réutilisées par le test de taille, ce n'est pas une perte sèche).

**(D2) Le test de taille est-il bien conçu ?** [FAIT] Un taux (1e-4), QLoRA NF4, 2 époques, confusion taille/quantification assumée, règle d'arrêt à trois branches, 4 h estimées, pic mesuré 27,14 Gio. [INFÉRÉ] Deux faiblesses sans doubler le coût : (1) le taux 1e-4 est au bord supérieur de la grille pour les trois élèves testés : un modèle de 31 milliards peut préférer un taux plus bas (conjecture), donc un résultat négatif conclurait « cette recette précise » et non « l'échelle ne paie pas » : inscrire cette phrase dans la fiche avant le run ; (2) sauvegarder la courbe de perte par pas et, si elle est encore en baisse à la fin, le dire dans la conclusion (le diagnostic d'époques d'ADR-007 a été raté une fois à cause de cela). Je ne changerais ni le taux ni la durée : la règle d'arrêt et la fiche hachée priment.

**(D3) La distillation est-elle défendable si l'élève est 11 points sous une référence lexicale ?** [INFÉRÉ] Défendable comme **mesure** (le but du projet est de quantifier ce que chaque technique apporte, y compris négativement), indéfendable comme **dépense sans condition**. [FAIT] Le professeur coûte 15,8 à 29 h, le confirmatoire 17,5 à 31,5 h, et la règle de puissance donne environ 12 % de verdict résolu. [INFÉRÉ] Expérience minimale qui la justifie ou l'éteint : le test de taille en cours (si l'IC du 31B contre le TF-IDF est entièrement positif, la voie LLM a un plafond crédible et la distillation a un objet ; sinon, un pilote de distillation sur un pli avec l'élève 4B et un seul professeur, environ 4 à 6 h, un seul chiffre : le gain de distillation contre la référence 4B au pli 0 ; IC contenant 0 à deux reprises = extinction consignée). La porte finale reste RM-17 et Cyril.

**(D4) Quels autres modèles valent encore la peine ?** [INFÉRÉ] Trois, tous à coût négligeable : (1) CamemBERT-bio à 6 époques comme **référence-2** (déjà mesuré, à figer) ; (2) un passage zero-shot du meilleur LLM sur le pli 0 pour mesurer la connaissance a priori de la hiérarchie CIM-10 (inférence seule, environ 0,2 à 0,4 h, estimation) : sans ce chiffre, on ne sait pas si l'affinage aide ou nuit ; (3) les variantes TF-IDF en cours (n-grammes de caractères). [CONJECTURE] Les « modèles de classification dédiés » ouverts pour le français clinique sont rares et à licence variable : à ne considérer que si leur licence est déjà vérifiée dans `docs/LICENCES.md`.

**5 corrections classées** :

| # | Correction | Effort | GPU | Gain attendu | Risque ou conflit | Preuve de fin |
|---|---|---|---|---|---|---|
| D-c1 | Finir les variantes TF-IDF en cours et figer la référence-1 réglée | 0,3 h | 0 (CPU) | Référence à effort de réglage complet, l'équité de C2 côté lexical | Aucun | Run + fiche hachée |
| D-c2 | Figer CamemBERT-bio 6 époques comme référence-2 (0,553, 0,04 h) | 0,2 h | 0 | Un deuxième plancher sérieux, 20 à 70 fois moins cher que tout LLM | Aucun | Fiche hachée |
| D-c3 | Zero-shot LLM sur le pli 0 (inférence seule) | 0,2 h | 0,2 à 0,4 h (estimation) | Sépare « le modèle sait » de « l'affinage aide » | Aucun (EXPLORE) | Run |
| D-c4 | Inscrire dans la fiche du test de taille la clause de lecture (un taux, 2 époques, QLoRA) | 0,2 h | 0 | Un résultat négatif correctement borné | Aucun (fiche déjà hachée : passer par un errata si la fiche est posée) | Errata ou fiche |
| D-c5 | Pilote de distillation à un pli (4B, un professeur) si le test de taille est positif ou sur décision de Cyril | 0,5 h | 4 à 6 h (estimation) | Le premier chiffre de distillation hors pli ; extinction ou justification de la ligne | **Conflit** : ne pas lancer avant RM-17 (ordre du protocole) ; décision de Cyril | Run + `RESULTATS.md` |

**Expérience décisive minimale** : le test de taille en cours, complété par D-c3 (zero-shot). Ces deux mesures ensemble coûtent moins de 4,5 h et tranchent l'orientation du reste du budget.

## 8. Axe E : incertitude et abstention

**Steelman** [FAIT, cahier § 3.5] : la chaîne complète existe (température, ECE, Brier, LAC et APS marginal et par classe, Wilson, prédiction sélective, décalage patient vers auteur), elle est testée sur cas synthétiques, appliquée avec étalonnage croisé, et les probabilités sont conservées par run sur règle écrite.

**(E1) La garantie tient-elle dans la configuration décrite ?** [INFÉRÉ] Non, sous trois angles : (1) calibration et évaluation sont deux moitiés d'un seul pli de 717 : la moitié de calibration (~358 patients) donne un niveau de couverture bruité ; (2) le test est prédit par un modèle entraîné sur 100 % du développement quand la calibration vient de modèles à 80 % : l'écart d'échangeabilité est documenté au protocole (6.6) mais il fait partie de la garantie annoncée ; (3) le non-déterminisme GPU (40 prédictions sur 717) ajoute du bruit aux scores de calibration. [INFÉRÉ] Conséquence honnête : annoncer la couverture comme **cible mesurée en développement**, jamais comme garantie sur le test ; c'est déjà la lettre du protocole, elle doit devenir la lettre du rapport.

**(E2) La couverture par classe est-elle évaluable pour des classes de 4 à 9 patients ?** [FAIT] Non : Wilson [0,38 ; 0,96] pour 5 patients, 9 chapitres sur 17 sous 30 patients au test. [INFÉRÉ] Ce qu'il faut rapporter honnêtement : la couverture marginale et la couverture par classe **regroupée par bloc CIM-10** (les blocs ont des effectifs décents), avec les intervalles de Wilson ; et la liste des classes dont la couverture individuelle est invérifiable au test. L'affirmation « une classe jamais couverte » du TF-IDF doit être reproduite avec son intervalle pour savoir si c'est un signal ou un artefact d'effectif.

**(E3) Quelle politique d'abstention défendable pour un usage fictif ?** [INFÉRÉ] Une table unique : couverture choisie (par exemple 70 %), exactitude conditionnelle mesurée (0,931 pour le TF-IDF, 0,892 à 0,934 pour les LLM), coût du renvoi humain (30 % des patients), le tout étiqueté « mesuré en développement, candidat, jamais validé sur le test ». [INFÉRÉ] Le risque à éviter est exactement celui nommé dans la question : présenter la politique du **modèle** (mesurée en développement) comme celle du **système** (qui exige la chaîne complète : préparation, prédiction, renvoi) ; le test de taille de la chaîne complète est le spike vLLM qui, au vu du cahier, reste à lancer.

**5 corrections classées** :

| # | Correction | Effort | GPU | Gain attendu | Risque ou conflit | Preuve de fin |
|---|---|---|---|---|---|---|
| E-c1 | Couverture par bloc CIM-10 avec Wilson, sur les prédictions existantes | 0,3 h | 0 | Une couverture par groupe lisible avec des effectifs décents | Aucun | JSON |
| E-c2 | Table d'abstention par modèle (couverture, exactitude conditionnelle, taux de renvoi) | 0,2 h | 0 | Politique candidate chiffrée | Aucun | `RESULTATS.md` |
| E-c3 | Intervalle de Wilson sur « la classe jamais couverte » du TF-IDF | 0,2 h | 0 | Sait si c'est un signal | Aucun | JSON |
| E-c4 | Réserve d'échangeabilité écrite dans le gabarit de rapport (déjà dans le protocole, à refléter) | 0,2 h | 0 | Cohérence protocole et rapport | Aucun | Gabarit |
| E-c5 | Simulation de couverture par classe sur les effectifs réels **du développement** (les effectifs du test simulés existent ; les plis réels manquent, même limite que la puissance) | 0,3 h | 0 | Attente chiffrée par classe avant toute ouverture | Aucun | Simulation au registre |

**Expérience décisive minimale** : E-c1 (couverture par bloc). Elle transforme un tableau de 17 colonnes illisibles en un tableau de 13 blocs interprétables, sans un pas de GPU.

## 9. Axe F : fuite, raccourcis et estimand

**Steelman** [FAIT, cahier § 3.6] : les partitions ont été contrôlées avant tout résultat, le raccourci d'auteur a une règle préenregistrée avec seuil, la stylométrie a été mesurée spontanément (0,917), et les quasi-doublons sont quantifiés à trois seuils (9 à 0,8, 45 à 0,7, 169 sur 171 du même auteur à 0,6) : le risque de fuite a été traité en objet de mesure, pas en slogan.

**(F1) La signature d'auteur est-elle une fuite exploitée, et quelle expérience départage ?** [FAIT] TF-IDF perd 3,87 points en plis groupés par auteur, retrouve l'auteur à 0,917, et son déficit contre le 9B est maximal sur les auteurs peu représentés (−7,6 points d'exactitude). [INFÉRÉ] Le faisceau penche pour une **part de fuite par répétition d'auteur** (le même style, le même gabarit, les mêmes patients-voisins), mais 0,917 est « confondu avec le thème » : l'auteur prédit aussi le thème. [INFÉRÉ] Expérience décisive la moins chère : **leave-one-author-out** : pour chaque auteur d'au moins 20 patients, entraîner le TF-IDF sans aucun patient de cet auteur, évaluer sur ses patients uniquement ; la moyenne de ces macro-F1 est l'estimation « nouveaux auteurs ». [INFÉRÉ] Trois lectures possibles : proche de 0,6844 (l'auteur n'aide pas, RM-14 est un artefact de découpage) ; proche de 0,6457 (l'écart patient/auteur est une signature) ; intermédiaire (les deux). Coût : CPU, quelques dizaines de régressions logistiques, moins d'une heure.

**(F2) Faut-il changer d'estimand avant l'ouverture ?** [INFÉRÉ] Non : le test scellé est un actif unique, jamais lu, et son estimand est écrit. [FAIT] Les déclencheurs écrits (écart supérieur à 3 points sur le candidat final avec borne basse positive ; lecture « fuite » confirmée) existent. [INFÉRÉ] Ce qui manque est l'opérationnalisation de « lecture fuite confirmée » : le leave-one-author-out est le candidat naturel ; l'écrire dans la fiche Q18 (déjà proposée en v3, C3-A5) plutôt que changer l'estimand maintenant.

**(F3) Quelle expérience de robustesse mesure la vraie généralisation sans GPU ?** [INFÉRÉ] Deux, en CPU : leave-one-author-out (nouveaux auteurs) et leave-one-specialty-out (déjà fait : 0,522, la spécialité détermine le chapitre). [FAIT] Les perturbations existent (sans accents : −5,6 points ; fautes : −0,7 ; casse : 0). [INFÉRÉ] La mesure manquante est précisément les **nouveaux auteurs** : c'est la seule dimension de généralisation du corpus qui n'a pas de chiffre.

**5 corrections classées** :

| # | Correction | Effort | GPU | Gain attendu | Risque ou conflit | Preuve de fin |
|---|---|---|---|---|---|---|
| F-c1 | Leave-one-author-out TF-IDF complet (66 auteurs d'au moins 20 patients) | 0,5 h | 0 | La première estimation « nouveaux auteurs » ; départage RM-14 | Aucun (développement) | Run + `RESULTATS.md` |
| F-c2 | Leave-one-author-out sur les prédictions du 9B quand un pli le permet (sinon programmé après P1-19) | 0,3 h | 0 (si prédictions existantes) ou report | Le même estimand pour un LLM : le déficit −7,6 sur auteurs peu représentés se lit là | Aucun | Run ou fiche |
| F-c3 | Opérationnaliser le déclencheur « lecture fuite confirmée » dans la fiche Q18 | 0,2 h | 0 | Un déclencheur exécutable, pas une impression | Aucun | Fiche hachée |
| F-c4 | Rapporter patient et auteur côte à côte dans chaque tableau de résultat | 0,2 h | 0 | Aucun chiffre présenté sans son estimand | Aucun | Gabarits |
| F-c5 | Sensibilité du seuil de quasi-doublons à 0,7 (45 paires) publiée sans changer le seuil gelé | 0,3 h | 0 | Prouve que le contrôle ne dépend pas d'un seuil ajusté | Aucun (seuil gelé intact) | JSON |

**Expérience décisive minimale** : F-c1. Elle coûte une heure de CPU et transforme RM-14 de « signalé, non tranché » en un fait départagé.

## 10. Axe G : ingénierie, reproductibilité, structure du travail

**Steelman** [FAIT, cahier § 4, axe G] : environnement verrouillé, 290 tests, typage strict, garde anti-affaiblissement, secrets contrôlés, registre en écriture unique, reconstruction à froid mesurée à 26 s cache chaud, audit hebdomadaire des dépendances, et un travail de nuit encadré par un contrat écrit avec délégations tracées.

**(G1) Que vaut la reproductibilité si deux runs de même graine diffèrent ?** [FAIT] 40 prédictions sur 717 changent, perte maximale écartée de 0,21, macro-F1 0,5807 contre 0,5867. [INFÉRÉ] Ce qu'il faut garantir et dire : reproductibilité **statistique** (même graine, même code, même données : écart de macro-F1 de l'ordre de 0,6 point, borné par la mesure de rejeu) et non reproductibilité bit-à-bit sur GPU ; rejeu identique reste vrai pour le TF-IDF (déterminisme CPU confirmé). [INFÉRÉ] Dans le rapport : une phrase par famille, avec le chiffre de rejeu cité. Ce qui me ferait changer d'avis : un rejeu avec un écart de plusieurs points (il signifierait un état instable à chercher).

**(G2) Le dispositif de nuit est-il sain ?** [INFÉRÉ] Sain dans ses garde-fous actuels (exclusions du gel, du test scellé, des poussées de code ; journal ; file de questions). [FAIT] L'auto-critique liste des erreurs réelles de stratégie (section 5 du cahier). [INFÉRÉ] Les contrôles qui manquent : (1) un point de contrôle humain obligatoire à chaque porte (déjà partiel : RM-17, gel) ; (2) un plafond de relances (voir G3) ; (3) une règle « toute surprise répétée (crash, écart inattendu) s'arrête et se consigne, ne se retente pas » ; (4) un récapitulatif hebdomadaire des écarts au plan (ADR-010 existe : en faire un rendu périodique court).

**(G3) Les relances automatiques peuvent-elles masquer des échecs réels ?** [FAIT] Oui : le tokenizer a segfaulté sur 3 runs sur 6, puis « une seconde passe à essais multiples a été nécessaire » : le motif exact du masquage. [INFÉRÉ] Règle minimale : chaque relance est consignée avec la raison au registre ; au-delà de 2 relances du même échec, arrêt et signalement ; un échec qui répète n'est pas une panne aléatoire, c'est un défaut à corriger.

**(G4) La dette d'orchestration.** [INFÉRÉ] Trois gestes, une demi-journée au total : un point d'entrée unique (`make` targets) pour les lots ; les journaux de session sous `results/logs/` (dépôt) au lieu d'un répertoire de session ; interdiction de créer une nouvelle file shell (toute nouvelle file passe par le backlog). La dette restante est bornée si aucune nouvelle file n'apparaît.

**5 corrections classées** :

| # | Correction | Effort | GPU | Gain attendu | Risque ou conflit | Preuve de fin |
|---|---|---|---|---|---|---|
| G-c1 | Déclaration de reproductibilité par famille dans le gabarit de rapport (statistique, pas bit-à-bit, chiffre de rejeu cité) | 0,2 h | 0 | La reproductibilité annoncée devient exacte | Aucun | Gabarit |
| G-c2 | Règle de relances : consignée, plafond 2, arrêt et signalement au-delà | 0,2 h | 0 | Les échecs réels ne se masquent plus | Aucun (renforce 6.4) | Règle + journal |
| G-c3 | Point d'entrée unique et journaux dans le dépôt | 0,5 h | 0 | La dette d'orchestration cesse de croître | Aucun | `Makefile` + répertoire |
| G-c4 | Deuxième rejeu de même graine (pour borner la distribution du bruit, pas seulement un point) | 0,1 h | 0,84 h | Intervalle de bruit de rejeu sur 3 points au lieu de 2 | Aucun | Runs `p1-26-*` |
| G-c5 | Rendu hebdomadaire des écarts au plan (ADR-010) | 0,2 h | 0 | La dérive reste visible | Aucun | Note périodique |

**Expérience décisive minimale** : G-c4 (un deuxième rejeu). Une seule mesure de bruit de rejeu ne permet pas de distinguer un incident d'une distribution ; trois points le font.

## 11. Axe H : efficience globale et plan minimal viable

**Steelman** [FAIT, cahier § 3.7] : les 9 h dépensées ont produit les mesures de mémoire, de compatibilité et de débit qui rendent le test de taille lancé et le plan restant chiffré ; chaque exploration négative (perte pondérée, ensembles) est consignée et publiée ; le budget est suivi (alerte à 80 %).

**(H1) Le plan minimal viable.** [INFÉRÉ] Livrable défendable : rapport honnête, carte de modèle, comparaison équitable de trois familles (lexicale, encodeur, LLM) avec leurs efforts de réglage publiés. Ensembling minimal et coût :

| Étape | GPU | Humain | Sortie |
|---|---|---|---|
| 1. Finir variantes TF-IDF (en cours, CPU) | 0 | 0,3 h | Référence-1 réglée à fond |
| 2. CamemBERT 6 époques figé référence-2 (déjà mesuré) | 0 | 0,2 h | Deuxième plancher |
| 3. Test de taille 31B (en cours) | ~4 h | 0,2 h | Décision de la voie LLM |
| 4. Époques × 4B (4 et 6 époques) | 1,7 à 2,5 h | 0,3 h | Quantification de la sous-entraînement LoRA |
| 5. Correction de priorité à l'inférence | 0 | 0,3 h | Réponse de l'axe A4 |
| 6. P1-19 cinq graines | 3,5 à 6,3 h | 0,5 h | Variance entre graines, corrélation |
| 7. RM-17 (CPU) puis décision de Cyril | 0 | 0,2 h | Verdict de la règle de puissance |
| 8. Conformal sur le candidat (blocs, Wilson) | 0 à 0,5 h | 0,3 h | Politique d'abstention candidate |
| 9. Carte de modèle + rapport | 0 | 1 j | Livrable défendable |
| **Total hors professeur et confirmatoire** | **≈ 10 à 14 h** | **~2 j** | |

[INFÉRÉ] La suite (professeur 15,8 à 29 h, confirmatoire 17,5 à 31,5 h) n'est engagée que si trois conditions tiennent : le test de taille n'est pas entièrement négatif, la règle de puissance réussit ou Cyril accepte le statut EXPLORE assumé, et l'élève réglé à fond revient à distance combattable du TF-IDF (conjecture : à moins de 6 points, sinon la distillation mesure un écart plus grand que son effet).

**(H2) Dépenses restantes classées par information attendue par heure**, avec critères d'arrêt :

| Rang | Dépense | GPU | Information attendue | Critère d'arrêt |
|---|---|---|---|---|
| 1 | Variantes TF-IDF (en cours) | 0 | Référence équitablement réglée | Fin des variantes listées, aucune extension |
| 2 | CamemBERT 6 époques (fait : 0,04 h) | 0 | Meilleur rapport de tout le cycle | Rien à dépenser |
| 3 | Test de taille (en cours) | ~4 h | Tranche 15,8 à 60,5 h de dépenses en aval | Règle d'arrêt écrite ; clause de lecture ajoutée |
| 4 | Époques × 4B | 1,7 à 2,5 h | La sous-entraînement LoRA, quantifiée | Si le gain sur 1e-4/2 époques est sous 1 point à pli 0 : grille et époques closes pour le cycle |
| 5 | Correction de priorité | 0 | Le mécanisme du déficit | Si gain sous 1 point : fermer le levier |
| 6 | P1-19 + RM-17 | 3,5 à 6,3 h | Variance, corrélation, verdict de règle | Ne relance jamais avec une autre graine |
| 7 | Leave-one-author-out | 0 | Départage RM-14 | Une mesure, publiée, quelle que soit la réponse |
| 8 | Professeur 5 plis | 15,8 à 29 h | Les cibles de distillation | Uniquement si rangs 3, 4, 6 favorables et décision de Cyril |
| 9 | Confirmatoire P3-07 | 17,5 à 31,5 h | Verdicts… probablement non résolus | P(résolu) ≈ 12 % : ne lancer qu'après RM-17 favorable et décision de Cyril |

**(H3) Que supprimer du plan actuel** : [INFÉRÉ] (1) le confirmatoire en forme actuelle (4 recettes × 5 graines, développement entier) tant que la largeur n'est pas mesurée : c'est 17,5 à 31,5 h pour environ 12 % de verdicts résolus ; (2) toute nouvelle exploration d'ensemble (mesuré : 0,650 à 0,659 contre 0,6971, aucune ne bat le TF-IDF) ; (3) la relance de la pondération à 2 époques seulement (déjà mesurée, négative) ; elle ne revient qu'accompagnée d'époques (C-c3) ; (4) le spike vLLM, reporté après le cycle (il est nécessaire à C7 mais rien n'en dépend avant la démo).

**5 corrections classées de l'axe H** :

| # | Correction | Effort | GPU | Gain attendu | Risque ou conflit | Preuve de fin |
|---|---|---|---|---|---|---|
| H-c1 | Adopter le plan minimal viable (10 à 14 h de GPU) comme ordre de dépense par défaut, le reste conditionnel | 0,2 h | 0 | 76 à 88 % du budget réservés jusqu'au verdict de RM-17 (estimation) | Aucun (ordre du backlog inchangé) | Fiche de séquencement hachée |
| H-c2 | Faire précéder l'ouverture du test d'un deuxième essai à blanc de la procédure temps B (données synthétiques) | 0,2 h | 0 | Le risque « consommé sans résultat » est réduit | Aucun (renforce 6.8) | Journal de la répétition générale |
| H-c3 | Passer C-c1 (sensibilité aux époques) avant P1-20 si l'ordre du backlog le permet | 0,2 h | voir C-c1 | Le gel de la référence n'enterre pas la question des époques | **Conflit possible** : l'ordre du backlog fige la référence en P1-20 avant les variantes ; exige un écart consigné (ADR-010) | ADR-010 |
| H-c4 | Automatiser le compteur de budget (somme du registre, alerte 72 h) en contrôle de CI | 0,3 h | 0 | L'alerte manuelle devient systématique | Aucun | Script + test |
| H-c5 | Figer tôt la structure du rapport final (carte de modèle, estimands, sections « ce que nous ne savons pas ») | 0,3 h | 0 | Le livrable défendable existe dès le premier chiffre | Aucun | Gabarit de rapport |

**Expérience décisive minimale de l'axe H** : [INFÉRÉ] ce n'est pas une expérience isolée, c'est la séquence elle-même : P1-19 (3,5 à 6,3 h) puis RM-17 (gratuit) ; le jour où ce verdict tombe, 78 % du budget est soit engagé avec une puissance mesurée, soit redirigé vers un livrable EXPLORE assumé.

**(H4) Décisions irréversibles et mal outillées** : [INFÉRÉ] (1) l'ouverture unique du test : le risque « consommé sans résultat » existe (le protocole a la répétition générale : la faire précéder d'un deuxième essai à blanc, H-c2) ; (2) les époques gelées à 2 : chaque run LLM dépensé à 2 époques produit un chiffre difficilement comparable à un futur chiffre à 3 époques ; la mesure de sensibilité (C-c1) est la façon la moins chère de désamorcer ce piège avant P1-20 ; (3) le gel de la référence (P1-20) avant la mesure des époques : si l'ordre du backlog permet de passer C-c1 avant P1-20, le faire (H-c3).

**(H5) Probabilité que l'élève ou le professeur batte le TF-IDF de façon résolue.** [INFÉRÉ] Deux conditions empilées : l'écart de 11,1 points se retourne (il faut gagner 13 points et plus, à comparer aux +10,5 points disponibles par les époques chez l'encodeur : possible mais non démontré pour un LoRA) **et** la largeur d'IC tombe sous 4 points (jamais le cas dans les simulations citées, 7,4 à 14,3 sur le test). [CONJECTURE] Sans changement de design, la probabilité d'un verdict résolu favorable est inférieure à 5 % ; avec la correction d'époques (si elle gagne 5 points ou plus) et une évaluation hors pli (largeur 3,8 à 6,7), elle monte vers 10 à 25 %. Ce qui la ferait monter davantage : une corrélation d'erreurs entre graines mesurée forte, et un estimand sur les blocs CIM-10 plutôt que sur 17 chapitres (mais ce dernier choix est un changement de métrique primaire : ADR et décision de Cyril).

## 12. Auto-critique de l'assistant (section 5 du cahier) : jugement

[INFÉRÉ] La liste est **complète sur le fond, légèrement biaisée vers l'autoflagellation mineure, avec deux omissions**. Point par point : (1) le criblage avant le réglage des références : exact et le plus grave (v3 l'avait déjà pointé, l'ordre n'a pas changé : le fait que le test de taille soit lancé alors que la pondération, le creux des longueurs et le leave-one-author-out sont encore ouverts le confirme) ; (2) CamemBERT à 2 époques laissé trompeur : exact ; (3) l'ensemble proposé avant mesure : mineur (il a été mesuré et publié en négatif : c'est le processus qui marche) ; (4) la recherche hors périmètre : mineure, consignée ; (5) les trois chargements perdus : exact, et c'est le pré-vol qui aurait dû attraper ; (6) les prédictions fausses : exact, et le Brier de l'assistant (B-c5) est la correction. Omissions : (a) **la grille de criblage n'était pas complète quand les conclusions ont circulé** (2 taux sur 4, le meilleur au bord : c'est un défaut de stratégie distinct du défaut d'ordre) ; (b) **P1-19 (la mesure la plus critique et la moins chère de la chaîne) n'a toujours pas commencé**, alors que tout l'axe B en dépend : c'est une erreur de priorisation qui devrait figurer dans la liste. Rien dans la liste n'est excessif sur le fond.

## 13. Affirmations de la section 6 : verdicts

| # | Affirmation | Verdict | Raison et test qui trancherait |
|---|---|---|---|
| 1 | « Aucun LLM ne bat le TF-IDF » | **Non établi** | [FAIT] Un pli, une graine, 2 époques, taux au bord supérieur, recettes sous-réglées (évidence CamemBERT). Test : C-c1 (époques) puis P1-19 ; si le 4B à plus d'époques ne monte pas, l'affirmation se rapproche de « vrai pour cette recette gelée ». |
| 2 | « Les recettes LoRA à 2 époques sont probablement sous-entraînées » | **Probablement vrai, non établi** | [FAIT] Monotone en taux, bord atteint ; analogue CamemBERT +10,5 points. Pas de run d'époques sur un LoRA. Test : C-c1. |
| 3 | « La perte pondérée n'est pas le levier principal » | **Vrai, à cette durée d'entraînement** | [FAIT] −2,3 [−5,3 ; +1,5] ; XXI sort de zéro mais XII et I baissent. Test : C-c3 (pondération × époques, interaction jamais mesurée). |
| 4 | « Le déficit vient des petits chapitres, donc de la rareté » | **Partiellement vrai** | [FAIT] Écart macro 13 contre F1 pondérée 4 : la concentration est réelle. [FAIT] Mais le déficit du 9B est maximal sur les auteurs peu représentés : la rareté peut être celle des **auteurs**, pas seulement des classes. Test : F-c1. |
| 5 | « Un ensemble par moyenne ne bat pas le TF-IDF » | **Vrai (mesuré, pli 0)** | [FAIT] 0,650 à 0,659 contre 0,6971. [INFÉRÉ] Ne généralise pas aux ensembles pondérés ou à un rassemblement plus large. Test : peu prioritaire ; si repris, pondération optimisée sur le développement (CPU). |
| 6 | « Le creux des longueurs moyennes est un effet de composition » | **Non établi** | [FAIT] Le creux existe (0,86 / 0,69 / 0,81) ; aucune mesure de composition dans le cahier. Test : relecture de 20 cas + distribution par spécialité (C5-A7 de la réponse v3). |
| 7 | « Les erreurs traversent les familles : un score hiérarchique n'aiderait presque pas » | **Vrai (probablement)** | [FAIT] 4,8 % (TF-IDF) et 3,9 % (9B) d'erreurs intra-familles. Test gratuit : calculer la macro-F1 par bloc sur les prédictions existantes (A-c4). |
| 8 | « Le style d'auteur est une fuite possible, non démontrée » | **Vrai (état exact)** | [FAIT] Stylométrie 0,917 confondue au thème ; RM-14 signalé ; pas de démonstration d'exploitation. Test : F-c1 (leave-one-author-out). |
| 9 | « Le 4B est un bon élève par la règle écrite d'avance » | **Vrai comme décision ; non établi comme performance** | [FAIT] ADR-009 appliquée telle quelle sur un IC contenant 0 (+2,16 [−1,78 ; +5,90]). [INFÉRÉ] La décision est saine ; la phrase « bon élève » ne l'est pas : le dire « le moins coûteux faute de distinction mesurable ». Test : cinq graines (P1-19). |
| 10 | « Le test de taille (31B, QLoRA, un taux) tranche la question de l'échelle » | **Faux en partie** | [FAIT] Taille et quantification varient ensemble (confusion assumée) ; un taux, au bord, 2 époques. [INFÉRÉ] Il tranche « cette recette 31B QLoRA 1e-4 2 époques », pas l'échelle en général. Test : clause de lecture (D-c4) ; aucune mesure supplémentaire nécessaire pour corriger la portée de la conclusion. |
| 11 | « La distillation est justifiée par l'objectif du projet même si les LLM perdent » | **Vrai, conditionnellement au budget** | [INFÉRÉ] L'objectif est de mesurer ; une mesure de distillation a une valeur d'information même négative. [FAIT] Mais 15,8 à 29 h (professeur) + 17,5 à 31,5 h (confirmatoire) sur 90 h pour environ 12 % de verdicts résolus : la justification doit passer par le test de taille et RM-17, pas l'inverse. Test : ordre 8 et 9 du plan H2. |
| 12 | « Le protocole gelé reste utile même si la règle de puissance échoue » | **Vrai** | [FAIT] Le repli EXPLORE est préenregistré ; les protections (fuite, sélection, comparaisons multiples, ouverture unique) restent actives. [INFÉRÉ] L'utilité est conditionnelle à une chose : publier le basculement et le « non résolu attendu » sans les présenter comme un échec. Test : aucun requis (structurel) ; la preuve sera la qualité du rapport final. |

## 14. Les trois erreurs que je ferais à votre place, et les trois choses que je referais exactement pareil

**Trois erreurs.** (1) [INFÉRÉ] **Geler les époques à 2 pour toutes les recettes** alors que la métrique primaire pèse également des chapitres de 4 à 9 patients : l'évidence ultérieure (CamemBERT +10,5 points) montre que la durée d'entraînement est un des plus gros leviers, et chaque heure de LLM passée à 2 époques devient difficile à interpréter ; je referais le gel après une mesure de sensibilité, pas avant. (2) [INFÉRÉ] **Dépenser le criblage LLM (9 h) avant de terminer le réglage des références à moins de 0,5 h** : l'information la plus chère a été achetée avant l'information la plus bon marché ; l'ordre inverse aurait probablement déplacé la décision d'élève et peut-être celle du test de taille. (3) [INFÉRÉ] **Construire le plan autour du confirmatoire** (70 à 84 h sur 90) alors que sa puissance mesurée est d'environ 12 % : le plan défendable est celui du H1, où le confirmatoire est une branche conditionnelle ; un plan structuré autour d'une épreuve qui échoue par construction transforme un budget en constat.

**Trois choses à refaire exactement pareil.** (1) [FAIT] **Le gel haché et les portes** : il a attrapé des erreurs de budget (2,9 contre 5,8 h), des effectifs faux, des contradictions internes ; c'est le dispositif qui donne au projet sa validité actuelle. (2) [FAIT] **La publication des résultats négatifs et des prédictions ratées** : la perte pondérée, les ensembles, le rejeu non identique, les trois prédictions fausses : c'est la monnaie la plus crédible du dossier de candidature, et elle est rare. (3) [FAIT] **Le test scellé jamais lu avec son ouverture unique en deux temps** : le risque de le « jeter un œil » est le plus commun du métier, et il n'a pas été pris.

## 15. Tableau de preuve de ma réponse

| Chiffre ou affirmation | Source |
|---|---|
| Effectifs (4 254 ; 4 219 ; 633 ; plis 717 à 718 ; plis de contrôle 663 à 763 ; 104 auteurs ; 174 à 4 patients au test) | cahier § 2 |
| TF-IDF 0,6844 [0,6573 ; 0,7089] ; pli 0 0,6971 ; v2 0,6889 ; groupé 0,6457 ; RM-14 +3,87 [1,27 ; 6,31] ; balanced 0,6805 | cahier § 3.1 |
| LLM : 4B 0,193 / 0,306 / 0,473 / 0,587 (strictement croissant) ; 9B 0,213 / 0,565 ; E4B 0,142 / 0,456 ; durées 3 024 / 3 623 / 4 226 s ; pics 12,9 / 21,6 / 24,8 Gio | cahier § 3.2 |
| 4B − 9B : +2,16 [−1,78 ; +5,90] ; 4B − TF-IDF : −11,1 [−16,4 ; −4,8] | cahier § 3.2 |
| CamemBERT : 0,448 / 0,526 / 0,553 ; 128 s ; non distinct du 4B (−3,4 [−8,2 ; +2,1]) ; −14,4 [−19,9 ; −7,4] | cahier § 3.3 |
| Perte pondérée : 0,5637 contre 0,5867 (−2,3 [−5,3 ; +1,5]) ; XXI 0 → 0,17 ; exactitude −3,3 | cahier § 3.4 |
| Rejeu : 40/717 ; 0,21 de perte max ; 0,5807 contre 0,5867 (−0,6 [−1,85 ; +0,69]) | cahier § 3.4 |
| Ensembles : 0,659 / 0,650 / 0,654 contre 0,6971 | cahier § 3.4 |
| Incertitude : ECE 0,028 / 0,049 / 0,039 ; LAC 0,901 / 0,902 / 0,898 ; 2,57 / 1,56 / 1,60 classes ; sélectif 0,931 / 0,934 / 0,892 à 70 % ; décalage 0,887 / 0,880 ; Wilson [0,38 ; 0,96] ; 9/17 sous 30 patients | cahier § 3.5 |
| Auteur : 1/4 254 identifiant ; stylométrie 0,917 (66 auteurs, hasard 0,015) ; quasi-doublons 9 / 45 / 169 sur 171 ; −7,6 points sur auteurs peu représentés | cahier § 3.6 |
| OOD 0,522 contre 0,818 ; obstétrique 0,013 ; perturbations −5,6 / −0,7 / 0 ; familles 4,8 % / 3,9 % ; tronqués 9/3 586 | cahier § 3.6 |
| Coûts : 9 h enregistrées sur 90 ; plan 70 à 84 h ; 4B 0,84 h ; CamemBERT 0,04 h ; professeur 15,8 à 29 h ; tokenizer 3/6 ; trois chargements de 9 min perdus | cahier § 3.7 |
| Test de taille : préenregistré, 4 h estimées, pic 27,14 Gio, règle d'arrêt à trois branches, confusion taille/quantification assumée | cahier § 3.8 |
| Log loss équilibrée : rapport signal/bruit de 4 à 43 % supérieur au simulateur près | cahier § 4 (axe A) |
| Puissance : ~12 % de verdict résolu à gain réel de 3 ; largeur 7,8 à 13,7 (esquisse) et 7,4 à 14,3 (audit précédent) contre 4,0 | cahier § 2 et § 4 (axe B) |
| 290 tests ; reconstruction à froid 26 s cache chaud ; TF-IDF déterministe ; flash-linear-attention | cahier § 4 (axes G et D) |
| Maximum de 4 essais bruités surcharge le gagnant de ~0,5 à 1,5 point | estimation (dérivée du bruit de rejeu de 0,6, pas de mesure directe) |
| Sous-estimation des LLM de ~5 à 15 points ; probabilité de verdict résolu favorable < 5 % sans changement de design, 10 à 25 % avec époques et hors pli | conjecture (bornée par les indices mesurés, expliquée dans le texte) |
| Gains attendus des corrections (priorité, planning de taux, rang, pondération × époques) | conjecture (un chiffre de mesure est proposé pour chacune) |
| Coûts GPU des runs proposés | estimation (dérivée des durées réelles du cahier : 0,84 h pour un run 4B de 2 époques) |
