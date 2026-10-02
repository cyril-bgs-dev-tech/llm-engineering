# ADR-008 : dépôt distant GitHub privé et intégration continue (micro-tâche P5-06, avancée sur demande de Cyril)

## Status
**Acceptée** le 02/10/2026 sur demande explicite de Cyril (« push le projet sur mon github, et montes le en CI/CD », puis « tu peux laisser la présentation mais rends le code privé »). Elle remplace la décision 2 de l'ADR-002 (« GitLab privé, plus tard, sur demande ») pour la plateforme ; le reste d'ADR-002 est inchangé.

## Date
2026-10-02

## Context
Le plan et l'offre du CHU citent GitLab, et la feuille de route réservait la CI à l'étape R15 « seulement après création autorisée du dépôt ». Cyril a autorisé la création et demandé GitHub. Son compte suit déjà une convention : une **vitrine publique** et un **dépôt de code privé** reliés par leurs descriptions (`multi-agent-lab` et `multi-agent-lab-code`). Le plan reste le même ici.

## Decision

| Sujet | Décision |
|---|---|
| Dépôt de code | `cyril-bgs-dev-tech/llm-finetuning-code`, **privé** (nom par convention du compte, modifiable en une commande) |
| Vitrine publique | **Non créée.** Cyril a répondu le 02/10/2026 d'attendre un premier résultat de fine-tuning (jalon A). Elle exigera un texte passé par `claim-gate` et ne contiendra aucune donnée ni source brute |
| CI | GitHub Actions, mêmes commandes qu'en local (`make check`, `make smoke`, `pip-audit`), actions **épinglées par SHA** |
| Ce que la CI ne couvre pas | Les tests marqués `gpu` (`make test-gpu`) et ceux qui lisent les données PARHAF, absentes du dépôt : ils restent **locaux** et la CI le dit au lieu de les compter comme verts |
| Déploiement | Aucun service n'existe avant R15 : le « CD » se limite à une release GitHub sur tag `vX.Y.Z`, après rejeu des contrôles. Rien d'autre n'est déployé |
| Dependabot | Actions GitHub seulement : les dépendances Python restent figées par `uv.lock` (la pile torch 2.11 + cu128 est validée par les spikes) |
| Portabilité | Toute la logique est dans le `Makefile` : un futur `.gitlab-ci.yml` (poste du CHU, P5-06) en sera un mince enrobage |

**Précision sur « local-données » (ADR-004).** La définition provisoire disait « aucun texte ni artefact dérivé ne quitte la machine ». Pousser vers un dépôt distant, même privé, la contredit pour les artefacts dérivés. Décision de Cyril, donc : **vont dans le dépôt privé** les identifiants de découpage, les empreintes, les statistiques agrégées et les sources du wiki ; **ne vont jamais** dans un dépôt (privé ou public) les textes du corpus, les prédictions, les poids, les probabilités de professeurs. PARHAF est publié sous CC BY 4.0 et Etalab 2.0, qui permettent la redistribution avec attribution. Vérifié avant le push : sur 300 extraits tirés du corpus, un seul fichier suivi en contient, `knowledge/raw/parhaf-readme-*.md` (la carte officielle du jeu, avec son exemple publié). **Ce fichier et les textes d'articles de `knowledge/raw/` ne doivent jamais aller dans la vitrine publique.**

## Alternatives Considered
- **Un seul dépôt public** : écarté par Cyril ; le protocole repose sur un test scellé qui ne doit pas fuiter.
- **Un seul dépôt privé sans vitrine** : possible, mais Cyril a dit laisser la présentation.
- **CI auto-hébergée avec GPU** : écartée, elle exposerait la machine de Cyril à du code de pull request et n'apporte pas de preuve que le poste local n'apporte déjà.
- **Dependabot sur `uv`** : écarté, une mise à jour automatique de torch invaliderait les spikes.

## Consequences
- **La protection de branche n'est pas disponible** : essayée le 02/10/2026, GitHub répond 403 (« Upgrade to GitHub Pro or make this repository public »). Le dépôt reste privé. Conséquence : la CI signale un échec mais rien n'empêche un push direct sur `main` ; la discipline repose sur le crochet pré-commit local (`make check-fast`) et sur la lecture du résultat de la CI. Si Cyril passe à GitHub Pro, il suffit de rendre les deux jobs obligatoires.
- Premier run vert sur GitHub : 169 s. Il a d'abord échoué sur 20 erreurs EXE001, que la machine locale ne voyait pas (drvfs affiche tout en `rwx`, `core.fileMode=false`) ; le bit exécutable des scripts à shebang est désormais enregistré dans l'index, sans toucher à une règle de ruff.
- L'exception W1 de `pip-audit` expire le 2026-12-31 : la CI échouera alors si elle n'est pas réexaminée, ce qui est voulu.
- L'ADR-002 reste vraie pour le périmètre, la démo locale et la date limite.
