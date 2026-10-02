# LLM_finetuning : distiller des LLM sur des comptes rendus médicaux français, en 100 % local

Plan v2, 01/10/2026. Statut : **à valider avant toute ligne de code.**
V2 : la recette LMSYS devient un point de départ ; ajout d'un état de l'art complet (section 2 bis) et d'un programme en vagues.

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

**La méthode de départ (pas la seule).** La solution 1re de la compétition Kaggle *LMSYS Chatbot Arena Human Preference
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

## 2 bis. État de l'art : tout ce qui peut améliorer la qualité (brainstorm, octobre 2026)

La solution LMSYS 2024 n'est qu'un point de départ. Ce catalogue rassemble les leviers connus à ce jour,
regroupés par famille. Pour chacun : ce que c'est, pourquoi il compte pour des comptes rendus hospitaliers,
et sa faisabilité sur une RTX 5090.

Légende faisabilité : **F** faisable tel quel · **C** faisable sous contrainte (taille de modèle, durée) · **H** hors budget local.
Légende priorité : **P1** testé à coup sûr · **P2** testé si P1 laisse de la marge · **P3** veille, mentionné seulement.

### Deux leçons à garder en tête avant d'empiler les techniques
- **Le taux d'apprentissage d'abord.** Une étude de 2026 (« Learning Rate Matters: Vanilla LoRA May Suffice »)
  montre qu'une bonne part des gains attribués aux variantes de LoRA disparaît quand on règle correctement
  le taux d'apprentissage de la référence. Toute variante sera donc comparée à une LoRA **déjà réglée**,
  jamais à une LoRA par défaut. L'auteur de LMSYS dit la même chose : 1e-5 contre 5e-5 = 0,01 point.
- **Le successeur de LMSYS a déjà amélioré la recette.** La 1re place du WSDM Cup 2025 (Multilingual Chatbot Arena,
  même format) a ajouté trois choses à la distillation : **5 professeurs** au lieu de 2, la **relecture manuelle des
  exemples où les professeurs contredisent l'étiquette humaine** (correction du bruit d'annotation), et des **données
  synthétiques**. Elle entraînait aussi les deux ordres d'une paire dans le même pas de gradient, et tronquait par le milieu.

### L1. Données (souvent le levier le plus rentable)
| Technique | Pourquoi ici | Faisab. | Prio. |
|---|---|---|---|
| Pré-entraînement continu sur corpus médical français (DAPT, ex. corpus NACHOS de DrBERT si accessible) | Le vocabulaire des comptes rendus est loin du web généraliste | C (petit élève, quelques centaines de millions de tokens) | P2 |
| Données synthétiques générées par le professeur (cas cliniques fictifs par classe rare) | DiaMED n'a que 739 cas et des chapitres CIM-10 très rares | F | P1 |
| Correction du bruit d'étiquettes : désaccords professeurs / étiquette relus (WSDM 2025), apprentissage « confiant » (cleanlab) | Les annotations médicales sont imparfaites ; c'est aussi la « mise en qualité » demandée par l'offre | F | P1 |
| Pseudo-étiquetage itératif (« noisy student ») sur textes non annotés | Exploiter le texte médical sans étiquette, comme le jeu « ut » de LMSYS | F | P2 |
| Déduplication et détection de quasi-doublons entre plis | Éviter des scores gonflés | F | P1 (hygiène) |

