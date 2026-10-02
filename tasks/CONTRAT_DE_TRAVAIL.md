# Contrat de travail autonome (journée du 02/10/2026)

Statut : **proposé par Claude à la demande de Cyril** (« un contrat de travail long afin de pouvoir avancer toute la journée sans avoir besoin de moi »). Il entre en vigueur pour les points marqués « sous réserve de validation » dès que Cyril coche la case du § 11 ; tout le reste s'applique tout de suite, parce que ce contrat n'ajoute aucun droit à ceux de `CLAUDE.md` et de `roadmap_unifié.md` : il les transforme en procédure.

Hiérarchie : `CLAUDE.md` et `CONSTRAINTS.md` priment sur ce contrat ; la feuille de route fixe l'ordre ; `MICROTACHES.md` fixe la preuve de fin de chaque tâche. En cas de doute, la règle la plus prudente s'applique et la question va dans la file (§ 6).

## 1. But de la journée

Avancer dans l'ordre de `roadmap_unifié.md` aussi loin que les portes le permettent, en ne laissant derrière moi que des états **prouvés** (tests verts, `run_id`, ADR datée) et une file de questions courte, prête à recevoir une réponse en une ligne.

Point de départ vérifié à la reprise après le crash de WSL (02/10/2026) : R0 à R3 faites sauf P0-02, RM-03, RM-04 (attendent Cyril) et RM-09 (fil synthétique rejoué sur environnement propre) ; 43 tâches cochées sur 165 ; `make check-fast` vert ; GPU libre hormis Ollama (1,4 Go de VRAM, non lancé par moi, il reste en place).

## 2. Boucle de travail (chaque tâche)

1. **Choisir** la première tâche non cochée de `tasks/todo.md` dont les dépendances sont cochées et qui ne figure pas au § 5 comme réservée à Cyril. Si elle est bloquée, passer à la suivante *de la même étape ou de l'étape suivante seulement si* la feuille de route ne la sépare pas par une porte (§ 4).
2. **Charger les skills** de l'étape (liste en tête de chaque étape de la feuille de route) puis les suivre. Pour une expérience : `experiment-preregistration` avant le run.
3. **Test d'abord** (`test-driven-development`), code minimal, `make check-fast` après chaque édition.
4. **Prouver** : exécuter la commande de la « preuve de fin » de `MICROTACHES.md`. `make check` en fin de tâche.
5. **Consigner** : `run-registry` pour tout run ; ADR pour toute décision ; wiki pour tout savoir durable (`wiki-ingest` ou `wiki-update`) ; `tasks/JOURNAL.md` pour chaque tâche (ce qui a été fait, preuve, prochain pas).
6. **Cocher** la case dans `tasks/todo.md` seulement avec la preuve citée dans le journal. Après tout changement de `MICROTACHES.md` ou de la feuille de route : `python3 scripts/check_microtasks.py` et `python3 scripts/check_roadmap.py`.
7. **Recommencer.** Une tâche qui dépasse environ 2 heures se découpe (règle 8 de la feuille de route).

Le journal et `tasks/todo.md` sont la mémoire de la journée : si le contexte est compacté ou si WSL replante, je reprends à partir d'eux et de `git status`, pas de ma mémoire.

## 3. Ce que je fais sans demander

- Écrire et modifier du code, des tests, des documents, des ADR et des pages wiki **dans ce dossier**.
- Lancer les vérificateurs et les tests, y compris les tests GPU courts.
- Télécharger des **poids de modèles sans accès conditionné** (liste de l'ADR-001) vers le cache du projet `artifacts/hf_cache` (`HF_HOME` positionné par les scripts ; ignoré par Git), et installer des dépendances figées (`uv sync --frozen`, jamais d'ajout sans audit de licence P0-12 et mise à jour de `docs/LICENCES.md`).
- Lire des sources publiques (articles, cartes de modèles, documentation) pour `wiki-ingest` et `source-driven-development`. Rien du projet n'est envoyé à ces sites.
- Lancer des entraînements et des bancs sur la RTX 5090, **après** `vram-preflight`, dans les plafonds du § 7.
- Utiliser les relecteurs locaux `code-reviewer`, `test-engineer`, `security-auditor` (`.claude/agents/`) et la contre-lecture en contexte neuf d'un sous-agent local. Un sous-agent ne lance jamais de GPU et n'écrit que dans `docs/`, `knowledge/` ou `tasks/`.
- Régénérer `tasks/` par `python3 scripts/check_roadmap.py --export`.
- Écrire des décisions **provisoires** avec défaut recommandé, datées, marquées « à ratifier », quand la feuille de route les autorise (§ 4 et § 5).

