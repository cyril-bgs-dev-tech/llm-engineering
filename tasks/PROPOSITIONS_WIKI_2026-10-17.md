# Propositions de mise à jour du wiki (17/10/2026), en attente de l'accord de Cyril

Règle du projet : chaque page du wiki se modifie avec ton accord, page par page (skill `wiki-update`). Rien n'a été écrit dans `knowledge/`. Pour chaque proposition : texte actuel, texte proposé, raison, source. Une réponse du type « wiki : 1 oui, 2 oui » suffit.

## 1. `knowledge/wiki/pages/etat-par-composante.md`, section « Efficience et déploiement »

**Actuel (fin du paragraphe)** : « … Pas 8 : compression jamais réussie, G servi par un banc seulement.[^12][^13] »

**Proposé** : « … Pas 8 à cette date : compression jamais réussie, G servi par un banc seulement.[^12][^13] **Mise à jour du 17/10/2026 (note 7 vers 8, estimation à plus ou moins 1)** : la cascade E puis G est retenue par sa fiche préenregistrée (cascade moins G −0,10 point [−0,23 ; +0,02] par blocs d'auteurs, 82,3 % des patients sans le LoRA, seuil 0,6 choisi hors pli dans les cinq plis) et G est servi par HTTP avec cette cascade : latence moyenne attendue de 38,4 ms (chemins mesurés par HTTP, E 25,3 ms et G 87,7 ms au p50, pondérés par la part hors pli) contre 97,4 ms en moyenne pour G complet. Pas 9 : énergie de la cascade non mesurée, aucune image GPU, aucune charge prolongée, et l'entraînement reste 7,9 fois celui de E.[^14][^15] »

Notes à ajouter : « [^14]: run `20261017-012416-cascade-e-puis-g` [synthesis] — analyse hors ligne de la cascade E puis G, fiche `2026-10-17-cascade-e-puis-g` » et « [^15]: run `20261017-015754-service-g-cascade` [synthesis] — service HTTP de G en cascade, fiche `2026-10-17-service-g-cascade` ». Frontmatter : `updated: 2026-10-17`.

**Raison** : la note d'efficience a changé (N32) sur deux preuves nouvelles ; la page dit encore « G servi par un banc seulement ».
**Source** : `RESULTATS.md` (sections RM-60 et service), `docs/presentation/PREUVES.md` lignes 67 et 68, runs cités.

## 2. `knowledge/wiki/pages/incidents-et-audits-externes.md`, section « Instabilité de calcul de la machine (07/10/2026) »

**Actuel (dernière phrase)** : « … la vérification du BIOS et d'un test de mémoire est demandée à Cyril (Q26). Conséquence pour les chiffres : double exécution (`agree_twice`) des chiffres publiés. »

**Proposé** : « … la vérification du BIOS et d'un test de mémoire est demandée à Cyril (Q26). Conséquence pour les chiffres : double exécution (`agree_twice`) des chiffres publiés. **Après la mise à jour du BIOS (17/10/2026)** : le même test, préenregistré avant le flash, donne 10 pannes sur 46 essais avant comme après (BIOS à jour avec ses réglages par défaut ; Fisher p = 0,60 ; aucun résultat divergent sur 72 essais réussis) : verdict écrit d'avance « toujours instable » ; le microcode n'est pas lisible depuis WSL. Conséquence appliquée : aucun calcul long publié (RM-61 et RM-62 préparés, non lancés) ; vérifications restantes côté Windows : microcode, journal WHEA-Logger, test de charge natif, test de mémoire.[^8] »

Note à ajouter : « [^8]: runs `20261016-230229-verification-machine-bios-avant` et `20261017-012310-verification-machine-bios-apres` [synthesis] — fiche `2026-10-17-verification-machine-apres-bios` ». Frontmatter : `updated: 2026-10-17` (vérifier le prochain numéro de note libre au moment d'écrire).

**Raison** : la page s'arrête au 07/10 ; le résultat négatif de RM-64 change ce qu'elle doit dire de la cause et de la suite.
**Source** : `RESULTATS.md` (section RM-64), `tasks/QUESTIONS_POUR_CYRIL.md` (Q26, mise à jour du 17/10), runs cités.

## Effets en aval à vérifier au moment d'écrire

- `wiki/overview.md` : vérifier s'il cite la note d'efficience (7) ou « G servi par un banc ».
- `wiki/index.md` : à régénérer (`python bin/generate-index.py`), jamais à la main ; `wiki/log.md` : une entrée `update`.

## 3. Lint du wiki (17/10/2026, phase déterministe seulement, rien écrit dans `knowledge/`)

`knowledge/bin/lint-mechanical.py` : **0 lien cassé, 0 frontmatter manquant, 0 collision de slug, 0 affirmation datée périmée, 0 concept manquant ; 4 pages orphelines** (aucun lien entrant) : `conclusions-corrigees-recette-et-tirage`, `contrats-des-modules-du-chemin-court`, `etat-par-composante`, `incidents-et-audits-externes`. Recherche ciblée d'affirmations rendues périmées par la nuit (notes, BIOS, Q26, service de G, test scellé) : seulement dans les deux pages des propositions 1 et 2.

**Proposé** (même règle : accord page par page) : ajouter dans `knowledge/wiki/overview.md` un lien vers chacune des quatre pages orphelines, à l'endroit où l'aperçu parle de leur sujet (état par composante, incidents et audits, conclusions corrigées, contrats des modules). **Non fait** : la phase 2 du lint (contradictions entre pages par groupes de tags) demande des sous-agents, que je ne lance pas sans ta demande ; à faire en séance si tu le souhaites.

## 4. `knowledge/wiki/pages/etat-par-composante.md`, sections « Efficience et déploiement » et « Sûreté, conformité, honnêteté » (P5-08 et P5-11, ajout du 17/10/2026)

**Actuel (fin de « Efficience et déploiement », après la proposition 1 si elle est acceptée)** : « … et l'entraînement reste 7,9 fois celui de E.[^14][^15] »

**Proposé (phrase ajoutée à la suite)** : « **Surveillance (17/10/2026, note inchangée à 8)** : seuils de dérive mesurés par simulation en développement (alerte sur la prévalence des chapitres prédits, lots de 100 patients, seuil 0,207) ; un changement d'auteurs coûte 5,17 points de macro-F1 à un substitut de E sans qu'aucun signal sans étiquette ne le voie : il faut un échantillon étiqueté d'environ 1 000 patients ; les deux services exposent la surveillance (`GET /drift`), image de service non reconstruite. Détail : [[surveillance-de-derive](pages/surveillance-de-derive.md)].[^16][^17] »

**Actuel (« Sûreté, conformité, honnêteté »)** : « Résultats négatifs publiés, claim-gate, carte de modèle v3 mise à jour, gabarit de rapport, journal des accès au test scellé.[^6] »

**Proposé** : « Résultats négatifs publiés, claim-gate, carte de modèle v3 mise à jour, gabarit de rapport, journal des accès au test scellé.[^6] Démo locale (17/10/2026) conforme à [[regles-de-formulation](pages/regles-de-formulation.md)] : boucle locale seulement, bannière « données fictives, recherche seulement », exemples fictifs choisis dans une liste, aucune saisie libre.[^18] »

Notes à ajouter (numéros à vérifier au moment d'écrire, selon le sort de la proposition 1) : « [^16]: run `20261017-090325-simulation-derive` [synthesis] — simulation de dérive, fiche `2026-10-17-simulation-derive`, `docs/SURVEILLANCE_DERIVE.md` », « [^17]: run `20261017-091931-taille-echantillon-etiquete` [synthesis] — taille de l'échantillon étiqueté, fiche `2026-10-17-taille-echantillon-etiquete` », « [^18]: scripts/demo_locale.py [synthesis] — démo locale P5-11 et ses tests `tests/test_demo_locale.py` ». Frontmatter : `updated: 2026-10-17`.

**Raison** : deux livrables du 17/10 (P5-08 mesuré et branché, P5-11) ne figurent pas dans la page ; la note ne change pas (N32), ce que la phrase dit.
**Source** : `RESULTATS.md` (sections « Simulation de dérive » et « Taille de l'échantillon étiqueté »), `docs/presentation/PREUVES.md` lignes 70 à 72, `docs/SURVEILLANCE_DERIVE.md`.

## 5. `knowledge/wiki/pages/regles-de-formulation.md`, ligne « Démo » du tableau

**Actuel (colonne « Permis »)** : « Locale, sur textes fictifs du corpus ou synthétiques, avec la bannière « données fictives, recherche seulement » »

**Proposé** : « Locale, sur textes fictifs du corpus ou synthétiques, avec la bannière « données fictives, recherche seulement » ; appliquée par `scripts/demo_locale.py` (17/10/2026 : adresse refusée hors de la boucle locale, exemples fictifs choisis dans une liste, aucune saisie libre, rien de journalisé)[^4] »

Note à ajouter : « [^4]: scripts/demo_locale.py [synthesis] — démo locale P5-11 ; les règles de cette ligne sont vérifiées par `tests/test_demo_locale.py` ». Frontmatter : `updated: 2026-10-17`.

**Raison** : la page dit ce qui est permis ; elle peut dire où la règle est appliquée et testée, pour qu'un relecteur la vérifie.
**Source** : `scripts/demo_locale.py`, `tests/test_demo_locale.py`.

## 6. Nouvelle page proposée : `knowledge/wiki/pages/surveillance-de-derive.md` (catégorie Analyses)

**Proposé (page entière)** :

```markdown
---
title: Surveillance de dérive du service, seuils mesurés et limites
category: Analyses
summary: Quels signaux sans étiquette détectent une dérive qui dégrade le classement, à quel seuil, et pourquoi un changement d'auteurs exige un échantillon étiqueté d'environ 1 000 patients
tags: [deploiement, derive, surveillance, efficience]
sources: [resultats]
created: 2026-10-17
updated: 2026-10-17
---

# Surveillance de dérive du service, seuils mesurés et limites

Trois signaux se calculent sans étiquette sur un lot de patients reçus : la baisse de la part servie par E seul, la variation totale de la prévalence des chapitres prédits et l'écart des longueurs de texte. Leurs seuils (99e centile de 2 000 lots tirés des prédictions hors pli) dépendent de la taille du lot : un seuil fixe donne 30 % de fausses alertes sur 100 patients.[^1]

Sur trois dérives simulées en développement, la prévalence des chapitres prédits détecte un afflux d'un chapitre dès 100 patients, et la longueur un changement de format ; mais **un changement d'auteurs**, le cas d'un nouvel hôpital, coûte 5,17 points de macro-F1 à un substitut de E sans qu'aucun signal ne le voie, même sur 500 patients.[^1] Seule la qualité mesurée sur un échantillon étiqueté le détecte : environ 1 000 patients en macro-F1 pour une puissance de 0,80 ; une dérive partielle (40 % de nouveaux auteurs) reste presque invisible.[^2]

Conséquence pour un déploiement : validation locale avant toute mise en service dans un nouvel hôpital ; alerte automatique sur la prévalence prédite ; échantillon étiqueté périodique pour la qualité. Lien avec l'état des composantes : [[etat-par-composante](pages/etat-par-composante.md)].

[^1]: run `20261017-090325-simulation-derive` [synthesis] — fiche `2026-10-17-simulation-derive` ; détail et fiches d'intervention dans `docs/SURVEILLANCE_DERIVE.md`
[^2]: run `20261017-091931-taille-echantillon-etiquete` [synthesis] — fiche `2026-10-17-taille-echantillon-etiquete`
```

**Raison** : savoir durable (méthode, résultat négatif, conséquence pour un déploiement) que le wiki n'a pas ; la page reçoit un lien entrant par la proposition 4 (pas d'orpheline).
**Source** : `RESULTATS.md`, `docs/SURVEILLANCE_DERIVE.md`, runs cités. **À vérifier au moment d'écrire** : forme de `sources:` attendue par `SCHEMA.md` pour une analyse appuyée sur `RESULTATS.md`, puis `python bin/generate-index.py` et une entrée `update` dans `wiki/log.md`.

## 7. `knowledge/wiki/pages/etat-par-composante.md`, section « Performance » (RM-61, ajout du 17/10/2026)

**Actuel (fin de la section)** : « … la règle de sélection retient l'ensemble LoRA + encodeur + TF-IDF (0,7799).[^8][^10] »

**Proposé (phrase ajoutée à la suite)** : « **Repère public (17/10/2026)** : transposé sans aucun réglage sur MorFITT, ce système gelé atteint un F1 pondéré de 72,30 [70,15 ; 74,35] sur le test public, contre 71,95 pour le meilleur système publié : au niveau, pas au-dessus (verdict « dans la bande » écrit d'avance ; un ensemble de sept modèles face à des modèles seuls). Deux entraînements du LoRA à la même graine ne donnent pas les mêmes prédictions (85,4 % des résumés aux mêmes étiquettes) : l'intervalle ne contient pas la variance d'entraînement.[^19] »

Note à ajouter (numéro à vérifier au moment d'écrire) : « [^19]: run `20261017-113948-morfitt-g-gele` [synthesis] — G gelé transposé sur MorFITT, fiche `2026-10-17-g-gele-morfitt` ». Frontmatter : `updated: 2026-10-17`.

**Raison** : premier repère public mesuré sur le système final lui-même (jusqu'ici, seul le mélange encodeurs + TF-IDF l'était) ; la note de performance ne change pas (N32), ce que la phrase dit.
**Source** : `RESULTATS.md` (section RM-61), `docs/presentation/PREUVES.md` ligne 76.