### L2. Adaptation des paramètres
| Technique | Pourquoi ici | Faisab. | Prio. |
|---|---|---|---|
| LoRA réglée (rang, alpha, lr, couches ciblées), **référence obligatoire** | Voir leçon 1 | F | P1 |
| rsLoRA (mise à l'échelle stable du rang) | Permet des rangs élevés sans réglage fin du lr | F | P1 (1 drapeau) |
| DoRA (magnitude + direction) | Réduit l'écart avec le fine-tuning complet, +5 à 10 % de VRAM | F | P1 |
| PiSSA (initialisation par valeurs singulières principales) ; LoftQ pour QLoRA | Convergence plus rapide ; LoftQ réduit l'erreur de quantification des professeurs | F | P2 |
| LoRA+ (lr différent pour A et B) | Gain de vitesse annoncé, une ligne de configuration | F | P2 |
| Fine-tuning complet d'un petit élève (≤ 3B, AdamW 8 bits) | Mesurer ce que LoRA laisse sur la table | C | P2 |
| GaLore, sélection de couches (Spectrum) | Fine-tuning quasi complet à mémoire réduite | C | P3 |

### L3. Comment faire classer un LLM
| Technique | Pourquoi ici | Faisab. | Prio. |
|---|---|---|---|
| Tête de classification sur le dernier token (méthode LMSYS) | Référence de la compétition | F | P1 |
| « Verbaliseur » : probabilités des tokens d'étiquette générés (« Chapitre IX ») | Exploite le savoir du modèle sur le nom des classes, utile quand il y a peu d'exemples | F | P1 |
| Attention bidirectionnelle (type LLM2Vec) + mise en commun des représentations | Les décodeurs ne voient pas la suite du texte ; les comptes rendus se lisent en entier | C | P2 |
| Troncature par le milieu (WSDM) ou tête + fin ; découpage en morceaux puis agrégation | Les comptes rendus dépassent souvent 1 024 tokens | F | P1 |
| Pour CLISTER : les deux ordres de la paire dans le même pas (WSDM), prédiction symétrisée | La similarité est symétrique, le modèle doit l'être aussi | F | P1 |

### L4. Pertes et déséquilibre des classes
| Technique | Faisab. | Prio. |
|---|---|---|
| KL directe, KL inverse, KL « asymétrique » (DistiLLM) ; température du professeur | F | P1 |
| Pondération des classes, perte focale, lissage des étiquettes | F | P1 |
| Pondération des professeurs selon leur score hors pli | F | P2 |

### L5. Distillation avancée
| Technique | Pourquoi ici | Faisab. | Prio. |
|---|---|---|---|
| Distillation des **justifications** (« Distilling step-by-step ») : le professeur explique son classement, l'élève apprend étiquette + explication | Gains forts quand les données sont rares ; l'explication est un atout pour un clinicien | F | P1 |
| Distillation « sur politique » (GKD, MiniLLM) : l'élève génère, le professeur corrige ses propres sorties | État de l'art 2025-2026 pour les tâches génératives | C | P2 (piste C) |
| Distillation par séquence (le professeur produit le JSON complet) | Base de la structuration générative | F | P1 (piste C) |

### L6. Post-entraînement génératif (piste C, structuration)
| Technique | Pourquoi ici | Faisab. | Prio. |
|---|---|---|---|
| SFT puis préférences (DPO, ORPO, SimPO, KTO) | Aligner le format et la prudence des sorties | F | P2 |
| **GRPO avec récompense vérifiable** (RLVR) : récompense = F1 des entités extraites + validité du JSON | Méthode dominante en 2025-2026 ; la structuration a une vérité terrain, donc une récompense calculable sans juge | C (élève ≤ 8B, LoRA) | P1 si piste C |
| Décodage contraint par schéma JSON (xgrammar, outlines) | Zéro sortie mal formée, exigence d'un système hospitalier | F | P1 si piste C |

### L7. Fusion de modèles et ensembles
| Technique | Faisab. | Prio. |
|---|---|---|
| Moyenne des LoRA des plis (LMSYS), comparée à l'ensemble des 5 plis | F | P1 |
| TIES, DARE, SLERP, « model soups » ; WiSE-FT (interpolation avec le modèle de base pour la robustesse) | F | P2 |

### L8. Calcul au moment de l'inférence
| Technique | Pourquoi ici | Faisab. | Prio. |
|---|---|---|---|
| TTA (LMSYS) : variantes de troncature, ordres de paire | Robustesse à budget connu | F | P1 |
| Auto-cohérence (plusieurs raisonnements, vote) | Souvent utile en génération ; à mesurer en classification où le raisonnement peut nuire | F | P2 |
| Modèles de raisonnement comme professeurs (traces longues) | Peut améliorer les étiquettes souples sur les cas ambigus | C | P2 |

### L9. Compression et service (contrainte hospitalière)
| Technique | Pourquoi ici | Faisab. | Prio. |
|---|---|---|---|
| GPTQ 8 et 4 bits (LMSYS), AWQ | Référence | F | P1 |
| **FP8 et NVFP4 natifs de Blackwell** (la 5090 les accélère en matériel) | Format d'avenir des serveurs d'inférence ; peu de retours publics sur des tâches médicales françaises | C (support logiciel à valider) | P2 |
| Entraînement conscient de la quantification (QAT) | Limiter la perte au passage en 4 bits | C | P3 |
| Service vLLM ou SGLang, décodage spéculatif | Débit réel d'un service hospitalier | F | P2 (P5) |

### L10. Calibration et abstention (sûreté clinique)
| Technique | Pourquoi ici | Faisab. | Prio. |
|---|---|---|---|
| Mise à l'échelle par température, mesure de l'ECE | Une probabilité doit vouloir dire quelque chose pour un codeur ou un clinicien | F | P1 |
| **Prédiction conforme** : le modèle renvoie un ensemble de classes garanti à 90 % ou s'abstient et passe la main à l'humain | Le bon usage hospitalier : automatiser les cas sûrs, router les autres. Garantie statistique, simple à mettre en œuvre | F | P1 |

### L11. Références à battre (sinon on le dit)
| Modèle | Pourquoi |
|---|---|
| DrBERT, CamemBERT-bio | Encodeurs médicaux français : sur peu de données, ils battent souvent les LLM |
| Encodeurs de type ModernBERT français médicaux (ex. doctomodernbert-fr de Doctolib) | Génération d'encodeurs plus récente, contexte long |
| LLM professeur en zéro-shot et en few-shot | Ce que donne « juste un prompt », sans entraînement |

### L12. Évaluation par LLM-juge (pour la génération, cœur de PARTAGES)
Un travail de 2026 (« Who Judges the Judge? ») évalue précisément les LLM-juges sur des questions médicales françaises ouvertes.
Si la piste C produit du texte libre, le juge sera lui-même validé contre un petit jeu annoté à la main, avec
juge distinct du générateur et stabilité mesurée (méthode déjà employée dans Aegis-RCA).

### Comment éviter l'explosion combinatoire
Plus de 40 leviers, chacun avec ses réglages : tout croiser est impossible sur un seul GPU. Règles :
1. **Vagues successives, gloutonnes** : chaque vague part de la meilleure configuration de la précédente.
2. **Budget GPU fixé par vague** avant de commencer, consigné dans le protocole.
3. **Décisions sur les jeux qui ont la puissance statistique** : DiaMED (≈ 150 cas de test) donne des intervalles
   de confiance larges ; les comparaisons fines se font sur MorFITT et CLISTER, ou en validation croisée répétée.
4. Un levier qui ne bat pas la référence réglée est **publié comme résultat négatif** et sort du programme.

### Programme proposé
| Vague | Leviers | Objectif |
|---|---|---|
| V0 | L11 références, LoRA réglée (L2), tête vs verbaliseur (L3) | Savoir où l'on part |
| V1 | Recette LMSYS complète (S1 à S7) | Reproduire fidèlement |
| V2 | Recette WSDM 2025 : plus de professeurs, correction des étiquettes, synthétiques (L1) | Mesurer l'amélioration publiée depuis |
| V3 | DoRA / rsLoRA / PiSSA (L2), KL et pertes (L4), distillation des justifications (L5) | Gains d'entraînement récents |
| V4 | Fusion (L7), FP8 / NVFP4 contre GPTQ (L9), calibration et prédiction conforme (L10) | Déployable et sûr |
| V5 (option) | Piste C : SFT, GRPO à récompense vérifiable, décodage contraint (L6) | Structuration générative |

---

## 3. Protocole d'évaluation (le livrable que le CHU demande explicitement)

L'offre parle de « protocoles d'évaluation de la performance des modèles » et de « capitalisation des méthodes ».
Le protocole est donc **écrit et figé avant toute mesure comparative**, dans l'esprit de Multi-Agent-Lab.

- **Découpage** : test scellé tiré une fois (graine fixée, empreinte SHA-256 du fichier), jamais vu pendant le réglage ;
  validation croisée en 5 plis sur le reste, **stratifiée par classe**.
- **Métriques** : macro-F1 (classes rares du CIM-10), log loss (métrique de LMSYS), calibration (ECE), Spearman pour CLISTER.
- **Incertitude** : intervalles de confiance par bootstrap sur le test ; comparaisons **appariées** entre variantes.
- **Coûts mesurés à chaque fois** : VRAM de pointe, durée d'entraînement, latence et débit d'inférence, taille du modèle.
- **Ablation, levier par levier** : chaque stratégie (S1 à S7, puis les leviers L1 à L12 retenus) est ajoutée seule à la meilleure configuration du moment et son gain est mesuré.
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
| **P1. Références (vague V0)** | DrBERT / CamemBERT-bio / encodeur ModernBERT médical français affinés ; LLM en zéro-shot et few-shot ; LoRA réglée, tête contre verbaliseur | Tableau de référence sur DiaMED, MorFITT, CLISTER avec intervalles de confiance |
| **P2. Professeurs (V1, V2)** | S2 puis S3 : post-pretrain bruité, professeurs en 5 plis, probabilités hors pli ; puis recette WSDM : professeurs supplémentaires, correction des étiquettes contestées, données synthétiques | Probabilités sauvegardées pour 100 % du jeu d'entraînement ; score hors pli de chaque professeur |
| **P3. Distillation (V1, V3)** | S4 : élève avec CE + KL, un puis plusieurs professeurs ; balayage lr et température ; puis variantes de KL, DoRA / rsLoRA / PiSSA, distillation des justifications | Gain (ou absence de gain) de la distillation mesuré contre P1, apparié |
| **P4. Compression et sûreté (V4)** | S5 moyenne des LoRA et fusions TIES / DARE / WiSE-FT ; S6 GPTQ contre FP8 / NVFP4 Blackwell ; S7 TTA ; calibration et prédiction conforme avec abstention | Perte de qualité due à la quantification mesurée ; latence et VRAM en inférence |
| **P5. Industrialisation** | Service FastAPI d'inférence, indexation des textes et des prédictions dans ElasticSearch (cité par l'offre), CI GitLab, carte de modèle, règles de maintenance (dérive, seuils de réentraînement) | Service qui tourne hors ligne, tests verts, carte de modèle publiée |
| **P6. Piste C (V5, option)** | Structuration générative (QUAERO / E3C vers JSON) : distillation par séquence, SFT, GRPO à récompense vérifiable, décodage contraint, juge validé | F1 par entité contre la référence encodeur |

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
- « J'ai reproduit les recettes gagnantes de deux compétitions Kaggle LLM (LMSYS 2024, WSDM 2025), puis testé les techniques
  plus récentes (DoRA, distillation des justifications, GRPO, FP8, prédiction conforme), en mesurant ce que chaque brique
  apporte vraiment, y compris celles qui n'apportent rien. »
