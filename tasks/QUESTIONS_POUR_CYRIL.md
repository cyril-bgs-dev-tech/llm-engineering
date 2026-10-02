# File de questions pour Cyril

Règle : une ligne par décision, un défaut recommandé, ce que la question bloque. Je n'applique un défaut que s'il est accepté au § 11 de `CONTRAT_DE_TRAVAIL.md` ou par la feuille de route. Une réponse en une ligne suffit (« Q1 : oui », « Q4 : 15 h »).

| # | Date | Question | Défaut recommandé | Bloque |
|---|---|---|---|---|
| Q1 | 02/10/2026 | Valides-tu `tasks/CONTRAT_DE_TRAVAIL.md` (cases du § 11) ? | Oui | Les points « sous réserve de validation » |
| Q3 | 02/10/2026 | Valides-tu `SPEC-P0.md` (RM-04) ? | Oui | Clôture de R0 |
| Q4 | 02/10/2026 | Date limite de candidature au CHUGA et jalon visé (ADR-002) | Aucune connue ; jalon B en passant par A | Choix du périmètre en R6 |
| Q5 | 02/10/2026 | **B** (heures GPU du premier cycle), **N** (essais de réglage par famille), **K** (graines, au moins 5), **seuil « pratiquement utile » δ** (ADR-004, ADR-007 : défaut 2,0 points de macro-F1, jugement de valeur) | Je propose des valeurs chiffrées après P0-08, P0-45 et RM-16 ; tu les fixes | Gel de `PROTOCOLE.md` (P0-46), G-P0, tout run comparatif |
| Q6 | 02/10/2026 | MedGemma : acceptes-tu toi-même les conditions Hugging Face (ADR-001) ? | Non, reste en R12 | Comparaison modèle médical contre généraliste |
| Q7 | 02/10/2026 | Autorises-tu une demande aux auteurs de PARHAF (accès au test embargoé, écart entre le parquet et le JSON) ? Action externe : je rédige seulement un brouillon | Brouillon seul, tu l'envoies si tu veux | Confirmation externe, plan de confirmation (P0-31) |
| Q8 | 02/10/2026 | Ollama occupe 1,4 Go de VRAM sur la RTX 5090 (processus que je n'ai pas lancé). Faut-il le garder tel quel ? | Oui, je compte cette VRAM dans `vram-preflight` | Marge de VRAM des gros professeurs |
| (Q2 traitée) | 02/10/2026 | Commit et push : demandés explicitement par Cyril le 02/10/2026 ; historique de 11 commits atomiques, dépôt privé `llm-finetuning-code` (ADR-008) | n/a | n/a |
| (Q9 traitée) | 02/10/2026 | Vitrine publique : Cyril a répondu « attendre un premier résultat ». Aucun dépôt public ; à recréer au jalon A (`claim-gate`, README seul, sans donnée ni source brute) | n/a | n/a |