## 4. Portes d'arrêt : comment je les traite seul

À chaque porte (RM-08, RM-15, RM-17, RM-19, RM-21, G-P0 à G-P5), j'écris l'ADR ou la scorecard avec **les chiffres et les preuves**, puis :

| Verdict | Ce que je fais |
|---|---|
| « Continuer », preuves nettes, étape suivante peu coûteuse et réversible (CPU, code, document) | Je continue ; l'ADR porte la mention « provisoire, à ratifier par Cyril » |
| « Continuer », mais l'étape suivante engage du GPU long ou une décision de Cyril du § 5 | Je prépare tout ce qui est indépendant, j'arrête devant la dépense, je pose la question (§ 6) |
| « Simplifier » ou « arrêter » | **Je m'arrête sur cette branche**, je documente, je propose le repli, j'attends. Je ne contourne jamais une porte qui dit non |
| Spike bloquant en échec (règle 7) | Je m'arrête et je présente le plan B (plan V6, § 9). Rien d'autre ne démarre qui en dépende |

Une porte ne se franchit jamais sur une impression : sans preuve citée, la note est absente et le plan de rattrapage écrit.

## 5. Réservé à Cyril : je prépare, je ne tranche pas

| Sujet | Pourquoi | Ce que je prépare pendant ce temps |
|---|---|---|
| `git commit`, push, dépôt distant, visibilité (RM-03) | Règle ferme de `CLAUDE.md` | Plan de commits atomiques (`git-workflow-and-versioning`), liste des fichiers, gitleaks vert, `git check-ignore` prouvé : un seul « oui » suffit |
| Validation de `SPEC-P0.md` (RM-04) | Elle clôt R0 | Le document est à jour avec l'état réel |
| P0-02 : date limite et jalon (ADR-002) | Seule la date manque ; les autres défauts sont appliqués | Question dans la file |
| **B, N, seuil « pratiquement utile »** (ADR-004) | Bloquent le gel de `PROTOCOLE.md` (P0-46), donc R5 et tout run comparatif | Proposition chiffrée à partir de P0-08, P0-45 et RM-16, avec trois valeurs (hypothèse, mesure, marge) |
| MedGemma, conditions d'accès (ADR-001) | Acte personnel : jamais à ma place | La comparaison reste en R12 |
| Location de GPU, API payante (ADR-003) | Dépense | Aucune ; fiche R-01 non remplie sans déclencheur |
| Revue croisée Codex ou Gemini, `wiki-audit strong` | Le contenu quitte la machine | Revue locale seulement |
| Ouverture du test scellé (RM-20) | Irréversible, une seule fois | Script prêt et testé sur la tâche jouet ; jamais lancé sur la vraie partition sans accord explicite |
| Relecture d'étiquettes (P2-06) | Tu n'es pas clinicien, Cyril fixe la limite | `cleanlab` seulement, aucune étiquette modifiée |
| Toute sortie hors du dépôt (README public, CV, LinkedIn, lettre, demande aux auteurs de PARHAF) | `claim-gate` et envoi externe | Brouillons dans `docs/`, jamais envoyés |
| Modifier `CONSTRAINTS.md` ou le plancher de `scorecards/` | Interdit d'affaiblir | Je propose un diff, je ne l'applique pas |

## 6. File de questions

`tasks/QUESTIONS_POUR_CYRIL.md` : une question = un identifiant, la décision, le **défaut recommandé**, ce qu'elle bloque, la date. Je ne pose pas de question en cours de journée : j'écris dans la file et je continue sur ce qui est indépendant. Je ne comble jamais une décision ouverte par une supposition ; un défaut recommandé n'est appliqué que s'il est écrit au § 11 ou dans la feuille de route comme réponse provisoire acceptée.

## 7. Ressources et plafonds

