# LLM_finetuning : distiller des LLM sur des comptes rendus médicaux français, en 100 % local

Plan v1, 01/10/2026. Statut : **à valider avant toute ligne de code.**

## 0. Pourquoi ce projet

**L'offre visée.** CHU Grenoble Alpes (CHUGA), Cellule d'Ingénierie des Données de Santé (EDS + CIC-IT),
poste « Ingénieur.e Data Science » pour **fine-tuner et évaluer des LLM sur les comptes rendus hospitaliers**,
dans le cadre du projet national **PARTAGES** (Plateforme des Données de Santé + AP-HP : corpus médicaux
français ouverts, modèles génératifs ouverts, « analyse, structuration et génération de comptes rendus »).
Missions : jeux de données textuels et leur mise en qualité, déploiement et **évaluation** d'algorithmes NLP,
**protocoles d'évaluation de la performance**, industrialisation, maintenance, documentation, GitLab.
Stack citée : Python, R, SQL, NoSQL, architectures NLP, ElasticSearch, GitLab, Wiki.

**Le trou à combler, dit honnêtement.** Cyril n'a encore jamais fine-tuné de LLM (vérifié le 01/10 :
le « fine-tuning » du Master 2 concerne un CNN d'images ; les lignes « CamemBERT, fine-tuning LLMs » de
`portfolio_master_projects.md` sont un gabarit non rempli). Ce projet existe pour que la réponse à
« avez-vous déjà fine-tuné un LLM ? » devienne « oui, voici le protocole, les chiffres et le code ».
**Rien n'en sera affiché sur le CV ou LinkedIn avant d'être réellement mesuré.**

**La méthode de référence.** La solution 1re de la compétition Kaggle *LMSYS Chatbot Arena Human Preference
Predictions* (sayoulala, août 2024, « Distill is all you need ») :

| # | Stratégie gagnante | Ce qu'elle résout |
|---|---|---|
| S1 | LLM décodeur + tête de classification (`AutoModelForSequenceClassification`), LoRA sur toutes les couches linéaires (r=64, α=128), max_len 1024, 2 époques, batch global 64 | Utiliser un LLM comme classifieur, pas comme générateur |
| S2 | « Post-pretrain » : 1 époque sur des données étiquetées mais bruitées (jeu « ut »), lr 1e-5 | Mettre le modèle dans le bon régime avant la vraie tâche |
| S3 | Gros professeurs (70B / 72B) en QLoRA, entraînés en 5 plis, qui produisent des probabilités hors pli sur tout le jeu d'entraînement | Fabriquer des étiquettes « souples » de qualité |
| S4 | Distillation vers un élève 9B : perte classique + KL vers les professeurs (plusieurs pertes), lr 5e-5, cosinus avec 100 pas d'échauffement ; plusieurs professeurs = plus stable | Garder la qualité des gros modèles dans un modèle déployable |
| S5 | Moyenne directe des poids LoRA des 5 plis, tête de classification comprise | Un seul modèle au lieu d'un ensemble de 5 |
| S6 | Quantification 8 bits GPTQ | Tenir le budget d'inférence |
| S7 | Augmentation au test (TTA), préférée à un contexte plus long | Gagner en robustesse à budget constant |

Le parallèle avec le CHU est direct : **les données de santé ne sortent pas de l'hôpital et le GPU sur place
est limité.** Un gros modèle sert à enseigner, un petit modèle quantifié sert en production. C'est exactement
la contrainte de la compétition (inférence sur 2 × T4), transposée à un serveur hospitalier.

---

## 1. Les tâches et les données (toutes publiques, aucune donnée patient réelle)

