# Boîte à outils : outils, dépôts et papiers retenus (veille du 01/10/2026)

Compagnon de `PLAN_PROJET_V6.md`. Chaque ligne dit **ce qui a été réellement vérifié** et ce qui reste à confirmer.

**Légende du statut**
- ✅ lu le 01/10/2026 (page, README, documentation ou résumé de la source)
- 🔎 repéré par recherche (résultat de moteur, pas la source elle-même), à confirmer en P0
- ◻ référence classique connue, **non relue ce jour** : à lire et à confirmer à l'ingestion dans le wiki

**Règle de licence** : un dépôt sans licence (tous droits réservés) se lit et se réimplémente, il ne se copie pas. Toute dépendance reçoit un audit de licence en P0 (micro-tâche P0-12).

---

## 1. Données et corpus

| Ressource | Rôle dans le projet | Licence / conditions | Statut | Remarque |
|---|---|---|---|---|
| **PARHAF** (HealthDataHub/PARHAF sur Hugging Face) | Jeu principal : comptes rendus cliniques français fictifs, rédigés par des internes | CC BY 4.0 et Etalab 2.0 ; usages interdits : décision clinique, validation clinique, généralisation au réel, déploiement | ✅ | 4 254 patients et environ 6 185 à 6 190 documents publiés, 755 patients et 1 209 documents sous embargo (test), 7 types de documents, parquet de 34 Mo ; 18 ou 20 spécialités selon la source, à compter |
| PARHAF annotés (conclusion, pseudo, biomarqueurs, infectiologie, réponse au traitement) | Sous-ensembles annotés par cas d'usage de PARTAGES | CC BY 4.0 et Etalab 2.0 | ✅ | Conclusion : 7 554 lignes (3 664 train, 108 dev), spans avec offsets |
| PARCOMED | Pré-entraînement continu léger, textes non étiquetés | CC BY 4.0 et Etalab 2.0 (version commerciale) ; variante « research only » en CC BY-NC | ✅ | 1,8 M de lignes, 2,93 Go, 16 sources, 71,8 % de textes scientifiques |
| MorFITT | Tâche multi-étiquettes (12 spécialités), tâche voisine de pré-entraînement | CC BY-SA 4.0 | ✅ (recherche DrBenchmark) | 3 624 résumés PMC |
| CLISTER | Tâche sur paires (similarité de cas cliniques) | à lire à la source | 🔎 | Type `pair_ordinal` |
| DiaMED | Option : 739 cas cliniques, trop petit pour décider | CC BY-SA 4.0 | ✅ (recherche DrBenchmark) | Garde de repli |
| DrBenchmark | Banc de 20 tâches biomédicales françaises, référence pour encodeurs | licences par jeu (certains sous accord d'usage) | ✅ | github.com/DrBenchmark/DrBenchmark |
| Nomenclature CIM-10 (ATIH / OMS) | Noms en clair et définitions des classes | à lire : conditions de réutilisation | 🔎 | Les noms officiels alimentent le contrat de cible |
| CodaBench | Évaluation du test embargoé de PARHAF | n.a. | 🔎 | Calendrier d'ouverture non précisé dans les sources lues |

## 2. Modèles

| Modèle | Rôle | Licence | Statut | Remarque |
|---|---|---|---|---|
| Qwen3.8-27B | Professeur | Apache 2.0 | ✅ (plusieurs sources) | Dense, multimodal, 262 k de contexte, publié le 14/08/2026. Carte officielle lue le 01/10 : `AutoModelForMultimodalLM`, aucune mention de classification (P0-06 bloquant) |
| Qwen3.5 (4B, 9B, 27B denses) | Élèves et professeur | Apache 2.0 | ✅ (un article) | Les variantes MoE (35B-A3B...) ne servent pas |
| Gemma 4 (E4B, 31B dense ; 26B MoE écarté) | Élève et professeur | Apache 2.0 | ✅ (un article) | Gemma 4 31B dense environ 20 à 24 Go en 4 bits d'après l'article. Carte officielle lue le 01/10 : `AutoModelForMultimodalLM`, Apache 2.0, aucun gating vu, aucune mention de classification |
| MedGemma 1.5 (4B ; 27B) | Candidat médical | termes Health AI Developer Foundations | 🔎 | Modèle à accès conditionné : Cyril accepte lui-même les conditions |
| Mistral Small 3.2 24B | Professeur déjà local (Multi-Agent-Lab) | Apache 2.0 | 🔎 | À reconfirmer |
| BioMistral 7B | Candidat médical plus ancien | à lire | 🔎 | Pré-entraîné sur PubMed Central |
| DrBERT, CamemBERT-bio, doctomodernbert-fr (Doctolib) | Références encodeurs à battre | à lire | 🔎 | Voir arXiv 2402.16689 pour les documents longs |
| TF-IDF + régression logistique | **Référence non neuronale** | n.a. | ◻ | Souvent très forte sur du texte clinique : si le LLM ne la bat pas, on le dit |

Règle de criblage : modèles **denses** uniquement ; au moins un généraliste par taille testée ; aucune hypothèse « le médical gagne » (arXiv 2411.08870).

## 3. Entraînement et distillation

| Outil / dépôt | Rôle | Licence | Statut | Risque ou limite |
|---|---|---|---|---|
| huggingface/trl (v1.14.1 en docs) | `SFTTrainer`, `DistillationTrainer` (JSD généralisée, vLLM colocate ou serveur), `GKDTrainer` en transition, `use_liger_kernel`, suivi Trackio | à confirmer (P0-12) | ✅ docs | `DistillationTrainer` : vocabulaire commun obligatoire, causal LM seulement |
| huggingface/peft | LoRA, QLoRA, DoRA, rsLoRA, PiSSA, LoftQ, LoRA+, `modules_to_save` pour la tête | à confirmer | ✅ docs | DoRA incompatible avec `all-linear` en quantifié |
| transformers v5 (docs v5.17) | Modèles `*ForSequenceClassification`, Trainer | à confirmer | ✅ docs | Support de classification à vérifier par modèle (P0-06) |
| bitsandbytes | QLoRA 4 bits, INT8 | à confirmer | 🔎 | Roues CUDA 12.8 signalées pour Blackwell |
| unslothai/unsloth | **Accélérateur optionnel** | à confirmer | ✅ docs | Blackwell supporté (triton 3.3.1 ou plus) ; la référence reste la pile Hugging Face, Unsloth sert seulement après test d'équivalence de la perte |
| Liger-Kernel | Noyaux fusionnés | à confirmer | 🔎 | Nightly cible SM90 et SM100/110 : consumer SM120 non garanti, à tester |
| PyTorch (builds cu128 ou cu130) | Base | BSD | 🔎 | Un guide communautaire rapporte torch 2.10 et 2.11 en cu130 fonctionnels sur 5090 : à vérifier en P0-04 |
| FlashAttention 2 / SDPA | Attention | BSD | 🔎 | FA2 OK sur SM120 à débit réduit ; FA4 non (SM100 seulement) |
| Optuna | Balayages de taux, rang, alpha | MIT | ◻ | Déjà maîtrisé par Cyril (Kaggle) |
| Hydra + Pydantic v2 | Composition de configurations et validation du contrat de tâche | MIT / MIT | ◻ | Décision à passer par `doubt-driven-development` en P0 |
| DVC | Versionnement des données et artefacts (déjà utilisé dans NeuroSig) | Apache 2.0 | ◻ | Remote local ; remplace les seules empreintes si le volume l'exige |
| uv | Environnements verrouillés | MIT / Apache 2.0 | ◻ | Le hook du wiki l'utilise déjà |
| Trackio (gradio-app/trackio) | Suivi local (SQLite), API compatible W&B, intégré à TRL | à confirmer | ✅ | Le **registre immuable** reste la source de vérité ; Trackio sert aux courbes |
| jongwooko/distillm-2 | Lecture du code DistiLLM-2 (ICML 2025) | à confirmer | ✅ existence | Pour la piste générative |
| shyoulala/LMSYS_BlackPearl | Lecture de la recette 1re place LMSYS | **aucune licence**, 2 commits | ✅ | **Lecture seule, réimplémentation obligatoire** ; PyTorch 2.3.1, perte `(CE + 2 pertes de gradient + 2 pertes cosinus)/5` |
| Lizhecheng02/Kaggle-Multilingual_Chatbot_Arena | Lecture de recettes WSDM 2025 | à confirmer | 🔎 | Idem |

## 4. Qualité des étiquettes, incertitude, évaluation

| Outil / dépôt | Rôle | Licence | Statut | Remarque |
|---|---|---|---|---|
| cleanlab | Détection d'erreurs d'étiquettes (confident learning) sur probabilités hors pli | Apache-2.0 (corrigé le 01/10/2026, voir docs/LICENCES.md) | ✅ (recherche) | Nos plis produisent déjà les probabilités hors pli nécessaires |
| scikit-learn-contrib/MAPIE (v1) | Prédiction conforme : LAC, APS, RAPS, top-k, multi-étiquettes, risk control, tests d'échangeabilité | BSD-3 | ✅ | Bibliothèque principale |
| TorchCP | Seconde bibliothèque conforme (JMLR 2025, 16 k lignes, tests à 100 %) | **LGPL-3.0** | ✅ (recherche) | Usage en vérification croisée ; attention à la licence si on redistribue |
| Implémentation maison de la conformité fractionnée (~30 lignes, testée) | Troisième mesure indépendante | n.a. | n.a. | Les trois doivent s'accorder à l'incertitude près |
| SciPy `stats.bootstrap`, statsmodels (McNemar) | Intervalles et tests appariés | BSD | ◻ | Voir `paired-comparison` |
| torchmetrics (ECE) et mise à l'échelle par température maison | Calibration | Apache 2.0 / n.a. | ◻ | |
| lm-evaluation-harness | Option : contrôle que le fine-tuning n'efface pas les capacités générales | MIT | ◻ | Seulement si on affine un modèle générique pour la piste générative |

## 5. Compression et service

| Outil / dépôt | Rôle | Licence | Statut | Remarque |
|---|---|---|---|---|
| vllm-project/llm-compressor | FP8, W8A8, NVFP4, MXFP4, GPTQ, AWQ, AutoRound ; format compressed-tensors | à confirmer | ✅ | Outil principal de quantification |
| ModelCloud/GPTQModel | GPTQ, AWQ, FP8, EXL3... | à confirmer | ✅ | Comparaison à llm-compressor |
| vLLM | Service et génération (pooling pour classification à vérifier) | Apache 2.0 | 🔎 | Noyaux SM120 depuis la 0.13 ; lacunes NVFP4 MoE (issue #31085) ; classification par `*ForSequenceClassification` à valider (P0-09) |
| Transformers + FastAPI | Service de repli si vLLM ne gère pas la classification | Apache 2.0 / MIT | ◻ | Version de référence du service dans tous les cas |
| xgrammar, llguidance, outlines | Décodage contraint (piste générative) | à confirmer | 🔎 | XGrammar et llguidance nettement plus rapides qu'Outlines en compilation et par token (comparatifs lus en recherche) |
| elasticsearch (client Python) | Indexation des textes et prédictions (cité par l'offre) | Apache 2.0 | ◻ | Conteneur local pour les tests |
| **aphp/edsnlp** (v0.23.0, BSD-3) | Cadre NLP de l'AP-HP pour le français clinique : règles, NER entraînable, composants LLM, Spark, Parquet | BSD-3-Clause | ✅ | Sert de base règles (négation, hypothèse), de **preuve d'interopérabilité** (notre classifieur exposé comme composant) et de passerelle vers l'écosystème PARTAGES |
| distilabel (Argilla) | Option : génération de données synthétiques | Apache 2.0 | ◻ | Seulement si la génération maison devient lourde |

---

## 6. Papiers (ordre de lecture à l'ingestion dans le wiki)

### Lot A : à ingérer en P0 (le socle)
| # | Papier | Apport | Utilisé en | Statut |
|---|---|---|---|---|
| A1 | 1re place LMSYS (sayoulala, août 2024) | Recette : distillation, fusion de LoRA, GPTQ, TTA | P2, P3, P4 | ✅ |
| A2 | 5e place LMSYS (Team Danube, août 2024) | Pré-entraînement sur tâche voisine, tête jetée, INT8 plus rapide que GPTQ | P1, P3, P4 | ✅ |
| A3 | 1re place WSDM Cup 2025 (whitefebruary) | 5 professeurs, relecture des désaccords, synthétique, ordres inversés | P2, P3 | ✅ (résumé) |
| A4 | arXiv 2603.20494 : PARHAF | Corpus principal, restrictions, test embargoé | P0, tout | ✅ |
| A5 | arXiv 2602.04998 : « Learning Rate Matters » | Régler la référence d'abord | P1, P3 | ✅ |
| A6 | arXiv 2512.12677 : affiner des LLM causaux pour la classification | Tête contre invite | P1 | ✅ |
| A7 | arXiv 2411.08870 : impact limité de l'adaptation médicale | Criblage ouvert aux généralistes | P1 | ✅ |
| A8 | TRIPOD-LLM (Nature Medicine 2025 ; PMC12104976) | Squelette du rapport : 19 items, 50 sous-items | P4, P5 | ✅ |

### Lot B : à ingérer avant la distillation (P2 à P3)
| # | Papier | Apport | Statut |
|---|---|---|---|
| B1 | arXiv 2306.13649 : GKD, distillation sur politique | Fondement du `DistillationTrainer` | ✅ |
| B2 | arXiv 2503.07067 : DistiLLM-2 (ICML 2025) | Perte contrastive de distillation | ✅ |
| B3 | arXiv 2605.26246 : Bridge-Garden (ICML 2026) | Mélange étiquettes dures et douces | ✅ |
| B4 | Distilling step-by-step | Étiquette plus justification, efficacité en peu de données | 🔎 |
| B5 | MiniLLM | KL inverse | 🔎 |
| B6 | arXiv 2310.01208 : LS-LLaMA ; arXiv 2404.05961 : LLM2Vec ; arXiv 2507.23386 : Causal2Vec (ACL 2026) | Attention bidirectionnelle et pooling | ✅ (résumés) |
| B7 | Confident Learning (JAIR 2021) | Théorie derrière cleanlab | ✅ (recherche) |
| B8 | Hinton et al. 2015, distillation | Température et cibles douces | ◻ |
| B9 | LoRA (Hu 2021), QLoRA (Dettmers 2023), DoRA, PiSSA (arXiv 2404.02948), rsLoRA, LoRA+, LoftQ | Famille LoRA | PiSSA ✅ ; autres ◻ |

### Lot C : incertitude, évaluation, sûreté (P4 à P5)
| # | Papier | Apport | Statut |
|---|---|---|---|
| C1 | arXiv 2402.12683 : TorchCP (JMLR 2025) | Panorama des méthodes conformes | ✅ |
| C2 | Angelopoulos et Bates 2021, introduction à la prédiction conforme ; Romano et al. 2020 (APS) ; RAPS | Méthodes et garanties | ◻ |
| C3 | Guo et al. 2017, calibration des réseaux modernes | Température, ECE | ◻ |
| C4 | Dror et al. 2018 (tests de signification en TAL) ; Bouthillier et al. 2021 (variance des bancs) ; Dodge et al. 2019 (« Show Your Work ») | Statistique et reporting | ◻ |
| C5 | arXiv 2609.11770 : l'écart d'évaluation des LLM médicaux 2023 à 2026 | Modestie des conclusions : 2,5 % d'études randomisées ou prospectives | ✅ |
| C6 | arXiv 2509.08087 : stratégies d'évaluation en santé | Limites des bancs automatiques | ✅ (résumé) |
| C7 | Mitchell et al. 2019 (cartes de modèles) ; Gebru et al. 2018 (fiches de jeux de données) ; Breck et al. 2017 (ML Test Score) | Documentation et rubrique de tests | ◻ |

### Lot D : français clinique, génératif, quantification (P5 à P6)
| # | Papier | Apport | Statut |
|---|---|---|---|
| D1 | arXiv 2402.13432 : DrBenchmark | Références françaises | ✅ |
| D2 | arXiv 2402.16689 : modèles biomédicaux français pour documents longs | Contexte long | 🔎 |
| D3 | arXiv 2506.19525 et TALN 2025 : structuration de la posologie en français | Seul le fine-tuning égale les systèmes de référence | 🔎 |
| D4 | arXiv 2603.04033 : « Who Judges the Judge ? » (LLM-juge, QA médicale française) | Validation du juge | 🔎 |
| D5 | Page UC3 de PARTAGES (résumé de comptes rendus, faits atomiques bidirectionnels) | Métrique de factualité | ✅ |
| D6 | arXiv 2411.15100 : XGrammar ; arXiv 2601.04426 : XGrammar-2 ; arXiv 2501.10868 : JSONSchemaBench | Décodage contraint | 🔎 |
| D7 | arXiv 2507.05201 : MedGemma ; arXiv 2604.05081 : MedGemma 1.5 | Candidats médicaux | 🔎 |
| D8 | arXiv 2603.05451 : FlashAttention-4 | Pourquoi FA4 ne tourne pas sur 5090 | 🔎 |

---

## 7. Écarté ou différé, avec la raison (jugements, pas des faits mesurés)

| Option | Décision | Raison |
|---|---|---|
| Frameworks tout-en-un (Axolotl, LLaMA-Factory) | Différé, **non évalués** ce jour | Le contrat de tâche impose une boucle d'entraînement maîtrisée ; à réévaluer si la maintenance de TRL et PEFT coûte trop |
| MLflow, Weights & Biases | Non retenus | Serveur ou cloud en plus ; Trackio et le registre immuable suffisent |
| LLM de type MoE comme élèves ou professeurs LoRA | Écartés | LoRA sur experts passe par `target_parameters`, surcoût d'inférence ; la classification se fait sur des denses |
| Fine-tuning générique via API payante | Écarté | Hors du principe « données et poids chez soi » |
| Données réelles de patients | Interdites dans ce dépôt | Ce projet prouve la méthode ; la transposition aux données du CHU se fait chez eux |
