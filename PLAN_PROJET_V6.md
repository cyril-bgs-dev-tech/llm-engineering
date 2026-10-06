# LLM_finetuning : plan maître V6

Plan v6, 01/10/2026. Statut : **à valider avant toute ligne de code.** Remplace la V5 comme référence ; V1 à V5 restent l'historique.

Fichiers compagnons :
- `MICROTACHES.md` : le backlog complet, découpé en micro-tâches (ordre d'exécution, critères de fin, catégories de qualité visées).
- `BOITE_A_OUTILS.md` : outils, dépôts et papiers retenus, avec ce qui a été vérifié et ce qui reste à confirmer.
- `docs/CATALOGUE_LEVIERS.md` : les leviers L1 à L12, corrigés par la veille.
- `roadmap_unifié.md` : **l'ordre d'exécution**, les portes d'arrêt et les skills à charger à chaque étape ; il intègre les audits de GLM 5.3 et de ChatGPT 5.6 (01/10/2026) et prévaut sur ce plan pour l'ordre.

Historique : V1 recette LMSYS, V2 état de l'art, V3 solution Danube, V4 matériel (5090 d'abord, location prévue), V5 contrat de cible unique, **V6 veille des outils et papiers, corpus PARHAF, 12 catégories de qualité, micro-tâches**.

---

## 0. Cap