Choix guidé par l'offre : **texte clinique français**, **structuration** et **évaluation**.
Source principale : **DrBenchmark** (Univ. Avignon, 20 tâches biomédicales françaises, jeux sur Hugging Face).
Licences à revérifier jeu par jeu en phase 0 (certains jeux DrBenchmark, comme CAS et ESSAI, exigent un accord d'usage).

### Piste A : classification de cas cliniques (reproduction fidèle de la méthode)
| Jeu | Contenu | Tâche | Licence annoncée |
|---|---|---|---|
| **DiaMED** | 739 cas cliniques français | Chapitre CIM-10 du diagnostic principal (multiclasse) | CC BY-SA 4.0 |
| **MorFITT** | 3 624 résumés PMC, 12 spécialités | Spécialités médicales (multi-label) | CC BY-SA 4.0 |
| DEFT 2021 (tâche 1), si accessible | Cas cliniques français | Profil clinique (multi-label) | à vérifier |

DiaMED est le plus proche d'un compte rendu et d'un geste de **codage**, mais petit (739 cas) :
c'est précisément là que la distillation et les données bruitées (S2) doivent prouver leur intérêt.
Le codage CIM-10 n'est **pas** cité dans l'offre : il est présenté comme un cas de « structuration », pas comme une exigence.

### Piste B : comparaison par paires (le format exact de LMSYS)
| Jeu | Contenu | Tâche |
|---|---|---|
| **CLISTER** | Paires de phrases issues de cas cliniques français | Similarité sémantique (score 0 à 5) |

LMSYS compare deux textes ; CLISTER aussi. C'est la transposition la plus fidèle de l'architecture gagnante
(deux segments dans une même entrée, tête de sortie unique), et elle sert directement l'**évaluation** de
textes générés, cœur de PARTAGES.

### Piste C (optionnelle) : structuration générative
| Jeu | Contenu | Tâche |
|---|---|---|
| **QUAERO** (EMEA, MEDLINE) | Textes médicaux français annotés | Extraction d'entités vers JSON (GFDL 1.3) |
| **E3C** (couche française) | Cas cliniques annotés | Entités cliniques (CC BY-NC, usage non commercial) |

Ici la distillation devient « par séquence » : le professeur génère le JSON, l'élève apprend à le reproduire.
Piste lancée seulement si A et B sont closes.

### Données « bruitées » pour S2 (l'équivalent du jeu « ut »)
- étiquettes produites en zéro-shot par le professeur sur des textes médicaux français non annotés (cas cliniques E3C, résumés) ;
- étiquettes de tâches voisines (MorFITT pour pré-chauffer DiaMED).
Leur bruit est **mesuré** sur un échantillon relu, pas supposé.

---

## 2. Modèles compatibles RTX 5090 (32 Go VRAM, ~96 Go RAM)

Principe : **professeur en QLoRA 4 bits, élève en LoRA**, tous ouverts et exécutables hors ligne.
Les choix définitifs sont figés en phase 0, après un banc de mémoire réel.

| Rôle | Candidats | Raison | Budget VRAM estimé (à mesurer) |
|---|---|---|---|
| Professeur 1 | **Qwen 3.6 27B** (déjà utilisé dans Multi-Agent-Lab) | Bon niveau multilingue, déjà en local | QLoRA 4 bits, 1 024 tokens, gradient checkpointing : ~22 à 28 Go |
| Professeur 2 | **Mistral Small 3.2 24B** (déjà utilisé, Apache 2.0) | Famille française, second avis pour S4 | ~20 à 26 Go |
| Élève | un 7-9B : Qwen 2.5 7B, BioMistral 7B (spécialisé médical), Gemma 2 9B (celui de la solution gagnante) | Taille déployable sur un GPU hospitalier | LoRA bf16 ~24 à 30 Go, sinon QLoRA |
| Élève léger | un modèle de 1 à 4B | Mesurer jusqu'où la distillation descend | < 16 Go |
| **Référence classique** | **DrBERT / CamemBERT-bio** (encodeurs français médicaux) | Ce qu'un CHU utilise déjà : le LLM doit le battre, sinon on le dit | < 8 Go |

Écart assumé avec la solution gagnante : professeurs de 24-27B au lieu de 70-72B (8 × A100 chez l'auteur).
La question de recherche devient : **la distillation garde-t-elle son intérêt quand le professeur n'est que 3 fois plus gros que l'élève ?**
Option si la réponse l'exige : louer quelques heures de GPU pour un professeur 70B, en dernier recours et chiffré d'avance.

Points techniques à valider en phase 0 sur Blackwell (sm_120) : PyTorch avec CUDA 12.8+, bitsandbytes,
FlashAttention, outil GPTQ (GPTQModel ou llm-compressor).

---

## 3. Protocole d'évaluation (le livrable que le CHU demande explicitement)

L'offre parle de « protocoles d'évaluation de la performance des modèles » et de « capitalisation des méthodes ».
Le protocole est donc **écrit et figé avant toute mesure comparative**, dans l'esprit de Multi-Agent-Lab.

- **Découpage** : test scellé tiré une fois (graine fixée, empreinte SHA-256 du fichier), jamais vu pendant le réglage ;
  validation croisée en 5 plis sur le reste, **stratifiée par classe**.
- **Métriques** : macro-F1 (classes rares du CIM-10), log loss (métrique de LMSYS), calibration (ECE), Spearman pour CLISTER.
- **Incertitude** : intervalles de confiance par bootstrap sur le test ; comparaisons **appariées** entre variantes.
- **Coûts mesurés à chaque fois** : VRAM de pointe, durée d'entraînement, latence et débit d'inférence, taille du modèle.
- **Ablation, stratégie par stratégie** : chaque S1 à S7 est ajoutée seule à la référence et son gain est mesuré.
  Une stratégie sans gain significatif est publiée comme telle.
- **Analyse d'erreurs** : matrice de confusion par chapitre CIM-10, relecture d'un échantillon d'erreurs.
- **Hygiène** : aucune fuite entre plis (les probabilités du professeur sont strictement hors pli) ; recherche de
  quasi-doublons entre entraînement et test.

---

## 4. Phases et portes de validation

Chaque phase se ferme sur une **preuve** (fichier de résultats, test, mesure), pas sur une impression.

| Phase | Contenu | Porte de sortie |
|---|---|---|
| **P0. Socle** | Environnement Blackwell, téléchargement et licences des jeux, banc VRAM des modèles candidats, protocole écrit et figé | Chaque modèle candidat entraîne 10 pas sans erreur de mémoire ; protocole daté et figé ; licences consignées |
| **P1. Références** | DrBERT / CamemBERT-bio affinés ; LLM élève en zéro-shot et en LoRA simple (S1) | Tableau de référence sur DiaMED, MorFITT, CLISTER avec intervalles de confiance |
| **P2. Professeurs** | S2 puis S3 : post-pretrain bruité, professeurs en 5 plis, probabilités hors pli | Probabilités sauvegardées pour 100 % du jeu d'entraînement ; score hors pli de chaque professeur |
| **P3. Distillation** | S4 : élève avec CE + KL, un puis deux professeurs ; balayage du taux d'apprentissage (1e-5 à 5e-5) et de la température | Gain (ou absence de gain) de la distillation mesuré contre P1, apparié |
| **P4. Compression** | S5 moyenne des LoRA des plis, S6 GPTQ 8 bits (et 4 bits pour comparer), S7 TTA | Perte de qualité due à la quantification mesurée ; latence et VRAM en inférence |
| **P5. Industrialisation** | Service FastAPI d'inférence, indexation des textes et des prédictions dans ElasticSearch (cité par l'offre), CI GitLab, carte de modèle, règles de maintenance (dérive, seuils de réentraînement) | Service qui tourne hors ligne, tests verts, carte de modèle publiée |
| **P6. Piste C (option)** | Structuration générative (QUAERO / E3C vers JSON), distillation par séquence | F1 par entité contre la référence encodeur |

---

## 5. Arborescence prévue

```
LLM_finetuning/
├── PLAN_PROJET.md          ← ce document
├── PROTOCOLE.md            ← figé en P0, jamais modifié après (versions datées sinon)
├── configs/                ← un YAML par expérience (modèle, LoRA, lr, graine, pli)
├── data/                   ← hors Git ; scripts de téléchargement et empreintes seulement
├── src/
│   ├── data/               ← chargement, nettoyage, découpage, détection de doublons
│   ├── train/              ← S1 classification LoRA, S2 post-pretrain, S4 distillation (CE + KL)
│   ├── merge/              ← S5 moyenne des LoRA et des têtes
│   ├── quantize/           ← S6 GPTQ
│   ├── infer/              ← S7 TTA, inférence par lots
│   └── eval/               ← métriques, bootstrap, comparaisons appariées, rapports
├── service/                ← FastAPI + indexation ElasticSearch (P5)
├── results/                ← un JSON par run, jamais écrasé
├── tests/                  ← pytest : fuite entre plis, déterminisme, formats
└── RESULTATS.md            ← chiffres réels uniquement, résultats négatifs compris
```

---

## 6. Ce que le projet permettra de dire en entretien au CHUGA

Seulement une fois mesuré :
- « J'ai affiné des LLM de 7 à 27 milliards de paramètres en local, en LoRA et QLoRA, sur des cas cliniques français. »
- « J'ai reproduit la stratégie gagnante d'une compétition Kaggle LLM (distillation, fusion de LoRA, GPTQ) et mesuré
  ce que chaque brique apporte vraiment, y compris celles qui n'apportent rien. »
- « Mon LLM distillé fait [X] de macro-F1 contre [Y] pour DrBERT, pour [Z] ms par compte rendu sur un seul GPU. »
- « J'ai écrit le protocole d'évaluation avant de mesurer : c'est ce que vous demandez pour PARTAGES. »

Les crochets restent vides tant que les résultats n'existent pas.

---

## 7. Décisions à prendre par Cyril avant P0

1. **Emplacement** : le dossier est créé dans `Projet Assistante IA/` ; le déplacer vers `D:\Projets persos\` avec les autres projets ?
2. **Dépôt** : GitLab (cité par l'offre) en privé dès le début, miroir GitHub plus tard ?
3. **Périmètre** : pistes A + B seulement (recommandé, environ 2 à 3 semaines selon le temps GPU), ou A + B + C ?
4. **Calendrier** : date limite de candidature au CHUGA, pour savoir quelle phase doit être close avant l'envoi
   (P1 + P3 suffisent pour répondre « oui, et voici les chiffres »).
5. **Location GPU** pour un professeur 70B : exclue, ou acceptée sous plafond de dépense ?

## Sources
- Solution 1re LMSYS : kaggle.com/competitions/lmsys-chatbot-arena/writeups/blackpearl-no-leak-1st-place-solution-distill-is-a
  (lue le 01/10/2026, réponses de l'auteur en commentaires : perte KL, cosinus avec 100 pas d'échauffement, 8 × A100, moyenne des têtes)
- Code d'entraînement de l'auteur : github.com/shyoulala/LMSYS_BlackPearl
- DrBenchmark : drbenchmark.univ-avignon.fr, arxiv.org/abs/2402.13432
- Offre CHUGA : texte collé par Cyril dans une autre session, résumé transmis le 01/10/2026 (aucun fichier sur disque)
