# Rapport final du projet LLM_Engineering (07/10/2026) : classer le chapitre CIM-10 de comptes rendus cliniques français fictifs

Texte destiné à sortir du dépôt, passé par `claim-gate` : chaque chiffre renvoie à un run du registre (tableau de la section 7). Corpus **fictif** (PARHAF) : aucun résultat ici n'est une mesure sur des patients réels. Aucune phrase de ce rapport n'affirme un « gain confirmé » : le verdict de la question primaire est « non résolu ».

## 1. Ce que le lecteur doit comprendre d'abord
- **Question** : quelle technique d'adaptation d'un modèle de langage apporte un gain réel, et de combien de points, pour prédire le chapitre CIM-10 du diagnostic principal d'un compte rendu, sous contrainte de calcul local (une carte de 32 Go) ?
- **Statut du résultat principal : confirmatoire.** Le système final a été choisi par une règle écrite d'avance, gelé et haché avant l'ouverture (ADR-016), puis comparé sur un test scellé de 633 patients ouvert **une seule fois** le 06/10/2026. Les mesures de développement, d'ancrage et de robustesse sont exploratoires.
- **Résultat en une phrase** : sur le test scellé, le système final atteint une macro-F1 de 0,8131 contre 0,7402 pour le meilleur TF-IDF, soit +7,28 points (intervalle à 95 % par blocs d'auteurs [+1,55 ; +12,62]) : **non résolu** au seuil d'utilité de 2,0 points, car la borne basse est sous 2,0.
- **Ce que les mesures disent en plus** : l'écart avec un TF-IDF bien réglé est réel au point estimé mais pas tranché ; plusieurs idées d'efficience ont échoué et sont publiées.

## 2. Estimand et données
- Test scellé : « nouveaux patients du même corpus » ; les patients du test peuvent partager des auteurs avec le développement. Ce chiffre n'estime pas la généralisation à de nouveaux auteurs, mesurée à part au développement.
- 4 254 comptes rendus fictifs, 4 219 utilisés, 17 chapitres évalués, 633 patients au test ; quatre chapitres comptent moins de 10 patients au test : leurs F1 ne sont pas vérifiables individuellement.
- Un second jeu, MorFITT (résumés d'articles biomédicaux français, public, licence à déclarations divergentes, CC BY-SA 4.0 retenue), sert uniquement de repère externe.

## 3. Résultats
| Métrique | Valeur | Intervalle | Périmètre |
|---|---|---|---|
| Macro-F1, système final (LoRA, encodeur, TF-IDF à parts égales) | 0,8131 | n/a | test scellé, 633 patients |
| Macro-F1, meilleur TF-IDF | 0,7402 | n/a | idem |
| Différence, final moins TF-IDF | +7,28 points | [+1,55 ; +12,62] par blocs d'auteurs | idem ; verdict « non résolu » à δ = 2,0 |
| Différence, final moins ensemble encodeur + TF-IDF | +0,99 | [−3,71 ; +5,00] | idem, sans verdict |
| Différence, final moins LoRA seul | +0,98 | [−1,39 ; +3,76] | idem, sans verdict |
| MorFITT, mélange encodeur + TF-IDF, F1 pondéré | 71,74 | [69,60 ; 73,71] | test public, 1 088 résumés ; meilleur publié 71,95 : dans la bande |
| Encodeur CamemBERT-bio seul, MorFITT | 65,53 (cinq graines, écart-type 0,89) | n/a | publié 67,53 : non reproduit au sens strict |
| Encodeur contre TF-IDF avec plis groupés par auteur | 0,7075 contre 0,6742, +3,32 | [+0,53 ; +6,29] | développement : non résolu ; perte de 5,2 points par rapport aux plis par patient, comparable à celle du TF-IDF |

Prédictions préenregistrées du gel : quatre réussites sur six ; échecs : la macro-F1 de G est au-dessus de l'intervalle prévu, et la couverture conforme minimale par famille (0,821) est sous le seuil prévu (0,87).

## 4. Incertitude
- Conforme à 90 % (quantiles calibrés au développement) : couverture marginale 0,924, par famille 0,916, **minimum 0,821 sur une famille de 56 patients** ; garantie marginale tenue, garantie conditionnelle tenue sauf pour cette famille.
- Abstention : exactitude 0,962 à 70 % de couverture (443 patients), 0,891 à couverture complète.
- Écart d'échangeabilité : calibration sur des prédictions hors pli ; le test est prédit par des modèles entraînés sur tout le développement ; le décalage d'auteur n'est pas mesuré sur le test.

## 5. Ce qui n'a pas marché (publié)
Distillation vers un encodeur : gain apparent de +3,5 non préservé avec des professeurs imbriqués (−0,77 [−2,46 ; +0,96], fuite de second ordre −4,24 [−6,00 ; −2,90]). Élagage à six couches : dégradé (−13,08 [−15,88 ; −10,14]). INT8 statique ONNX : macro-F1 0,0227 et 39 % plus lent. Lissage d'étiquettes, moyenne de poids et curriculum : aucun gain. Empilement appris : non supérieur au mélange 50/50.

## 6. Ce que nous ne savons pas, limites
- **Fragilité du LoRA à la fin du texte** : retirer 10 % de la fin fait tomber sa macro-F1 de 0,78 à 0,14 au pli 0 ; le seul retrait du saut de ligne final coûte 7,7 points. Vérifié : les 3 586 textes de développement finissent par un saut de ligne ; **non vérifié pour les 633 textes du test** (erratum de l'ADR-016). Une correction par augmentation est en cours d'évaluation.
- Un seul LoRA final (variance entre graines non mesurée) ; un seul benchmark externe, de résumés d'articles ; le LoRA n'est pas mesuré en plis d'auteurs.
- **Revue indépendante par trois agents du même modèle** (pas de relecture humaine) : 0 constat bloquant, 12 importants, 88 tests ajoutés et 12 défauts corrigés après coup ; le garde du test scellé est procédural, pas technique.
- **Fiabilité de la machine** (complément du 17/10/2026 : la mise à jour du BIOS n'a rien changé, 10 pannes sur 46 essais avant comme après, section 8) : des pannes internes impossibles en Python correct (TypeError de scikit-learn, segfaults du tokenizer) et des plantages de WSL ont été observés ; hypothèse d'instabilité matérielle non prouvée ; les résultats reposent sur des rejeux identiques et des vérifications, pas sur une garantie matérielle.
- Reconstruction à froid : un clone neuf du dépôt, avec PARHAF et la CIM-10 téléchargés par scripts versionnés dont les empreintes sont vérifiées, redonne la macro-F1 du TF-IDF de référence (0,7201565961621372) identique à 1e-9 près en 834 s ; limites : cache des paquets chaud, image Docker non reconstruite, aucune version taguée.

## 7. Tableau de preuve
| Affirmation | Preuve | Statut |
|---|---|---|
| 0,8131 contre 0,7402, +7,28 [+1,55 ; +12,62], non résolu | run `20261006-210015-ouverture-test-scelle-g` ; `data/splits/sealed_access.log` (une seule ouverture) | prouvé |
| Prédictions préenregistrées, 4 réussites sur 6 | ADR-016, run `20261006-210015-ouverture-test-scelle-g` | prouvé |
| Conforme 0,924 marginal, 0,916 par famille, minimum 0,821 ; exactitude 0,962 à 70 % | run `20261006-210015-ouverture-test-scelle-g` | prouvé |
| MorFITT : 71,74 [69,60 ; 73,71], 65,53, publiés 71,95 et 67,53 | run `20261006-223731-morfitt-final-resume` ; arXiv 2402.16689 tableau 3 | prouvé (publiés vérifiés à la source) |
| Encodeur en plis d'auteurs : 0,7075, +3,32 [+0,53 ; +6,29], perte 5,2 | run `20261006-213214-encodeur-plis-auteurs-analyse` | prouvé (développement) |
| Distillation non préservée, élagage dégradé, INT8 effondré | runs `distillation-analyse-cinq-plis` (verdict RM-56, fiche `2026-10-05-distillation-imbriquee`), `20261006-121213-encodeur-elague-analyse-cinq-plis`, `20261006-091535-onnx-int8-statique-partiel-camembert-deploy-ep10-lr1e-4` | prouvé |
| Fragilité du LoRA à la fin du texte | runs `20261006-173250-robustesse-modeles-appris-lora`, `20261006-182233-robustesse-lora-saut-de-ligne` | prouvé (un pli, une graine) |
| Reconstruction à froid : macro-F1 de référence identique à 1e-9 | runs `20261006-230806-reconstruction-a-froid-chiffre-cle`, `20261006-210819-reconstruction-a-froid-partielle` | prouvé (cache uv chaud, Docker non reconstruit) |
| « le système final bat le TF-IDF » | verdict « non résolu » | **reformulé** : « +7,28 points, non résolu à δ = 2,0 » |
| « état de l'art » sur MorFITT | mélange dans la bande du meilleur publié, pas au-dessus | **reformulé** ; « état de l'art » **retiré** |
| « validé sur des patients réels » | corpus fictif | **retiré** |
| Cascade E puis G : −0,10 [−0,23 ; +0,02] contre G, 82,3 % des patients sans le LoRA | run `20261017-012416-cascade-e-puis-g` (fiche `2026-10-17-cascade-e-puis-g`) | prouvé (développement, hors pli ; le test scellé n'a pas été relu) |
| Service HTTP de G en cascade : 38,4 ms et 3,06 Wh pour 1 000 patients attendus, contre 97,4 ms et 10,67 Wh pour G complet | runs `20261017-015754-service-g-cascade`, `20261017-025855-energie-service-g-cascade` | prouvé comme mesure ; **reformulé** en « attendus » (chemins mesurés pondérés par la part de routage hors pli) |
| Mise à jour du BIOS sans effet sur les pannes : 10 sur 46 avant et après | runs `20261016-230229-verification-machine-bios-avant`, `20261017-012310-verification-machine-bios-apres` | prouvé ; cause des pannes non établie |
| « la cascade vaut G » | non-infériorité à la marge de 2,0 en développement seulement | **reformulé** : « non inférieure à G à la marge de 2,0 points, en développement » |
| G gelé transposé sans réglage sur MorFITT : F1 pondéré 72,30 [70,15 ; 74,35] contre 71,95 publié au mieux, « dans la bande » | run `20261017-113948-morfitt-g-gele` | prouvé ; **reformulé** : « au niveau du meilleur chiffre publié », jamais « au-dessus » ; ensemble de sept modèles face à des modèles seuls |

## 8. Complément du 17/10/2026

Ajouté après le 07/10 ; mêmes règles (`claim-gate`, tableau de la section 7). Aucun chiffre de la section 3 ne change.
- **Servir G à moindre coût** : une cascade où l'ensemble encodeurs + TF-IDF répond seul quand sa probabilité maximale atteint 0,6 (seuil choisi hors pli), et G complet sinon, est **non inférieure à G à la marge de 2,0 points** en développement (−0,10 [−0,23 ; +0,02], 82,3 % des patients sans le LoRA). Servie par HTTP, sa latence moyenne attendue est de 38,4 ms et son énergie attendue de 3,06 Wh pour 1 000 patients, contre 97,4 ms et 10,67 Wh pour G complet dans les mêmes mesures. L'entraînement reste celui de G. La cascade n'a pas été lue sur le test scellé, déjà consommé.
- **Machine** : la mise à jour du BIOS, mesurée avant et après par une fiche écrite d'avance, n'a pas changé le taux de panne (10 sur 46 essais dans les deux cas) ; les deux expériences prêtes ont été lancées le 17/10 sur autorisation écrite de Cyril malgré cette instabilité, avec tampon de santé et double calcul ; la première a subi une panne (relance automatique, aucune métrique perdue ni lue).
- **Repère public** : transposé sans aucun réglage sur MorFITT, le système final G atteint un F1 pondéré de 72,30 [70,15 ; 74,35] sur le test public, contre 71,95 pour le meilleur système publié : **au niveau du meilleur chiffre publié, pas au-dessus** (verdict « dans la bande » de la règle écrite d'avance) ; c'est un ensemble de sept modèles face à des modèles seuls, pas une comparaison à budget égal. Deux entraînements du LoRA à la même graine ne donnent pas les mêmes prédictions (85,4 % des résumés aux mêmes étiquettes) : l'intervalle ne contient pas la variance d'entraînement.
