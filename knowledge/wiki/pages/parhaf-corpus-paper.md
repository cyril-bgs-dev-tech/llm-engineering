---
title: PARHAF, un corpus de comptes rendus cliniques français pour patients fictifs (Tannier et al., 2026)
category: Sources
summary: Article de présentation du corpus PARHAF (7 394 comptes rendus fictifs rédigés par 104 internes, scénarios tirés du SNDS), avec son protocole, ses limites déclarées et ce qu'il impose à notre classification du chapitre CIM-10
tags: [parhaf, corpus, cim-10, donnees-fictives, partages, source-arxiv]
sources: [parhaf-corpus-paper]
created: 2026-10-02
updated: 2026-10-02
---

# PARHAF, un corpus de comptes rendus cliniques français pour patients fictifs

**Source:** raw/arxiv-2603.20494.txt (texte extrait du PDF arXiv 2603.20494v1, 20 mars 2026 ; https://arxiv.org/abs/2603.20494)
**Date ingested:** 2026-10-02
**Type:** paper

Les numéros `L…` des notes renvoient aux lignes de `raw/arxiv-2603.20494.txt` : le texte a été extrait du PDF par `pypdf` et ses retours à la ligne suivent la mise en page, pas les phrases. Les chiffres de cette page sont ceux des auteurs, pas des résultats de notre projet : aucun `run_id` ne les concerne.

## Résumé

Le papier décrit la construction de PARHAF, un corpus de comptes rendus hospitaliers en français rédigés à la main par des médecins, sur des patients entièrement fictifs. Le problème de départ est le partage : la nature sensible des dossiers médicaux freine le développement du traitement automatique du langage clinique.[^1] Un texte désidentifié reste pseudonymisé et non anonymisé, donc non librement diffusable.[^2] Les auteurs font écrire de nouveaux comptes rendus à 104 internes de 18 spécialités, qui les rédigent puis les relisent entre pairs.[^3]

Pour que le corpus ne soit pas arbitraire, chaque rédacteur reçoit un scénario tiré des données de séjours du SNDS : groupes homogènes de malades, diagnostic principal CIM-10, âge, sexe, mode d'entrée et de sortie.[^4] Le tirage applique une racine carrée aux fréquences observées, plafonnée à une probabilité maximale correspondant à 0,1 %, pour limiter la domination des diagnostics les plus fréquents.[^5] Le corpus résultant n'est donc pas un échantillon fidèle de la prévalence réelle : les auteurs l'écrivent eux-mêmes.[^6]

Le jeu est publié sous CC BY 4.0 et Etalab 2.0 ; une partie est mise sous embargo pour évaluer plus tard sans contamination par les grands modèles.[^7][^8]

## Méthode

- **Scénarios.** Un cas clinique est défini par l'association d'un groupe homogène de malades, d'un sexe, d'une tranche d'âge et d'une classe de durée de séjour ; la base d'échantillonnage couvre environ 4 000 diagnostics principaux CIM-10 distincts.[^9] Les rédacteurs étoffent ensuite le cas à partir de ces éléments de base.[^10]
- **Deux composantes.** La composante principale vise 3 900 patients répartis sur de nombreuses spécialités ; la composante secondaire regroupe des patients choisis hors de la distribution principale pour des cas d'usage ciblés (codage CIM-10, oncologie, infectiologie).[^11] Le sous-ensemble « codage » rassemble des comptes rendus de chirurgie digestive, orthopédique, de traumatologie et d'urologie.[^12]
- **Allocation réelle.** Les rédacteurs avaient des compétences inégales selon les spécialités : la production n'a pas pu être répartie uniformément et toutes les spécialités n'ont pas pu être couvertes.[^13]
- **Formats.** Des modèles de document par type d'hospitalisation (médicale, chirurgicale, obstétrique, oncologie) ; un bloc de synthèse structuré est rempli à la fin de chaque compte rendu.[^14] L'usage d'IA générative est découragé pour ne pas biaiser contenu et style.[^15]
- **Validation.** Des validateurs humains contrôlent la cohérence clinique et le respect des consignes ; le taux de rejet est de 3,6 % des documents soumis.[^16] Après la vérification automatique, 120 documents ont reçu une correction manuelle, qui n'a pas modifié le contenu clinique sous-jacent.[^17] Un accord entre relecteurs sur le diagnostic principal n'est pas rapporté par les auteurs.[^18]

## Résultats chiffrés (description du corpus)

Le papier ne rapporte aucune performance de modèle ; ses chiffres décrivent le corpus.

- 7 394 comptes rendus pour 5 009 cas de patients.[^19]
- Diffusés : 6 185 documents pour 4 254 patients fictifs.[^20] Sous embargo : 755 patients et 1 209 documents.[^21] Les sommes concordent (4 254 + 755 = 5 009 ; 6 185 + 1 209 = 7 394).
- Chaque patient a entre 1 et 3 comptes rendus ; chaque document est un fichier de texte brut en français, sans balise ni étiquette.[^22][^23]
- Effort de production : 5 518 heures de travail effectif.[^24]

## Format des données utile à l'étiquetage

Chaque patient porte un `suggested_scenario`, décrit comme le « scénario de base suggéré au rédacteur », avec le code CIM-10 du diagnostic principal.[^25][^26] Le `structured_abstract` rempli par le rédacteur est qualifié par les auteurs de non relu et pouvant ne pas refléter le contenu réel du compte rendu.[^27] Les champs `author` et `reviewer` (trigrammes) et `pool` (partition, dont les cas d'usage) permettent de grouper les cas.[^28][^29]

## Limites déclarées par les auteurs

- Le corpus ne couvre pas toutes les spécialités ni toutes les variantes du texte clinique français.[^30] Les rédacteurs travaillant surtout à l'hôpital, le corpus porte principalement sur des situations hospitalières.[^31]
- Sa taille ne permet pas de couvrir tout le spectre des cas cliniques possibles.[^32]
- Les distributions ne reflètent pas la prévalence réelle, ce qui exclut l'inférence épidémiologique.[^6]
- Les résultats obtenus sur ce corpus ne peuvent pas être présentés comme preuve de performance ou de sécurité cliniques.[^33]
- Le corpus ne capture pas les contraintes opérationnelles réelles (pression de temps, charge, interruptions).[^34]

## Incohérences relevées dans le texte

Le résumé annonce quatre sous-ensembles spécialisés,[^35] l'introduction en annonce trois.[^36] Le détail de la section 2.3.2 en liste quatre (codage, biomarqueurs, réponse au traitement, infectiologie) ;[^37] ce wiki retient quatre, sans pouvoir trancher entre ces formulations.

## Ce que cela change pour notre projet

*Cette section est notre lecture ; ce sont des propositions, pas des affirmations de l'article.*

1. **L'étiquette n'est pas un codage médical.** Le diagnostic principal CIM-10 vient du scénario suggéré au rédacteur, tiré du SNDS, et non d'un codeur relisant le texte.[^25][^26] Le chapitre CIM-10 se déduit de ce code. La relecture humaine vérifie la cohérence clinique et le respect des consignes,[^16] pas un accord sur le code. Tout rapport doit donc dire « chapitre du scénario de référence », comme le prévoit [[regles-de-formulation](pages/regles-de-formulation.md)].
2. **Les fréquences de classes ne sont pas celles de la France.** Le tirage en racine carrée plafonnée aplatit les fréquences,[^5] et le jeu ne soutient pas d'inférence de prévalence.[^6] Pour un chapitre CIM-10, il faut mesurer la distribution des chapitres dans nos plis avant de choisir la métrique (macro-F1 plutôt qu'exactitude si les classes sont déséquilibrées) et ne rien dire de la prévalence.
3. **Le test officiel est embargoé.** Les 755 patients sous embargo servent à évaluer sans contamination.[^21][^8] Nous n'y avons pas accès : notre test scellé est interne, et toute comparaison distillation contre LoRA de référence se fait sur ce test interne, jamais présenté comme le test officiel.
4. **Fuite entre documents d'un même patient.** Un patient a jusqu'à 3 documents,[^22] et le champ `author` identifie le rédacteur ;[^28] avec 104 rédacteurs pour 5 009 cas,[^3][^19] chacun en écrit en moyenne environ 48 (calcul du wiki). Pour `leakage-guard`, nous proposons de découper par patient, et de mesurer en plus la sensibilité au rédacteur (découpe groupée par `author`), car le style d'un auteur peut s'apprendre.
5. **Piscines distinctes.** Le champ `pool` sépare la distribution principale des cas d'usage choisis hors distribution.[^29][^11] Nous proposons de rapporter séparément le chapitre CIM-10 sur la distribution principale et sur le sous-ensemble « codage » chirurgical.[^12]
6. **Allégations.** Aucun chiffre sur PARHAF ne doit être présenté comme performance clinique.[^33] La partie « RTX 5090 » n'est pas traitée par l'article : voir [[env-blackwell](pages/env-blackwell.md)].
7. **Texte fictif, style non réel.** Les auteurs notent que des textes traduits diffèrent sensiblement du texte clinique natif ;[^38] ils comparent PARHAF à d'autres proxies, pas à de vrais dossiers : l'écart entre PARHAF et un compte rendu réel n'est pas mesuré dans l'article.

## Entités et concepts

- Autres sources du lot : [[learning-rate-matters](pages/learning-rate-matters.md)] et [[causal-llm-classification-heads](pages/causal-llm-classification-heads.md)].
- Page de formulation liée : [[regles-de-formulation](pages/regles-de-formulation.md)].

## Relation aux autres pages du wiki

La fiche du jeu (`raw/parhaf-readme-60426cc.md`) liste des usages exclus, et l'article en formule d'équivalents en section 1.4 (non comparés ligne à ligne) ; [[regles-de-formulation](pages/regles-de-formulation.md)] en tire les phrases permises. Les licences concordent entre l'article et la fiche : CC BY 4.0 et Etalab 2.0.[^7][^39]

[^1]: [[parhaf-corpus-paper](pages/parhaf-corpus-paper.md)] §Abstract L18-19 — "is severely hampered by the sensitive nature of medical records"
[^2]: [[parhaf-corpus-paper](pages/parhaf-corpus-paper.md)] §1.1 L69-70 — "the resulting text is pseudonymized (directly identifying information has been removed) but not anonymized"
[^3]: [[parhaf-corpus-paper](pages/parhaf-corpus-paper.md)] §Abstract L27 — "residents across 18 specialties authored and peer-reviewed the reports"
[^4]: [[parhaf-corpus-paper](pages/parhaf-corpus-paper.md)] §2.2.1 L190-192 — "Scenarios were constructed by sampling observed distributions of Diagnosis-Related Groups (DRGs), principal diagnoses (ICD-10), age, sex"
[^5]: [[parhaf-corpus-paper](pages/parhaf-corpus-paper.md)] §2.3.1 L248-252 — "we applied a square-root transformation to the empirical frequencies" ; "(corresponding to a 0.1% sampling chance)"
[^6]: [[parhaf-corpus-paper](pages/parhaf-corpus-paper.md)] §1.4 L164-165 — "as its distributions do not reflect real-world prevalence"
[^7]: [[parhaf-corpus-paper](pages/parhaf-corpus-paper.md)] §6 L339 — "(CC BY 4.0) license and the Etalab 2.0 license. It was released on March 25, 2026."
[^8]: [[parhaf-corpus-paper](pages/parhaf-corpus-paper.md)] §1.2 L134-135 — "thereby limiting the risk of large language model contamination through prior exposure to the data"
[^9]: [[parhaf-corpus-paper](pages/parhaf-corpus-paper.md)] §2.3.1 L242-245 — "we defined clinical cases as the association of a DRG, sex, age group, and length-of-stay group" ; "These cases covered around 4,000 distinct ICD-10 primary diagnoses"
[^10]: [[parhaf-corpus-paper](pages/parhaf-corpus-paper.md)] §2.2.1 [synthesis] L197-200 — les rédacteurs sont encouragés à développer les détails du cas à partir des éléments de base, en gardant la cohérence médicale
[^11]: [[parhaf-corpus-paper](pages/parhaf-corpus-paper.md)] §2.3 [synthesis] L232-236 — composante principale (n = 3 900) et composante secondaire hors distribution pour le codage CIM-10, l'oncologie et l'infectiologie
[^12]: [[parhaf-corpus-paper](pages/parhaf-corpus-paper.md)] §2.3.2 L269-270 — "Surgery reports from digestive surgery, orthopedic surgery, traumatology, and urology"
[^13]: [[parhaf-corpus-paper](pages/parhaf-corpus-paper.md)] §2.3.1 L259-260 — "not all specialties could be covered"
[^14]: [[parhaf-corpus-paper](pages/parhaf-corpus-paper.md)] §2.2.2 [synthesis] L201-227 — modèles par type d'hospitalisation et section de synthèse structurée en fin de compte rendu
[^15]: [[parhaf-corpus-paper](pages/parhaf-corpus-paper.md)] §2.2.2 L228 — "The use of generative artificial intelligence tools was discouraged"
[^16]: [[parhaf-corpus-paper](pages/parhaf-corpus-paper.md)] §5 L358-360 — "Human validators were responsible for content quality control, assessing clinical coherence and adherence to the instructions." ; "a rejection rate of 3.6% of submitted documents"
[^17]: [[parhaf-corpus-paper](pages/parhaf-corpus-paper.md)] §5 L366-369 — "Following automated validation, 120 documents required manual correction." ; "No corrections altered the underlying clinical content"
[^18]: [[parhaf-corpus-paper](pages/parhaf-corpus-paper.md)] §5 [synthesis] L349-370 — la section de validation technique décrit la formation des contributeurs, la relecture humaine, les contrôles automatiques et les corrections manuelles ; aucun accord entre relecteurs sur le diagnostic n'y figure
[^19]: [[parhaf-corpus-paper](pages/parhaf-corpus-paper.md)] §Abstract L29 — "The corpus contains 7,394 clinical reports covering 5,009 patient cases"
[^20]: [[parhaf-corpus-paper](pages/parhaf-corpus-paper.md)] §1.2 L132-133 — "We release 6,185 documents corresponding to 4,254 fictitious patients under an open-source CC-BY license"
[^21]: [[parhaf-corpus-paper](pages/parhaf-corpus-paper.md)] §4 L345-346 — "keep 755 patients (1,209 documents) under embargo"
[^22]: [[parhaf-corpus-paper](pages/parhaf-corpus-paper.md)] Table 1 L460 — "documents[] (between 1 and 3 patient reports)"
[^23]: [[parhaf-corpus-paper](pages/parhaf-corpus-paper.md)] §3 L328-329 — "raw, unannotated plain text in French, with no markup, labels, or structural tags applied"
[^24]: [[parhaf-corpus-paper](pages/parhaf-corpus-paper.md)] §2.4 L319 — "5,518 hours of effective work"
[^25]: [[parhaf-corpus-paper](pages/parhaf-corpus-paper.md)] Table 1 L443 — "Basic scenario suggested to the report author"
[^26]: [[parhaf-corpus-paper](pages/parhaf-corpus-paper.md)] Table 1 L457 — "primary_diagnosis.codestring ICD10 code"
[^27]: [[parhaf-corpus-paper](pages/parhaf-corpus-paper.md)] Table 1 L445-447 — "Optional and uncurated abstract filled by the author. May not reflect the real content of the report."
[^28]: [[parhaf-corpus-paper](pages/parhaf-corpus-paper.md)] Table 1 L439 — "Author trigram"
[^29]: [[parhaf-corpus-paper](pages/parhaf-corpus-paper.md)] Table 1 L441-442 — "Dataset partition. Some patients are part of specific use cases"
[^30]: [[parhaf-corpus-paper](pages/parhaf-corpus-paper.md)] §1.4 L153-154 — "the corpus does not cover all specialties and variations of French clinical text"
[^31]: [[parhaf-corpus-paper](pages/parhaf-corpus-paper.md)] §2.2 L182-183 — "the resulting corpus of documents focused predominantly on hospital-based clinical situations"
[^32]: [[parhaf-corpus-paper](pages/parhaf-corpus-paper.md)] §2.3 L233-234 — "the target size does not allow full coverage of the spectrum of possible clinical cases"
[^33]: [[parhaf-corpus-paper](pages/parhaf-corpus-paper.md)] §1.4 L161-162 — "results obtained on this corpus cannot be presented as evidence of clinical performance or safety"
[^34]: [[parhaf-corpus-paper](pages/parhaf-corpus-paper.md)] §1.4 L167-168 — "does not capture the operational constraints of real clinical environments"
[^35]: [[parhaf-corpus-paper](pages/parhaf-corpus-paper.md)] §Abstract L31-32 — "and four specialized subsets"
[^36]: [[parhaf-corpus-paper](pages/parhaf-corpus-paper.md)] §1.2 L128 — "We further provide three specialized subsets"
[^37]: [[parhaf-corpus-paper](pages/parhaf-corpus-paper.md)] §2.3.2 [synthesis] L267-280 — quatre ensembles : codage, biomarqueurs en oncologie, réponse au traitement en oncologie, infectiologie
[^38]: [[parhaf-corpus-paper](pages/parhaf-corpus-paper.md)] §1.1 L83-85 — "cultural and health system differences make the resulting text sensibly different from native clinical text"
[^39]: raw/parhaf-readme-60426cc.md L547-548 — "- CC BY 4.0"
