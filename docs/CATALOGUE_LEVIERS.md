# Catalogue des leviers L1 à L12 (état de l'art, mis à jour le 01/10/2026)

Extrait de la V5 (section 2 bis), conservé tel quel sous la rubrique « Catalogue », puis corrigé par la veille du 01/10/2026.
Légende faisabilité : **F** faisable tel quel, **C** sous contrainte, **H** hors budget local. Priorité : **P1** testé à coup sûr, **P2** si la marge le permet, **P3** veille.

## Corrections de la veille du 01/10/2026 (elles priment sur le catalogue ci-dessous)

| Levier | Ce que la veille a établi | Source (statut) | Effet sur la priorité |
|---|---|---|---|
| L2 variantes de LoRA | Une fois le taux d'apprentissage réglé pour chaque méthode, vanilla LoRA et neuf variantes (DoRA, PiSSA, rsLoRA, LoRA+...) atteignent des pics proches (à 1 à 2 % près) ; chaque méthode préfère une plage de taux différente | arXiv 2602.04998 (résumé lu) | Variantes passent en **P2** ; chacune reçoit son propre balayage de taux, sinon la comparaison est invalide |
| L2 DoRA | Incompatible avec `target_modules="all-linear"` sur un modèle quantifié (doc PEFT) | doc PEFT (lue) | DoRA réservé aux élèves en bf16, pas aux professeurs QLoRA |
| L2 initialisations | PEFT propose `pissa`, `loftq`, `olora`, `eva`, `corda`, plus LoRA+ (`create_loraplus_optimizer`) et `use_rslora` | doc PEFT (lue) | Tous testables par configuration, sans code propre |
| L3 tête contre invite | Sur de la classification mono-étiquette, la tête sur le dernier token égale ou dépasse BERT avec 10 à 30 fois moins de paramètres entraînés ; l'instruction-tuning n'est compétitif qu'en multi-étiquettes et avec au moins 100 M de paramètres entraînables | arXiv 2512.12677 (résumé lu) | **Tête = défaut** ; verbaliseur = branche de contrôle |
| L3 attention | Retirer le masque causal (LS-LLaMA, LLM2Vec) donne des représentations bidirectionnelles ; avec max-over-time pooling, meilleur que moyenne ou dernier token en classification | arXiv 2310.01208 et 2404.05961 (résumés de recherche) | Nouveau levier **L3b : pooling** (dernier, moyenne, max) à tester avec et sans masque bidirectionnel |
| L5 distillation | `DistillationTrainer` de TRL (v1.14.1) : JSD généralisée, `beta` de 0 (KL directe) à 1 (KL inverse), génération par l'élève, **vocabulaire commun obligatoire**, causal LM seulement | doc TRL (lue) | Utilisable pour la piste générative P6 ; la distillation de classifieur se fait **au niveau des classes** (pas de contrainte de vocabulaire, professeurs hétérogènes possibles) |
| L5 mélange | Mélanger étiquettes dures et douces bat chacune seule (Bridge-Garden, ICML 2026) ; DistiLLM-2 (ICML 2025) apporte une perte contrastive | arXiv 2605.26246 et 2503.07067 (résumés lus) | Justifie la perte `alpha*CE + (1-alpha)*KL`, avec `alpha` balayé |
| L1 adaptation médicale | Dix LLM médicaux ne battent pas systématiquement leur modèle de base (prompting et SFT) | arXiv 2411.08870 (résumé lu) | Le criblage des points de départ inclut des généralistes ; MedGemma ou BioMistral ne sont **pas présumés meilleurs** |
| L1 corpus | PARCOMED (CC BY 4.0 et Etalab 2.0 pour la version commerciale, 1,8 M de lignes, 2,93 Go) est conçu pour le pré-entraînement continu français biomédical | dataset card HF (lue) | Source du pré-entraînement continu léger et des textes non étiquetés |
| L9 attention | FlashAttention 2 tourne sur SM120 (RTX 5090) à débit réduit ; FlashAttention 4 exige les GPU de centre de données SM100 | guides communautaires (recherche) | SDPA de PyTorch par défaut ; FA2 en variante mesurée |
| L9 quantification | llm-compressor (NVFP4, MXFP4, FP8, W8A8, GPTQ, AWQ, AutoRound) et GPTQModel (GPTQ, AWQ, FP8...) ; noyaux vLLM SM120 présents depuis la 0.13 mais des lacunes NVFP4 MoE et un choix de backend MXFP4 limité à SM100 sont signalés | docs et issues (recherche) | NVFP4 testé sur **modèle dense** ; MoE écartés de la quantification |
| L10 conforme | MAPIE v1 (BSD-3, LAC, APS, RAPS, multi-étiquettes, risk control, tests d'échangeabilité) et TorchCP (LGPL-3.0, JMLR 2025) | docs et dépôts (lus) | Deux bibliothèques indépendantes plus une implémentation maison de 30 lignes : trois mesures qui doivent s'accorder |
| L12 juge | Les LLM-juges sont évalués sur des QA ouvertes médicales françaises ; évaluation de la génération en santé : faits atomiques bidirectionnels (UC3 de PARTAGES) | arXiv 2603.04033, page UC3 (lues) | Métrique de factualité par faits atomiques pour la piste générative |

---

## Catalogue (version V5, inchangée)

### État de l'art : tout ce qui peut améliorer la qualité (brainstorm, octobre 2026)

La solution LMSYS 2024 n'est qu'un point de départ. Ce catalogue rassemble les leviers connus à ce jour,
regroupés par famille. Pour chacun : ce que c'est, pourquoi il compte pour des comptes rendus hospitaliers,
et sa faisabilité sur une RTX 5090.

Légende faisabilité : **F** faisable tel quel · **C** faisable sous contrainte (taille de modèle, durée) · **H** hors budget local.
Légende priorité : **P1** testé à coup sûr · **P2** testé si P1 laisse de la marge · **P3** veille, mentionné seulement.

### Deux leçons à garder en tête avant d'empiler les techniques
- **Le taux d'apprentissage d'abord.** Une étude de 2026 (« Learning Rate Matters: Vanilla LoRA May Suffice »)
  montre qu'une bonne part des gains attribués aux variantes de LoRA disparaît quand on règle correctement
  le taux d'apprentissage de la référence. Toute variante sera donc comparée à une LoRA **déjà réglée**,
  jamais à une LoRA par défaut. L'auteur de LMSYS dit la même chose : 1e-5 contre 5e-5 = 0,01 point.
- **Le successeur de LMSYS a déjà amélioré la recette.** La 1re place du WSDM Cup 2025 (Multilingual Chatbot Arena,
  même format) a ajouté trois choses à la distillation : **5 professeurs** au lieu de 2, la **relecture manuelle des
  exemples où les professeurs contredisent l'étiquette humaine** (correction du bruit d'annotation), et des **données
  synthétiques**. Elle entraînait aussi les deux ordres d'une paire dans le même pas de gradient, et tronquait par le milieu.

