# Surveillance de dérive, maintenance et retour arrière du service de G (P5-08)

État au 17/10/2026. Seuils et taux de détection **mesurés par simulation en développement** (fiche `2026-10-17-simulation-derive`, run `20261017-090325-simulation-derive`, 3 586 patients, prédictions hors pli, processeur seulement, calcul fait deux fois et identique). **Branchement (17/10/2026)** : les deux services exposent `GET /drift` quand on leur donne un fichier de référence (`--reference`, produit par `scripts/reference_prevalence.py` : `deploy/reference_prevalence_tfidf.json`, `deploy/reference_prevalence_g_cascade.json`) ; le moniteur (`llmft.drift_monitor`) garde les étiquettes prédites et les étages des 100 dernières prédictions, jamais un texte ni une probabilité individuelle, et rend S2 avec son alerte et la part servie par E seul. Vérifié de bout en bout sur le service TF-IDF, processeur seulement : 100 patients fictifs tirés au hasard, S2 = 0,170, pas d'alerte ; 100 patients du seul chapitre II, S2 = 0,741, alerte. **Approximation déclarée** : le seuil de 0,207 est mesuré sur la prévalence prédite de E ; il est appliqué tel quel au TF-IDF et à la cascade. L'image de service n'est pas reconstruite (Docker indisponible côté WSL, Q27) et son lancement par défaut n'active pas le moniteur. Ce document fixe ce que la surveillance calcule et ce qu'il faut faire quand elle alerte. Corpus fictif : rien ici ne vaut validation sur des comptes rendus réels.

## 1. Questions d'exploitation

1. Les documents reçus ressemblent-ils encore à ceux du développement ? (signaux S2 et S3)
2. Le service est-il moins sûr de lui qu'en développement, donc plus lent et plus coûteux ? (signal S1 : part des patients servis par E seul, sans le LoRA)
3. La qualité a-t-elle baissé ? (échantillon étiqueté de 1 000 patients : seule réponse possible pour les nouveaux auteurs, sections 3 et 5)
4. Quand réentraîner, quand revenir en arrière ? (sections 5 et 6)

## 2. Signaux sans étiquette et seuils mesurés

Chaque signal se calcule sur un lot de n patients reçus, contre la référence hors pli de E. **S1** : baisse de la part des patients où E atteint τ = 0,6 (référence 82,26 %). **S2** : variation totale entre la prévalence des chapitres **prédits** du lot et celle de la référence. **S3** : statistique de Kolmogorov-Smirnov des longueurs de texte. Seuil = 99e centile sur 2 000 lots tirés de la référence, soit 1 % de fausse alerte par signal et par lot.

| Taille du lot | S1 (baisse de part) | S2 (variation totale) | S3 (Kolmogorov-Smirnov) | Fausse alerte des trois réunis |
|---|---|---|---|---|
| 100 | 0,0926 | 0,207 | 0,167 | 2,9 % |
| 200 | 0,0576 | 0,150 | 0,110 | 2,75 % |
| 500 | 0,0386 | 0,0877 | 0,0645 | 2,75 % |

**Constantes actuelles de `llmft.drift` (non modifiées par ce run)** : la variation totale de 0,15 donne 30 % de fausses alertes sur des lots de 100 patients, 1 % à 200, 0 % à 500 ; le Kolmogorov-Smirnov de 0,2 ne donne presque jamais d'alerte (0,1 % à 100), donc presque aucune puissance. Un seuil fixe ne convient pas : il dépend de la taille du lot.

## 3. Ce que chaque signal détecte

Taux de détection (part des lots du scénario au-dessus du seuil de même taille) et impact sur la macro-F1 regroupée (17 chapitres), en points.

| Scénario | n | S1 | S2 | S3 | Impact moyen |
|---|---|---|---|---|---|
| A, nouveaux auteurs (substitut E′, impact apparié) | 100 / 200 / 500 | 4 % / 10 % / 22 % | 1 % / 1 % / 1 % | sans objet | −3,84 / −4,68 / −5,24 |
| B, prévalence (chapitre II pesé 3 fois) | 100 / 200 / 500 | 0 % | 92 % / 99,8 % / 100 % | 19 % / 57 % / 98 % | −5,38 / −3,68 / −1,88 |
| C, textes courts (quart le plus court pesé 3 fois) | 100 / 200 / 500 | 0 % | 15 % / 35 % / 89 % | 97 % / 100 % / 100 % | −2,05 / −1,55 / −0,23 |

Lecture selon le critère écrit d'avance (taille de décision n = 200 ; « nuisible » si l'impact moyen est d'au plus −2,0 points, δ du protocole ; signal « retenu » s'il détecte au moins 80 % des lots) :

- **A, nouveaux auteurs : nuisible et non surveillable sans étiquettes.** Sur les mêmes patients, passer des plis par patient aux plis par auteur fait perdre 5,17 points au substitut E′ (77,39 contre 72,22) alors que la part servie par E′ seul ne baisse que de 82,46 % à 79,81 % : aucun signal ne détecte 80 % des lots, même à 500 patients. C'est le cas le plus probable d'un déploiement (autres médecins, autre hôpital) : il relève d'un **échantillon étiqueté**, pas d'une alarme automatique.
- **B, prévalence : nuisible à n = 200, S2 retenu** (dès 100 patients). Réserve déclarée : pour B et C, l'impact compare des lots différents et mêle une vraie baisse et un effet de composition de la macro-F1 sur de petits lots (il rétrécit quand le lot grandit : −1,88 à 500). S3 n'atteint 80 % qu'à 500 patients (rapporté à part, hors règle).
- **C, textes courts : non nuisible, S3 retenu** : la longueur trahit ce changement de format sans que la qualité baisse de 2 points.

