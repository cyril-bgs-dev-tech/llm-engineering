# Audit du lancement de projet (spec-driven), GLM 5.3, v1

Date : 01/10/2026. Périmètre : `PLAN_PROJET_V6.md`, `MICROTACHES.md`, `BOITE_A_OUTILS.md`, `PROMPT_LANCEMENT.md`, `scripts/check_microtasks.py`, `docs/CATALOGUE_LEVIERS.md`, squelette `knowledge/`, dossier `.claude/`.

Question posée par Cyril : où peut-on gagner du temps sans perdre en qualité ni en sécurité, dans ce déroulé d'exécution P0 et au-delà ? Ce document liste des observations ; rien n'irréversible n'est proposé. Les numéros de plans cités renvoient aux sections concernées.

Méthode : lecture intégrale des fichiers cités, exécution de `python scripts/check_microtasks.py` (vert, exit 0, 135 micro-tâches dont 68 sur le chemin court ★ : le compte annoncé au plan V6, section 8, est cohérent avec le backlog), consultation matérielle de l'environnement réel (RTX 5090 présente, 32 Go, driver 610.47 ; WSL rapporte 68 Go de RAM ; 198 Go libres sur D:). Aucun fichier hors du dossier de travail n'a été ouvert, hors ces requêtes matérielles.

---

## 1. Constats structurants (à traiter en premier)

### 1.1 Le registre de runs n'existe pas quand les spikes écrivent "au registre"

Constat : P0-08 (banc QLoRA du professeur) exige "Pic de mémoire... et temps par pas **au registre**". Idem pour la logique de preuve de P0-07 et P0-10. Or le squelette du registre (P0-41) dépend de P0-11 (uv.lock et Docker) et arrive **après** les spikes dans l'ordre du prompt (étape 5 avant étape 6). Aucun contrôle de `check_microtasks.py` ne détecte cette contradiction sémantique (il ne vérifie que l'existence et les cycles des dépendances).

