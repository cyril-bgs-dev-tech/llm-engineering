# Index des préenregistrements

Chaque ligne fige un document par son empreinte SHA-256, calculée **avant** la première mesure qui en dépend. Le dépôt Git n'a pas encore de commit ; l'empreinte tient lieu d'horodatage de gel.

| Date | Objet | Fichier | SHA-256 | Avant quelle mesure |
|---|---|---|---|---|
| 2026-10-02 | Sections 1 à 3 de PROTOCOLE.md : unité d'entrée, classes rares, règles de split et seuil du raccourci d'auteur | `PROTOCOLE.md` (état entier du fichier à cette date) | `61c646e2c76c17dbf46ce91548cac4cc5093f82afde0c34a51a2fbe282d8a526` | P0-28, P0-29 et P0-30 |
| 2026-10-02 | Section 4 de PROTOCOLE.md : seuil de quasi-doublon 0,8 et règle de split par groupes (ajoutée après la mesure des quasi-doublons, découpage régénéré) | `PROTOCOLE.md` (état entier du fichier à cette date) | `3d3cefb06129bf04471d17b63fb3bacfed0467050c7c1e912ba948b57fa9738d` | P1 et toute évaluation de modèle (l'empreinte précédente reste celle des sections 1 à 3) |