**Règle d'alerte recommandée par la fiche** : S2 sur des lots de 100 patients, seuil 0,207. S3 (lots de 200, seuil 0,110) et S1 (lots de 200, seuil 0,0576) restent **informatifs** : S3 signale un changement de format ; S1 mesure directement le coût, puisque chaque point de part perdu envoie des patients vers le LoRA (latence et énergie du chemin G, `docs/FICHE_DE_DEPLOIEMENT.md`).

## 4. Fiches d'intervention

Aucune de ces alertes ne justifie une intervention immédiate : un humain relit déjà toute sortie (aide à la décision seulement). Toutes sont des tickets à traiter dans la semaine.

**Alerte S2 (prévalence des chapitres prédits).** *Signifie* : la répartition des chapitres prédits sort de sa plage habituelle (nouveau service émetteur, changement du flux, ou modèle qui dérive). *Premier contrôle* : comparer, chapitre par chapitre, la prévalence prédite du lot à celle de la référence, et identifier la source des documents du lot. *Escalade* : la personne responsable du modèle ; trois lots de suite en alerte déclenchent un échantillon étiqueté anticipé (section 5).

**Signal S3 (longueurs).** *Signifie* : le format des documents a changé (textes tronqués, nouveau type de compte rendu). *Premier contrôle* : distribution des longueurs et types de documents du lot. *Escalade* : si le changement est durable, mesurer la qualité sur un échantillon étiqueté du nouveau format avant de continuer.

**Signal S1 (part servie par E seul).** *Signifie* : le service est moins sûr de lui ; latence et énergie montent. *Premier contrôle* : latence p95 et part des requêtes passées par le LoRA. *Escalade* : revoir la capacité GPU ; S1 ne prouve pas à lui seul une baisse de qualité (scénario A).

## 5. Maintenance et réentraînement

- **Échantillon étiqueté périodique, obligatoire** : c'est la seule défense contre le scénario A. **Taille mesurée** (fiche `2026-10-17-taille-echantillon-etiquete`, run `20261017-091931-taille-echantillon-etiquete`, seuil au 5e centile des lots sans dérive) : pour voir avec une puissance de 0,80 un lot entièrement écrit par de nouveaux auteurs, il faut **1 000 patients étiquetés en suivant la macro-F1** (puissance 0,81 ; l'exactitude en demande 2 000, car elle ne perd que 2,17 points là où la macro-F1 en perd 5,17) ; 500 patients ne donnent qu'une chance sur deux (0,51). Un flux où 40 % seulement des patients viennent de nouveaux auteurs (−1,70 point de macro-F1) reste presque invisible : puissance 0,20 à 1 000 patients, 0,51 à 2 000. **Limite** : lots tirés sans remise dans 3 586 patients, ce qui sous-estime la dispersion pour les grandes tailles (environ 15 % à 1 000) : en production, compter un peu plus de 1 000 cas. Conséquence pratique : l'échantillon étiqueté surveille un changement massif d'auteurs, pas une dérive partielle ; un nouvel hôpital demande une validation locale avant la mise en service.
- **Réentraînement** : seulement si l'échantillon étiqueté montre une macro-F1 sous la référence de développement avec un intervalle à 95 % entièrement sous −2,0 points (δ), et par une nouvelle fiche préenregistrée ; recette gelée d'ADR-016, test scellé jamais réutilisé pour régler.
- **Avant tout nouvel hôpital** : validation locale et analyse de risques (limite 1 de la fiche de déploiement), le scénario A étant invisible pour les signaux automatiques.

## 6. Retour arrière

- **Version précédente** : les artefacts du système gelé sont hachés (ADR-016, `results/frozen_final.json`) ; revenir en arrière, c'est servir la version précédente identifiée par ses empreintes.
- **Mode dégradé sans le LoRA** : si le chemin G (GPU) tombe, servir E seul (la cascade avec τ = 0). En développement, la cascade fait +0,68 point de mieux que E seul (run `20261017-012416-cascade-e-puis-g`) : c'est le coût mesuré du mode dégradé. Sans GPU du tout : le TF-IDF seul, avec son image de service (`docs/FICHE_DE_DEPLOIEMENT.md`).
- **Non fait** : reprise automatique sur panne du GPU, charge prolongée (limites 4 et 5 de la fiche de déploiement), alerte poussée vers un humain (le moniteur se lit sur `GET /drift`, rien n'est envoyé).

## 7. Limites

Scénarios simulés : B et C par tirage pondéré de patients réels du développement, A par un substitut de E (un encodeur au lieu de cinq) faute de prédictions de E en plis par auteur ; impact de B et C mêlé à un effet de composition (section 3) ; corpus fictif ; machine instable (Q26), compensée ici par le double calcul identique.
