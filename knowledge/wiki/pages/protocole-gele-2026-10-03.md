---
title: Protocole gelé du 03/10/2026 (P0-46) : empreintes et périmètre
category: Méthodes
summary: Date de gel de PROTOCOLE.md, périmètre des neuf instantanés conservés dans experiments/frozen et leurs empreintes SHA-256, règles de modification après gel
tags: [protocole, gel, empreinte, p0-46, preregistration]
sources: [protocole-gele-2026-10-03]
created: 2026-10-03
updated: 2026-10-03
---

# Protocole gelé du 03/10/2026 (P0-46) : empreintes et périmètre

Cette page est le **témoin daté** du gel de `PROTOCOLE.md` exigé par P0-46 : l'empreinte y est consignée en plus de `experiments/INDEX.md`. Elle ne décrit pas les règles (elles sont dans l'instantané) ; elle dit **ce qui est gelé, quand, et comment le vérifier**.[^1]

## Ce qui est gelé

Le 03/10/2026, après trois relectures adversariales en contexte neuf (54 constats classés dans `tasks/JOURNAL.md`) et huit confirmations de Cyril (C1 à C8), neuf fichiers ont été copiés dans `experiments/frozen/` avec leur empreinte SHA-256 :[^2]

| Instantané | SHA-256 |
|---|---|
| `PROTOCOLE-2026-10-03.md` | `aba89842a1c7da2cd500620cf7fdf47f7a345f3b2279cf87d50c148f07dac3a8` |
| `ADR-004-cap-du-premier-cycle.md` | `3af160becbaece629b9193f03179100b76ea686a1894170720493e5dd7b85deb` |
| `ADR-007-estimand-et-regle-de-decision.md` | `5519da5639f86efcdc4ebbb15b0185da3e9f829bb782a0336011c21805d42646` |
| `ADR-009-preselection-de-l-eleve.md` | `e2660fc990b2d3af3505a4d76d79d31fe4f77c021ae72a2c2b3344b49392fb28` |
| `ADR-010-ecarts-du-protocole-au-plan-v6.md` | `21190acfacbc84d0ee03bdd3e61a08be8c78034e718834cba7c4c29b0adb245b` |
| `parhaf_cim10_chapter.yaml` | `90671bf49a69701b9b25238eb6a762b199567421517aa085000989b88479dedc` |
| `metrics.py` | `65c9fd8208082d03cc76857a2f015d1ab1b72dda46a264706aae2558ee0c25b7` |
| `splits_summary.json` | `edcbfb76b09cb2a6da946b4de2d8781c2b1a62e2ccf58612f3f76e5e21e225b2` |
| `parhaf_cim10_chapter.sha256` | `aa28252571d63b30acf7e037f10a3df94ee15bfddaaaaf112a817056a13475dc` |

**L'instantané fait foi** : le fichier vivant `PROTOCOLE.md` ne peut recevoir que des errata (`experiments/ERRATA-PROTOCOLE.md`), jamais une modification de règle, de valeur, de seuil, de graine ni d'effectif de strate. Une nouvelle version cite l'ancienne, dit pourquoi, ne dépend d'aucun résultat vu et reçoit sa propre empreinte ; la section 5 (budget) peut être révisée seule après la mesure pilote RM-16, par décision de Cyril.[^3]

## Vérification

`python3 scripts/check_frozen.py` (lancé par `make check`) échoue si l'empreinte d'un instantané diffère de l'index, si une ligne d'instantané est illisible, ou si l'une des neuf entrées obligatoires manque.[^4]

## Limites dites

- Les corrections faites **après la troisième relecture** n'ont été relues que par leur auteur.
- Les empreintes des sections 1 à 4 figées les 01 et 02/10/2026 portent sur des états du fichier dont aucun instantané n'existe : elles ne prouvent rien sur ces sections, d'où la confirmation C4 de Cyril le 03/10/2026.
- Le gel n'est pas un horodatage Git : le dépôt peut recevoir un tag sur demande de Cyril.
- Plusieurs règles gelées n'ont pas encore leur code (classement des échecs par le registre, `sealed.py` à deux temps, répétition générale du temps B) : elles sont portées par les tâches P1-19 et RM-20.

- Repère externe sur la macro-F1 (moyenne arithmétique des F1 par classe, classes absentes du test, plis stratifiés) : [[automated-medical-coding-mimic-replicability](pages/automated-medical-coding-mimic-replicability.md)] ; intervalles asymptotiques du MCC multiclasse apparié (grands échantillons) : [[mcc-multiclass-statistical-inference](pages/mcc-multiclass-statistical-inference.md)] ; scoring à crédit partiel sur une taxonomie (pas validé sur du texte clinique) : [[hierarchical-scoring-classifier-error-impact](pages/hierarchical-scoring-classifier-error-impact.md)].

[^1]: experiments/INDEX.md [synthesis] — lignes du 2026-10-03 : un instantané par fichier, empreinte et date
[^2]: experiments/frozen [synthesis] — neuf fichiers copiés au gel
[^3]: experiments/frozen/PROTOCOLE-2026-10-03.md §6.10 [synthesis] — règles de gel 1 à 5
[^4]: src/llmft/frozen.py [synthesis] — contrôle de l'index
