# Fiche du jeu MorFITT (RM-49, dataset-intake, 06/10/2026)

**Statut de l'entrée** : jeu public sans donnée de patient, utilisé uniquement pour l'ancrage sur un benchmark à résultats publiés (RM-49). Cette fiche a été écrite **après** le téléchargement du 05/10/2026 et **avant** tout run sur le test public ; l'entrée régulière (script, manifeste, fiche, contrat) a été régularisée le 06/10/2026 à la suite de la revue indépendante (P5-10), qui avait relevé l'absence de manifeste et de fiche.

## Source, version, empreintes
- Dépôt : `Dr-BERT/MORFITT` (Hugging Face), format parquet, **révision épinglée `5f381299bb113fdba325538d65ef412650a4d98e`** (dépôt modifié le 15/01/2026).
- Script : `data/scripts/download_morfitt.py` ; manifeste versionné : `data/manifests/morfitt.json` (README et trois parquet `source/`). Le jeu local (téléchargé le 05/10/2026) a été comparé le 06/10/2026 à un téléchargement propre de cette révision : **les quatre fichiers sont identiques octet pour octet**.
- Données dans `data/raw/morfitt/` (ignoré par Git). Contrat de cible : `task_specs/morfitt_specialities.yaml`.

## Licence : trois déclarations divergentes, la plus restrictive retenue
- Données, README du dépôt GitHub `qanastek/MORFITT` (lu le 06/10/2026) : « licensed under *Attribution-ShareAlike 4.0 International* (CC BY-SA 4.0) ».
- Code du même dépôt, fichier LICENSE : « MIT License … Copyright (c) 2023 Labrak Yanis ».
- Carte Hugging Face `qanastek/MORFITT` : métadonnée `license: apache-2.0` ; carte de `Dr-BERT/MORFITT` (notre source) : **aucune licence déclarée**.
- **Décision** : appliquer **CC BY-SA 4.0** (la plus restrictive pour les données). Usages : recherche et évaluation avec attribution ; aucune redistribution du jeu ni de ses dérivés par ce projet. Citation : Labrak et al., 2023 (HAL hal-04125879), à citer dans tout texte qui rapporte un chiffre MorFITT. La divergence est à signaler dans le rapport ; elle ne change pas l'usage, qui reste interne.

## Contenu
3 624 résumés d'articles biomédicaux français, 12 étiquettes de spécialité, multi-étiquettes (au moins une par résumé ; moyenne 1,39 sur l'entraînement). Découpage officiel : entraînement 1 514, validation 1 022, test 1 088. Étiquettes (entraînement, validation, test) : microbiologie 115 / 72 / 86, étiologie 317 / 202 / 222, virologie 76 / 57 / 67, physiologie 217 / 125 / 148, immunologie 106 / 86 / 70, parasitologie 68 / 34 / 50, génétique 207 / 139 / 159, chimie 94 / 53 / 65, vétérinaire 320 / 250 / 254, chirurgie 223 / 169 / 157, pharmacologie 112 / 84 / 103, psychologie 255 / 175 / 179.
Longueur (échantillon de 600 résumés, tokenizer de CamemBERT-bio) : médiane 338 tokens, 95e centile 588, maximum 1 527 : environ 5 à 10 % des résumés dépassent les 508 positions de l'encodeur et sont tronqués tête et fin (règle du projet) ; en mots : médiane 225, 95e centile 374.

## Ce que le jeu ne représente pas, biais connus
Ce sont des résumés d'articles scientifiques, pas des comptes rendus cliniques ; les étiquettes de spécialité viennent du jeu et n'ont pas été ré-annotées (leur mécanisme de dérivation n'a pas été relu dans l'article publié : à confirmer). Résultat sur MorFITT = repère de méthode et d'état de l'art, **pas une preuve de transférabilité à des textes cliniques**.

## Contrôle des données personnelles
Recherche de motifs sur les 3 624 résumés : courriels 0, numéros de téléphone français 1, dates complètes jj/mm/aaaa 3, adresses web 1. Les cinq occurrences ont été relues le 06/10/2026 : un identifiant de registre d'essai cité comme numéro de téléphone (faux positif), deux dates de périodes d'étude dans une section Méthodes, un dosage « 20/5/5 mg » pris pour une date (faux positif), une adresse web d'un document cité ; aucune n'identifie une personne. Aucune donnée de patient réel : ce sont des résumés publiés.
