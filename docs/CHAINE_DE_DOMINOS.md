# Chaîne de dominos : des petits objectifs aux notes maximales (05/10/2026)

Statut : plan de travail, **estimations de l'assistante, non mesurées** (les notes viennent de `docs/presentation/PREUVES.md`, à ±1). Les identifiants RM, P renvoient à `MICROTACHES.md` et à `roadmap_unifié.md`. Rien ici ne modifie le protocole gelé ni ne décide à la place de Cyril.

## 1. La métaphore, prise au sérieux

Un domino n'en fait tomber un plus grand que si la **cause physique est écrite** : chaque objectif produit une pièce de preuve dont le suivant a besoin pour exister. Trois règles en découlent.

1. **On commence par le plus petit domino qui touche le suivant**, pas par le plus spectaculaire : un objectif n'est « petit » que s'il est borné (au plus une demi-journée d'ingénierie, quelques heures de GPU) et falsifiable.
2. **Un domino qui ne produit aucune pièce de preuve ne fait rien tomber** : un résultat sans identifiant de run, sans fiche hachée ou sans intervalle ne déclenche pas la suite.
3. **Le domino géant est connu d'avance** : ici, l'ouverture unique du test scellé sur un candidat figé et préenregistré, et l'ancrage sur un benchmark public à résultats publiés. Tout le reste sert à ce que ces deux pièces tombent proprement.

## 2. Ce qu'un 10/10 veut dire, et ce qui plafonne (honnêteté)

| Composante | Note actuelle | Critères vérifiables d'un 10/10 | Plafond réaliste dans nos limites |
|---|---|---|---|
| Performance du modèle | 6 | résultat confirmatoire sur le test scellé ; ancrage vérifiable face à des chiffres **publiés** sur au moins un benchmark public ; gain résolu sur cinq plis | **8, 9 si un chiffre publié est dépassé sur le benchmark public** ; 10 exigerait de battre des systèmes fermés ou cliniques sur données réelles, non vérifiable avec un corpus fictif |
| Rigueur statistique et protocole | 8 | protocole v2 accepté puis exécuté sans écart ; test scellé ouvert une fois ; toutes les prédictions préenregistrées notées ; revue indépendante | **10** |
| Données et anti-fuite | 7 | fiche de données, audit d'étiquettes, lignée du synthétique, contrôles de fuite exécutables, transposition à un second jeu | **9** (le corpus est fictif et l'étiquette vient d'un scénario) |
| Fiabilité de l'incertitude | 7 | couverture conditionnelle validée sur le test scellé, sous nouveaux auteurs, par famille ; coût en taille d'ensemble rapporté | **9** |
| Analyse d'erreurs et robustesse | 6 | taxonomie complète, audit des erreurs confiantes, nouveaux auteurs pour le LoRA et l'encodeur, ablations de contenu pour tous | **9** |
| Reproductibilité et ingénierie | 8 | conteneur vérifié par un build, reconstruction à froid du chiffre clé, release taguée, déterminisme statistique déclaré | **10** |
| Efficience et déploiement | 5 | élève distillé mesuré, service de chaque profil mesuré (latence, débit, énergie), cascade validée hors pli, fiche de déploiement | **9** (10 supposerait une industrialisation hors de notre matériel) |
| Sûreté, conformité, honnêteté | 8 | tout texte sortant passé par `claim-gate`, résultats négatifs publiés, TRIPOD-LLM remplie, calibration des prédictions de l'assistante, audits externes consignés | **10** |

**Lecture honnête** : « 10/10 partout » et « dépasser le meilleur niveau connu » ne sont **pas** simultanément atteignables ni vérifiables ici. Cinq composantes peuvent atteindre 9 ou 10 sur des critères contrôlables ; la performance plafonne à 8 (9 sous condition) parce qu'aucun repère publié n'existe pour PARHAF, corpus nouveau ; l'efficience et les données plafonnent à 9. La moyenne atteignable est de l'ordre de **9,2 à 9,4** (contre 6,9 aujourd'hui), au-dessus du niveau ouvert estimé (7,6) et au niveau du niveau absolu estimé (9,4) au mieux, sans prétendre le dépasser composante par composante.

## 3. La chaîne, dans l'ordre causal

Chaque ligne : le domino, ce qu'il fait tomber, les composantes qu'il fait monter (note actuelle vers cible), le coût, la condition d'arrêt.

| # | Domino (objectif) | Ce qu'il fait tomber | Composantes | Coût | Condition |
|---|---|---|---|---|---|
| 0 | **Plis 3 et 4 du LoRA et leur post-traitement** (RM-28, en cours, fin vers 03h20Z) | professeur strictement hors pli ; verdict LoRA contre encodeur à cinq plis | perf 6 vers 7, rigueur | 7,5 h GPU déjà lancées | aucun |
| 1 | **Mesures de service, énergie et zéro-shot** (RM-34, RM-42, RM-30 ; lots en file) | preuve d'efficience par profil ; premier repère externe sans affinage | effic. 5 vers 6, honnêteté | 1,5 h GPU | aucun |
| 2 | **Distillation vers l'encodeur** (RM-32 ; 30 runs préenregistrés) | si l'élève est à moins de 2 points du professeur : le LoRA n'est plus à servir, cascade et quantification deviennent accessoires | effic. 6 vers 8, perf (rapport qualité par coût) | 2,5 h GPU | arrêt si l'élève reste à plus de 4 points sous l'encodeur non distillé |
| 3 | **Débit d'entraînement à résultat équivalent** (RM-41) : le petit domino qui libère du budget | divise le coût de tous les runs suivants (graines du LoRA, second cycle) | effic. | une demi-journée et 3 h GPU | équivalence statistique d'abord, jamais pendant un lot |
| 4 | **Audit des étiquettes confiantes et synthétique ciblé** (P2-06, P2-10) | corrige la source du plafond d'ambiguïté et le déficit des cinq petits chapitres | perf 7 vers 8, données 7 vers 8, erreurs 6 vers 8 | 6 h GPU, 1 jour | arrêt si aucun gain résolu |
| 5 | **Système final figé** : ensemble (LoRA à plusieurs graines, encodeur, TF-IDF, élève) choisi sur les prédictions hors pli | une seule hypothèse à confirmer ; fin des comparaisons ouvertes | rigueur | 8 h GPU (graines du LoRA) | règle écrite avant lecture |
| 6 | **Acceptation du protocole v2 par Cyril** (RM-37, ADR-015) | autorise un second cycle et une ouverture confirmatoire | rigueur 8 vers 9 | décision humaine | décision de Cyril |
| 7 | **Ouverture unique du test scellé, en deux temps** (RM-20) | transforme EXPLORE en confirmatoire ; premier chiffre extérieur au développement | perf 8, rigueur 9 vers 10, incertitude, honnêteté | 1 h | une seule fois |
| 8 | **Incertitude et nouveaux auteurs confirmés** (RM-33, RM-39, leave-one-author-out du LoRA et de l'encodeur) | couverture conditionnelle validée hors développement ; robustesse mesurée pour tous les modèles | incertitude 7 vers 9, erreurs 8 vers 9 | 6 h GPU | arrêt si couverture hors cible sans cause |
| 9 | **Ancrage sur benchmark public à résultats publiés** (RM-49, MorFITT avec le même code) | seule base vérifiable pour parler de l'état de l'art ; transposabilité du code | perf 8 vers 9 (sous condition), données 8 vers 9 | 5 h GPU, 1 jour | chiffres publiés cités avec source, jamais extrapolés |
| 10 | **Livraison reproductible** (P5-09, P5-12, RM-48 : conteneur vérifié, reconstruction à froid, release taguée, rapport et textes passés par `claim-gate`, fiche de déploiement) | rend tout le reste vérifiable par un tiers | repro 8 vers 10, honnêteté 8 vers 10, effic. 9 | 1 jour | un push ou une création de dépôt distant exige Cyril |
| 11 | **Revue indépendante** (P5-10 ; audits GLM v5 et v6) | clôt les angles morts des conclusions de l'assistante | rigueur 10, honnêteté 10 | 1 jour | aucun envoi externe sans Cyril |

**Chemin critique** : 0, 5, 6, 7 (la ligne qui détermine la rigueur et le caractère confirmatoire) ; **chemin le moins cher pour le plus grand gain de note** : 1, 2, 3 (efficience, de 5 à 8 en environ quatre heures de GPU) ; **le domino géant** : 7 puis 9.

## 4. Pourquoi cet ordre

- **0 avant 5** : sans cinq plis du LoRA, on ne sait pas si le LoRA entre dans le système final, et la distillation n'a pas de professeur hors pli.
- **2 avant 3 et 4** : si la distillation réussit, l'effort sur le débit d'entraînement du LoRA vaut moins ; si elle échoue, le débit devient prioritaire. Le résultat de 2 aiguille donc le budget.
- **4 avant 5** : l'audit d'étiquettes peut déplacer le plafond d'ambiguïté (8,2 % d'erreurs communes) et donc ce qu'un système final peut espérer.
- **5 avant 6 et 7** : le test scellé ne s'ouvre qu'une fois, sur un candidat figé et préenregistré, avec la prédiction chiffrée écrite d'avance.
- **9 après 7** : l'ancrage public ne doit pas influencer le choix du candidat ; il le situe.
- **10 et 11 en dernier** : on ne rend reproductible et on ne fait relire que ce qui est figé.

## 5. Points de bifurcation (le plan change selon la mesure)

- **Distillation (2)** : élève à moins de 2 points du professeur, le LoRA sort du service (efficience, simplicité) ; élève à plus de 4 points, l'élève bon marché reste l'ensemble encodeur + TF-IDF et le LoRA devient un modèle de qualité maximale servi sur GPU par cascade.
- **LoRA à cinq plis (0)** : LoRA au moins 2 points au-dessus de l'ensemble à cinq plis, il devient le système final ; sinon l'ensemble reste le système final et le LoRA un professeur.
- **Audit et synthétique (4)** : gain résolu sur les cinq petits chapitres, il entre dans le système final ; sinon il est publié comme résultat négatif et retiré.
- **Benchmark public (9)** : chiffre publié dépassé, la performance monte à 9 sur ce repère ; non dépassé, elle reste à 8 avec un repère honnête.

## 6. Ce qui reste hors de portée (et pourquoi on le dit)

Battre des systèmes fermés ou cliniques sur données réelles ; valider sur des patients réels (interdit par les règles du projet) ; industrialiser à l'échelle d'un hôpital ; toute comparaison avec un « état de l'art absolu » sur PARHAF, faute de repère publié. Ces limites sont déclarées dans la carte de modèle et dans le rapport.
