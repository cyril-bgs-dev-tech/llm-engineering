# Checklist TRIPOD-LLM renseignée (P4-10, 07/10/2026)

Guide : Gallifant et al., Nature Medicine 2025 (page wiki `tripod-llm-reporting-guideline`, numérotation des 19 items principaux relue sur le texte brut le 07/10/2026). Type d'étude : **développement (affinage d'un modèle existant) et évaluation**, tâche de **classification**. Statuts : rempli, partiel, non applicable (avec la raison), à compléter par l'auteur. Chaque chiffre renvoie à un run ou à un document du dépôt ; aucun item n'est coché sans preuve.

| Item | Contenu demandé (résumé) | Réponse du projet | Statut |
|---|---|---|---|
| 1 Titre | Étude de développement ou d'évaluation, tâche, population, résultat | « Affiner et distiller des LLM sur des textes cliniques français » : classer le chapitre CIM-10 de comptes rendus fictifs ; à préciser « corpus fictif » dans tout titre sortant | partiel |
| 2 Résumé | Voir le résumé TRIPOD-LLM | `docs/RAPPORT_FINAL_2026-10-07.md` section 1 (question, statut confirmatoire, résultat, verdict « non résolu ») ; pas de résumé structuré au format du guide | partiel |
| 3a Contexte | Cas d'usage et justification | Démonstration méthodologique pour un poste de data science hospitalière : mesurer ce que chaque technique apporte (`PLAN_PROJET_V6.md`) | rempli |
| 3b Population et usage | Population cible, usage dans le parcours de soin | Aucun usage de soin : corpus fictif, aide à la décision exclue (carte de modèle v4, « Usage prévu et hors usage ») | rempli |
| 4 Objectifs | Développement, affinage ou validation | Affinage (LoRA, encodeur) et validation sur test scellé ; comparaisons de techniques (rapport final) | rempli |
| 5a Sources des données | Entraînement, réglage, évaluation | PARHAF (4 254 comptes rendus fictifs), `docs/FICHE_DE_DONNEES_PARHAF.md`, `data/cards/parhaf.md` ; MorFITT en repère externe, `data/cards/morfitt.md` | rempli |
| 5b Description | Distribution des données | Classes très déséquilibrées (chapitre II : 1 153 contre XXII : 31 sur développement et test confondus) ; `results/measures/splits_summary.json` | rempli |
| 5c Dates | Plus ancien et plus récent texte | Les dates de PARHAF sont fictives : à dire ; non relevées | partiel |
| 5d Prétraitement | Qualité et prétraitement | Texte non modifié ; contrôle de quasi-doublons (seuil 0,8), politique des classes rares, quarantaine d'un code invalide ; `PROTOCOLE.md` sections 1 à 4 | rempli |
| 5e Manquants, déséquilibre | Traitement | Quatre chapitres rares fusionnés dans « AUTRE » exclu de la moyenne ; perte pondérée par classe testée (écart non résolu) ; synthétique ciblé non exécuté | rempli |
| 6a Modèle et version | Nom, version, dernière date d'entraînement | Qwen3.5-4B, CamemBERT-bio, TF-IDF : noms et versions au registre (`run_id`) ; dates d'entraînement dans les runs `final-*` | rempli |
| 6b Développement | Architecture et affinage | LoRA rang 16, alpha 32, dropout 0,05, bf16, lot effectif 32, 4 096 tokens, 10 époques ; encodeur 10 époques, taux 1e-4 ; `PROTOCOLE_V2.md`, fiches `experiments/` | rempli |
| 6c Génération, inférence | Invites, réglages | Pas de génération : classifieur à tête ; zéro-shot par invite à noms et définitions de classes (runs `zero-shot-*`) | rempli |
| 6d Sorties | Brutes et post-traitées | Probabilités sur 18 sorties, argmax ; ensembles conformes et abstention en post-traitement | rempli |
| 6e Classification, seuils | Raison et seuils | Pas de seuil de probabilité pour la décision ; conforme LAC à 90 % (calibré au développement), seuil d'abstention par table de couverture ; ADR-016 | rempli |
| 7a Qualité des sorties | Métriques | Macro-F1 sur 17 chapitres (définie avant les runs), exactitude, log loss, ECE, couverture conforme | rempli |
| 7b Pertinence pour l'usage | Lien avec le déploiement | Macro-F1 choisie pour la sensibilité aux chapitres rares ; pas de corrélation à une évaluation humaine | partiel |
| 7c Définition du résultat | Formule, code, date d'inférence | Code au dépôt (`src/llmft`), registre, graine fixée ; modèles ouverts, aucune API | rempli |
| 7d Évaluateurs subjectifs | Qualification, consignes | Audit de 65 erreurs confiantes relu par l'assistante, **sans contre-expertise humaine** ; à compléter | partiel |
| 7e Comparaison | Autres modèles, humains, repères | TF-IDF, encodeur, ensembles, zéro-shot, MorFITT (références publiées vérifiées à la source) ; pas de comparaison à des humains | rempli |
| 8a à 8c Annotation | Si annotation | Non applicable : étiquettes issues du scénario (CIM-10) ou du jeu public ; aucune annotation propre | non applicable |
| 9a, 9b Invites | Si invites | Zéro-shot seulement : une invite fixe, pas de conception d'invite ; à décrire dans RESULTATS | partiel |
| 10 Résumé | Si résumé | Non applicable | non applicable |
| 11 Alignement | Si instruction ou alignement | Non applicable (pas d'instruction tuning) | non applicable |
| 12 Calcul | Machines, temps, coût | RTX 5090 32 Go ; durées et énergie par run au registre ; 46,6 h enregistrées sur B = 90 h ; latence et énergie de service par composante (carte v4) | rempli |
| 13 Éthique | Comité, consentement | Non applicable : corpus fictif, aucune donnée de patient réel ; à formuler ainsi | rempli |
| 14a Financement | Source et rôle | Projet personnel sans financement externe : **à déclarer par l'auteur** | à compléter |
| 14b Conflits d'intérêts | Déclaration | **À déclarer par l'auteur** | à compléter |
| 14c Protocole | Accès | `PROTOCOLE.md`, `PROTOCOLE_V2.md`, instantanés hachés dans `experiments/INDEX.md` | rempli |
| 14d Enregistrement | Registre externe | Non enregistré dans un registre public : préenregistrement interne par fiches hachées avant les runs | partiel |
| 14e Disponibilité des données | Données | PARHAF et MorFITT publics sous leurs conditions ; scripts à révision épinglée et empreintes ; dépôt de code privé (ADR-008) | rempli |
| 15 Implication des patients et du public | Si applicable | Aucune : corpus fictif | rempli |
| 16a Flux | Documents du début à l'analyse | 4 254, 4 220 avec code résolu, 4 219 utilisés ; test scellé 633 ; développement 3 586 en cinq plis de 717 à 718 ; plis par auteur de 663 à 763 ; 104 auteurs | rempli |
| 16b Caractéristiques | Par source et par partition | `results/measures/splits_summary.json`, fiche de données | rempli |
| 16c Variables cliniques | Distribution | Spécialités et types de documents décrits ; âge et sexe non analysés | partiel |
| 16d Effectifs par analyse | Par analyse | Chaque tableau du rapport donne son périmètre (pli, nombre de graines, patients) | rempli |
| 17 Performance | Selon les métriques prévues | Test scellé : G 0,8131, +7,28 [+1,55 ; +12,62] contre le TF-IDF, non résolu ; run `20261006-210015-ouverture-test-scelle-g` | rempli |
| 18 Mise à jour | Si mise à jour du modèle | Non applicable à ce jour (une seule version gelée) | non applicable |
| 19a Interprétation | Résultats principaux, équité | Rapport final section 1 et 3 ; **équité par sous-groupe non analysée** (spécialités et auteurs partiellement : `RESULTATS.md`) | partiel |
| 19b Limites | Biais, incertitude, généralisation | Rapport final section 6 ; carte v4 | rempli |
| 19c Difficultés des données | Représentation, harmonisation | Chapitres rares, signature d'auteur d'environ 2 points, étiquettes dérivées d'un scénario, corpus fictif | rempli |
| 19d Usage visé | Entrée, utilisateur, supervision | Aide à la décision, supervision humaine requise, aucun usage clinique (carte v4) | rempli |
| 19e Entrées de mauvaise qualité | Gestion | Fragilité du LoRA à la fin du texte documentée (runs de robustesse) ; abstention par ensemble conforme ; **pas de procédure de rejet d'entrée** | partiel |

**Bilan** : 19 items principaux, 50 sous-items ; sur les 43 lignes ci-dessus (certaines regroupent des sous-items), 27 remplies, 10 partielles, 4 non applicables, 2 à compléter par l'auteur (financement, conflits d'intérêts). Ce n'est pas un rapport soumis à une revue : la checklist guide le rapport final et sera rejouée si le rapport sort du dépôt.
