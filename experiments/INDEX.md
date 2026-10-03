# Index des préenregistrements

Chaque ligne fige un document par son empreinte SHA-256, calculée **avant** la première mesure qui en dépend. Le dépôt Git n'a pas encore de commit ; l'empreinte tient lieu d'horodatage de gel.

| Date | Objet | Fichier | SHA-256 | Avant quelle mesure |
|---|---|---|---|---|
| 2026-10-02 | Sections 1 à 3 de PROTOCOLE.md : unité d'entrée, classes rares, règles de split et seuil du raccourci d'auteur | `PROTOCOLE.md` (état entier du fichier à cette date) | `61c646e2c76c17dbf46ce91548cac4cc5093f82afde0c34a51a2fbe282d8a526` | P0-28, P0-29 et P0-30 |
| 2026-10-02 | Section 4 de PROTOCOLE.md : seuil de quasi-doublon 0,8 et règle de split par groupes (ajoutée après la mesure des quasi-doublons, découpage régénéré) | `PROTOCOLE.md` (état entier du fichier à cette date) | `3d3cefb06129bf04471d17b63fb3bacfed0467050c7c1e912ba948b57fa9738d` | P1 et toute évaluation de modèle (l'empreinte précédente reste celle des sections 1 à 3) |
| 2026-10-03 | PROTOCOLE.md gelé (sections 1 à 6 ; P0-46) après trois relectures adversariales | `experiments/frozen/PROTOCOLE-2026-10-03.md` | `aba89842a1c7da2cd500620cf7fdf47f7a345f3b2279cf87d50c148f07dac3a8` | P1-02 et tout run de P1 |
| 2026-10-03 | Instantané de `docs/decisions/ADR-004-cap-du-premier-cycle.md` au gel du protocole | `experiments/frozen/ADR-004-cap-du-premier-cycle.md` | `3af160becbaece629b9193f03179100b76ea686a1894170720493e5dd7b85deb` | P1-02 et tout run de P1 |
| 2026-10-03 | Instantané de `docs/decisions/ADR-007-estimand-et-regle-de-decision.md` au gel du protocole | `experiments/frozen/ADR-007-estimand-et-regle-de-decision.md` | `5519da5639f86efcdc4ebbb15b0185da3e9f829bb782a0336011c21805d42646` | P1-02 et tout run de P1 |
| 2026-10-03 | Instantané de `docs/decisions/ADR-009-preselection-de-l-eleve.md` au gel du protocole | `experiments/frozen/ADR-009-preselection-de-l-eleve.md` | `e2660fc990b2d3af3505a4d76d79d31fe4f77c021ae72a2c2b3344b49392fb28` | P1-02 et tout run de P1 |
| 2026-10-03 | Instantané de `docs/decisions/ADR-010-ecarts-du-protocole-au-plan-v6.md` au gel du protocole | `experiments/frozen/ADR-010-ecarts-du-protocole-au-plan-v6.md` | `21190acfacbc84d0ee03bdd3e61a08be8c78034e718834cba7c4c29b0adb245b` | P1-02 et tout run de P1 |
| 2026-10-03 | Instantané de `task_specs/parhaf_cim10_chapter.yaml` au gel du protocole | `experiments/frozen/parhaf_cim10_chapter.yaml` | `90671bf49a69701b9b25238eb6a762b199567421517aa085000989b88479dedc` | P1-02 et tout run de P1 |
| 2026-10-03 | Instantané de `src/llmft/metrics.py` au gel du protocole | `experiments/frozen/metrics.py` | `65c9fd8208082d03cc76857a2f015d1ab1b72dda46a264706aae2558ee0c25b7` | P1-02 et tout run de P1 |
| 2026-10-03 | Instantané de `results/measures/splits_summary.json` au gel du protocole | `experiments/frozen/splits_summary.json` | `edcbfb76b09cb2a6da946b4de2d8781c2b1a62e2ccf58612f3f76e5e21e225b2` | P1-02 et tout run de P1 |
| 2026-10-03 | Instantané de `data/splits/parhaf_cim10_chapter.sha256` au gel du protocole | `experiments/frozen/parhaf_cim10_chapter.sha256` | `aa28252571d63b30acf7e037f10a3df94ee15bfddaaaaf112a817056a13475dc` | P1-02 et tout run de P1 |
| 2026-10-03 | Fiche préenregistrée TF-IDF et régression logistique (P1-04 doctype, P1-06 chapitre) | `experiments/2026-10-03-p1-04-06-tfidf.md` | `59fd6b0c737ca4766a22fa6aa1ee86a541a251c2a05bf25f857be19b7e494f90` | P1-04 et P1-06 (premier run TF-IDF) |
