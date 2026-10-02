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
| Q11 | 02/10/2026 | **N** (essais de réglage par famille) : 4, soit les quatre taux d'apprentissage de P1-13, même budget de réglage pour la référence et chaque variante ? **Niveau de couverture conforme** : 90 % ? **Ratifies-tu l'estimand et la règle de décision d'ADR-007** (bootstrap hiérarchique, famille de 3 comparaisons, verdict en trois valeurs) pour cocher RM-11 ? | N = 4 ; 90 % ; oui | Gel de `PROTOCOLE.md` (P0-46), G-P0, tout run comparatif |
| (Q2 traitée) | 02/10/2026 | Commit et push : demandés explicitement par Cyril le 02/10/2026 ; historique de 11 commits atomiques, dépôt privé `llm-finetuning-code` (ADR-008) | n/a | n/a |
| (Q9 traitée) | 02/10/2026 | Vitrine publique : Cyril a répondu « attendre un premier résultat ». Aucun dépôt public ; à recréer au jalon A (`claim-gate`, README seul, sans donnée ni source brute) | n/a | n/a |