Effet : soit les résultats de spike sont notés "à la main" puis transcrits (double saisie, risque d'incohérence de numéro de run), soit on retarde les spikes (contre la règle "le risque d'abord", règle 4 du backlog).

Action : extraire du P0-41 une variante minimale, environ 30 minutes, purement bibliothèque standard (fichier JSON append-only + validateur, aucun `env` requis pour un spike), dépendant de rien, et l'exécuter **avant** P0-04. P0-41 complet garde ses dépendances actuelles. Ce point est le seul vrai bug d'ordonnancement relevé dans le backlog.

### 1.2 Stratification des plis (P0-28) vs politique des classes rares (P0-33) : l'ordre logique est inversé

Constat : P0-28 exige des "5 plis stratifiés" et ne dépend que de P0-22 (présence du diagnostic). P0-33 (seuil de classe rare, regroupement, classe "autre") dépend de P0-23 et arrive donc après le point de décision du découpage. Stratifier un multiclass de 20 chapitres CIM-10 dans lequel des dizaines de classes tombent sous un seuil minimal est impossible sans avoir d'abord décidé quoi faire des classes rares : sinon on re-découpe plusieurs fois, avec le risque d'incohérence d'empreintes entre les deux découpages.

Effet : perte de temps directe (découpage refait) et risque qualité (deux découpages cohabitants dans le dépôt).

Action : faire dépendre P0-28 de P0-22 **et** de P0-33 (ou déplacer la partie "seuil" de P0-33 avant P0-28 ; l'application par script reste après). Une ligne de modification de dépendance, vert au script de contrôle.

### 1.3 Git et .gitignore doivent venir avant le premier téléchargement

Constat : le dossier n'est pas un dépôt Git (vérifié ce jour). P0-02 (décision dépôt GitLab) arrive au début, mais P0-14 (téléchargement PARHAF) n'est sécurisé "données ignorées par Git" que par sa preuve de fin ; rien n'impose que `.gitignore` existe avant que `data/` soit rempli. Un téléchargement accidentellement commité de données sous licence et d'usages interdits (déploiement, publication) est le pire scénario simplement évitable ici.

Effet : sécurité et conformité (Q10) ; un `git rm --cached` après coup laisse une empreinte dans l'historique, ce qui n'est pas un rattrapage propre.

Action : dans l'étape 2 du prompt (décisions), dès que P0-02 est tranché, faire `git init`, écrire `.gitignore` (`data/`, `models/`, `artifacts/`, `.venv/`, caches, répertoires de runs non versionnés) et le premier commit d'amorçage avant P0-14. Les commits restent à la demande de Cyril (règle CLAUDE.md), donc lui montrer ce commit unique d'amorçage.

### 1.4 L'unité de lieu des poids et des caches : ext4, pas /mnt/d

Constat : le projet vit sur `/mnt/d` (NTFS via drvfs). Sur ce cheminement, les I/O aléatoires (loading de shards de poids safetensors, écritures de checkpoints) sont nettement plus lentes que sur ext4 natif du côté Linux ; git et `uv` y sont également ralentis. La VRAM de la 5090 n'est pas le goulot d'étranglement ici, le disque l'est. Le disque D: a 198 Go libres ; l'espace libre de la partition ext4 du côté Linux (`/`) n'a pas été mesuré ce jour, à vérifier avant de choisir.

Effet : plusieurs fois gainés sur les spikes de P0 (chargements répétés), et surtout sur les professeurs cinq plis QLoRA de P2 (checkpointing répété de multiples gigaoctets).

Action : fixer dès P0-11 `HF_HOME` et le répertoire de checkpoints sur un chemin ext4 (par exemple `~/.cache/huggingface` et un `artifacts/` Linux), documenté dans la page wiki `env-blackwell` ; garder le code et le git sur `/mnt/d` si Cyril veut rester éditable depuis Windows. `df -h /home` avant de choisir. Mesurer au moins un chargement NTFS contre ext4 dans le spike P0-05 (une mesure, un chiffre, un run_id).

### 1.5 RAM réellement vue : 68 Go, pas environ 96

Constat : `free -g` voit un total de 68 Go dans cette session WSL, alors que CLAUDE.md indique environ 96 Go pour la machine. Avec WSL2, la mémoire visible depuis Linux est plafonnée par `.wslconfig` (ou par défaut à une fraction de la RAM Windows) ; si la RAM Windows est de 96 Go, WSL est vraisemblablement plafonné (68 Go implicites vus ci-dessus).

Effet : la tokenisation et l'assembly de datasets de PARHAF tiennent de toute façon dans 68 Go ; mais toute opération "hors GPU" gourmande (par exemple le chargement complet d'un tokenizer ou le manifeste DVC sur un gros corpus de PARCOMED) doit viser la mémoire vue par WSL, pas celle de la machine hôte. Si Cyril veut lever le plafond, c'est une ligne dans `.wslconfig` à tenter à froid (redémarrage WSL) et à documenter.

Action : consigner la RAM WSL réelle dans la page `env-blackwell` ; une ligne de `.wslconfig` si besoin, décision de Cyril (c'est sa machine).

---

## 2. Gains de temps concrets dans le même déroulé, sans perte de qualité

### 2.1 Réordonner le prompt pour télécharger pendant que Cyril décide

Constat du prompt actuel : étape 1 contrôle, étape 2 interview P0-01 à P0-03 (bloquent sur une réponse humaine), étape 3 SPEC, étape 4 plan de tâches, étape 5 spikes. Chaque spike installe des paquets de plusieurs gigaoctets (torch cu128/cu130, transformers v5, un modèle d'au moins 1 milliard de paramètres).

Action, sans ordonner de quoi que ce soit d'irréversible : dès l'étape 1, lancer en tâche de fond les téléchargements (paquets uv dans un environnement jetable, un premier model hub léger), puis conduire l'interview pendant qu'ils tournent. Idem pour les époques d'écriture de SPEC-P0.md et de tasks/plan.md : écrire en attendant les téléchargements. Le gain est matérialisé par des temps d'attente de minutes ou de dizaines de minutes par téléchargement paresseux. Rien d'irréversible : l'environnement jetable n'engage rien.

### 2.2 Réutiliser un seul environnement la première fois au lieu de trois installations

Constat : P0-04 demande un environnement jetable pour PyTorch, P0-05 en installe un autre pour transformers v5/peft/trl/bitsandbytes, P0-11 fige ensuite uv.lock et le Dockerfile. Deux installations complètes (et des téléchargements en gigaoctets) sont faites pour ce qui peut être une seule, suivie d'un figement.

Action : P0-04 et P0-05 partagent le même environnement jetable (torch installé d'abord, puis le reste des paquets par-dessus, chaque bibliothèque vérifiée séparément), que P0-11 fige ensuite dans le lock. Les critères d'acceptation des deux spikes restent inchangés (liste d'architectures, journal de 10 pas, tableau sm_120 oui ou non). Gain : un cycle de téléchargement évité, aucun compromis sur la preuve.

### 2.3 Fusionner P0-06 et P0-08 en un seul passage "le plus gros professeur chargé une fois"

Constat : P0-06 (compatibilité de classification pour chaque candidat) et P0-08 (banc de 10 pas du plus gros professeur en QLoRA) chargent chacun le modèle de 27 ou 31 milliards de paramètres. Le poids est le goulot de tout ce chargement (dizaines de gigaoctets).

Action : un script unique lance l'ordre de priorité : d'abord les élèves en taille réduite (4B, 9B, E4B), puis le plus gros professeur une fois chargé sert simultanément les deux vérifications (classification, puis 10 pas QLoRA dans la même session). Deux preuves séparées, un seul chargement lourd. Gain en temps de téléchargement et en temps GPU.

### 2.4 Repousser hors du chemin critique P0-09 (vLLM) et moitié de P0-10 (quantification fine)

Constat : P0-09 (service vLLM) et P0-10 (INT8/FP8/NVFP4) sont déjà non étoilés. Or le prompt de lancement étape 5 dit "spikes d'abord (P0-04 à P0-10)", c'est-à-dire les ordonne dans le chemin critique de la phase P0 ("le risque d'abord"). Or vLLM sur machine de développement Windows/WSL impose des téléchargements lourds et des conflits de noyaux CUDA ; son besoin scientifique n'apparaît réellement qu'en P5, avec un plan de repli Transformers dès le départ documenté, et P0-10 ne récolte un retour d'expérience réel qu'en P4-02.

Action : garder les spikes étoilés dans le début de phase (P0-04, P0-05, P0-06, P0-08), décaler P0-09 et P0-10 comme "prélude" avant P5-01/P4-02 (au plus tard, D-1 de la phase consommatrice). Le plan de repli du plan V6, section 9, reste écrit. Gain : une installation de quelques gigaoctets et une demi-journée de risque de mise au point sortent du chemin critique, sans rien creuser en qualité car les décisions correspondantes (P5-03, P4-02) restent mesurées et appariées.

### 2.5 Les cinq fiches de jeux optionnels (P0-18, P0-19, P0-24, P0-25, P0-26) sont hors du chemin court

Constat : ces fiches existent pour des usages P2 et P6 (sous-ensembles annotés, PARCOMED, MorFITT, CLISTER, DiaMED). Elles sont déjà non étoilées, donc hors du chemin court, et ce n'est pas un défaut. Le risque est seulement de les croire "flashées" à échéance de G-P0 si l'agent exécute dans l'ordre séquentiel du bloc P0-C.

Action : les étiqueter explicitement "à clore avant leur premier usage, pas avant G-P0" dans le wiki ou dans `tasks/plan.md`, et les retirer du lot quotidien P0. Les cinq fiches restent obligatoires avant P2 (exigences de `dataset-intake` intactes), simplement pas en début de projet. Gain : demi-journée reportée où elle est utile, zéro perte (ce sont des lectures de licence).

### 2.6 P0-47 (ingestion wiki des huit papiers du Lot A) en tâche de fond

Constat : P0-47 n'a **aucune dépendance** (dépendance "-") dans le backlog ; c'est le seul travail de la phase P0 complètement indépendant du reste. Or le prompt le place en étape 7, en fin de session, là où le contexte d'agent est le plus chargé et où le risque d'être coupé est maximal. C'est également la tâche où un sous-agent peut avancer en parallèle pendant que Cyril relit un livrable, et où des relectures croisées avec claims sourcés sont plus utiles en début de session qu'en fin.

Action : lancer l'ingestion wiki (`wiki-ingest` du Lot A, fiches sources à citations par lignes, puis `wiki-lint`) le plus tôt possible, idéalement pendant les téléchargements ou pendant les temps d'attente de relecture de Cyril. Si la session manque de temps, c'est la seule tâche P0 suffisamment indépendante pour être déplacée vers une session suivante sans en retarder aucune autre.

### 2.7 Parallélisation par sous-agent quand un document attend une relecture humaine

Constat : le prompt précise, à juste titre, "montre-moi le livrable et attends ma validation" à chaque étape. Ces temps d'attente se cumulent. Un sous-agent peut préparer en tâche de fond le brouillon documentaire suivant (fiche de jeu, page de wiki, ADR à partir d'une réponse déjà donnée) sans rien lancer de lourd au GPU et sans rien pousser sur disque hors de `docs/` ou `knowledge/`.

Action : habitude d'exécution : pendant chaque validation humaine, lancer la tâche de fond suivante. Gain de temps réel sans que la validation humaine soit contournée.

---

## 3. Durcissement qualité à coût quasi nul (checklists, garde-fous, tests)

### 3.1 Renforcer `check_microtasks.py` avec trois contrôles bon marché

Constat actuel du script (vérifié vert ce jour) : il vérifie identifiants, nombre par phase, numérotation continue, dépendances existantes, cycles, chemin court fermé, plafonnages de planchers, identifiants cités, tirets interdits. Trois choses faciles qu'il ne vérifie pas encore, mais qui sont déjà des invariants énoncés ailleurs :

1. **Chaque `GPU` ou `spike` cite un outil de calcul**. La règle 3 du backlog (fiche préenregistrée, `vram-preflight`, `run-registry`) n'est pas vérifiée. Un contrôle textuel (présence de `vram-preflight` dans la colonne Skill pour toute ligne de type GPU ou spike, scorecards exclues) le rend opportun à corriger avant la première réelle exécution.
2. **Le compte affiché "68 des 135" du plan est une affirmation morte** si le backlog évolue. Faire lire le nombre d'étoiles par le plan depuis une seule source de vérité, à savoir le résultat du script, et corriger le plan en cas d'écart, ou écrire le compte calculé dans la section 8 à chaque édition.
3. **Les skills cités dans la colonne Skill existent réellement**. Comparer les noms de skills de la colonne à `ls .claude/skills/` (les noms de skills sont déjà uniques). Aujourd'hui rien n'empêche une faute de frappe ou un renommage de rendre un lien vers des instructions muet.

Effet : les trois contrôles tiennent en quelques dizaines de lignes de bibliothèque standard, aucun compromis de contenu, une seule source de vérité maintenue.

### 3.2 `make check` (P0-42) : inclure wiki-lint et check_microtasks dès le départ

Constat : `CONSTRAINTS.md` apparaît en P0-42 comme commande `make check` (types, lint, tests, gitleaks, couverture). Deux vérifications déjà existantes du projet ne sont pas citées à la liste : `scripts/check_microtasks.py` et `wiki-lint` (du savoir de la veille à jour). Les intégrer à `make check` transforme deux vérifications manuelles en gate automatique, exactement ce que coûte le plus cher en temps quand on les oublie (plus bas, une contradiction documentaire est passée dans `BOITE_A_OUTILS.md` à la section 6). Un gitleaks de projet apparaît réellement seulement à P0-42, alors que le coût d'une fuite est le plus bas quand il est intercepté le plus tôt (premier commit).

Action : une ligne par integration, aucune nouvelle dépendance, `pre-commit` si on veut aller plus loin mais cela n'est pas nécessaire dès le départ.

### 3.3 Le test de transposabilité (P0-44) doit tourner dans la CI sans GPU

Constat : la preuve de P0-44 exige la même chaîne "chargement, 10 pas, évaluation, registre" sur la tâche de jugeling et sur `parhaf_doctype`. Dix pas sur un vrai LLM ne tiennent pas dans une CI locale sans GPU ni dans des délais raisonnables.

Action : conserver P0-44 tel quel sur la 5090 (c'est un rituel exécution réelle) et ajouter une variante CI avec un modèle mock ou un petit encodeur CPU (par exemple un encodeur de type sentencepiece ou un classifieur à tête fine, 10 pas se comptent en secondes sur CPU). La preuve de transposabilité reste identique, la CI ne dépend pas du matériel. Écrire le test comme paramétrable `backend:{cpu,gpu}` depuis le début.

### 3.4 Un test anti-oubli dès le premier chargement de données : conserver la taille exacte par partition au registre

Constat : P0-21 compte les documents, patients, spécialités une fois, à l'intake. Rien ne recharge ces nombres à chaque run ou ouverture de phase. Or la divergence des sources (18 ou 20 spécialités, 6 185 ou 6 190 documents) est exactement le genre de chose qu'une acquisition ou un remplacement de version fait dériver silencieusement.

Action : au chargement (l'adaptateur de P0-43), vérifier un hash de configuration des partitions vs une référence versionnée, et jeter si divergence non déclarée. Coût : une dizaine de lignes. Filet de sécurité au-delà des tests de P0-40.

### 3.5 `PROTOCOLE.md` figé : l'empreinte passe aussi dans le wiki

Constat : P0-46 calcule le SHA-256 et la preuve est "fichier figé, empreinte consignée avant tout run". Aucun emplacement n'est imposé à l'empreinte. Un fichier peut être modifié après empreinte en session suivante sans qu'une relecture le voie. Un seul fichier, en clair, réglé au plancher.

Action : consigner l'empreinte aussi dans une page wiki datée (par exemple `protocole-v1`), une seule autorité à relecture.

---

## 4. Incohérences documentaires relevées (petit mais à corriger avant P0-47)

Ces points coûtent quelques minutes à corriger et évitent des antigènes au moment de la relecture par Cyril ou d'un audit wiki.

| # | Où | Incohérence | Effet |
|---|---|---|---|
| 1 | `BOITE_A_OUTILS.md` section 6, Lot A ligne A1 | Le papier A1 cite "1re place LMSYS (sayoulala, août 2024)" alors que la section 3 cite le dépôt "shyoulala/LMSYS_BlackPearl". Une orthographe des deux est probablement une typo | Un wikilien ou une recherche cassée plus tard ; à corriger à l'ingestion en P0-47, en citant le vrai propriétaire du dépôt telles que le GitHub l'affiche |
| 2 | `BOITE_A_OUTILS.md` section 1 | PARHAF annotés "Conclusion : 7 554 lignes (3 664 train, 108 dev)" : 3 664 + 108 fait 3 772, ne pas valoir 7 554. Les 7 554 peuvent être la somme sur des plis d'une autre définition, le doute est méthodique | Chiffre à revérifier à P0-18 avec la fiche réelle et à corriger si faux, sinon à expliquer en note |
| 3 | Dépendance du P0-28 | P0-28 ne dépend pas de P0-33 (seulement P0-22), cf. 1.2 | Découpage refait si les classes rares sont regroupées après coup |
| 4 | `MICROTACHES.md` P0-14 | Sa preuve finit par "`data/` ignoré par Git", mais rien dans "Dép." ou dans le prompt n'exige que `.gitignore` soit en place avant P0-14 | Cf. 1.3, installer `.gitignore` via le premier P0-02 |
| 5 | `PROMPT_LANCEMENT.md` étape 5 | "spikes d'abord (P0-04 à P0-10)" contient P0-09 et P0-10, dont le plus urgent est non bloquant ; le plan V6 de la section "risques" ne les oblige pas au chemin critique | Cf. 2.4, les décaler comme préludes optionnels vers P4/P5 |
| 6 | `CLAUDE.md` section Matériel | "environ 96 Go de RAM" contre 68 Go visibles par WSL ce jour | Consigner l'écart dans `env-blackwell` ; correction documentée pour éviter un faux diagnostic « la machine manque de RAM » |

Rien d'irréversible n'a été proposé : ce sont des lignes de documentation et une dépendance de tâche à ajuster.

---

## 5. Ce qui est déjà bien fait (à ne pas saboter sous prétexte d'aller plus vite)

Les points suivants valent de l'or et ne coûtent presque rien à conserver ; les retirer produirait une dette qu'on paierait en P2 ou pire :

- **Le test scellé à accès restreint par un seul script (P0-34) avec un test qui échoue si un autre module le lit** : rare d'y penser avant le premier run.
- **Le test de transposabilité (P0-44) sur une tâche de jugeling de deux classes et sans branche propre à une tâche** dans le code : le plus gros risque de "code propre à une tâche" écrit par un agent est prévenu par un test, pas par une règle morale.
- **Le chemin court fermé et vérifié par un script** (68 étoiles dont aucune ne dépend d'une non-étoile) : rarement écrit formellement ; ce contrôle est la vraie défense MVP.
- **Un gain n'est valide que si sa méthode de calcul se joue à détection d'écart-type supérieure à deux fois l'écart-type de graines** (règle Q3), et l'écart-type de graines est mesuré avant toute décision (P1-19) : correct.
- **Le verdict en trois valeurs** (gain, absence de gain, non résolu) et les résultats négatifs publiés au même rang que les positifs, à un statut égal dans RESULTATS.md : économiquement rare et scientifiquement solide.
- **Deux implémentations indépendantes de la prédiction conforme** (MAPIE, TorchCP, maison) doivent s'accorder (P4-06) : exactement ce qu'une affirm à usage clinique demande.
- **`claim-gate`** : chaque affirmation sortie passe un tableau de preuve, ça protège les outputs professionnels (CV, LinkedIn, lettre) du piège où la promesse dépasse le chiffre.
- **Le caractère immuable des fiches préenregistrées** de run-GPU et de location (R-01) avec plafond plausible validé par Cyril : protège aussi bien contre l'excès de CPU que contre le gonflement de promesse.
- **La règle GPU : un processus non lancé par l'agent est signalé et laissé en place** : très bon garde-fou d'environnement partagé.

En bref, ne pas gratter le socle pour aller plus vite. Les gains retenus ci-dessus sont des réorganisations d'ordonnancement, pas des raccourcis de protocole.

---

## 6. Ce que je n'ai pas vérifié (limites de l'audit)

Pour l'honnêteté du compte rendu, et conformément à `claim-gate` dès maintenant, dès le début :

- Les accès réseau (HF, CodaBench, site ATIH) n'ont pas été testés ce jour, pas plus que la disponibilité de Docker Desktop sur la machine ; le spike P0-04 le révélera.
- Les licences réelles affichées dans `BOITE_A_OUTILS.md` (statut ✅ ou 🔎) sont celles de la veille du même jour mais restent à confirmer à la source pendant P0-12 ; rien de neuf n'a été re-vérifié dans cet audit.
- Le support SM120 des noyaux cu128/cu130 de PyTorch n'a pas été testé, c'est le rôle de P0-04 et P0-05.
- Aucun run GPU ; aucune charge VRAM ; les ordres de grandeur de durée annoncés dans le plan (par exemple "environ 2 h de travail" par micro-tâche, plusieurs semaines au total) ne sont pas challengés, faute de runs réels enregistrés.
- Les contenus de `.claude/agents/` (les trois relecteurs) et de `.claude/references/` n'ont pas été ouverte, par absence de lien direct avec la question du déroulé d'exécution.

---

## 7. Synthèse : la liste d'actions triées par rapport temps et qualité

| # | Action | Effet principal | Coût estimé | Tranche |
|---|---|---|---|---|
| 1 | Mini-registre JSON append-only avant P0-04 (extrait de P0-41) | Corrige la seule contradiction d'ordonnancement du backlog | 30 min | P0, avant tout spike |
| 2 | `.gitignore` + premier commit d'amorçage dès P0-02 tranché | Sécurité de la donnée PARHAF sous licence | 10 min | P0 |
| 3 | Déplacer P0-09 et P0-10 hors du chemin critique de P0 (préludes vers P4/P5) | Sort des installations lourdes de l'étape risquée | 0 | P0 |
| 4 | Environnement unique pour P0-04 et P0-05, une seule session de téléchargements | Évite un second cycle de téléchargement lourd | 0 (organisation) | P0 |
| 5 | Un seul chargement du gros professeur pour P0-06 + P0-08 | Économie de téléchargement et de temps GPU | 0 (organisation) | P0 |
| 6 | Téléchargements en arrière-plan (paquets, modèles) pendant les interviews P0-01 à P0-03 | Réduit le temps d'attente de dizaines de minutes par cycle | 0 | P0 |
| 7 | `HF_HOME` et checkpoints sur disque ext4, mesure NTFS contre ext4 dans P0-05 | I/O d'entraînement nettement plus rapides sur les professeurs cinq plis de P2 | 15 min | P0-11 |
| 8 | P0-28 dépend de P0-33 (politique des classes rares avant stratification) | Évite un redécoupage et une double empreinte | 1 ligne + script vert | P0 |
| 9 | `make check` inclut `check_microtasks` et `wiki-lint` dès P0-42 | Deux gates manuelles deviennent automatiques | 5 min | P0-42 |
| 10 | Trois contrôles bon marché ajoutés à `check_microtasks.py` (vram-preflight obligatoire sur GPU et spike, compte d'étoiles cohérent, skills existants) | Prévient la dérive silencieuse des documents de référence | 30 lignes | P0-42 |
| 11 | Test de transposabilité P0-44 avec backend CPU pour la CI | CI tenable sans GPU, même preuve | 20 min de refactor | P0-44 |
| 12 | Correction des six incohérences de l'article 4 | Fiable en relecture et en citation | 15 min | avant G-P0 |
| 13 | RAM WSL réelle (68 Go) consignée dans `env-blackwell`, décision `.wslconfig` à Cyril | Évite un diagnostic à l'aveugle d'un OOM système pendant P2 | 5 min | P0-04 |
| 14 | P0-47 (ingestion wiki du Lot A) avancé au plus tôt, pendant les temps d'attente ou dans une session parallèle | Supprime le risque de le couper en fin de session chargée | 0 (organisation) | P0 |

Sur ces quatorze actions, aucune ne touche à un contrat de tâche, à une métrique, à un seuil, à un protocole statistique, à une règle de fuite ou de licence : toutes sont des réorganisations d'exécution, des garde-fous supplémentaires ou des corrections documentaires. Leur somme devrait éviter un nombre de jours de délai sans toucher à un seul chiffre scientifique du projet. À l'inverse, aucune proposition ici ne vise à réduire les preuves exigées par les portes G-P0 à G-P5.

---

*Audit informatif, sans action irréversible exécutée. Toutes les actions proposées restent à valider par Cyril avant modification des fichiers du projet (règle "décisions de Cyril" de CLAUDE.md).*