- **Le 5e de LMSYS (Team Danube) a pris le chemin inverse, sans aucune distillation.** Leur levier principal :
  un **pré-entraînement sur une tâche voisine** avant la vraie tâche. En criblant des modèles déjà publiés
  (classement RewardBench), ils ont vu que des modèles entraînés sur des données de préférence (UltraFeedback)
  partaient mieux que les versions de base ou « instruct ». Ils ont donc pré-entraîné Gemma 2 9B sur UltraFeedback
  (simple étiquette gagné / perdu) : **jusqu'à 20 points de gain** en validation croisée comme au classement public.
  Détails donnés en commentaire : LoRA de pré-entraînement fusionnée, **tête de classification jetée puis réapprise**
  (la garder était un peu moins bon), réglages du pré-entraînement peu sensibles. Le reste : 2 entraînements sur toutes
  les données avec l'ordre des réponses inversé, et l'ordre inversé aussi à l'inférence (TTA).
  Côté inférence, une observation précieuse : **pour une classification (un seul token produit), INT8 bitsandbytes
  était plus rapide que GPTQ et AWQ**, qui ralentissent le premier token ; tri des textes par longueur, répartition
  équilibrée entre GPU, contexte de 4 000 à 8 000 tokens au lieu de 2 000.
  Limite à garder en tête : un participant du WSDM Cup 2025 rapporte n'avoir rien gagné avec la même recette.
  Le gain d'un pré-entraînement voisin dépend donc de la proximité réelle entre les deux tâches : **il se mesure, il ne se suppose pas.**

