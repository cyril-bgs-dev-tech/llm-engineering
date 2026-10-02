---
name: dataset-intake
description: Fait entrer un jeu de données dans le projet avec sa licence, sa provenance et sa fiche. À utiliser avant de télécharger ou d'utiliser un jeu (DrBenchmark, corpus externe, données générées), en changeant de version d'un jeu, ou quand une donnée pourrait concerner un vrai patient.
---

# Entrée d'un jeu de données

Projet de santé : la provenance et le droit d'usage passent avant le score. Aucune donnée de patient réel n'entre dans ce projet ; tout est public, synthétique ou généré, et l'est de façon vérifiable.

## Étapes

1. **Licence** : lire la licence à sa source (page du jeu, dépôt, article), pas un résumé. Consigner le texte exact de la licence et l'URL. Un jeu sous accord d'usage (DUA, ex. CAS et ESSAI) ou sous licence non commerciale (ex. E3C, CC BY-NC) est signalé à Cyril avant téléchargement, avec ce que la licence permet et interdit.
2. **Téléchargement** par script versionné dans `data/scripts/`, jamais à la main ; les données restent hors Git (`data/` ignoré), seules les empreintes SHA-256 sont versionnées.
3. **Fiche du jeu** `data/cards/<jeu>.md` : source, licence, version ou date, taille, découpage officiel, distribution des classes, longueur des textes (médiane, 95e centile, en tokens du tokenizer de l'élève), langue, biais connus, et ce que le jeu ne représente pas (un cas clinique publié n'est pas un compte rendu hospitalier).
4. **Contrôle des données personnelles** : recherche de motifs (noms propres hors termes médicaux, dates complètes, numéros, adresses) sur un échantillon ; tout résultat douteux est signalé, pas filtré en silence.
5. **Contrat de cible** `task_specs/<task_id>.yaml` (section 4 du plan V6) : type (`multiclass`, `multilabel`, `pair_ordinal`), entrées, et pour chaque classe un identifiant stable, un nom en clair et une définition opérationnelle avec ses exclusions. Les noms viennent de la nomenclature officielle quand elle existe (CIM-10, spécialités) ; une classe sans définition bloque l'entrée du jeu.
6. **Wiki** : une page source par jeu via `wiki-ingest`, qui cite la fiche et le contrat.

**Terminé quand** la licence est consignée avec sa source, le script de téléchargement rejoue l'empreinte attendue, la fiche et le contrat de cible sont complets, et le contrôle des données personnelles est documenté.
