---
title: The Limited Impact of Medical Adaptation of LLMs and VLMs (Jeong et al., 2025)
category: Sources
summary: Comparaison tête à tête de dix LLM médicaux et deux VLM contre leurs modèles de base : peu ou pas de gain une fois les invites réglées par modèle et l'incertitude prise en compte, d'où le criblage ouvert aux généralistes
tags: [medgemma, adaptation-medicale, comparaison-equitable, bootstrap, source-arxiv]
sources: [limited-impact-medical-adaptation]
created: 2026-10-02
updated: 2026-10-02
---

# The Limited Impact of Medical Adaptation of LLMs and VLMs (Jeong et al., 2025)

**Source:** raw/arxiv-2411.08870.txt (texte extrait du PDF arXiv 2411.08870v3, 28 juin 2025, par `pypdf` ; https://arxiv.org/abs/2411.08870, licence CC BY 4.0)
**Date ingested:** 2026-10-02
**Type:** paper

Les numéros `L…` des notes renvoient aux lignes de `raw/arxiv-2411.08870.txt` (retours à la ligne selon la mise en page ; l'extraction colle parfois des mots). Les chiffres sont ceux des auteurs, pas des résultats de notre projet : aucun `run_id` ne les concerne. Les tâches du papier sont des questions-réponses fermées (connaissances médicales, notes cliniques, images), pas de la classification de documents (voir « Portée »).

## Résumé

Les auteurs comparent dix LLM « médicaux » (obtenus par pré-entraînement adaptatif au domaine, DAPT) et deux VLM à leur modèle de base exact, sur 22 jeux de questions textuelles (dont 8 fondés sur des notes cliniques) et 8 jeux visuels.[^1] Les deux modèles d'une paire ne diffèrent que par l'adaptation médicale ; l'invite et les exemples sont choisis séparément pour chaque modèle, et l'incertitude est évaluée par bootstrap.[^2][^3]

Résultat : tous les VLM médicaux et presque tous les LLM médicaux n'améliorent pas de façon constante leur modèle de base, en invite zéro ou quelques exemples comme en fine-tuning supervisé.[^4] Sur les questions fondées sur des notes cliniques avec trois exemples, les modèles médicaux gagnent dans 26,7 % des cas, font égalité dans 16,7 % et perdent dans 56,7 %.[^5] Après fine-tuning, les LLM médicaux progressent de façon significative mais marginale (1,6 point d'exactitude en moyenne) sur les questions de connaissances, pas sur celles issues de notes cliniques où ils sont presque indiscernables de leur base.[^6][^7]

La méthode est aussi un modèle de rigueur : un réglage d'invite propre à chaque modèle, un bootstrap sur les questions du test à 10 000 rééchantillonnages, et le constat qu'une comparaison à invite unique, sans test, surestime le bénéfice de l'adaptation.[^3][^8]

## Points à retenir

- Une adaptation médicale annoncée gagnante doit se comparer à **son** modèle de base, réglé séparément et avec un intervalle de confiance.[^4][^8]
- Le gain apparent disparaît largement quand on règle l'invite de chaque modèle et qu'on tient compte de l'incertitude.[^8]
- Sur des notes cliniques réelles, après fine-tuning, médical et général se valent presque.[^7]

## Portée et limites (dites par les auteurs et par nous)

- Les auteurs se limitent à des questions-réponses fermées et reconnaissent que d'autres tâches cliniques pourraient donner un autre résultat.[^9] Ils n'évaluent pas le fine-tuning complet, seulement des adaptateurs LoRA (rang 16, 32 ou 64 ; taux 1e-5 à 2e-4 ; 10 époques au plus, arrêt anticipé sur la perte de validation).[^10][^11] Leur conclusion peut changer avec un fine-tuning complet.[^10]
- Ils ne corrigent pas les comparaisons multiples, ce qui rendrait moins de différences significatives.[^3]
- **Aucune de ces tâches n'est de la classification de documents cliniques français.** Le papier ne dit rien de MedGemma (modèle postérieur à l'étude), ni du français.