- « Mon LLM distillé fait [X] de macro-F1 contre [Y] pour DrBERT, pour [Z] ms par compte rendu sur un seul GPU. »
- « J'ai écrit le protocole d'évaluation avant de mesurer : c'est ce que vous demandez pour PARTAGES. »

Les crochets restent vides tant que les résultats n'existent pas.

---

## 7. Décisions à prendre par Cyril avant P0

1. **Emplacement** : le dossier est créé dans `Projet Assistante IA/` ; le déplacer vers `D:\Projets persos\` avec les autres projets ?
2. **Dépôt** : GitLab (cité par l'offre) en privé dès le début, miroir GitHub plus tard ?
3. **Périmètre** : vagues V0 à V4 sur les pistes A + B (recommandé ; durée à chiffrer après le banc de P0), ou jusqu'à V5 (piste C) ?
   Ordre de grandeur indicatif, à confirmer : V0 + V1 en 2 à 3 semaines, le programme complet en plusieurs mois de temps GPU.
4. **Calendrier** : date limite de candidature au CHUGA, pour savoir quelle phase doit être close avant l'envoi
   (P1 + P3 suffisent pour répondre « oui, et voici les chiffres »).
5. **Location GPU** pour un professeur 70B : exclue, ou acceptée sous plafond de dépense ?

## Sources
- 1re place WSDM Cup 2025 Multilingual Chatbot Arena (whitefebruary) : kaggle.com/competitions/wsdm-cup-multilingual-chatbot-arena/writeups/whitefebruary-1st-place-solution
- « Learning Rate Matters: Vanilla LoRA May Suffice for LLM Fine-tuning », arxiv.org/abs/2602.04998
- PiSSA, arxiv.org/abs/2404.02948 ; comparatif DoRA / GaLore / PiSSA / VeRA (Spheron, 2026)
- Survol de la distillation sur politique, arxiv.org/abs/2604.00626
- « Who Judges the Judge? Evaluating LLM-as-a-Judge for French Medical open-ended QA », arxiv.org/abs/2603.04033
- « Structuration automatique de la posologie en français : quel rôle pour les LLM ? », TALN 2025 (le fine-tuning seul égale les systèmes de référence)
- doctomodernbert-fr-base (Doctolib), huggingface.co/doctolib-lab/doctomodernbert-fr-base
- Solution 1re LMSYS : kaggle.com/competitions/lmsys-chatbot-arena/writeups/blackpearl-no-leak-1st-place-solution-distill-is-a
  (lue le 01/10/2026, réponses de l'auteur en commentaires : perte KL, cosinus avec 100 pas d'échauffement, 8 × A100, moyenne des têtes)
- Code d'entraînement de l'auteur : github.com/shyoulala/LMSYS_BlackPearl
- DrBenchmark : drbenchmark.univ-avignon.fr, arxiv.org/abs/2402.13432
- Offre CHUGA : texte collé par Cyril dans une autre session, résumé transmis le 01/10/2026 (aucun fichier sur disque)
