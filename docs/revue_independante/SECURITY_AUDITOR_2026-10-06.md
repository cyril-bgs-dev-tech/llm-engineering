# Audit de sécurité indépendant (P5-10), 06/10/2026

Périmètre : dépôt versionné (`git ls-files`, 1 732 fichiers, 347 commits), `CLAUDE.md`, `CONSTRAINTS.md`, `data/cards/`, `docs/FICHE_DE_DONNEES_PARHAF.md`, `scripts/*.sh`, `src/llmft/tokenizer_guard.py`, `tokenizer_child.py`, `sealed.py`, `scripts/sealed_evaluation.py`, `uv.lock`, workflows, Dockerfile, Makefile. Lecture seule : aucune commande n'a écrit dans le dépôt, lancé un calcul GPU, lu une étiquette du test scellé ni touché à `data/raw`. Rien n'a quitté la machine.

Méthode : frontières de confiance (fichiers de cache et d'artefacts relus par le code, partitions et marqueur du test scellé, scripts lancés avec des variables d'environnement, dépendances tirées d'un registre), puis STRIDE sur chacune. Les constats sont classés bloquant, important, mineur.

## Résumé

- Bloquant : 0
- Important : 6
- Mineur : 9

Aucun secret, aucune donnée de patient réel, aucune écriture hors du dossier du projet n'ont été trouvés. Le point faible principal n'est pas une faille exploitable à distance : c'est que la protection du test scellé est procédurale (honneur et journal), pas technique, et que quelques portes d'API contournent la garantie « une seule ouverture » pour qui aurait la main sur le code.

## Constats importants

### I1. `sealed_labels_and_score` laisse l'appelant choisir le marqueur et le mode « répétition »

- Fichier : `src/llmft/sealed.py:71` (paramètres `marker`, `rehearsal`), `:82-85` (branche répétition), `:86` (`open_sealed_test(split, marker, ...)`), `:85` et `:90` (`compute` reçoit les étiquettes brutes).
- Scénario : un appel `sealed_labels_and_score(vraie_partition, full_frame(), "label", {i: None ...}, compute=lambda y, p: {"y": y}, marker=tmp/"m", reason="x", out_path=..., rehearsal=True)` renvoie les étiquettes des 633 patients du test, sans toucher au marqueur réel, et sans ligne de journal si `journal=None`. Même sans `rehearsal`, un `marker` pointant vers un dossier jetable ouvre le test autant de fois qu'on veut. La vérification de couverture des prédictions (`:78`) est vide en pratique : `scripts/sealed_evaluation.py:187` passe `{i: None for i in test_ids}`, les vraies probabilités sont capturées dans la fermeture `compute`.
- Aujourd'hui : le test a été ouvert une seule fois (voir section « Test scellé ») ; le risque porte sur toute affirmation « confirmatoire » future et sur une seconde ouverture par erreur ou après réécriture du code.
- Correctif : ignorer le paramètre `marker` et utiliser une constante absolue dérivée de l'emplacement du module (`Path(__file__).resolve().parents[2] / MARKER_PATH`) ; rendre `rehearsal=True` incompatible avec la vraie partition (refuser si `split["test"]` a l'empreinte `data/splits/parhaf_cim10_chapter.sha256` ; la répétition de `sealed_evaluation.py:152` utilise une partition factice dont l'empreinte diffère) ; rendre `journal` obligatoire (jamais `None` hors tests) ; vérifier que les prédictions sont des vecteurs, pas `None`.

### I2. Le test anti-lecture du test scellé est textuel et contournable ; les étiquettes restent lisibles sans passer par `split["test"]`

- Fichier : `tests/test_sealed_access.py:19-31` (regex `\["test"\]|\.test\b|sealed` sur `src`, `scripts`, `data/scripts` uniquement, fichiers `.py` seulement, lignes commentées exclues).
- Scénario : `parts.get("test")`, `parts[k]` avec `k = "test"`, `for k, v in parts.items()`, un notebook, un `python -c`, un script `.sh`, ou le dossier `tests/` ne sont pas vus. Surtout, aucune lecture du fichier de partitions n'est nécessaire : plusieurs scripts lisent déjà `suggested_scenario` de tous les patients dans le parquet brut (`scripts/make_splits.py:25-31`, `scripts/sealed_evaluation.py:95-97`, `scripts/measure_author_shortcut.py:44`), et les étiquettes du test se déduisent par complément (`~df.id.isin(plis)`). Le garde de code est donc une barrière contre l'erreur involontaire, pas contre un contournement. Constat conforme au plan (le test est un sous-ensemble du jeu public), mais à ne pas présenter comme une garantie technique.
- Correctif : (a) dire dans `PROTOCOLE.md` et la carte de modèle que la garantie est procédurale plus journal ; (b) étendre le test à `tests/`, `*.sh`, `*.ipynb` et aux motifs `.get("test")`, `items()`, `values()` sur le résultat de `load_partitions` ; (c) pour la prochaine phase de test (autre jeu), séparer physiquement les étiquettes du test (fichier chiffré ou gardé hors du dossier de travail, lu seulement par le script d'ouverture).

### I3. Le marqueur et le journal ne sont pas inviolables et rien ne les recoupe

- Fichier : `src/llmft/sealed.py:40` (marqueur créé en mode `x`), `:17-25` (journal en ajout simple), `scripts/sealed_evaluation.py:105-122` (`preconditions`).
- Scénario : `rm data/splits/sealed_opened.marker` (disque Windows monté en 777, aucun attribut immuable possible) rend `check` vert et `open` rejouable ; aucun test ni `make check` ne vérifie que « `results/sealed_result.json` existe implique marqueur présent, une seule ligne `open` au journal, dates égales ». `preconditions` ne vérifie pas non plus l'empreinte des fichiers du temps A contre le registre (`results/runs/*-temps-a-*.json`, champ `metrics.sha256`) : seul leur existence est testée.
- Vérifié à la main aujourd'hui (voir section « Test scellé ») : tout est cohérent. Le risque est la dérive future.
- Correctif : ajouter à `scripts/check_frozen.py` (ou un test) les invariants ci-dessus ; épingler dans `results/frozen_final.json` ou une ADR l'empreinte SHA-256 du marqueur et du journal après ouverture ; poser un tag Git annoté (idéalement signé) sur `e705d4d` ; dans `preconditions`, recalculer le SHA-256 de chaque `*.probs.npz` du temps A et le comparer au registre.

### I4. Désérialisation `pickle` / `joblib` sans intégrité ni authenticité (point 4 de la demande)

- Fichiers : `src/llmft/tokenizer_guard.py:47` (`pickle.loads(out.read_bytes())`), `:67` (`pickle.loads(cache_file.read_bytes())`), `:82` (écriture), `src/llmft/tokenizer_child.py:15` et `:18`, `scripts/sealed_evaluation.py:201` (`joblib.load(FINAL / "tfidf.joblib")`, sans vérification d'empreinte), `src/llmft/serving.py:83-85` (empreinte comparée à celle de `meta.json`, stockée à côté du fichier).
- Risque réel d'exécution de code : faible. Un fichier du cache n'est lu que sur le même poste, par le même utilisateur, dans `artifacts/token_cache` (ignoré par Git, 30 fichiers). Pour y planter un pickle malveillant, il faut déjà pouvoir écrire dans le dossier du projet sous ce compte (alors le code de `src/` est modifiable aussi). Le nom de fichier est un SHA-256 des textes (publics), calculable par un attaquant, donc pas de protection par obscurité. Voies réalistes : restauration d'un dossier `artifacts/` reçu d'un tiers ou d'une sauvegarde non fiable, image Docker partagée, copie du dossier sur le disque Windows monté en 777 (modifiable par tout processus Windows de la session). Le fichier temporaire du fils est dans `tempfile.TemporaryDirectory()` (mode 0700), sans risque. Constat positif vérifié : j'ai parcouru les opcodes des 30 fichiers du cache avec `pickletools` sans les exécuter ; aucun ne contient `GLOBAL`, `STACK_GLOBAL`, `REDUCE`, `INST`, `OBJ`, `NEWOBJ`, `BUILD` : ce sont de simples listes d'entiers.
- Risque réel d'intégrité : moyen. Le cache alimente les prédictions du test scellé (`p1_finetune.build_inputs` appelé par `predict_final`). Sa clé ne contient pas l'empreinte des fichiers du tokenizer (limite déjà notée dans la docstring `:60-64`), et rien ne détecte un fichier altéré mais valide. Un cache altéré fausserait des résultats sans erreur.
- Correctif (proposé, non appliqué) :
  1. Remplacer `pickle` par JSON (`json.dumps(ids)` pour le cache et les échanges père-fils ; les textes passent aussi en JSON) ou par `np.savez_compressed` lu avec `allow_pickle=False` (tableau aplati d'`int32` plus tableau des longueurs). Cela supprime la classe d'attaque.
  2. Écrire à côté de chaque fichier de cache un champ de contrôle : SHA-256 du contenu plus la clé complète, et refuser (et recalculer) si l'un ne correspond pas.
  3. Ajouter à la clé l'empreinte des fichiers `tokenizer.json` / `tokenizer_config.json` du modèle (`huggingface_hub.snapshot_download` renvoie le chemin) pour lever la limite documentée.
  4. Pour `joblib` : vérifier l'empreinte du fichier contre le registre (`results/runs/*final-tfidf*.json`) avant `joblib.load` dans `sealed_evaluation.py:201`, ou sérialiser le TF-IDF sans pickle (vocabulaire et coefficients en `npz` + JSON). `serving.py:83` : épingler l'empreinte dans une source séparée du fichier (registre ou constante), sinon elle ne prouve que l'absence de corruption, pas l'authenticité.
  5. Pour les caches `.npz` de `results/` : tous les `np.load` du dépôt passent `allow_pickle=False` (vérifié par recherche : aucun appel sans), bon point.

### I5. `scripts/cold_rebuild.sh` : `rm -rf` sur un argument non contrôlé, répertoire prévisible dans `/tmp`

- Fichier : `scripts/cold_rebuild.sh:5-7` (`dest="${1:-/tmp/llmft-cold}"` puis `rm -rf "$dest"`), `:9` (journaux écrits en `"$dest.$name.log"`, donc hors du dossier du projet).
- Scénario : `scripts/cold_rebuild.sh ..`, `~`, `/mnt/d/Projets persos` ou une faute de frappe supprime récursivement ce dossier, sans confirmation. Avec le défaut, un autre utilisateur de la machine peut pré-créer `/tmp/llmft-cold` comme lien symbolique (le script suit le lien pour `rm -rf` et pour le clonage ; le dossier appartient alors à un tiers). Peu probable en mono-utilisateur WSL, mais c'est la seule commande destructive des scripts, et la règle du projet interdit `/tmp` pour les écritures temporaires.
- Correctif : `dest="${1:-$(mktemp -d "${TMPDIR:-/tmp}/llmft-cold.XXXXXX")}"` ; refuser tout `dest` existant non vide sans `--force` ; refuser si `realpath "$dest"` est `/`, `$HOME`, `$src` ou un de leurs parents ; ne supprimer que si le dossier contient un fichier témoin créé par le script ; écrire les journaux dans `"$dest/logs"`.

### I6. Entrée de MorFITT incomplète au regard de `dataset-intake` (point 2 de la demande)

- Fichiers : `docs/FICHE_DE_DONNEES_MORFITT.md:5` (« copie locale `data/raw/morfitt/` »), `scripts/morfitt_run.py:22` (`DATA = ROOT / "data/raw/morfitt/source"`), `data/` (aucun `data/cards/morfitt.md`, `data/manifests/morfitt.json`, `data/scripts/download_morfitt.py`), `task_specs/` (aucun contrat `morfitt_specialites`, pourtant prévu par P0-24 : `MICROTACHES.md:92`).
- Scénario : le jeu est public, textuel, sans donnée de patient (fiche : résumés d'articles PubMed / PMC OA) : aucune violation de la règle de fond. Mais la révision et les empreintes ne sont pas épinglées, donc un téléchargement futur peut différer sans alerte, et `scripts/morfitt_run.py` charge un parquet sans vérifier son intégrité ni son contrat de tâche. PARHAF, lui, a un manifeste et un script de rejeu.
- Correctif : créer le manifeste (révision Hugging Face de `DrBenchmark/MORFITT`, 3 fichiers parquet, SHA-256), le script de rejeu sur le modèle de `data/scripts/download_parhaf.py`, la fiche dans `data/cards/`, et vérifier le manifeste au début de `morfitt_run.py`. Licence CC BY-SA 4.0 : tout jeu dérivé redistribué doit porter la même licence (la fiche le dit, le dépôt ne redistribue pas les données : conforme).

## Constats mineurs

- M1. `bash -c "... $LOGDIR ... $FICHE ... $slug ..."` : valeurs interpolées dans une chaîne de commande. `scripts/run_temps_a.sh:11`, `run_lora_final_reprise.sh:11-12`, `run_modeles_finaux.sh:10-18`, `run_morfitt.sh:11-12`, `run_encodeur_auteurs.sh:14`, etc. (plus de 25 lignes). Injection possible seulement si `LOGDIR`, `FICHE` ou `slug` contient `"`, `$`, une apostrophe ou un accent grave ; ces valeurs viennent de l'opérateur, pas d'un tiers, et les espaces de `LOGDIR` sont protégés par `\"`. Correctif : `export LOGDIR FICHE slug` puis `bash -c '... > "$LOGDIR/x.out"'` entre apostrophes, ou une fonction exportée.
- M2. `scripts/run_distillation_imbriquee_reprise.sh:34` : `xargs -I{} bash -c 'IFS=, read j k <<< "{}"; ...'` insère `{}` dans du code shell. `PAIRS` est fabriqué par la boucle du script (chiffres et virgule), donc sûr aujourd'hui ; passer par `xargs -n1 bash -c '... "$1"' _` pour que la donnée ne devienne jamais du code.
- M3. `scripts/run_p1_11.sh:7` et `scripts/run_p1_11_missing.sh` : `LOGDIR="${LOGDIR:-/tmp}"` écrit les journaux dans `/tmp` (hors projet, lisible par les autres comptes, nom prévisible). Mettre `${LOGDIR:?LOGDIR requis}` comme les 40 autres scripts.
- M4. `scripts/silence_watch.sh:11` : `for f in ... $(ls -t ...) $( ... ls -t "$LOGDIR"/*.log ...)` sans guillemets ; un chemin avec espaces (le dossier du projet en contient, `LOGDIR` aussi d'après la mémoire du projet) est coupé, `stat` échoue, la date retombe à 0 et l'alerte de silence se déclenche à tort ou, à l'inverse, ne voit pas l'activité. Défaut de fiabilité, pas de sécurité. Utiliser `find ... -printf '%T@ %p\n' | sort -n | tail`.
- M5. `scripts/mem_guard.sh:9-16` et `run_guarded.sh:12-19` : `kill` sur un PID passé en argument ou capturé, sans vérifier que le PID n'a pas été réutilisé entre `kill -0` et `kill -TERM` (fenêtre de quelques secondes avec `sleep 5`). Risque très faible ; ajouter `kill -0` juste avant `kill -KILL` et comparer `/proc/$pid/cmdline`.
- M6. Chaîne d'approvisionnement des outils : `Makefile:3` exécute `zricethezav/gitleaks:latest` (étiquette flottante, sur l'intégralité du dépôt monté en lecture seule : bien) ; `Dockerfile:2` utilise `ghcr.io/astral-sh/uv:python3.12-bookworm-slim` sans condensat et s'exécute en root (pas de `USER`). Épingler par condensat (`@sha256:`) et ajouter un utilisateur non privilégié. Les actions GitHub sont épinglées par SHA de commit (bien), mais les versions affichées (`v7.0.1`, `v10.2.0`) dépassent ma connaissance : non vérifiables ici.
- M7. Modèles Hugging Face non épinglés : `AutoTokenizer.from_pretrained(name)` et `AutoModelForSequenceClassification.from_pretrained(...)` sans `revision=` ni `use_safetensors=True` (`scripts/sealed_evaluation.py:207-218`, `scripts/final_models.py:58,82`, `scripts/p3_distill.py:82`, `src/llmft/models.py:71-72`, `scripts/morfitt_run.py:83`). Un dépôt de modèle modifié en amont changerait silencieusement les tokenizers ou les poids (seul PARHAF est épinglé). Aucun `trust_remote_code` dans le dépôt (bien). Correctif : épingler la révision de chaque modèle dans `hardware/` ou les contrats, passer `use_safetensors=True`, travailler en `HF_HUB_OFFLINE=1` une fois le cache rempli.
- M8. `.gitleaks.toml:5-7` et `Makefile:3` : le contrôle `dir` ne parcourt que l'arbre de travail, pas l'historique, et la liste d'exclusion couvre `artifacts/` et `data/raw/`. Contrôle de substitution fait ici : balayage de l'historique (347 commits) par motifs `hf_`, `glpat-`, `ghp_`, `AKIA`, clés privées, `Bearer` : aucun résultat ; balayage de l'arbre versionné : aucun. Ajouter `gitleaks git` dans `make check-full`. Compléter `.gitignore` (`.netrc`, `.git-credentials`, `.gitlab_token`, `id_*`, `*.p12`, `*.pkl`, `*.joblib`, `.aws/`).
- M9. Documentation : `docs/FICHE_DE_DONNEES_PARHAF.md:9` dit « test scellé 633 patients (jamais lu) » ; or les textes du test ont été lus 15 fois au temps A (journal, sans étiquette) et le test a été ouvert le 06/10/2026 20:59:42Z. Reformuler : « ouvert une fois le 06/10/2026 (RM-20), étiquettes lues uniquement à cette ouverture ». Autre point de forme : au chemin `open` de `sealed_evaluation.py`, `full_frame()` (`:181`, lit les étiquettes de tous les patients, test compris) s'exécute avant l'écriture du marqueur (`sealed.py:86`, appelée à `:187`) : aucun contenu n'est écrit ni affiché entre les deux, mais l'invariant « marqueur avant toute lecture d'étiquette » n'est vrai qu'au niveau de la fonction `sealed_labels_and_score`, pas du script.
- Hors sécurité stricte : `knowledge/raw/lmsys-blackpearl-readme.md` copie (5 Ko) le README d'un dépôt sans licence, ce que `docs/LICENCES.md` interdit (« se lit et se réimplémente, il ne se copie pas ») ; `knowledge/raw/` versionne aussi le texte complet de neuf articles arXiv et d'un article PMC (733 Ko) : droits de redistribution à vérifier si le dépôt est public (`origin` est sur GitHub ; sa visibilité n'est pas vérifiable hors ligne).

## Test scellé (point 5) : ce que le garde de code garantit réellement

Vérifié par lecture du code et des artefacts, sans lire d'étiquette :

- Seconde ouverture : empêchée par `open(path, "x")` (création exclusive, `sealed.py:40`) puis `AlreadyOpenedError` ; la précondition `preconditions` refuse aussi si le marqueur existe (`sealed_evaluation.py:108`). C'est correct contre une relance involontaire du script. Voir I1 et I3 pour les contournements par l'API ou par suppression du fichier.
- Lecture des étiquettes : le temps A (`sealed_inputs`, `sealed.py:62-66`) ne renvoie que `id` et `text` ; `text_frame()` (`sealed_evaluation.py:87-90`) ne lit que `id` et `documents` dans le parquet. Les chargeurs de développement filtrent sur les identifiants des plis (`scripts/p1_04_06_tfidf.py:35-38`, `p1_03_bounds.py:29-32`, `hier_supervision_tfidf.py`, `measure_author_shortcut.py:46`) ; une recherche de `["test"]`, `.test`, `"test"`, `sealed` dans `src/` et `scripts/` ne trouve rien hors des quatre fichiers autorisés (`morfitt_run.py:87` lit le test public de MorFITT, sans rapport). Étiquettes tout de même lisibles par complément (voir I2).
- Recoupement marqueur, journal, résultat, partitions :
  - Marqueur `data/splits/sealed_opened.marker` : `opened_at` 2026-10-06T20:59:42Z, 633 identifiants, raison citant RM-20 et l'autorisation de Cyril du 06/10/2026.
  - Journal `data/splits/sealed_access.log` : 15 lignes `inputs` (633 identifiants chacune ; 10 le 05/10 de 15:18:49Z à 15:30:50Z, 3 le 05/10 de 20:45 à 21:33, 2 le 06/10 à 02:27 et 02:29, soit les essais répétés du LoRA après les plantages du tokenizer, le dernier réussi, enregistré à 02:34:02Z au registre) puis une ligne `open` à 20:59:42Z, 633 identifiants. Même seconde que le marqueur, une seule ligne `open` : cohérent.
  - Historique Git du journal : ajout seul sur trois commits (`4cff962`, `2e2781a`, `e705d4d`), aucune ligne retirée ni modifiée ; le marqueur n'apparaît qu'au commit `e705d4d` (06/10/2026 23:03 +0200, soit 21:03Z, après l'ouverture).
  - `results/sealed_result.json` : écrit à 22:59:43 (heure locale), `n` = 633, `ids_sha256` égal au SHA-256 recalculé des identifiants du test ; fichier de partitions : empreinte égale à `data/splits/parhaf_cim10_chapter.sha256` ; intersection test et plis : 0.
  - Temps A : les 10 fichiers `results/sealed_temps_a/*.probs.npz` ont un SHA-256 identique à celui du registre (`results/runs/*-temps-a-*.json`) ; dates du 05/10 17:18 à 17:30 (hors LoRA : 06/10 04:34 heure locale), toutes antérieures au gel (`results/frozen_final.json`, 06/10 20:27, ADR-016 20:28) et à l'ouverture.
  - Code : `src/llmft/sealed.py` et `scripts/sealed_evaluation.py` sont inchangés depuis le commit `62b75ef` (06/10 20:37), antérieur à l'ouverture ; aucune différence avec l'arbre de travail.
- Conclusion de ce point : l'ouverture unique du 06/10/2026 est cohérente et traçable ; le garde de code empêche une seconde ouverture par le chemin normal, il n'empêche ni un contournement volontaire ni une lecture des étiquettes par le parquet brut.

## Données (points 1 et 2)

- Aucun secret : arbre versionné et historique balayés (motifs de jetons Hugging Face, GitLab, GitHub, AWS, Google, Slack, clés privées, `Bearer`, affectations `password/api_key/secret`), aucun résultat. Les seules adresses électroniques sont celles d'auteurs d'articles (`knowledge/raw`), de `test@example.com` et d'une adresse de nomenclature ATIH. Aucun fichier `.env`, clé, jeton ou identifiant suivi (`git ls-files`, y compris l'historique des ajouts). `.gitignore` ignore `.env`, `.env.*`, `*.pem`, `*.key`, `hf_token*`, `data/*` (sauf `cards`, `scripts`, `manifests`, `splits`), `artifacts/`, `models/`. `.gitleaks.toml` étend les règles par défaut.
- Aucune donnée de patient réel visible : `data/` versionné ne contient que fiches, script de téléchargement, manifeste, partitions (identifiants fictifs du type `ANATOMOPATHOLOGIE-00004`) et journal ; aucun parquet, zip ou texte brut suivi hors `knowledge/raw` (articles). Recherche de motifs de noms (`Dr Prénom NOM`, `Madame`, dates de naissance) dans les fichiers suivis hors `knowledge/raw` et skills : aucun résultat. `results/` ne contient que des identifiants, des prédictions et des mesures (pas de texte libre long, vérifié sur `results/measures/*.json`).
- Règle « publiques, synthétiques ou générées, entrées par `dataset-intake` » : PARHAF (comptes rendus fictifs rédigés par des humains, CC BY 4.0 et Etalab 2.0, révision `60426cc…` épinglée, manifeste de 8 fichiers, preuve de rejeu au registre, usages exclus cités et respectés dans la fiche), la nomenclature CIM-10 ATIH (empreintes, aucun dérivé redistribué) sont conformes. MorFITT : voir I6. `docs/FICHE_DE_DONNEES_PARHAF.md` et `data/cards/parhaf.md` sont cohérentes entre elles ; elles rappellent qu'un balayage par expressions régulières ne prouve pas l'absence de donnée réelle (balayage de 200 patients seulement : une preuve d'échantillon, pas de population).

## Dépendances (point 6)

- `uv.lock` : 127 paquets, 126 depuis le registre PyPI, `torch 2.11.0+cu128` depuis l'index PyTorch déclaré `explicit`, tous les paquets ont des empreintes (aucun sans `hash`), aucune source Git ni URL ni chemin local. CI en `uv sync --frozen`.
- Mes connaissances s'arrêtent avant ces versions (transformers 5.18.0, torch 2.11.0, numpy 2.5.3, pandas 3.0.6, tokenizers 0.23.2, setuptools 81.0.0, etc.) : je ne peux ni confirmer ni infirmer de CVE sur elles. Je m'appuie sur `pip-audit` du projet (`make check-full`, job `audit` de la CI, audit hebdomadaire) : bon dispositif. Limites déjà connues et acceptables : torch `+cu128` non auditable ; exception W1 (`PYSEC-2026-3447`, setuptools 81.0.0), motivée et expirant le 31/12/2026, à ne pas laisser expirer sans réévaluation.
- Paquets sensibles à la désérialisation présents : `joblib` 1.6.0, `dill` 0.4.1, `multiprocess` (via `datasets`) : usage `joblib.load` limité aux deux sites de I4.
- Chaîne d'approvisionnement des skills tiers : `.claude/SKILLS_PROVENANCE.txt` (commits épinglés, hooks exclus). Recherche de `curl`, `wget`, `base64`, `eval`, `exec`, `socket`, `os.system` dans `.claude`, `.agents`, `.codex`, `knowledge/bin` : aucune commande réseau ou d'obfuscation ; les scripts Python du wiki et le hook `pre-commit` ne font que des vérifications locales.

## Scripts shell (point 3)

Lus en entier : `scripts/lib/lot.sh`, `run_guarded.sh`, `mem_guard.sh`, `mem_watch.sh`, `silence_watch.sh`, `archive_logs.sh`, `cold_rebuild.sh` ; les 42 autres par recherche de motifs (`rm`, `/tmp`, `eval`, `bash -c`, `xargs`, `kill`, `cd`, variables non entre guillemets).

- Bien : tous commencent par `cd "$(dirname "$0")/.."` entre guillemets (chemin du projet avec espaces géré) ; `set -u` presque partout ; `run_lot` capture le code de sortie avant tout affichage et limite les essais ; `mem_guard.sh` ne vise qu'un PID donné ; aucun `sudo`, `chmod`, `chown`, `curl | sh`, `eval` ; un seul `rm -rf` (I5) ; écritures confinées à `results/` et `$LOGDIR`.
- Écritures hors du projet : `cold_rebuild.sh` (I5), `run_p1_11*.sh` (M3), `$LOGDIR` choisi par l'opérateur (hors dépôt par conception, journaux de session).
- Défauts : I5, M1 à M5.

## Points positifs

- Journal d'accès au test scellé sans contenu, en ajout seul dans l'historique, recoupé avec le marqueur et le résultat ; gel haché avant ouverture ; code de la porte inchangé avant l'ouverture.
- Tous les `np.load` du dépôt en `allow_pickle=False` ; aucun `trust_remote_code`, `shell=True`, `os.system`, `eval` ou `exec` dans `src/` et `scripts/`.
- Cache de tokens : les 30 fichiers ne contiennent que des listes d'entiers (opcodes inspectés sans exécution).
- Révision et empreintes de PARHAF épinglées, manifeste vérifié au rejeu ; licences et usages exclus consignés ; refus de redistribuer la nomenclature CIM-10.
- CI : permissions minimales (`contents: read`), actions épinglées par SHA, valeurs d'événement passées par `env` (pas d'interpolation dans `run:`), `uv sync --frozen`, audit hebdomadaire des dépendances, gitleaks dans `check-fast`.
- Plancher de qualité qui interdit les suppressions de contrôle, avec un garde automatisé (`floor_guard.py`).

## Recommandations proactives

1. Corriger I1 à I3 avant d'écrire « confirmatoire » ou « test scellé inviolé » dans le portfolio ou la carte de modèle ; en attendant, écrire « ouvert une fois, journal et marqueur cohérents, protection procédurale » (claim-gate).
2. Remplacer le cache `pickle` par JSON ou `npz` et signer les entrées par empreinte (I4) : changement petit, tests existants (`tests/test_token_cache.py`, `tests/test_tokenizer_guard.py`) à adapter.
3. Épingler les révisions des modèles Hugging Face et passer `use_safetensors=True` (M7).
4. Compléter l'entrée de MorFITT (I6) avant toute publication d'un chiffre d'ancrage.
5. Ajouter un test de cohérence marqueur, journal, résultat, empreintes du temps A (I3).

## Verdict

Aucun secret ni donnée de patient réel n'a été trouvé et aucun défaut bloquant n'apparaît, mais le garde du test scellé et le cache `pickle` méritent les six correctifs « importants » avant toute présentation du test scellé comme garanti techniquement.

## Ce que je n'ai pas pu vérifier

- Les contrôles du projet eux-mêmes : `make check`, `pytest`, gitleaks (Docker), `pip-audit`, `mypy`, `ruff` n'ont pas été exécutés (ils écrivent dans le dépôt ou le réseau). J'ai remplacé gitleaks par des motifs et un balayage de l'historique, ce qui ne couvre pas les règles d'entropie.
- Les CVE des dépendances : versions postérieures à mes connaissances, pas d'accès réseau ; `torch+cu128` non auditable.
- Le contenu de `data/raw/` (consigne de ne pas y toucher) : l'absence de donnée réelle dans PARHAF lui-même, l'intégrité locale de PARHAF face au manifeste, et l'existence et l'intégrité des fichiers MorFITT.
- Le comportement de `open(..., "x")` sur le disque Windows monté (`/mnt/d`, 9p) : l'atomicité de la création exclusive n'a pas été testée ; ce serait à vérifier par un test dans un dossier jetable.
- La visibilité du dépôt GitHub `origin` et le contenu publié sur le distant ; la réalité des versions et condensats des actions GitHub épinglées (`v7.0.1`, `v10.2.0`).
- Les droits de redistribution des textes d'articles de `knowledge/raw/`.
- Les 42 scripts shell restants n'ont été relus que par motifs ; `scripts/spikes/*.py` et les scripts Python d'analyse n'ont pas été relus ligne à ligne (recherche des motifs dangereux seulement) ; `shellcheck` n'est pas installé.
- Le contenu de `artifacts/final/tfidf.joblib` et des adaptateurs (non inspectés : `joblib` exécute du code à l'ouverture, `pickletools` n'a été appliqué qu'au cache de tokens).
- L'exactitude des étiquettes dans `results/sealed_result.json` (aucune lecture d'étiquette ni de contenu du résultat hors `n` et `ids_sha256`).