## Conséquence pour ce projet

*Proposition, non issue de la source.* L'étude justifie de **ne pas écarter les généralistes** au criblage des élèves (ADR-009, ADR-001) et de **comparer tout modèle médical à son modèle de base** avec la même discipline de réglage et un intervalle apparié ; elle ne démontre pas qu'un modèle médical est inutile sur nos données. Un modèle médical reste un candidat à tester (MedGemma : voir `tasks/QUESTIONS_POUR_CYRIL.md`, Q6).

## Pages liées

- [[learning-rate-matters](pages/learning-rate-matters.md)] : même exigence de réglage séparé de chaque branche avant de conclure.
- [[reglage-taux-apprentissage-lora](pages/reglage-taux-apprentissage-lora.md)] : règle de comparaison équitable du projet.
- [[parhaf-corpus-paper](pages/parhaf-corpus-paper.md)] : le corpus sur lequel ce principe sera appliqué.

[^1]: [[limited-impact-medical-adaptation](pages/limited-impact-medical-adaptation.md)] §3 [synthesis] L326-L328 — dix LLM médicaux et deux VLM comparés à leurs modèles de base ; 22 jeux textuels dont 8 sur notes cliniques, 8 jeux visuels
[^2]: [[limited-impact-medical-adaptation](pages/limited-impact-medical-adaptation.md)] §1 [synthesis] L234-L240 — invites et exemples choisis séparément pour chaque modèle sur la validation, bootstrap percentile pour juger si les gains tiennent au hasard ; L326-L328 : les deux modèles d'une paire ne diffèrent que par l'adaptation médicale
[^3]: [[limited-impact-medical-adaptation](pages/limited-impact-medical-adaptation.md)] §3 L463-L471 [synthesis] L463-L471 — bootstrap percentile sur les questions du test, 10 000 itérations, intervalle à 95 %, aucune correction des comparaisons multiples
[^4]: [[limited-impact-medical-adaptation](pages/limited-impact-medical-adaptation.md)] Abstract L19-L21 — "ical VLMs and nearly all medical LLMs fail to consistently improve over their base models"
[^5]: [[limited-impact-medical-adaptation](pages/limited-impact-medical-adaptation.md)] Abstract L22-L25 [synthesis] L22-L25 — 26,7 % de victoires, 16,7 % d'égalités et 56,7 % de défaites sur les tâches de notes cliniques à trois exemples
[^6]: [[limited-impact-medical-adaptation](pages/limited-impact-medical-adaptation.md)] §5.1 [synthesis] L1485-L1489 — après fine-tuning, les LLM médicaux gagnent en moyenne 1,6 point d'exactitude absolue sur les questions de connaissances, le plus souvent de façon significative
[^7]: [[limited-impact-medical-adaptation](pages/limited-impact-medical-adaptation.md)] §5.2 L1537-L1538 — "fine-tuning performances of"
[^8]: [[limited-impact-medical-adaptation](pages/limited-impact-medical-adaptation.md)] §6 [synthesis] L1752-L1760 — les bénéfices disparaissent en grande partie quand l'invite est adaptée à chaque modèle et l'incertitude prise en compte ; optimiser l'invite seulement pour le modèle médical surestime son gain
[^9]: [[limited-impact-medical-adaptation](pages/limited-impact-medical-adaptation.md)] §6 Limitations L1784-L1786 — "closed-ended medical QA"
[^10]: [[limited-impact-medical-adaptation](pages/limited-impact-medical-adaptation.md)] §6 Limitations L1795-L1801 [synthesis] L1795-L1801 — pas de fine-tuning complet, la conclusion peut différer dans ce régime
[^11]: [[limited-impact-medical-adaptation](pages/limited-impact-medical-adaptation.md)] App. E.1 L2894-L2900 [synthesis] L2894-L2900 — alpha fixé à 16, rangs 16, 32, 64, cinq taux d'apprentissage, 15 essais par modèle et jeu, 10 époques au plus et arrêt anticipé