- **Offre visée** : poste « Ingénieur.e Data Science » de la cellule données de santé du CHU Grenoble Alpes, pour affiner et évaluer des LLM sur des comptes rendus hospitaliers, dans le projet national PARTAGES (texte intégral archivé dans `docs/offre/`, empreinte SHA-256 consignée ; l'annonce ne donne ni URL, ni date de publication, ni date limite).
- **Trou à combler, dit honnêtement** : Cyril n'a jamais affiné de LLM (vérifié le 01/10). Ce projet doit rendre la réponse « oui, voici le protocole, les chiffres et le code » défendable. Rien n'est publié (CV, LinkedIn, lettre) avant d'être mesuré (`claim-gate`).
- **Livrable cible** : une chaîne expérimentale reproductible et un candidat final choisi après comparaison préenregistrée (référence non neuronale, encodeur, LoRA, distillation), calibré et capable de s'abstenir. Le candidat peut être TF-IDF, un encodeur, une LoRA simple ou un élève distillé ; si aucun n'atteint les critères, le livrable est un verdict négatif documenté et reproductible.
- **Trois promesses** : (1) un compromis qualité, calibration et coût mesuré, sous un budget de calcul B et un nombre d'essais N fixés par Cyril (RM-02) sur une RTX 5090, (2) chaque chiffre est prouvé et réplicable, (3) ajouter une tâche de même famille ne modifie pas le noyau : seuls un contrat YAML et un adaptateur de données changent.

---

## 1. Ce que la veille du 01/10/2026 change

| # | Découverte | Source (statut) | Conséquence sur le plan |
|---|---|---|---|
| 1 | **PARHAF** : corpus ouvert de comptes rendus cliniques français fictifs, écrits par des internes et relus par des pairs ; 4 254 lignes `train` dans la révision observée (60426ccd, modifiée le 09/06/2026 ; les autres sources donnent d'autres totaux, à trancher par P0-21), 7 types de documents, CC BY 4.0 et Etalab 2.0 | arXiv 2603.20494 et fiche HF (lues) | Devient le **jeu principal** ; DiaMED est rétrogradé en option |
| 2 | Le test de PARHAF est **sous embargo** (755 patients, 1 209 documents), évalué via CodaBench, calendrier non précisé | fiche HF et article (lus) | Test scellé interne en attendant ; une seule soumission préenregistrée le jour où l'embargo s'ouvre |
| 3 | PARTAGES liste ses cas d'usage : pseudonymisation, **codage médical (DIM)**, résumé, biomarqueurs, infectiologie... et ses 7 modèles | page Health Data Hub (lue) | Les tâches du projet s'alignent sur les cas d'usage de PARTAGES, sans prétendre que l'offre les liste |
| 4 | Plusieurs documents par patient, un auteur par patient, des gabarits de documents | article PARHAF (lu) | Découpage **par patient**, plis **par auteur** en contrôle, mesure des raccourcis (section 3.3) |
| 5 | `DistillationTrainer` de TRL exige un vocabulaire commun et génère ; distiller des classes n'a pas cette contrainte | doc TRL (lue) | Distillation de classifieur **au niveau des classes**, professeurs de familles différentes autorisés ; `DistillationTrainer` réservé à la piste générative |
| 6 | Avec un taux d'apprentissage réglé, vanilla LoRA et neuf variantes finissent à 1 à 2 % l'une de l'autre | arXiv 2602.04998 (lu) | Gros budget de réglage sur la **référence** ; les variantes passent derrière |
| 7 | En classification mono-étiquette, une tête sur le dernier token égale ou bat BERT ; l'invite ne tient qu'en multi-étiquettes | arXiv 2512.12677 (lu) | Tête par défaut, verbaliseur en contrôle ; pooling max ou moyenne testé |
| 8 | Les LLM médicaux ne battent pas systématiquement leur base | arXiv 2411.08870 (lu) | Criblage ouvert aux généralistes ; MedGemma n'est pas présumé meilleur |
| 9 | RTX 5090 (SM120) : FlashAttention 2 oui, FlashAttention 4 non ; PyTorch avec noyaux SM120 seulement en builds cu128 ou cu130 récents ; lacunes NVFP4 signalées sur vLLM | recherche (🔎) | Premier bloc de P0 : **spikes** de compatibilité avant tout le reste |
| 10 | MAPIE v1 (BSD-3) et TorchCP (LGPL-3.0, JMLR 2025) | dépôts et docs (lus) | Trois implémentations de la prédiction conforme qui se recoupent (MAPIE, TorchCP, code maison), plus la validation de RM-22 |
| 11 | TRIPOD-LLM (Nature Medicine 2025) : 19 items et 50 sous-items pour rapporter une étude de LLM en santé | PMC12104976 (lu) | Squelette du rapport et de la carte de modèle |
| 12 | Le dépôt de la solution 1re de LMSYS n'a **aucune licence** | GitHub (lu) | Lecture seule, réimplémentation |
| 13 | Modèles : Qwen3.8-27B (Apache 2.0, 14/08/2026), Qwen3.5 (4B, 9B, 27B denses), Gemma 4 (E4B, 31B dense), MedGemma 1.5 | articles et pages (lus ou 🔎) | Liste de candidats de la section 5 |
| 14 | Pour la médecine, 2,5 % seulement des études de LLM sont randomisées ou prospectives | arXiv 2609.11770 (lu) | Modestie des conclusions : « sur données fictives, accord avec le scénario » |

---

## 2. Les 12 catégories de qualité : le barème du projet

Un projet de ce genre se juge sur douze dimensions. Chacune a un **seuil** (ce que « sérieux » veut dire ici), une **preuve observable**, et des micro-tâches dédiées dans `MICROTACHES.md` (colonne Q).

| Q | Catégorie | Seuil sérieux | Preuve observable |
|---|---|---|---|
| Q1 | **Données** | Licence lue à la source, provenance, étiquettes dérivées par script déterministe, aucune fuite (patient, auteur, gabarit, doublon), raccourcis mesurés | Fiches `data/cards/`, tests `leakage-guard` verts, rapport de raccourcis |
| Q2 | **Protocole et rigueur expérimentale** | Préenregistrement, test scellé, **références fortes et réglées** (TF-IDF, encodeurs, LoRA réglée), ablation levier par levier, budgets égaux | Fiches `experiments/` figées par empreinte, registre complet |
| Q3 | **Validité statistique** | Variance entre graines mesurée, intervalles de confiance, tests appariés, correction des comparaisons multiples, verdict en trois valeurs (gain, absence de gain, non résolu) | Rapports `paired-comparison`, écart-type de graines publié |
| Q4 | **Analyse d'erreurs et robustesse** | Erreurs par classe, spécialité, auteur, longueur ; perturbations ; hors distribution (spécialité exclue) ; relecture d'échantillons | Tableaux d'erreurs, courbes de dégradation, matrice de confusion hiérarchique |
| Q5 | **Fiabilité de l'incertitude** | Calibration (ECE), prédiction conforme avec couverture mesurée, politique d'abstention chiffrée, recalibration après quantification | Diagrammes de fiabilité, couverture empirique contre niveau visé, courbe automatisation contre exactitude |
| Q6 | **Reproductibilité** | Environnement verrouillé, graines, déterminisme mesuré, empreintes, **reconstruction à froid** testée | `make reproduce-small` reproduit un chiffre clé dans la tolérance, depuis un clone neuf |
| Q7 | **Ingénierie logicielle** | Typage strict, tests, CI, revue indépendante, code sans logique propre à une tâche | CI verte, test de transposabilité, rapports `code-reviewer` |
| Q8 | **Efficience et coût** | VRAM de pointe, latence p50 et p95, débit, énergie ou coût réel, front de Pareto qualité contre coût | Tables de coûts dans le registre, graphique de Pareto |
| Q9 | **Déploiement et opérations** | Service testé, quantification vérifiée sur la tâche, surveillance de dérive, règles de maintenance, retour arrière | Service qui tourne hors ligne, tests de charge, document de maintenance |
| Q10 | **Sûreté, éthique et conformité** | Usages permis et interdits du corpus respectés, aucune donnée de patient réel, limites écrites, sous-groupes rapportés, checklist TRIPOD-LLM remplie | Carte de modèle, checklist TRIPOD-LLM, bannière « données fictives » |
| Q11 | **Documentation et transmission** | Wiki à jour avec citations vérifiées, décisions tracées (ADR), guide de transposition testé à blanc | Wiki sans lien cassé ni contradiction, `docs/TRANSPOSER_AU_CHU.md` exécuté par un tiers ou à blanc |
| Q12 | **Honnêteté scientifique** | Question claire, résultats négatifs publiés, comparaison à l'état de l'art, **toute affirmation tracée vers un run** | `claim-gate` : tableau de preuve joint à chaque texte sortant |

### Échelle de notation (0 à 3), appliquée à chaque porte de phase
- **0** absent. **1** partiel ou non prouvé. **2** satisfait, avec preuve dans le dépôt. **3** satisfait et **confirmé de façon indépendante** : seconde implémentation, relecture croisée, reconstruction à froid ou revue externe.

### Planchers exigés à chaque porte
| Catégorie | G-P0 | G-P1 | G-P2 | G-P3 | G-P4 | G-P5 |
|---|---|---|---|---|---|---|
| Q1 Données | 2 | 2 | 3 | 3 | 3 | 3 |
| Q2 Protocole | 2 | 2 | 2 | 3 | 3 | 3 |
| Q3 Statistique | 1 | 2 | 2 | 3 | 3 | 3 |
| Q4 Erreurs | 0 | 1 | 2 | 2 | 3 | 3 |
| Q5 Incertitude | 0 | 1 | 1 | 1 | 3 | 3 |
| Q6 Reproductibilité | 2 | 2 | 2 | 2 | 2 | 3 |
| Q7 Ingénierie | 2 | 2 | 2 | 2 | 2 | 3 |
| Q8 Efficience | 1 | 1 | 1 | 2 | 3 | 3 |
| Q9 Déploiement | 1 | 1 | 1 | 1 | 2 | 3 |
| Q10 Sûreté et éthique | 2 | 2 | 2 | 2 | 2 | 3 |
| Q11 Documentation | 1 | 1 | 2 | 2 | 2 | 3 |
| Q12 Honnêteté | 2 | 2 | 2 | 3 | 3 | 3 |

Chaque porte se clôt par une micro-tâche « scorecard » (G-Px) : une note par catégorie, **une preuve citée par note**, et un plan de rattrapage pour toute note sous le plancher. Une note ne se pose jamais sans preuve.

---

## 3. Données : PARHAF d'abord

### 3.1 Les jeux
| Jeu | Rôle | Licence | Statut |
|---|---|---|---|
| **PARHAF** (HealthDataHub/PARHAF) | Jeu principal ; clés : `id` patient, `specialty`, `author`, `reviewer`, `pool`, `suggested_scenario` (diagnostic principal CIM-10, diagnostics associés, acte CCAM, âge, sexe, modes d'entrée et de sortie), `documents[]` | CC BY 4.0 et Etalab 2.0 | ✅ |
| PARHAF annotés (conclusion, pseudo, biomarqueurs, infectiologie, réponse au traitement) | Tâches de la piste générative et de l'extraction | CC BY 4.0 et Etalab 2.0 | ✅ |
| PARCOMED | Pré-entraînement continu léger et textes non étiquetés | CC BY 4.0 et Etalab 2.0 (version commerciale) | ✅ |
| MorFITT | Tâche multi-étiquettes et pré-entraînement sur tâche voisine | CC BY-SA 4.0 | ✅ |
| CLISTER | Tâche sur paires (type `pair_ordinal`) | à lire | 🔎 |
| DiaMED | Option de repli (739 cas) | CC BY-SA 4.0 | ✅ |

### 3.2 Les tâches dérivées (une par contrat `task_specs/`)
| task_id | Type | Étiquette | Rôle | Remarque |
|---|---|---|---|---|
| `parhaf_doctype` | multiclass (7) | type de document | Contrôle de bon fonctionnement | Plafond attendu très haut : ne départage rien |
| `parhaf_specialty` | multiclass (18 ou 20) | spécialité | Preuve de transposabilité ; tâche voisine | Risque de raccourci par le lexique et l'auteur |
| **`parhaf_cim10_chapter`** | multiclass (environ 20) | chapitre CIM-10 du diagnostic principal du scénario | **Tâche principale, niveau 1** | Étiquette = scénario suggéré, pas vérité clinique |
| `parhaf_cim10_block` | multiclass (environ 200) | bloc CIM-10 | Niveau 2 | Classes rares |
| `parhaf_cim10_3char` | multiclass (plusieurs centaines) | code à 3 caractères | Niveau 3, très difficile | Macro-F1 par classe, regroupement hiérarchique |
| `morfitt_specialites` | multilabel (12) | spécialités | Preuve du type multi-étiquettes | Résumés d'articles, pas des comptes rendus |
| `clister_similarite` | pair_ordinal (niveaux 0 à 5) | niveau de similarité | Preuve du type paire | Chaque niveau nommé et défini |
| (option) `parhaf_infectiology_*` | multilabel dérivé des spans | bactérie ou site présent | Extraction vers classification | À cadrer en P6 |
| (option) `parhaf_conclusion` | génératif | conclusion | Piste P6 (cas d'usage 3 de PARTAGES) | Métrique : faits atomiques |

L'**échelle de difficulté CIM-10** (chapitre, bloc, trois caractères) est un atout scientifique : le même code, trois niveaux de finesse, et la prédiction conforme montre comment la taille des ensembles croît avec la finesse.

### 3.3 Les pièges propres à ce corpus (et la parade de chacun)
| Piège | Pourquoi c'est grave | Parade (micro-tâche) |
|---|---|---|
| Plusieurs documents par patient (7 394 rapports pour 5 009 patients) | Un découpage par document fait fuiter le patient entre entraînement et test | Unité de découpage = **patient** (P0-28), test dédié (P0-40) |
| Un auteur écrit plusieurs patients, souvent d'une même spécialité | Le style de l'auteur devient un raccourci vers la spécialité | Plis **groupés par auteur** en contrôle (P0-29), modèle témoin entraîné sur l'auteur seul (P0-30) |
| Documents produits à partir de gabarits | Quasi-doublons structurels qui gonflent les scores | MinHash et comparaison par gabarit (P0-40) |
| Étiquette = diagnostic **suggéré** par le scénario | Le score mesure l'accord avec le scénario, pas la vérité clinique | Libellé honnête des résultats ; cleanlab sur probabilités hors pli ; relecture d'un échantillon (P2-06) |
| Scénarios échantillonnés depuis la base nationale SNDS | La prévalence n'est pas celle du réel | Macro-F1 avant exactitude ; aucune inférence épidémiologique |
| Test embargoé évalué par CodaBench | Impossible de s'y mesurer tout de suite | Test scellé interne ; vérification régulière de l'ouverture (P0-31) ; **une** soumission préenregistrée |
| Usages interdits : décision clinique, validation clinique, généralisation au réel, déploiement | Un texte de CV ou une démo mal formulés enfreignent les conditions | `claim-gate` ; bannière ; démo locale par défaut (décision de Cyril, section 10) |
| 18 ou 20 spécialités, 6 185 ou 6 190 documents selon les sources | Chiffres cités à tort | On compte dans les données (P0-21) |
| Textes fictifs plus propres que le réel | Les scores sur du texte fictif ne se transposent pas tels quels | Perturbations (P4-07) ; formulation « sur données fictives » |

### 3.4 Alignement avec PARTAGES
PARTAGES prévoit une plateforme d'évaluation fédérée et un cas d'usage de résumé qui démarre en octobre 2026 pour finir en juin 2027, avec évaluation par faits atomiques sur des sites partenaires sans transfert de données. Notre chaîne se garde donc **découplée des données** (contrat de tâche, artefacts portables), ce qui est compatible avec l'architecture fédérée décrite (inférence de ma part, pas une exigence démontrée).

---

## 4. Contrat de cible unique (rappel V5, mis à jour)

Même type de cible que LMSYS : un ou deux textes en entrée, une **catégorie descriptive** dans une liste fermée en sortie, format fixe, tout dans `task_specs/<task_id>.yaml` (type, entrées, classes avec identifiant stable, nom en clair, définition opérationnelle et exclusions, format de sortie, métriques, abstention). Le code ne contient rien de propre à une tâche ; la **preuve de transposabilité** est un test (P0-44) et un guide testé à blanc (P5-07).

Mises à jour V6 :
- Les noms de classes viennent de la **nomenclature officielle** (CIM-10 de l'ATIH ou de l'OMS, spécialités de PARHAF) ; les conditions de réutilisation sont lues avant usage.
- Une tâche déclare son **unité d'entrée** : un document, ou un patient (documents concaténés par type, ordre fixe).
- Une tâche déclare son **niveau hiérarchique** (`parent` et `enfants`) pour que la prédiction conforme et les erreurs se calculent aussi par niveau.

---

## 5. Modèles et matériel

### 5.1 Candidats (à reconfirmer et à cribler en P1)
| Rôle | Candidats | Notes |
|---|---|---|
| Élèves | Qwen3.5 4B et 9B, Gemma 4 E4B, MedGemma 1.5 4B | Denses ; classification par `*ForSequenceClassification` à vérifier modèle par modèle (P0-06) |
| Professeurs | Qwen3.8-27B, Gemma 4 31B dense, MedGemma 27B, Mistral Small 3.2 24B | QLoRA 4 bits ; la mémoire réelle vient de P0-08 |
| Références à battre | TF-IDF + régression logistique ; DrBERT, CamemBERT-bio, doctomodernbert-fr ; LLM en zéro-shot et few-shot | Obligatoires : sans elles, aucun gain n'est interprétable |

Règles : denses seulement ; au moins un généraliste par taille ; modèles à accès conditionné (MedGemma ; Gemma 4 et Qwen3.8 sont en Apache 2.0 sans gating vu sur leurs cartes le 01/10/2026) : c'est Cyril qui accepte les conditions sur Hugging Face. Les cartes officielles de Qwen3.8-27B et de Gemma 4 31B recommandent `AutoModelForMultimodalLM` et ne mentionnent aucune classification : P0-06 est bloquant pour les professeurs.

### 5.2 Matériel (rappel V4)
Tests et démo sur la RTX 5090 (32 Go). La location de GPU est **prévue dans l'architecture** (profils `hardware/`, image identique, artefacts portables) mais ne se déclenche que sur une question scientifique que la 5090 ne tranche pas : professeur de 70B, fine-tuning complet d'un 7 à 9B, plus de professeurs. Chaque location : fiche préenregistrée, plafond de dépense validé par Cyril, résultats présentés à côté des résultats 5090.

---

## 6. La chaîne technique, étape par étape

Pour chaque étape : le choix principal, pourquoi, ce qu'on garde en réserve, et le risque connu. Les références sont dans `BOITE_A_OUTILS.md`.

| Étape | Choix principal | Pourquoi | En réserve | Risque connu |
|---|---|---|---|---|
| E1 Environnement | `uv` verrouillé, PyTorch cu128 ou cu130 avec noyaux SM120, Transformers v5, PEFT, TRL, bitsandbytes ; image Docker identique en local et en location | Reproductibilité et passage à la location sans réécriture | Conda | PyTorch stable sans SM120 selon des sources de recherche : spike P0-04 |
| E2 Données et découpage | Découpage par **patient**, stratifié, 5 plis, test scellé interne ; plis par auteur en contrôle ; DVC pour les artefacts | Seule façon d'éviter la fuite documentée en 3.3 | Empreintes SHA-256 seules | Stratification multi-étiquettes : outil à choisir (P0-28) |
| E3 Références | TF-IDF + régression logistique ; DrBERT, CamemBERT-bio, doctomodernbert-fr ; LLM en zéro-shot et few-shot ; règles EDS-NLP en option | Une base forte rend les gains interprétables | DrBenchmark pour l'étalonnage des encodeurs | Les encodeurs peuvent gagner : c'est un résultat |
| E4 Classifieur LLM | `AutoModelForSequenceClassification` + LoRA toutes couches linéaires, tête sur le dernier token ; pooling max et moyenne testés ; verbaliseur en contrôle | arXiv 2512.12677, solution LMSYS | Retrait du masque causal (LS-LLaMA, LLM2Vec) | Support de classification variable selon l'architecture (P0-06) |
| E5 Réglage | Balayage Optuna **du taux d'apprentissage d'abord**, puis rang et alpha, puis longueur de contexte ; trois graines par point ; budget de calcul égal entre méthodes | arXiv 2602.04998 | Sweeps par plan factoriel | Coût en temps GPU : budget par vague |
| E6 Professeurs | 5 plis en QLoRA, probabilités **strictement hors pli** stockées en Parquet avec manifeste | Recette 1re place LMSYS | 70B loué (déclencheurs de la section 5.2) | Mémoire du 27B à 31B en QLoRA : P0-08 |
| E7 Qualité des étiquettes | cleanlab sur probabilités hors pli ; file de relecture humaine ; **jamais** de réétiquetage du test | Recette WSDM 2025, confident learning | Relecture clinique externe (hors périmètre) | Cyril n'est pas clinicien : on évalue la cohérence texte et définitions, pas la vérité médicale |
| E8 Distillation | Perte `alpha*CE + (1-alpha)*T²*KL` **au niveau des classes** ; professeurs hétérogènes autorisés ; justifications en tâche auxiliaire | Aucune contrainte de vocabulaire ; arXiv 2605.26246 | `DistillationTrainer` TRL pour la piste générative | Surapprentissage de la distillation signalé par des participants LMSYS |
| E9 Leviers | Pré-entraînement sur tâche voisine (tête jetée) ; DAPT léger sur PARCOMED ; données synthétiques avec lignée ; variantes LoRA | Solution Danube ; arXiv 2411.08870 pour la prudence | Fine-tuning complet d'un petit élève | Gain non garanti : tout est mesuré |
| E10 Fusion et compression | Fusion de LoRA des plis, comparée à l'ensemble ; INT8 bitsandbytes, GPTQ, FP8, NVFP4 via llm-compressor ; TTA | Danube : INT8 plus rapide que GPTQ en classification | AWQ, AutoRound | Lacunes NVFP4 sur SM120 signalées : test sur modèle dense seulement |
| E11 Incertitude | Température, **MAPIE** (LAC, APS, RAPS), TorchCP, version maison ; abstention chiffrée ; recalibration après quantification | Trois implémentations qui doivent se recouper ; RM-22 valide au-delà | Conformité par classe (Mondrian) | La garantie est conditionnelle à l'échangeabilité et évaluée sur le split PARHAF observé ; elle ne vaut pas pour du réel |
| E12 Évaluation | Macro-F1 d'abord ; log loss, ECE ; bootstrap apparié, McNemar, Holm ; verdict en trois valeurs ; analyse par spécialité, auteur, longueur | Dror 2018, Bouthillier 2021 | Plus de graines | Variance entre graines : mesurée en P1 avant toute décision |
| E13 Suivi et CI | Registre immuable (JSON) + Trackio ; CI GitLab : pytest, mypy, ruff, gitleaks ; revue `code-reviewer` | Preuve et ingénierie | MLflow écarté | Aucun |
| E14 Service et intégrations | FastAPI qui lit le contrat ; vLLM si la classification est validée, sinon Transformers ; indexation ElasticSearch ; composant **EDS-NLP** | Termes de l'offre ; interopérabilité AP-HP | Streamlit pour la démo | vLLM et classification : P0-09 |
| E15 Piste générative | SFT LoRA, distillation sur politique (TRL), GRPO à récompense vérifiable (F1 d'extraction), décodage contraint (xgrammar), faits atomiques, LLM-juge validé | Cas d'usage 3 de PARTAGES | llguidance | Option : seulement si P0 à P5 sont clos |

---

## 7. Programme d'expériences (vagues) et leur place dans les phases

| Vague | Phase | Contenu | Question |
|---|---|---|---|
| V0 | P1 | Références, criblage des points de départ, LoRA réglée, tête contre verbaliseur, pooling | D'où part-on, et avec quel élève ? |
| V1 | P2 et P3 | Distillation (1re place) contre pré-entraînement sur tâche voisine (5e place) | Laquelle tient sur du texte clinique français, et se cumulent-elles ? |
| V2 | P2 | Recette WSDM : plus de professeurs, nettoyage d'étiquettes, synthétiques | Qu'a ajouté la recette de 2025 ? |
| V3 | P3 | Variantes LoRA, pertes et températures, justifications, courbes d'apprentissage à 10, 25, 50, 100 % | Les gains récents tiennent-ils face à une référence réglée ? |
| V4 | P4 | Fusion, quantification, calibration, prédiction conforme, robustesse | Est-ce déployable, calibré et sûr ? |
| V5 | P6 | Génératif | Option |

Le catalogue détaillé des leviers L1 à L12 est dans `docs/CATALOGUE_LEVIERS.md`. Règles de conduite : vagues successives et gloutonnes, budget GPU fixé avant chaque vague, un levier sans gain devient un résultat négatif publié.

---

## 8. Phases, portes et chemin court

| Phase | Contenu (micro-tâches) | Porte de sortie (preuves) |
|---|---|---|
| **P0 Socle** | P0-01 à P0-47 : décisions, spikes de compatibilité, intake des données, découpage, raccourcis, garde-fous, protocole | Spikes verts ; PARHAF entré avec fiche et contrats ; tests anti-fuite verts ; test de transposabilité vert ; `PROTOCOLE.md` figé ; scorecard G-P0 au plancher |
| **P1 Références** | P1-01 à P1-26 | Tableau de référence complet avec intervalles ; élève et professeurs choisis ; variance de graines mesurée ; LoRA de référence gelée ; G-P1 |
| **P2 Professeurs et données** | P2-01 à P2-12 | Probabilités hors pli pour 100 % de l'entraînement ; qualité des étiquettes auditée ; tâche voisine mesurée ; G-P2 |
| **P3 Distillation et leviers** | P3-01 à P3-15 | Verdict apparié sur chaque levier ; courbes d'apprentissage ; analyse d'erreurs et de raccourcis ; G-P3 |
| **P4 Compression et sûreté** | P4-01 à P4-10 | Pareto qualité contre coût ; calibration et couverture conforme mesurées ; robustesse ; carte de modèle et TRIPOD-LLM ; G-P4 |
| **P5 Industrialisation** | P5-01 à P5-12 | Service hors ligne ; ElasticSearch et EDS-NLP ; CI ; guide de transposition testé à blanc ; reconstruction à froid ; revue indépendante ; G-P5 |
| **P6 Générative (option)** | P6-01 à P6-08 | Selon décision de Cyril |
| **R Location (option)** | R-01 à R-05 | Seulement sur déclencheur |

**Chemin court (MVP)** : 111 des 193 micro-tâches de `MICROTACHES.md` sont marquées ★ (dont 36 tâches de cadrage, de portes d'arrêt et de mesures issues des audits et du premier cycle) (P0 essentiel, références de P1, un professeur, une distillation, une calibration et la prédiction conforme, la carte de modèle, la reconstruction à froid, les textes sortants passés par `claim-gate`). Le contrôle `scripts/check_microtasks.py` vérifie que cet ensemble est **fermé** : aucune tâche ★ ne dépend d'une tâche hors ★. Dans le chemin court, la LoRA de référence n'est réglée que sur le taux d'apprentissage (P1-13) ; rang et contexte (P1-14, P1-15) viennent avec le chemin complet ; **les époques ne le peuvent plus** : la mesure du 04/10/2026 montre que la recette à 2 époques sous-estime les modèles appris (encodeur 0,448 contre 0,73, LoRA 0,587 contre 0,78), d'où RM-25 et RM-27 dans le chemin court. Le chemin complet ajoute les leviers, la fusion, la quantification, le service, l'indexation et la CI. La durée reste à mesurer (RM-16) : aucune estimation en semaines n'est annoncée avant la mesure pilote. Deux jalons de communication : A (premier résultat honnête, fin de R7) et B (MVP complet, fin de R11) ; la date limite de candidature (décision 4) dira lequel viser.

---

## 9. Risques et spikes (on traite l'incertain d'abord)

| Risque | Gravité | Spike | Plan B |
|---|---|---|---|
| PyTorch ou bibliothèques sans noyaux SM120 | Bloquante | P0-04, P0-05 | Image NGC ou build nightly ; location le temps de corriger |
| Classification non supportée pour un modèle candidat | Élevée | P0-06 | Tête ajoutée à la main ; autre modèle |
| Professeur de 27 à 31B qui ne tient pas en QLoRA sur 32 Go | Élevée | P0-08 | Professeur plus petit ; location (déclencheur 1) |
| vLLM sans classification validée | Moyenne | P0-09 | Service Transformers |
| NVFP4 instable sur SM120 | Moyenne | P0-10 | FP8 ou INT8 |
| Raccourcis (auteur, gabarit) qui gonflent les scores | Élevée | P0-30 | Plis par auteur comme métrique principale |
| Diagnostic principal absent pour une partie des patients | Moyenne | P0-22 | Tâches restreintes aux patients étiquetés, dit explicitement |
| CodaBench indisponible | Faible | P0-31 | Test scellé interne seul |
| Accès aux modèles conditionnés non accordé | Moyenne | P0-01 | Modèles Apache 2.0 seulement |
| Conditions d'usage de PARHAF incompatibles avec une démo publique | Moyenne | P0-20 | Démo locale |
| Temps GPU insuffisant pour tout le programme | Élevée | Budget par vague (P0-45) | Réduire les leviers P2 et P3 ; location |

---

## 10. Décisions ouvertes pour Cyril

1. **Emplacement** du dossier : rester dans `Projet Assistante IA/` ou passer sous `D:\Projets persos\` avec les autres projets.
2. **Dépôt** : GitLab privé dès le départ (cité par l'offre), miroir GitHub plus tard.
3. **Périmètre** : chemin court (★) puis complet, avec P6 en option ; ou tout jusqu'à P5.
4. **Date limite** de candidature au CHUGA : fixe la phase à clore avant l'envoi.
5. **Démo** : locale (entretien) ou publique, au vu des conditions d'usage de PARHAF.
6. **Modèles à accès conditionné** (MedGemma ; Gemma 4 est en Apache 2.0) : accepter les conditions sur Hugging Face, ou rester sur des modèles Apache 2.0.
7. **Location de GPU** : fournisseur et plafond de dépense par location, le moment venu.
8. **Revue croisée** par Codex ou Gemini (envoi de contenu à un tiers) : jamais sans accord explicite à chaque fois.
9. **Relecture des étiquettes** : Cyril n'est pas clinicien ; accepter la limite (« cohérence avec les définitions ») ou chercher un relecteur.

---

## 11. Outillage agentique et suite

- `CLAUDE.md` (règles permanentes), `PROMPT_LANCEMENT.md` (démarre P0 seulement), 38 skills dans `.claude/skills/` (dont les 10 skills du projet), 3 relecteurs dans `.claude/agents/`, wiki dans `knowledge/`.
- Les micro-tâches de `MICROTACHES.md` alimentent `tasks/plan.md` et `tasks/todo.md` à l'ouverture de P0 (`planning-and-task-breakdown`), identifiants inchangés. `python scripts/check_microtasks.py` contrôle le backlog (identifiants, dépendances, cycles, chemin court fermé, couverture des 12 catégories de qualité à chaque porte).
- Sources et statut de vérification : `BOITE_A_OUTILS.md`.