### L1. Données (souvent le levier le plus rentable)
| Technique | Pourquoi ici | Faisab. | Prio. |
|---|---|---|---|
| **Pré-entraînement sur une tâche voisine étiquetée (Danube)**, puis fusion de la LoRA et nouvelle tête. Candidats : MorFITT avant DiaMED (spécialités puis chapitres CIM-10), FrenchMedMCQA, similarité générale en français avant CLISTER, autres tâches DrBenchmark | Équivalent direct d'UltraFeedback pour LMSYS : beaucoup de données proches avant peu de données cibles | F | P1 |
| Pré-entraînement continu sur corpus médical français (DAPT, ex. corpus NACHOS de DrBERT si accessible) | Le vocabulaire des comptes rendus est loin du web généraliste | C (petit élève, quelques centaines de millions de tokens) | P2 |
| Données synthétiques générées par le professeur (cas cliniques fictifs par classe rare) | DiaMED n'a que 739 cas et des chapitres CIM-10 très rares | F | P1 |
| Correction du bruit d'étiquettes : désaccords professeurs / étiquette relus (WSDM 2025), apprentissage « confiant » (cleanlab) | Les annotations médicales sont imparfaites ; c'est aussi la « mise en qualité » demandée par l'offre | F | P1 |
| Pseudo-étiquetage itératif (« noisy student ») sur textes non annotés | Exploiter le texte médical sans étiquette, comme le jeu « ut » de LMSYS | F | P2 |
| Déduplication et détection de quasi-doublons entre plis | Éviter des scores gonflés | F | P1 (hygiène) |

