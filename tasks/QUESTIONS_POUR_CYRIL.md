# File de questions pour Cyril

Règle : une ligne par décision, un défaut recommandé, ce que la question bloque. Je n'applique un défaut que s'il est accepté au § 11 de `CONTRAT_DE_TRAVAIL.md` ou par la feuille de route. Une réponse en une ligne suffit (« Q1 : oui », « Q4 : 15 h »).

| # | Date | Question | Défaut recommandé | Bloque |
|---|---|---|---|---|
| Q1 | 02/10/2026 | Valides-tu `tasks/CONTRAT_DE_TRAVAIL.md` (cases du § 11) ? | Oui | Les points « sous réserve de validation » |
| Q3 | 02/10/2026 | Valides-tu `SPEC-P0.md` (RM-04) ? | Oui | Clôture de R0 |
| Q4 | 02/10/2026 | Date limite de candidature au CHUGA et jalon visé (ADR-002) | Aucune connue ; jalon B en passant par A | Choix du périmètre en R6 |
| (Q5 traitée en partie) | 02/10/2026 | Cyril a fixé le 02/10/2026 : δ = 2,0, K = 5, B = 90 h. Reste N, voir Q11 | n/a | n/a |
| Q6 | 02/10/2026 | MedGemma : acceptes-tu toi-même les conditions Hugging Face (ADR-001) ? | Non, reste en R12 | Comparaison modèle médical contre généraliste |
| Q7 | 02/10/2026 | Autorises-tu une demande aux auteurs de PARHAF (accès au test embargoé, écart entre le parquet et le JSON) ? Action externe : je rédige seulement un brouillon | Brouillon seul, tu l'envoies si tu veux | Confirmation externe, plan de confirmation (P0-31) |
| Q8 | 02/10/2026 | Ollama occupe 1,4 Go de VRAM sur la RTX 5090 (processus que je n'ai pas lancé). Faut-il le garder tel quel ? | Oui, je compte cette VRAM dans `vram-preflight` | Marge de VRAM des gros professeurs |
| Q10 | 02/10/2026 | A2 (5e LMSYS, Team Danube) et A3 (1er WSDM Cup 2025) : leurs pages Kaggle ne se chargent pas hors navigateur. Peux-tu coller le texte des deux solutions (ou me donner un export) ? Sinon je les laisse non ingérés | Je continue sans, et je dis que ces deux sources ne sont pas lues | Fin de RM-18 (A2 et A3), avant leur première utilisation (P2-07, P3) |
| (Q11 traitée) | 03/10/2026 | Cyril a fixé N = 4, niveau conforme 90 %, et accepté ADR-007 ; relecteur local autorisé ; commit et push autorisés pour le lot en cours | n/a | n/a |
| Q12 | 02/10/2026 | **Risque de puissance sur δ = 2,0** : une esquisse simulée (run `20261002-200851-power-sketch-ic-width`) donne un intervalle de 7,5 à 13,5 points de large sur le test scellé, contre 4 admis par ADR-007. Je ne change rien sans toi. Options si RM-15 le confirme : garder δ = 2,0 et accepter « non résolu » comme résultat attendu ; relever δ ; élargir le test (changer la part de 15 %, ce qui touche des partitions figées, donc une nouvelle version) ; ou déclarer la comparaison exploratoire | Attendre RM-15 avec les vraies prédictions, puis décider | Gel de `PROTOCOLE.md` si tu veux trancher avant |
| Q13 | 03/10/2026 | Suite à la relecture adversariale de `PROTOCOLE.md`, cinq confirmations avant le gel (C1 à C5, `PROTOCOLE.md` 6.10) : repli si la règle de puissance échoue ; budget du réglage égal des variantes (B = 90 h insuffisant selon la section 5) ; ratification d'ADR-009 ; confirmation des sections 1 à 4 ; comparaisons TF-IDF et encodeurs EXPLORE | Défauts écrits dans 6.10 | P0-46, G-P0 |
| Q14 | 03/10/2026 | Seconde relecture de `PROTOCOLE.md` : trois confirmations avant le gel (C6 à C8, 6.10) : 2 époques pour toutes les recettes ; budget (B = 90 h ne tient pas avec le Qwen3.5-9B en pessimiste) ; risque d'une graine divergente et probabilité faible de verdict résolu | Défauts écrits dans 6.10 | P0-46, G-P0 |
| Q15 | 03/10/2026 | **Métrique de décision** : garder la macro-F1 (17 chapitres) comme seul critère confirmatoire, ou y ajouter la **différence appariée de log loss** comme co-critère (variance plus faible attendue, non mesurée) ? Changer la primaire exige une ADR à partir de P1-02, donc c'est le moment le moins coûteux. La log loss est déjà publiée en secondaire | Garder la macro-F1 primaire ; publier la log loss appariée à côté, sans verdict | Nouvelle version du protocole (hors gel : ADR) |
| Q16 | 03/10/2026 | **Mesures secondaires dans les fiches de P1** : préenregistrer la log loss équilibrée par chapitre (G, `docs/METRIQUE_UNIFIEE_2026-10-03.md`) comme métrique secondaire rapportée avec son erreur-type dans chaque fiche, sans toucher au critère confirmatoire gelé ? | Oui (appliqué par défaut dans mes fiches de nuit, réversible) | Lecture des runs de P1 ; pas d'effet sur le gel |
| Q17 | 03/10/2026 | **Fenêtre glissante** (papier sliding-window) : une ablation « fenêtre glissante » sur un élève (fiche préenregistrée à part, GPU) vaut-elle le temps ? Mon avis : non, nos Qwen3.5 sont des hybrides natifs que les auteurs excluent et nos textes demandent l'attention complète | Non, rien d'ajouté à la feuille de route | Aucun ; remplaçable plus tard |
| Q18 | 03/10/2026 | **RM-14, raccourci d'auteur « signalé »** sur le TF-IDF du chapitre : macro-F1 0,684 par patient contre 0,646 par auteur, écart +3,87 points IC 95 % [+1,27 ; +6,31] (ADR-011 proposée). Garder la métrique primaire gelée par patient et rapporter les deux chiffres (ma recommandation), ou ouvrir une v2 du protocole avec plis groupés par auteur ? | Garder le gel, rapporter les deux, étendre la grille TF-IDF pour départager | Aucun avant RM-15 ; le test scellé est stratifié, non groupé |
| Q19 | 03/10/2026 | **Pourquoi les LLM sont sous le TF-IDF** : analyse d'erreurs du pli 0 (runs `p1-23-errors-p1-11-*`) : le Qwen3.5-9B a une exactitude de 0,788 (TF-IDF 0,818) mais **F1 nulle sur les chapitres rares** XII (6 patients), XXI (8), XXII (5) ; la macro-F1 compte chaque chapitre pareil. Piste : une perte pondérée par classe (poids en 1/√n) changerait la recette de référence, donc pas sans fiche. Autorises-tu une fiche d'exploration (Qwen3.5-4B, pli 0, un taux) avec perte pondérée, statut EXPLORE, qui n'entre pas dans le choix de l'élève ? | Oui, une exploration à un run, après P1-11 | Aucun avant la fin de P1-11 |
| (Q2 traitée) | 02/10/2026 | Commit et push : demandés explicitement par Cyril le 02/10/2026 ; historique de 11 commits atomiques, dépôt privé `llm-finetuning-code` (ADR-008) | n/a | n/a |
| (Q9 traitée) | 02/10/2026 | Vitrine publique : Cyril a répondu « attendre un premier résultat ». Aucun dépôt public ; à recréer au jalon A (`claim-gate`, README seul, sans donnée ni source brute) | n/a | n/a |

## Décisions prises par délégation (Cyril, 03/10/2026 : « pour chaque décision humaine en attente, fais le choix le plus professionnel »)

Réversibles par une ligne de Cyril. Les exclusions de N23 restent : test scellé, protocole gelé, push, location ou API payante, lecture hors dossier.

| # | Décision | Motif |
|---|---|---|
| Q1, Q3 | Oui : contrat de travail et SPEC-P0 validés | Rien n'est en contradiction avec le protocole gelé ; sans validation, le suivi par cases reste ouvert pour rien |
| Q4 | Aucune date connue ; jalon B en passant par A | Seule option sans hypothèse inventée |
| Q6 | Non, MedGemma reste en R12 | Accepter des conditions Hugging Face est un acte personnel de Cyril, je ne peux pas le faire à sa place |
| Q7 | Brouillon seul, jamais envoyé par moi | Action externe, hors des bornes ; brouillon dans `docs/BROUILLON_DEMANDE_PARHAF.md` |
| Q8 | Oui, Ollama reste en place, 1,4 Go comptés au pré-vol | Règle du projet : un processus que je n'ai pas lancé reste en place |
| Q10 | Continuer sans A2 et A3, dire qu'elles ne sont pas lues | Aucune source inventée |
| Q12 | Garder δ = 2,0 ; « non résolu » est un résultat attendu et annoncé d'avance | Le protocole est gelé ; la règle RM-17 de puissance décidera du design confirmatoire |
| Q13, Q14 | Défauts écrits dans 6.10 du protocole | Déjà intégrés au gel |
| Q15 | Macro-F1 seule critère confirmatoire ; log loss appariée publiée en secondaire sans verdict | Un co-critère passerait Bonferroni de 98,33 à 99,17 % et aggraverait « non résolu » ; avis concordant de GLM |
| Q16 | Oui, log loss équilibrée rapportée avec erreur-type en secondaire | Applique déjà par défaut ; sans effet sur le gel |
| Q17 | Non à l'ablation de fenêtre glissante | Les Qwen3.5 sont des hybrides natifs ; budget mieux employé ailleurs |
| Q18 | Garder le gel, rapporter les deux chiffres ; ADR de repli préparée (fiches à écrire) ; lectures de RM-14 étiquetées « non tranchées » | Le test scellé estime de nouveaux patients du même corpus ; avis concordant de GLM. Élément nouveau : l'identifiant d'auteur n'apparaît dans le texte que pour 1 patient sur 4 254, la fuite par identifiant explicite est donc exclue |
| Q19 | Oui : une exploration EXPLORE à un run, **sur le Qwen3.5-9B à 1e-4** (meilleur candidat, comparaison appariée au run non pondéré du même taux, un seul changement : poids 1/√n), pli 0, après le lot P1-11 ; n'entre pas dans le choix de l'élève | Le 4B n'a pas de référence au même taux ; le 9B donne la comparaison la plus propre |
| Poids Gemma-4-31B (58 Go) | À conserver | Candidat professeur de P2 ; les retélécharger coûterait plus que le disque |
| Adoption de flash-linear-attention | Oui, après la fin du lot P1-11 (pas pendant), avec contrôle de la prise en charge sm_120, test, et mesure avant/après de débit et de perte | Gain de débit probable sur les hybrides ; ne jamais changer l'environnement en cours de lot |
| Push des commits | Non | Seul Cyril le demande (règle ferme) |
| Cahier GLM | Fait : réponse reçue et triée (`docs/AUDIT_GLM_v3_TRIAGE.md`) | |
| RM-17 (porte go/no-go) | **Décision déléguée, provisoire** : la distillation se poursuit comme question scientifique jusqu'à la porte réelle, qui reste après P1-19, P1-20 et la règle de puissance ; aucun run de professeur (P2-01) avant ce verdict | Le LoRA (4B, 0,587) domine l'encodeur (0,448) mais pas le TF-IDF (0,697 au même pli) ; décider plus tôt serait décider sans la largeur d'intervalle que la porte exige. Un professeur ne s'entraîne qu'après RM-17 |
