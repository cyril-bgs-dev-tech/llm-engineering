# Fiche de données : PARHAF

Statut au 02/10/2026 : P0-14 (téléchargement, empreintes), P0-15 (licence), P0-17 (données personnelles), P0-21 (comptes et longueurs en tokens) et P0-31 (test embargoé) faits ; P0-22 (formats d'étiquette), P0-23 (classes), P0-30 (raccourci d'auteur) et P0-16 (fiche complète) faits.

## Provenance

| Champ | Valeur |
|---|---|
| Source | Hugging Face, `HealthDataHub/PARHAF` (projet PARTAGES, Plateforme des Données de Santé) |
| Révision épinglée | `60426ccdbbbb335e0281f2e5c236b89100ffbd42` (dépôt modifié le 09/06/2026) |
| Consulté | 01/10/2026 |
| Script | `data/scripts/download_parhaf.py` (rejoue le téléchargement et vérifie le manifeste) |
| Manifeste | `data/manifests/parhaf.json` : 8 fichiers, tailles et SHA-256 |
| Preuve de rejeu | téléchargement refait dans un dossier propre (`artifacts/replay_parhaf`, supprimé ensuite) : 8 fichiers identiques. **Rejeu dans un conteneur vierge** (image construite depuis `uv.lock`, dossier de destination vide) : 8 fichiers identiques au manifeste ; la reproduction à froid complète reste à faire en P5-09 |
| Registre | `results/runs/20261001-214229-parhaf-download-replay.json` |
| Données dans Git | non (`data/raw/` ignoré) ; seuls fiche, script et manifeste sont versionnés |

## Licence et usages (P0-15)

Citations littérales de la fiche du jeu (`README.md` de la révision épinglée) :