### L2. Adaptation des paramètres
| Technique | Pourquoi ici | Faisab. | Prio. |
|---|---|---|---|
| LoRA réglée (rang, alpha, lr, couches ciblées), **référence obligatoire** | Voir leçon 1 | F | P1 |
| rsLoRA (mise à l'échelle stable du rang) | Permet des rangs élevés sans réglage fin du lr | F | P1 (1 drapeau) |
| DoRA (magnitude + direction) | Réduit l'écart avec le fine-tuning complet, +5 à 10 % de VRAM | F | P1 |
| PiSSA (initialisation par valeurs singulières principales) ; LoftQ pour QLoRA | Convergence plus rapide ; LoftQ réduit l'erreur de quantification des professeurs | F | P2 |
| LoRA+ (lr différent pour A et B) | Gain de vitesse annoncé, une ligne de configuration | F | P2 |
| Fine-tuning complet d'un petit élève (≤ 3B, AdamW 8 bits) | Mesurer ce que LoRA laisse sur la table | C | P2 |
| GaLore, sélection de couches (Spectrum) | Fine-tuning quasi complet à mémoire réduite | C | P3 |

### L3. Comment faire classer un LLM
| Technique | Pourquoi ici | Faisab. | Prio. |
|---|---|---|---|
| Tête de classification sur le dernier token (méthode LMSYS) | Référence de la compétition | F | P1 |
| « Verbaliseur » : probabilités des tokens d'étiquette générés (« Chapitre IX ») | Exploite le savoir du modèle sur le nom des classes, utile quand il y a peu d'exemples | F | P1 |
| Attention bidirectionnelle (type LLM2Vec) + mise en commun des représentations | Les décodeurs ne voient pas la suite du texte ; les comptes rendus se lisent en entier | C | P2 |
| Troncature par le milieu (WSDM) ou tête + fin ; découpage en morceaux puis agrégation | Les comptes rendus dépassent souvent 1 024 tokens | F | P1 |
| Pour CLISTER : les deux ordres de la paire dans le même pas (WSDM), prédiction symétrisée | La similarité est symétrique, le modèle doit l'être aussi | F | P1 |

### L4. Pertes et déséquilibre des classes
| Technique | Faisab. | Prio. |
|---|---|---|
| KL directe, KL inverse, KL « asymétrique » (DistiLLM) ; température du professeur | F | P1 |
| Pondération des classes, perte focale, lissage des étiquettes | F | P1 |
| Pondération des professeurs selon leur score hors pli | F | P2 |

### L5. Distillation avancée
| Technique | Pourquoi ici | Faisab. | Prio. |
|---|---|---|---|
| Distillation des **justifications** (« Distilling step-by-step ») : le professeur explique son classement, l'élève apprend étiquette + explication | Gains forts quand les données sont rares ; l'explication est un atout pour un clinicien | F | P1 |
| Distillation « sur politique » (GKD, MiniLLM) : l'élève génère, le professeur corrige ses propres sorties | État de l'art 2025-2026 pour les tâches génératives | C | P2 (piste C) |
| Distillation par séquence (le professeur produit le JSON complet) | Base de la structuration générative | F | P1 (piste C) |

### L6. Post-entraînement génératif (piste C, structuration)
| Technique | Pourquoi ici | Faisab. | Prio. |
|---|---|---|---|
| SFT puis préférences (DPO, ORPO, SimPO, KTO) | Aligner le format et la prudence des sorties | F | P2 |
| **GRPO avec récompense vérifiable** (RLVR) : récompense = F1 des entités extraites + validité du JSON | Méthode dominante en 2025-2026 ; la structuration a une vérité terrain, donc une récompense calculable sans juge | C (élève ≤ 8B, LoRA) | P1 si piste C |
| Décodage contraint par schéma JSON (xgrammar, outlines) | Zéro sortie mal formée, exigence d'un système hospitalier | F | P1 si piste C |

### L7. Fusion de modèles et ensembles
| Technique | Faisab. | Prio. |
|---|---|---|
| Moyenne des LoRA des plis (LMSYS), comparée à l'ensemble des 5 plis | F | P1 |
| TIES, DARE, SLERP, « model soups » ; WiSE-FT (interpolation avec le modèle de base pour la robustesse) | F | P2 |

### L8. Calcul au moment de l'inférence
| Technique | Pourquoi ici | Faisab. | Prio. |
|---|---|---|---|
| TTA (LMSYS) : variantes de troncature, ordres de paire | Robustesse à budget connu | F | P1 |
| Auto-cohérence (plusieurs raisonnements, vote) | Souvent utile en génération ; à mesurer en classification où le raisonnement peut nuire | F | P2 |
| Modèles de raisonnement comme professeurs (traces longues) | Peut améliorer les étiquettes souples sur les cas ambigus | C | P2 |

### L9. Compression et service (contrainte hospitalière)
| Technique | Pourquoi ici | Faisab. | Prio. |
|---|---|---|---|
| GPTQ 8 et 4 bits (LMSYS), AWQ, **INT8 bitsandbytes** | Danube a mesuré bitsandbytes INT8 plus rapide que GPTQ et AWQ en classification (un seul token produit) : la vitesse dépend du type de charge, elle se mesure sur notre tâche | F | P1 |
| Tri par longueur et lots dynamiques ; contexte long (4 000 à 8 000 tokens) contre troncature | Les comptes rendus sont longs : garder plus de texte peut valoir plus que la TTA | F | P1 |
| **FP8 et NVFP4 natifs de Blackwell** (la 5090 les accélère en matériel) | Format d'avenir des serveurs d'inférence ; peu de retours publics sur des tâches médicales françaises | C (support logiciel à valider) | P2 |
| Entraînement conscient de la quantification (QAT) | Limiter la perte au passage en 4 bits | C | P3 |
| Service vLLM ou SGLang, décodage spéculatif | Débit réel d'un service hospitalier | F | P2 (P5) |

### L10. Calibration et abstention (sûreté clinique)
| Technique | Pourquoi ici | Faisab. | Prio. |
|---|---|---|---|
| Mise à l'échelle par température, mesure de l'ECE | Une probabilité doit vouloir dire quelque chose pour un codeur ou un clinicien | F | P1 |
| **Prédiction conforme** : le modèle renvoie un ensemble de classes garanti à 90 % ou s'abstient et passe la main à l'humain | Le bon usage hospitalier : automatiser les cas sûrs, router les autres. Garantie statistique, simple à mettre en œuvre | F | P1 |

### L11. Points de départ et références à battre
**Criblage des points de départ (Danube)** : avant tout réglage, affiner rapidement (1 pli, réglages identiques) plusieurs
modèles déjà spécialisés et garder le meilleur départ, au lieu de supposer que la version « instruct » est la bonne.
Candidats médicaux ouverts à cribler en P0-P1 (licences à vérifier) : MedGemma (Google, 4B et 27B), BioMistral 7B,
Meditron, à côté des modèles généralistes (Qwen, Mistral, Gemma).

| Modèle | Pourquoi |
|---|---|
| DrBERT, CamemBERT-bio | Encodeurs médicaux français : sur peu de données, ils battent souvent les LLM |
| Encodeurs de type ModernBERT français médicaux (ex. doctomodernbert-fr de Doctolib) | Génération d'encodeurs plus récente, contexte long |
| LLM professeur en zéro-shot et en few-shot | Ce que donne « juste un prompt », sans entraînement |

### L12. Évaluation par LLM-juge (pour la génération, cœur de PARTAGES)
Un travail de 2026 (« Who Judges the Judge? ») évalue précisément les LLM-juges sur des questions médicales françaises ouvertes.
Si la piste C produit du texte libre, le juge sera lui-même validé contre un petit jeu annoté à la main, avec
juge distinct du générateur et stabilité mesurée (méthode déjà employée dans Aegis-RCA).

### Comment éviter l'explosion combinatoire
Plus de 40 leviers, chacun avec ses réglages : tout croiser est impossible sur un seul GPU. Règles :
1. **Vagues successives, gloutonnes** : chaque vague part de la meilleure configuration de la précédente.
2. **Budget GPU fixé par vague** avant de commencer, consigné dans le protocole.
3. **Décisions sur les jeux qui ont la puissance statistique** : DiaMED (≈ 150 cas de test) donne des intervalles
   de confiance larges ; les comparaisons fines se font sur MorFITT et CLISTER, ou en validation croisée répétée.
4. Un levier qui ne bat pas la référence réglée est **publié comme résultat négatif** et sort du programme.

### Programme proposé
| Vague | Leviers | Objectif |
|---|---|---|
| V0 | L11 références, LoRA réglée (L2), tête vs verbaliseur (L3) | Savoir où l'on part |
| V1 | **Deux recettes du top 5 de LMSYS, face à face** : distillation (1re place, S1 à S7) contre pré-entraînement sur tâche voisine + criblage des départs (5e place, Danube) | Savoir laquelle des deux philosophies tient sur des textes médicaux français, puis si elles se cumulent |
| V2 | Recette WSDM 2025 : plus de professeurs, correction des étiquettes, synthétiques (L1) | Mesurer l'amélioration publiée depuis |
| V3 | DoRA / rsLoRA / PiSSA (L2), KL et pertes (L4), distillation des justifications (L5) | Gains d'entraînement récents |
| V4 | Fusion (L7), FP8 / NVFP4 contre GPTQ (L9), calibration et prédiction conforme (L10) | Déployable et sûr |
| V5 (option) | Piste C : SFT, GRPO à récompense vérifiable, décodage contraint (L6) | Structuration générative |
