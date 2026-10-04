# Cahier d'audit pour GLM, v4 : efficacité des méthodes, protocoles de validation et stratégies structurelles

Version du 04/10/2026. Document **autonome** : tout ce dont tu as besoin est ici, aucune pièce jointe n'est requise. Aucune donnée de patient réel ni aucun texte clinique : seulement des effectifs agrégés, des mesures et des noms de fichiers. À envoyer à GLM **seulement sur décision de Cyril** (envoi hors machine) ; l'assistant ne l'envoie pas. Ce fichier contient, en section 8, un **prompt augmenté** prêt à coller.

## 0. Ce que Cyril attend, en une phrase

Un audit **sans complaisance** de la valeur réelle de ce que nous faisons : les méthodes sont-elles **efficaces** (information obtenue par heure de GPU et par heure humaine), les protocoles de validation sont-ils **valides** (ils protègent-ils vraiment d'une conclusion fausse), les stratégies structurelles (ordre des expériences, gel du protocole, délégation à un assistant) sont-elles **les bonnes** ? Réponse en **un fichier Markdown unique**.

## 1. Rôle demandé

Tu es un **chercheur principal** au niveau le plus exigeant : formation de type MIT, vingt ans de pratique en apprentissage automatique appliqué au texte clinique, en méthodologie statistique de l'évaluation, en adaptation de grands modèles de langage (fine-tuning, distillation, quantification) et en revue par les pairs. Tu as vu passer des centaines de projets qui concluaient trop vite. Tu es **adversarial par métier** : ton travail est de trouver ce qui ne tient pas, d'estimer **à quel point** et de dire **quoi faire en premier**. Pas de flatterie, pas de précautions oratoires sans chiffre, pas de recommandation générique : chaque point doit renvoyer à une mesure ou à une décision de ce document.

Posture exigée : (1) *steelman* d'abord (la meilleure défense de la méthode, en une ou deux phrases), (2) attaque ensuite, (3) quantifie l'enjeu (points de macro-F1, heures de GPU, probabilité d'une conclusion fausse), (4) propose la **correction la moins chère** qui lève le doute, (5) dis ce qui te ferait changer d'avis.

## 2. Le projet en quinze lignes

- **But déclaré** : mesurer ce que chaque technique d'adaptation apporte à un classifieur de textes cliniques français : LoRA réglée (référence), distillation d'un gros professeur vers un petit élève (H1), pré-entraînement sur une tâche voisine (H2), les deux (H3). Objectif secondaire assumé : démontrer une méthode rigoureuse pour un poste d'ingénieur data science hospitalier (CHU Grenoble Alpes).
- **Données** : PARHAF, comptes rendus **fictifs** en français : 4 254 patients ; 4 220 avec code CIM-10 résolu ; 4 219 utilisés ; test scellé 633 (jamais lu) ; développement 3 586 en 5 plis stratifiés par patient de 717 à 718 ; plis de contrôle groupés par auteur de 663 à 763 ; 104 auteurs.
- **Tâche** : prédire le **chapitre CIM-10** du diagnostic principal ; 17 classes évaluées (4 chapitres rares fusionnés en `AUTRE`, exclue de la moyenne). Effectifs au test : de 174 (chapitre II) à 4 (chapitre XXII) ; XII 6, XXI 7, IV 9, V 9.
- **Métrique primaire gelée** : macro-F1 sur 17 chapitres ; seuil d'utilité δ = 2,0 points ; K = 5 graines (`1000 + k`) ; budget B = 90 h de GPU ; N = 4 taux d'apprentissage (1e-5, 2e-5, 5e-5, 1e-4), une graine, **grille jamais étendue** ; **2 époques pour toutes les recettes**.
- **Protocole** : tout est préenregistré (fiches hachées SHA-256 avant le run), registre de runs en écriture unique, test scellé ouvert **une seule fois** en deux temps, verdict en trois valeurs (gain confirmé, absence de gain utile, non résolu) par bootstrap hiérarchique apparié (patients stratifiés par classe, même tirage pour les deux recettes), IC à 98,33 % (Bonferroni, trois comparaisons), règle de puissance : si la largeur moyenne d'IC entre graines dépasse 2 fois δ (4,0 points), les comparaisons confirmatoires passent EXPLORE.
- **Matériel** : une RTX 5090 (32 Gio, plafond de sécurité 28 Gio), 68 Gio de RAM, pas de location de GPU, pas d'API payante.
- **Statut** : premier cycle classé **EXPLORE** (à δ = 2,0 un vrai gain de 3 points n'est confirmé que dans environ 12 % des cas). Phase de références et de criblage terminée ; test de taille en cours (section 3.8).
- **Équipe** : un seul ingénieur, Cyril, aidé d'un assistant de code (Claude) qui travaille de nuit avec un contrat écrit et des délégations de décision, tracées. L'assistant a **reconnu des erreurs de stratégie** dans la nuit (section 6) : tu dois les juger.
- **Langue** : documentation en français, code en anglais.

## 3. Faits mesurés (tout est au développement ; aucun résultat confirmatoire n'existe)

Les chiffres des LLM sont **un pli (le pli 0, 717 patients), une graine** ; le TF-IDF a 5 plis. Chaque chiffre a un `run_id` dans un registre que tu ne vois pas : tu dois nous dire ce que tu aurais besoin de voir pour le croire.

### 3.1 Référence TF-IDF + régression logistique
- Macro-F1 : **0,6844** [0,6573 ; 0,7089] sur 5 plis par patient ; **0,6971 au pli 0** ; grille de C étendue : 0,6889 (non résolu contre 0,6844). Plis groupés par auteur : 0,6457.
- **Écart patient moins auteur (RM-14) : +3,87 points [+1,27 ; +6,31]**, « signalé » par la règle préenregistrée ; lecture non tranchée.
- Variante poids de classe équilibrés : 0,6805 (cinq plis ; pas de gain apparent). Variantes n-grammes de caractères en cours de calcul.

### 3.2 Élèves LLM (LoRA r = 16, alpha 32, 4 096 tokens, lot effectif 32, 2 époques, pli 0, graine 1000)

| Modèle | 1e-5 | 2e-5 | 5e-5 | 1e-4 | durée (1e-4) | pic mémoire |
|---|---|---|---|---|---|---|
| Qwen3.5-4B | 0,193 | 0,306 | 0,473 | **0,587** | 3 024 s | 12,9 Gio |
| Qwen3.5-9B | 0,213 | n/a | n/a | 0,565 | 3 623 s | 21,6 Gio |
| Gemma-4-E4B | 0,142 | n/a | n/a | 0,456 | 4 226 s | 24,8 Gio |

- **Le meilleur taux est toujours au bord supérieur** de la grille gelée ; la macro-F1 du 4B est **strictement croissante** avec le taux.
- 4B moins 9B au même taux : +2,16 points [−1,78 ; +5,90], non résolu : le 4B, moins coûteux, est retenu comme élève par la règle écrite d'avance (ADR-009 appliquée telle quelle). Le 4B est **11,1 points sous le TF-IDF** au pli 0 [−16,4 ; −4,8]. **Aucun LLM ne bat le TF-IDF.**
- Chapitres rares : le 9B et le 4B ont une F1 nulle sur XXI et/ou XXII (5 à 8 patients au pli 0), pourtant l'exactitude est proche (9B 0,788 contre 0,818). Écart de macro-F1 avec le TF-IDF : 13 points ; écart de F1 pondérée : 4 points.
- Prédiction écrite avant le criblage (« le 9B sera le meilleur ») : **fausse**.

### 3.3 Encodeur CamemBERT-bio (affinage complet, 508 tokens)
- 2 époques (recette gelée) : **0,448** ; 4 époques : 0,526 ; **6 époques : 0,553** (128 s). Non distinct du Qwen3.5-4B à 6 époques (−3,4 points [−8,2 ; +2,1]) ; 14,4 points sous le TF-IDF [−19,9 ; −7,4]. Le critère de la fiche (gain supérieur à δ) confirme le **sous-entraînement** de la recette gelée.

### 3.4 Perte, déterminisme, ensembles
- **Perte pondérée 1/√n** sur le 4B (seul changement) : 0,5637 contre 0,5867, **−2,3 points [−5,3 ; +1,5], non résolu** ; XXI sort de zéro (0 → 0,17), XII et I baissent ; exactitude −3,3 points. L'hypothèse « l'entropie croisée non pondérée explique le déficit des petits chapitres » n'est pas soutenue à cette durée d'entraînement.
- **Rejeu de même graine** du 4B à 1e-4 : **non identique** : 40 prédictions sur 717 diffèrent, perte maximale par pas écartée de 0,21, macro-F1 0,5807 contre 0,5867 (−0,6 [−1,85 ; +0,69]). Le bruit d'un run isolé est de l'ordre du point, pour un δ de 2 points.
- **Ensembles par moyenne de probabilités** (pli 0, bootstrap stratifié) : TF-IDF + CamemBERT 6 époques 0,659 ; TF-IDF + 4B 0,650 ; les trois 0,654 ; **aucun ne dépasse le TF-IDF seul (0,697)**.

### 3.5 Incertitude (développement, étalonnage croisé)
- TF-IDF (5 plis) : ECE 0,028 ; conforme LAC à 90 % : couverture marginale 0,901 (une classe jamais couverte), par classe 0,904 (minimum 0,893), 2,57 classes par ensemble ; exactitude 0,931 à 70 % de couverture (0,818 à 100 %) ; sous décalage patient vers auteur : couverture 0,887 (marginale) et 0,880 (par classe).
- CamemBERT 6 époques (pli 0, deux moitiés stratifiées du pli) : ECE 0,049 ; LAC 0,902 avec 1,56 classe par ensemble ; exactitude 0,934 à 70 % de couverture.
- Qwen3.5-4B (rejeu, même méthode) : ECE 0,039 ; LAC 0,898, 1,60 classe par ensemble ; exactitude 0,892 à 70 %.
- Simulation (effectifs du test attendus, aucune étiquette de test) : la couverture par classe d'un chapitre de 5 patients a un intervalle de Wilson [0,38 ; 0,96] ; neuf chapitres sur dix-sept auront moins de 30 patients.

### 3.6 Données, fuite, raccourcis
- L'identifiant d'auteur est dans le texte pour **1 patient sur 4 254**. Mais un TF-IDF **retrouve l'auteur à 0,917** d'exactitude (66 auteurs d'au moins 20 patients ; hasard 0,015), confondu avec le thème. **169 des 171 paires de quasi-doublons à Jaccard 0,6 sont du même auteur** (9 paires à 0,8, seuil gelé ; 45 à 0,7).
- Le déficit du 9B contre le TF-IDF est le plus grand sur les **auteurs peu représentés** (−7,6 points d'exactitude) et nul sur les auteurs très représentés.
- Hors distribution : TF-IDF entraîné sans une spécialité puis évalué sur elle : exactitude moyenne **0,522** (contre 0,818) ; la spécialité détermine en grande partie le chapitre (obstétrique : 0,013).
- Perturbations sur le TF-IDF : sans accents **−5,6 points** de macro-F1 ; fautes de frappe sur 5 % des mots −0,7 ; casse 0.
- Seulement 4,8 % des erreurs du TF-IDF (3,9 % du 9B) restent dans la même famille de chapitres : les erreurs traversent les familles (second diagnostic rival, pas confusion de voisins).
- Patients tronqués à 4 096 tokens : 9 sur 3 586, aucun dans les chapitres rares.

### 3.7 Coûts réels
- 9 h de GPU d'entraînement enregistrées au registre avant le test de taille, sur B = 90 h (la somme exclut le chargement des modèles, les relances sur panne, l'inférence). Estimation du plan complet (professeur Qwen ou Gemma-31B plus élève 4B) : **70 à 84 h nominal**, hypothèses du début du projet, à recalculer.
- Un run du 4B coûte 0,84 h ; **CamemBERT-bio à 6 époques 0,04 h** ; TF-IDF quelques minutes de CPU.
- Professeur de distillation : 5 plis estimés **15,8 à 29 h** de GPU, plus 5 à 7 minutes de chargement par modèle.
- Pannes : le tokenizer Rust a **segfaulté ou paniqué** sur plusieurs lancements (3 runs sur 6 du premier lot, puis des essais supplémentaires ; une seconde passe à essais multiples a été nécessaire) ; une tête de classifieur restée sur le processeur a coûté trois chargements de 9 minutes du modèle de 31 milliards de paramètres.

### 3.8 Ce qui est en cours à l'écriture de ce cahier
- **Test de taille** : Gemma-4-31B, QLoRA 4 bits NF4, pli 0, taux 1e-4, 2 époques (préenregistré, fiche hachée, règle d'arrêt écrite d'avance) : (1) IC de « 31B moins TF-IDF » entièrement positif : la voie LLM continue ; (2) IC contenant 0 : décision avec Cyril sur d'autres critères ; (3) IC entièrement négatif : on arrête de monter en taille et on livre TF-IDF + CamemBERT réglés avec abstention conforme. Taille et quantification varient ensemble (confusion assumée). Durée estimée 4 h, pic mémoire mesuré au pire cas 27,14 Gio.
- Variantes de recette du TF-IDF (poids équilibrés, n-grammes de caractères) pour donner à la référence peu coûteuse le même effort de réglage que les LLM.

## 4. Stratégies et méthodes à auditer

Pour chaque axe : ce qui est fait, puis **les questions auxquelles tu dois répondre**.

### Axe A : choix du problème, de la cible et de la métrique
Fait : macro-F1 sur 17 chapitres, δ = 2,0, `AUTRE` exclue ; log loss équilibrée par chapitre en secondaire (simulation : meilleur rapport signal sur bruit que la macro-F1 de 4 à 43 %, mais le simulateur la favorise) ; la perte d'entraînement est une entropie croisée non pondérée.
Questions : (A1) La macro-F1 à 17 classes, avec des classes de 4 à 9 patients au test, est-elle une cible évaluable ? Quelle part du verdict est du bruit de petits chapitres ? (A2) δ = 2,0 est-il cohérent avec un bruit d'un point entre deux runs de même graine ? (A3) Le plafond de la tâche (diagnostic principal ambigu, erreurs entre familles) rend-il le classement des techniques peu informatif ? (A4) Le décalage entre perte d'entraînement et métrique de jugement mérite-t-il un levier (perte équilibrée au niveau des logits, correction par la prévalence, sélection du point sur la macro-F1) et lequel testerais-tu **en premier** ?

### Axe B : protocole de validation
Fait : gel hâché, test scellé unique en deux temps, bootstrap hiérarchique apparié, Bonferroni, règle de puissance, EXPLORE par défaut, criblage et réglage au pli 0 une graine, jamais de lecture du test.
Questions : (B1) Le **pli 0 sert à choisir** (taux, élève, recette) **et** à rapporter : quel biais de sélection, de quelle taille attendue ? (B2) Un criblage à un pli et une graine, avec un bruit d'un point, est-il décisionnel pour un écart de 2 points ? (B3) Le choix de l'élève « le moins coûteux si l'IC contient 0 » est-il une règle saine ou un artefact de puissance ? (B4) Le test scellé, stratifié et non groupé, partage ses auteurs avec le développement : l'estimand « nouveaux patients du même corpus » est-il honnête compte tenu de la stylométrie à 0,917 ? (B5) La règle de puissance échouera presque sûrement (largeur simulée 7,8 à 13,7 contre 4,0) : le protocole est-il alors une coquille, et que faudrait-il changer **avant** de dépenser le budget confirmatoire ? (B6) Les prédictions préenregistrées (probabilités écrites) sont-elles bien calibrées par rapport aux issues (plusieurs étaient fausses) ?

### Axe C : stratégie de réglage et équité des comparaisons
Fait : grille de 4 taux gelée, 2 époques pour tous, un taux par run, un seul run par taux ; le TF-IDF a eu une grille de C (puis une version étendue) ; les LLM un diagnostic d'époques *a posteriori* (encodeur seulement), une perte pondérée, un rejeu.
Questions : (C1) Le gel de la grille et des époques équivaut-il à comparer des LLM mal réglés à un TF-IDF bien réglé ? Quantifie la sous-estimation probable du LLM (points) en t'appuyant sur le comportement monotone en taux et le gain de CamemBERT avec les époques. (C2) Quel est le **protocole de réglage à budget égal** correct (même nombre d'essais, même heures par famille) et comment le décrire pour qu'il reste honnête malgré le gel ? (C3) Le rang LoRA, le nombre d'époques et le planning de taux, laquelle de ces dimensions rapporte le plus par heure de GPU ?

### Axe D : choix des modèles et ordre des expériences
Fait : criblage de 3 élèves (4B, 9B, E4B) à 2 taux, puis 4B retenu ; professeur de 27 à 31 milliards (QLoRA) prévu après une porte (RM-17) ; test de taille Gemma-31B lancé ; l'encodeur CamemBERT-bio et le TF-IDF coûtent 20 à 70 fois moins.
Questions : (D1) L'ordre « références bon marché complètes d'abord, LLM ensuite » aurait-il changé les décisions ? Quel est le coût d'opportunité chiffré de l'ordre suivi ? (D2) Le test de taille est-il bien conçu (un taux, QLoRA, confusion taille et quantification, règle d'arrêt) ? Qu'améliorerais-tu **sans** doubler son coût ? (D3) La distillation est-elle défendable si l'élève est 11 points sous une référence lexicale à coût quasi nul ? Quelle expérience minimale la justifierait ou l'éteindrait ? (D4) Quels autres types de modèles auraient dû être dans le criblage (encodeurs plus récents, modèles de classification dédiés, LLM en zero-shot pour mesurer la connaissance a priori de la CIM-10) et lesquels valent encore la peine ?

### Axe E : incertitude et abstention
Fait : température, ECE, Brier, conforme LAC et APS marginal et par classe, Wilson, prédiction sélective, décalage patient vers auteur ; étalonnage croisé hors pli ; probabilités conservées par run (règle écrite).
Questions : (E1) La garantie de couverture tient-elle quand l'étalonnage et l'évaluation sont deux moitiés d'un seul pli de 717 patients et que le test est prédit par un modèle entraîné sur 100 % du développement ? (E2) La couverture par classe est-elle évaluable pour des classes de 4 à 9 patients (voir simulation) ? Que rapporter honnêtement ? (E3) Quelle politique d'abstention (seuil, coût) serait défendable pour un usage hospitalier fictif, et quel risque de la présenter comme celle du système ?

### Axe F : fuite, raccourcis et estimand
Fait : contrôles de partition, quasi-doublons (seuil gelé 0,8), garde de réglage, raccourci d'auteur mesuré (RM-14), stylométrie, quasi-doublons presque tous du même auteur.
Questions : (F1) La signature d'auteur est-elle une fuite exploitée par le TF-IDF (qui perd 3,9 points en plis par auteur) et moins par les LLM (écart plus grand sur les auteurs peu représentés) ? Propose **l'expérience décisive la moins chère** qui départage fuite et thème. (F2) Faut-il changer d'estimand principal avant l'ouverture du test ? Les déclencheurs écrits (écart supérieur à 3 points sur le candidat final avec borne basse positive, lecture « fuite » confirmée) te semblent-ils bons ? (F3) Quelle expérience de robustesse mesure vraiment la généralisation (nouveaux auteurs, nouvelles spécialités) sans dépenser de GPU ?

### Axe G : ingénierie, reproductibilité, structure du travail
Fait : environnement verrouillé, 290 tests, typage strict, garde anti-affaiblissement, secrets, registre en écriture unique, reconstruction à froid en 26 s (cache chaud), déterminisme GPU non garanti (40 prédictions sur 717), audit hebdomadaire des dépendances ; travail de nuit par un assistant avec contrat, règles numérotées, journal, file de questions, délégations de décision tracées.
Questions : (G1) Que vaut la reproductibilité annoncée si deux runs de même graine diffèrent ? Que garantir (bit-à-bit, statistique) et que dire dans le rapport ? (G2) Le dispositif « assistant autonome de nuit + délégations + exclusions » est-il sain ? Quels contrôles manquent pour qu'une décision déléguée ne devienne pas une dérive (le gel protocolaire, le test scellé, les poussées de code sont exclus) ? (G3) Les relances automatiques sur panne (essais multiples) peuvent-elles masquer des échecs réels ? (G4) Que faire de la dette d'orchestration (scripts de lot détachés, journaux dans un répertoire de session, files d'attente par scripts shell) ?

### Axe H : efficience globale et plan minimal viable
Fait : environ 9 h de GPU d'entraînement enregistrées, presque toutes pour des LLM, sans résultat qui batte la référence bon marché ; plusieurs explorations (perte pondérée, ensembles) à résultat nul ou négatif, consignées ; un plan complet évalué à 70 à 84 h sur 90.
Questions : (H1) Donne le **plan minimal viable** : l'ensemble le plus petit d'expériences qui produit un livrable défendable (rapport honnête, carte de modèle, comparaison équitable) et son coût en heures de GPU et d'humain. (H2) Classe toutes les dépenses restantes par **information attendue par heure** et propose des critères d'arrêt chiffrés. (H3) Que supprimerais-tu du plan actuel ? (H4) Quelles décisions sont **irréversibles** et mal outillées ? (H5) Quelle est la probabilité que, au terme du cycle, l'élève ou le professeur batte le TF-IDF de façon résolue, et qu'est-ce qui la ferait monter ?

## 5. Auto-critique de l'assistant à juger (ne la prends pas pour argent comptant)

L'assistant s'est reproché, la nuit du 03 au 04/10/2026 : (1) d'avoir exécuté le plan de criblage LLM **avant** de pousser les références bon marché à leur plein réglage, sans alerter tôt sur l'efficience ; (2) d'avoir laissé CamemBERT à 2 époques (0,448, trompeur) jusqu'à ce que ton audit précédent (v3) incite à regarder ; (3) d'avoir proposé un ensemble comme piste avant de le mesurer (il n'aide pas) ; (4) d'avoir lancé une recherche de fichier sur tout le système de fichiers (écart de périmètre, aucun contenu lu) ; (5) d'avoir perdu trois chargements de modèle sur un défaut de placement de tête de classifieur que le pré-vol aurait dû attraper (le pré-vol était justement le test) ; (6) d'avoir mal prédit (prédictions préenregistrées fausses : TF-IDF 0,20 à 0,50, « le 9B sera le meilleur », « la perte pondérée aidera »). Dis si cette liste est **complète, excessive, ou biaisée**, et ajoute ce qu'elle a omis.

## 6. Affirmations de l'assistant à attaquer une par une

Pour chacune : **vrai, faux, non établi**, avec ta raison et le test qui trancherait.
1. « Aucun LLM ne bat le TF-IDF » (un pli, une graine, 2 époques, taux au bord).
2. « Les recettes LoRA à 2 époques sont probablement sous-entraînées. »
3. « La perte pondérée n'est pas le levier principal du déficit des petits chapitres. »
4. « Le déficit vient des petits chapitres, donc de la rareté des données. »
5. « Un ensemble par simple moyenne ne bat pas le TF-IDF. »
6. « Le creux d'exactitude des longueurs moyennes est un effet de composition. »
7. « Les erreurs traversent les familles de chapitres : un score hiérarchique n'aiderait presque pas. »
8. « Le style d'auteur est une fuite possible, non démontrée. »
9. « Le 4B est un bon élève par la règle écrite d'avance » (écart non résolu avec le 9B).
10. « Le test de taille (31B, QLoRA, un taux) tranche la question de l'échelle. »
11. « La distillation est justifiée par l'objectif du projet même si les LLM perdent. »
12. « Le protocole gelé reste utile même si la règle de puissance échoue. »

## 7. Ce que tu dois produire (un seul fichier Markdown)

**Format imposé : un fichier Markdown (`.md`) unique, rien d'autre.** Si tu ne peux pas joindre de fichier, réponds par **un seul bloc de code Markdown** contenant le fichier entier, que Cyril copiera dans `audit_GLM_v4.md`. Plan obligatoire :

1. **En-tête** : date, modèle, ce que tu as lu (ce cahier seulement) et ce que tu n'as pas pu vérifier.
2. **Verdict en 12 lignes maximum** : le projet est-il sur la bonne voie, où va-t-il perdre sa crédibilité, quelle est la décision la plus urgente.
3. **Tableau de notes par axe A à H** : note sur 10 de **l'efficacité** et de la **validité**, niveau de preuve (E0 aucune, E1 anecdote, E2 mesure unique, E3 mesure répliquée, E4 mesure confirmatoire), principale faiblesse, correction la moins chère.
4. **Axes A à H** : pour chacun, steelman (2 lignes), les réponses numérotées aux questions, **les 5 corrections classées** (effort humain, heures de GPU, gain attendu en points ou en probabilité, risque ou conflit avec le gel, preuve de fin), et **l'expérience décisive minimale**.
5. **Section « affirmations »** : les douze verdicts de la section 6.
6. **Plan minimal viable (H1)** et **classement des dépenses restantes par information par heure (H2)**, avec critères d'arrêt chiffrés.
7. **Les trois erreurs que tu ferais à notre place**, et **les trois choses que tu referais exactement pareil**.
8. **Tableau de preuve de ta réponse** : chaque chiffre cité renvoie au cahier (« cahier § x ») ou est marqué *estimation* ou *conjecture*. **Étiquette chaque phrase factuelle** par `[FAIT]` (vient du cahier), `[INFÉRÉ]` (déduction que tu expliques) ou `[CONJECTURE]` (jugement d'expert sans preuve ici). Ne mélange jamais les trois.

Règles de style : français, prose sans tiret cadratin ; tableaux pour les notes et les plans ; pas de paragraphe de plus de six lignes ; pas de remerciement ni de reformulation du cahier.

## 8. Règles que toute recommandation doit respecter (sinon, dis-le et propose une variante)

1. **Le protocole gelé ne se modifie pas en silence** : toute règle changée = nouvelle version du protocole + ADR + décision de Cyril. Dis explicitement si une action l'exige.
2. **Le test scellé n'est jamais lu** avant son ouverture unique ; aucune recommandation ne peut s'appuyer dessus.
3. **Pas de donnée de patient réel**, pas de location de GPU, pas d'API payante, pas de modèle à accès conditionné non accepté.
4. **Toute affirmation chiffrée renvoie à une mesure** ; les résultats négatifs sont publiés.
5. **Simple** = au plus une demi-journée de travail et 3 h de GPU ; sinon, découpe.
6. Les décisions de **promotion d'une recette en référence**, de **changement d'estimand**, de **poursuite de la distillation** et d'**envoi hors machine** appartiennent à Cyril : donne un avis chiffré, ne tranche pas.
7. Ne propose pas de calcul que tu ne peux pas justifier ; si une simulation est nécessaire, décris-la (entrées, tirages, critère) pour que l'assistant l'exécute.

## 9. Prompt augmenté, prêt à coller avec ce fichier

> Tu es un chercheur principal en apprentissage automatique appliqué au texte clinique, formé au plus haut niveau (type MIT), avec vingt ans de pratique en méthodologie d'évaluation, en adaptation de grands modèles de langage (fine-tuning, distillation, quantification) et en revue par les pairs. Tu es adversarial par métier et jamais complaisant.
>
> Je te joins un cahier d'audit autonome (`BRIEF_GLM_v4_audit_efficacite_methodes.md`). Lis-le en entier avant de répondre. Ta mission : auditer l'**efficacité** des méthodes employées, la **validité** des protocoles de validation et la **pertinence** des stratégies structurelles du projet, axe par axe (A à H), puis juger les douze affirmations de la section 6 et l'auto-critique de la section 5.
>
> Méthode obligatoire, dans cet ordre, pour chaque point : (1) steelman en deux lignes ; (2) attaque la plus forte ; (3) chiffre l'enjeu (points de macro-F1, heures de GPU, probabilité d'une conclusion fausse) ; (4) la correction la moins chère qui lève le doute ; (5) ce qui te ferait changer d'avis. Avant de rendre ta réponse, **relis-la en cherchant tes propres erreurs** : une affirmation sans étiquette `[FAIT]`, `[INFÉRÉ]` ou `[CONJECTURE]` est interdite ; un chiffre qui n'est pas dans le cahier doit être marqué *estimation* ou *conjecture*.
>
> Interdits : flatterie, précautions oratoires sans chiffre, recommandations génériques (« augmenter la taille des données », « utiliser plus de graines » sans coût et sans gain attendu), reformulation du cahier, tout calcul invérifiable. Sois dur, précis et utile : Cyril décide ensuite.
>
> Format de réponse : **un seul fichier Markdown** (`audit_GLM_v4.md`) suivant exactement le plan de la section 7 du cahier ; si tu ne peux pas joindre de fichier, un seul bloc de code Markdown contenant le fichier entier. Respecte les règles de la section 8 (protocole gelé, test scellé jamais lu, aucune donnée réelle, pas de location, pas d'API payante, décisions réservées à Cyril).

## 10. Tableau de preuve de ce cahier (claim-gate)

| Groupe de chiffres | Source dans le dépôt (non fournie à GLM) | Statut |
|---|---|---|
| Effectifs, plis, auteurs, classes | `results/measures/splits_summary.json` | prouvé |
| TF-IDF 0,6844 [0,6573 ; 0,7089], pli 0 0,6971, v2 0,6889, groupé 0,6457, RM-14 +3,87 | `RESULTATS.md`, runs `p1-06-*`, `rm-14-*` | prouvé |
| LLM : 4B (0,193, 0,306, 0,473, 0,587), 9B (0,213 ; 0,565), E4B (0,142 ; 0,456), durées, pics | `RESULTATS.md`, runs `p1-11-*`, `p1-13-*` | prouvé (pli 0, une graine) |
| Écarts appariés (4B moins 9B, 4B moins TF-IDF, 5e-5 moins 1e-4) | runs `p1-11-qwen4b-minus-*`, `p1-13-4b-5e-5-minus-1e-4-fold0` | prouvé |
| CamemBERT 2, 4, 6 époques et écarts | runs `p1-07-*`, `camembert-epoques-*`, `camembert-ep6-minus-*` | prouvé (EXPLORE) |
| Perte pondérée, rejeu de même graine, ensembles | runs `q19-*`, `p1-26-*`, `results/measures/p1_26_determinism.json`, `ensemble_fold0.json` | prouvé (EXPLORE) |
| Incertitude TF-IDF, CamemBERT, 4B ; simulation de couverture | runs `q5-uncertainty-*`, `results/measures/glm_v3_coverage_sim.json` | prouvé (périmètres dits) |
| Auteur : identifiant dans le texte, stylométrie 0,917, quasi-doublons 9, 45, 171, hors spécialité 0,522, perturbations, familles, tronqués, sous-groupes | `results/measures/glm_v3_*.json` | prouvé (agrégats, développement) |
| Coûts : 9 h enregistrées, plan 70 à 84 h, professeur 15,8 à 29 h, pannes | `scripts/budget_alert.py`, `scripts/spikes/budget_v2.py`, journal de nuit | prouvé pour 9 h ; estimation pour le reste |
| Test de taille et variantes TF-IDF en cours ; TF-IDF « balanced » 0,6805 | fiches `2026-10-04-*`, run `tfidf-variant-balanced` | en cours (balanced prouvé, autres sans résultat) |
| Auto-critique, affirmations à attaquer | journal de nuit, échanges avec Cyril | jugement de l'assistant, à contre-expertiser |