| Ressource | Plafond de la journée |
|---|---|
| GPU | Un seul processus à la fois que j'ai lancé ; aucun run isolé de plus de 2 h ; au plus 8 h de GPU cumulées ce jour ; marge d'au moins 10 % de VRAM après `vram-preflight`, en comptant les 1,4 Go qu'Ollama occupe déjà |
| Processus étrangers | Ollama ou tout autre processus GPU que je n'ai pas lancé : signalé dans le journal, jamais arrêté, jamais redémarré |
| Disque | Poids dans `artifacts/hf_cache` (dans le dossier du projet, ignoré par Git, sur `/mnt/d` : environ 160 Go libres) ; si l'espace manque pour un gros professeur, je le dis et je propose un emplacement ext4 au lieu de l'inventer. Un seul professeur de plus de 50 Gio à la fois ; je ne supprime que ce que j'ai créé et qui est reproductible. **Je ne lis ni ne liste jamais `~/.cache` ni aucun autre dossier de ton home** (règle globale de `CLAUDE.md`) |
| Réseau | Poids ouverts, paquets figés, sources publiques ; pas d'envoi de texte du corpus ni d'artefact dérivé |
| Argent | Zéro |
| Mémoire | RAM visible dans WSL : 68 Go ; un chargement qui s'en approche passe par `vram-preflight` avant |

Le plafond de GPU de la journée est un garde-fou de cette session, **pas le budget B** du protocole, qui reste à fixer par Cyril (§ 5).

## 8. Interdits absolus (rappel, sans exception)

Donnée de patient réel ; secret ou jeton dans le dépôt, dans un journal ou dans une réponse ; lecture hors du dossier du projet ou de ses caches de poids sans l'accord de Cyril ; ouverture de fichiers d'identifiants ; commit sans demande ; affaiblissement de `CONSTRAINTS.md` (seuil relevé pour passer, test sauté ou supprimé, assertion retirée, `# noqa` ou `type: ignore` pour faire taire) ; chiffre sans `run_id` ; écrasement d'un run ou d'un fichier figé ; allégation clinique ; affirmation sortante non passée par `claim-gate` ; tiret cadratin dans un texte de candidature ; deviner un nom de classe, de modèle ou de tâche dans le noyau `src/llmft/`.

## 9. Quand je m'arrête de moi-même

1. Tout ce qui est possible sans Cyril est fait et la file de questions contient le reste : je rédige le **compte rendu de fin de journée** (§ 10) et je m'arrête.
2. Un test, `make check` ou un vérificateur reste rouge après deux tentatives de correction de la cause : je m'arrête sur cette branche (`debugging-and-error-recovery`), je consigne l'état exact, je ne contourne pas.
3. Un résultat surprenant (score trop beau, écart énorme entre plis) : `leakage-guard` avant toute suite ; le résultat n'est pas cru tant que la fuite n'est pas écartée.
4. Un événement système (WSL replante, GPU en erreur, disque presque plein) : je constate d'abord (`nvidia-smi`, `df`, `git status`), je consigne, je reprends depuis le dernier état prouvé.
5. Une règle de ce contrat me semble gêner : je ne la contourne pas, je note la question.

## 10. Compte rendu de fin de journée

Dans `tasks/JOURNAL.md`, en tête, à la fin de la session ou à l'arrêt : (1) cochées aujourd'hui, avec la preuve de chacune ; (2) ce qui est prouvé, ce qui ne l'est pas ; (3) état de chaque porte rencontrée ; (4) les questions de la file par ordre d'importance, chacune avec son défaut ; (5) processus étrangers et ressources consommées ; (6) la prochaine tâche exacte. Je n'annonce aucune durée, aucun gain, aucun classement sans `run_id`.

## 11. Validation de Cyril

Cocher ou répondre « validé » ; chaque ligne est indépendante.

- [ ] Je valide ce contrat comme cadre de travail autonome.
- [ ] Sous réserve de validation : les défauts de l'ADR-002 (dépôt local, jalon B en passant par A, démo locale) valent réponse provisoire, la date limite restant à fournir.
- [ ] Sous réserve de validation : les plafonds de GPU du § 7 s'appliquent aujourd'hui.
- [ ] Sous réserve de validation : les portes qui disent « continuer » avec preuves nettes se franchissent à titre provisoire (§ 4).

Date de validation : ____ ; remarques : ____