- Licences : « This dataset is released under licenses: - CC BY 4.0 - Etalab 2.0 » (URLs dans `standalone/patients.json` : https://creativecommons.org/licenses/by/4.0/ et https://www.etalab.gouv.fr/wp-content/uploads/2018/11/open-licence.pdf).
- Usages visés : « Benchmarking French medical LLMs », « Enabling reproducible clinical NLP research », « Promoting work on PARTAGES's 7 use cases ».
- Usages exclus : « Clinical decision-making or patient care (no diagnostic, prognostic, or therapeutic use) », « Clinical validation or performance claims (models trained on this data are not clinically validated) », « Generalization to unseen hospitals, regions, or practices », « Epidemiological or population-level inference (≠ real-world prevalence or distributions) », « Replacing real clinical data for deployment (research-only) ».
- Test : « the documents for the test set of all use cases are excluded. They will remain under embargo [...] You can evaluate your system on the test set through the CodaBench platform. » ; l'accès aux données de test non publiées passe par un contact avec les auteurs.
- Citation : la section « Citation Information » de la fiche contient « [More Information Needed] » ; la publication associée est https://arxiv.org/pdf/2603.20494 (non relue à ce stade).

Conséquence pour le projet : toute conclusion est écrite comme **mesure sur un corpus fictif**, jamais comme performance clinique ni généralisable à un hôpital réel. Le label « chapitre CIM-10 » est le diagnostic du scénario suggéré aux rédacteurs, pas une vérité clinique.

## Comptes mesurés (P0-21, part sans tokenizers)

Chaque ligne cite sa source ; le périmètre est précisé.

| Mesure | Valeur | Source et périmètre |
|---|---|---|
| Patients, parquet publié | 4 254 | `data/train-00000-of-00001.parquet`, révision épinglée ; ids uniques |
| Documents, parquet publié | 6 185 | idem (1 document : 3 285 patients ; 2 : 7 ; 3 : 962) |
| Patients, JSON canonique | 4 259 | `standalone/patients.json` ; ids uniques ; 6 190 documents, 6 190 fichiers dans `data.zip` |
| Spécialités | 20 | colonne `specialty` (les « 18 » de certaines sources sont infirmés) |
| Types de documents | CRH 3 563, CRC 1 079, CRO 889, ANAPATH 433, ACCOUCHEMENT 74, MATERNITE 74, URGENCES 73 | parquet publié |
| Mots par document | médiane 514, p95 1 619, max 5 370, total 3 952 647 | colonne `word_count`, parquet publié |
| Pools (parquet) | General 3 577, CU 2 288, CU 5a 147, CU 5b 108, CU 6 134 | colonne `pool` ; pas de pool CU 1 |
| Auteurs, relecteurs | 104 auteurs, 99 relecteurs ; le plus prolifique : 143 patients (3,4 %) ; les 5 premiers : 14,7 % | colonnes `author`, `reviewer` : l'auteur reste un raccourci possible, split à contrôler |
| Textes en doublon exact | 0 sur 6 185 | hachage MD5 des textes ; les quasi-doublons de gabarit restent à mesurer |
| Longueurs en tokens | voir la section suivante | `results/measures/token_lengths.json`, script `scripts/measure_token_lengths.py` |

### Longueurs en tokens (P0-21)

Mesure sur le parquet publié (4 254 patients, 6 185 documents), tokenizers des modèles candidats sans les poids ; l'unité « patient » concatène ses documents séparés par une ligne vide. Tokenizer Mistral chargé avec `fix_mistral_regex=True` (regex erronée dans la version publiée).

| Tokenizer | Tokens par mot | Document : médiane, p95, max | Patient : médiane, p95, p99, max | Patients au-delà de 4 096 |
|---|---|---|---|---|
| Qwen3.5-9B (identique à Qwen3.8-27B) | 1,41 | 737, 2 218, 6 207 | 1 143, 2 826, 3 696, 6 207 | 0,2 % |
| Gemma 4 (E4B, 31B identiques) | 1,37 | 715, 2 170, 5 924 | 1 109, 2 747, 3 607, 5 924 | 0,1 % |
| Mistral Small 3.2 | 1,37 | 715, 2 163, 6 055 | 1 110, 2 767, 3 582, 6 055 | 0,1 % |

Aucun patient ne dépasse 8 192 tokens : une fenêtre de 4 096 tokens couvre plus de 99,8 % des patients, 8 192 la totalité. Les tokenizers Qwen3.5 et Qwen3.8 d'une part, Gemma 4 E4B et 31B d'autre part, donnent des longueurs identiques : ce sont des familles de vocabulaire communes, condition de la distillation de logits (à confirmer par P0-06).

### Écart entre les deux formats (constat nouveau)

La fiche affirme que le JSON et le parquet « contain identical information ». **Mesuré : ce n'est pas le cas.**

- 4 220 patients ont le même identifiant et le **même texte** dans les deux formats (0 différence de contenu).
- 39 patients du JSON canonique n'existent pas dans le parquet, 34 patients du parquet n'existent pas dans le JSON ; **tous du pool CU 5a (oncologie, biomarqueurs)**, spécialité ANATOMOPATHOLOGIE, document ANAPATH. Leurs textes n'existent pas non plus sous un autre identifiant : ce n'est pas un renumérotage.
- 4 220 + 34 = 4 254 (parquet) ; 4 220 + 39 = 4 259 (JSON). Les « 4 254 ou 4 259 » et « 6 185 ou 6 190 » des sources sont donc deux versions du corpus, pas une erreur de comptage.

Décision provisoire (à confirmer, voir ADR-005) : le jeu de travail est l'**intersection** des 4 220 patients identiques ; les 34 patients exclusifs du parquet sont mis en quarantaine (0,8 % du parquet, pool étranger à la tâche principale). Signalement aux auteurs via l'onglet « Community » : **non fait**, action externe qui attend l'accord de Cyril.

## Présence et formats du diagnostic principal (P0-22)

- **Présence : 100 %** dans tous les pools (General, CU 2, CU 5a, CU 5b, CU 6) et toutes les spécialités ; **aucun patient sans étiquette**, donc aucune exclusion à décider. Chaque patient a **exactement un** diagnostic principal (`suggested_scenario.primary_diagnosis`, un code et un libellé).
- **Formats de code** (4 254 codes) : 3 caractères 470, 4 caractères 3 342, 5 caractères 373 (extensions françaises du type `I21400`), et **69 codes avec suffixe `+`** (`F03+01`, `R53+1`, `C259+8`, `J961+0`), soit 1,6 % : ils suivent la convention de l'ATIH. Le niveau « chapitre » se dérive des trois premiers caractères (lettre et deux chiffres), qui existent pour tous les formats.
- Autre source d'étiquette : `structured_abstract.primary_diagnosis` renseigné pour 3 615 patients, « non vérifié » selon la fiche ; ses trois premiers caractères concordent avec le scénario dans 99,9 % des cas (sur 3 615), ce qui n'en fait **pas** une seconde annotation indépendante : les deux viennent de la même rédaction.
- Rappel de portée : l'étiquette est le **diagnostic du scénario suggéré aux rédacteurs**, pas un codage par un médecin DIM ; les textes écrits peuvent s'en écarter.
- Reste pour P0-23 : distribution par chapitre, bloc, trois caractères (nécessite la nomenclature de P0-27).

## Données personnelles (P0-17)

Balayage par expressions régulières de 200 patients tirés au hasard (graine 0), 284 documents : 0 adresse électronique, 0 numéro de sécurité sociale, 0 adresse postale, 0 IBAN, 1 numéro de téléphone (`01 99 99 99 99`, manifestement fictif). Les **noms fictifs de patients** figurent dans le texte pour 194 patients sur 200, les **dates complètes** (544 occurrences) et les **noms de médecins** (347 occurrences de « Dr Prénom Nom ») sont présents par construction : le corpus est fictif et sert aussi au cas d'usage de pseudonymisation. Un balayage par expressions régulières ne prouve pas l'absence de donnée réelle ; il ne trouve rien d'anormal. **Cas douteux à signaler à Cyril : aucun.** Conséquence de conception : les noms, dates et en-têtes des documents ne doivent pas servir de variables prédictives, et leur retrait est à décider avec l'unité d'entrée (P0-32).

## Test embargoé et CodaBench (P0-31, consulté le 01/10/2026)

- La fiche Hugging Face dit : « Please contact us for information about how to evaluate your system on our unreleased test data » ; elle ne donne aucun lien CodaBench.
- **Vérifié par moi** : l'API publique de CodaBench expose une page « [Test] PARTAGES CU2 » (id 18027), créée le 08/09/2026, publiée, phase unique « Final » du 31/12/2023 au 30/12/2028 (dates qui ressemblent à des valeurs par défaut).
- **Rapporté par un sous-agent de recherche, non revérifié** : cette page et ses sœurs CU1, CU3, CU5a, CU5b, CU6 demandent la **soumission de code** (un fichier `model.py` exécuté par la plateforme), pas de simples prédictions ; le CU2 mesure l'exactitude du code CIM-10 à 4 caractères (secondaire : 3) ; ses 288 textes « CU 2 - ICD-10 coding » sont **déjà dans le jeu public** ; les étiquettes de codage par un médecin DIM ne sont pas publiées. Le test embargoé complet compterait 755 patients et 1 209 documents (article arXiv 2603.20494, section 4).
- Conclusion : on ne peut pas affirmer qu'une évaluation sur le test officiel soit ouverte au public ; la question « le test est-il accessible ? » reste **à poser aux auteurs** (contact sur la fiche), action externe soumise à l'accord de Cyril. Nouvelle vérification prévue en P3-15. Le test du projet reste un sous-ensemble scellé du jeu publié (RM-20).
- Citation de l'article, à utiliser telle quelle : Tannier X., Abbara S., Flicoteaux R., Khalil Y., Névéol A., Zweigenbaum P., Bacry E., « PARHAF, a human-authored corpus of clinical reports for fictitious patients in French », arXiv:2603.20494, 2026 (la fiche HF porte « [More Information Needed] »).

## Distribution des classes (P0-23, jeu de travail)

Parquet publié, chapitre CIM-10 dérivé des trois premiers caractères : 21 chapitres présents (le chapitre XX est absent), le plus grand (II, tumeurs) pèse 27,9 % ; 165 blocs et 554 catégories à 3 caractères, dont 105 blocs et 506 catégories sous 20 exemples. Après la règle de PROTOCOLE.md section 2 : 17 classes évaluées (de 31 à 1 153 patients) et une classe `AUTRE` de 18 patients. Détails dans `results/measures/class_distribution.json` et `results/measures/splits_summary.json`.

## Ce que le jeu ne représente pas

Hôpitaux, régions et pratiques réels ; la prévalence réelle des diagnostics (scénarios échantillonnés pour réduire les cas très fréquents) ; les types de documents absents (imagerie, ordonnances, courriers, comptes rendus opératoires non retenus) ; les contraintes du travail clinique (pression, interruptions) ; un codage PMSI par un médecin DIM (l'étiquette est le diagnostic du scénario suggéré). Source : fiche du jeu, sections « Excluded usages » et « Intended usages », et limites déclarées dans l'article arXiv:2603.20494 (rapportées par un sous-agent de recherche, non relues par moi).

## Pièges connus pour ce corpus

- Split au niveau patient, jamais au niveau document (962 patients ont 3 documents).
- L'auteur est un raccourci potentiel : `RM-14` mesure un classifieur « auteur seul ».
- Gabarits : la fiche décrit un modèle de compte rendu commun ; les quasi-doublons sont à mesurer en P0-23.
- Test scellé non publié (CodaBench) : aucune évaluation « finale » n'est possible localement ; le test du projet est un sous-ensemble scellé du jeu publié (RM-20).
