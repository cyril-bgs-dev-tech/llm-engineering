# Revue indépendante de la qualité des tests (P5-10), 06/10/2026

Rôle : test-engineer. Périmètre : `cluster_bootstrap`, `paired`, `power_rule`, `conformal`, `final_report`, `sealed`, `freeze`, `budget`, `tokenizer_guard`, `leakage`, `splits` (dans `src/llmft/`) et leurs tests dans `tests/`.
Aucun fichier du dépôt n'a été modifié en dehors de ce rapport. Aucun calcul GPU, aucune lecture de `data/`, aucune étiquette du test scellé.

## 1. Verdict en une phrase

Le verrou d'ouverture de `sealed` et le cœur numérique de référence (`power_rule.pair_widths`, McNemar, Holm, permutation exacte, bootstrap d'exactitude) sont bien testés, mais les tests de `final_report.py` (le module qui écrit le verdict publié) ne vérifient presque rien (1 mutation sur 21 détectée, et par un plantage) et, au total, 72 mutations plausibles sur 124 non équivalentes passent la suite actuelle sans qu'aucun test échoue : la suite est verte, pas probante, sur le chemin du résultat publié.

## 2. Méthode et chiffres

- Base : j'ai lu les 11 modules et leurs tests, puis exécuté dans le dépôt les 13 fichiers de tests correspondants : `.venv/bin/python -m pytest <13 fichiers> -q -p no:cacheprovider` donne **94 passed en 388 s** (le disque `/mnt/d` ralentit tout). Je n'ai pas exécuté `tests/test_leakage.py` ni `tests/test_splits_real.py` (ils lisent `data/`).
- Mutation : un harnais écrit à la main, **hors dépôt** (dossier temporaire de session `scratchpad/mutate.py`), applique **132 mutations** une à une sur une copie de `src/llmft` et lance les tests du module sur la copie (une copie par groupe, pour éviter toute contamination). Mutations : inversion de comparaison, mauvaise unité de regroupement, décalage d'indice, quantile ou niveau mal calculé, fuite de calibration, constantes changées, entrée permutée.
- Une mutation « survit » quand tous les tests du module passent malgré elle. 7 survivantes sont équivalentes ou neutres (même comportement : `os.replace` vers `rename`, `3600.0` vers `3600`, F1 symétrique en fp/fn, ordre des poids permuté au sein d'une classe, taille de bloc 1, garde `k=0`) et 1 (`BU5`) est en fait le correctif proposé. Je les liste à part.
- Contre-épreuve : pour chaque survivante non équivalente, j'ai écrit un test (esquisses plus bas), vérifié qu'il **passe sur le code actuel** et qu'il **tue la mutation**. Les 72 survivantes non équivalentes sont toutes tuées par les ajouts ; 12 de ces tests décrivent un défaut réel du code actuel (ils échouent aujourd'hui, voir « preuves Prove-It »).

| Module | Mutations | Tuées par la suite actuelle | Survivantes non équivalentes | Équivalentes ou neutres |
|---|---|---|---|---|
| cluster_bootstrap | 8 | 4 | 4 | 0 |
| paired | 21 | 8 | 11 | 2 |
| power_rule | 10 | 5 | 4 | 1 |
| conformal | 15 | 7 | 7 | 1 |
| final_report | 21 | 1 (par un KeyError, pas une assertion) | 20 | 0 |
| sealed | 11 | 6 | 4 | 1 |
| freeze | 8 | 4 | 4 | 0 |
| budget | 6 | 2 | 2 | 2 |
| tokenizer_guard | 6 | 1 | 5 | 0 |
| leakage | 12 | 6 | 5 | 1 |
| splits | 14 | 8 | 6 | 0 |
| **Total** | **132** | **52** | **72** | **8** |

## 3. Les dix constats qui comptent, par priorité

1. **`final_report.py` n'est pas testé là où il décide.** `test_full_report_answers_the_primary_question...` affirme seulement que le verdict est l'une des trois valeurs possibles et que les clés existent. Survivent : `verdict(hi, lo, delta)` au lieu de `verdict(lo, hi, delta)`, final et référence inversés, `delta` publié à 0, `scored` réduit à la seule classe AUTRE, la sensibilité « sans XVIII » qui garde seulement XVIII, la calibration conforme faite **sur le test** (fuite), l'abstention qui garde les moins confiants. `system_metrics` (F1 par chapitre, exactitude, macro-F1 publiés) n'est appelée par aucun test avec vérification de valeur.
2. **Deux `verdict()` en double, testés inégalement.** `paired.verdict` est testé aux bornes (`lo == delta`) ; `final_report.verdict`, celui que `full_report` publie, ne l'est pas (`>=` au lieu de `>` et `<=` au lieu de `<` survivent). Source unique, ou test d'équivalence sur une grille.
3. **`sealed.sealed_labels_and_score` consomme le test pour une erreur récupérable.** Le marqueur est écrit avant de vérifier que les identifiants du test et la colonne d'étiquettes existent dans le tableau : un identifiant absent ou un nom de colonne faux lève `ConsumedWithoutResultError` avec le marqueur écrit (sonde exécutée). Un identifiant dupliqué dans le tableau désaligne étiquettes et prédictions sans erreur (étiquettes en 2 exemplaires, prédictions en 1). L'alignement étiquettes/prédictions n'est pas testé de façon discriminante (les données des tests sont dans l'ordre du split, donc `SE6` et `SE8` survivent).
4. **`power_rule.mean_width` n'a aucun test de valeur** : `np.mean` remplacé par `np.max`, ou « trois graines » remplacé par « quatre », survivent. C'est la fonction de la règle RM-17 (largeur moyenne contre 4,0). La comparaison à 4,0 (`mean <= THRESHOLD_POINTS`) vit dans `scripts/rm17_power_rule.py:48`, hors suite.
5. **`conformal` : la définition d'APS n'est vérifiée nulle part.** Les tests de couverture marginale passent pour n'importe quel score (garantie d'échangeabilité) : ordre croissant, masse cumulée exclusive ou gestion des égalités supprimée survivent. `predict_sets` avec `<` au lieu de `<=` survit aussi (cas du score exactement égal au quantile).
6. **Niveaux d'intervalle non épinglés** : `cluster_bootstrap` avec alpha non divisé par 2 (IC 90 % au lieu de 95 %), `pooled_interval` avec alpha non divisé ou sans stratification, `hierarchical_bootstrap` avec la borne basse au percentile 5 au lieu de 2,5 (le test compare à scipy avec une tolérance de 0,012, environ le tiers de l'erreur standard) survivent. Le test « les erreurs corrélées élargissent l'IC » compare un IC blocs à 95 % à un IC patients à 98,33 % (niveaux par défaut différents), ce qui masque justement l'erreur de niveau.
7. **`paired` : rééchantillonnage des graines asymétrique non détecté** (graines de A ou de B toujours la première : survit), plafond à 1 de Holm retiré (survit : aucun p ajusté du test ne dépasse 1), correction `+1` du p Monte-Carlo (survit), garde « énumération limitée à 20 » (survit), et le chemin pondéré de `_metric_per_replicate` (poids autres que 1) n'est couvert que par des tests statistiques.
8. **`tokenizer_guard` : la clé de cache.** Le tri des textes dans la clé (donc un cache renvoyé avec les identifiants dans le mauvais ordre) survit, comme la suppression du séparateur `\0` (« tok » + « 16 » se confond avec « tok1 » + « 6 »), la version de `transformers` retirée de la clé, et le nombre de tentatives réduit d'une unité.
9. **`leakage` : la boucle par blocs n'est jamais exercée au-delà du premier bloc** (3 textes pour un bloc de 500) : l'oubli du décalage `start` (`ids[int(row)]`) survit. Le seuil exact, la longueur 5 des n-grammes, le caractère binaire de la matrice et la fusion en étoile d'union-find survivent. Deux textes identiques de moins de 5 caractères ne sont jamais signalés (sonde).
10. **`splits.check_tolerance` : la branche des petites classes (< 50 patients, minimum 3 en test et 2 par pli) n'est testée par aucun test** (`minimum = 0` survit), ni le déficit, ni la frontière 50 ; la stratification de `make_splits` n'est pas vérifiée (le test non stratifié survit) ; la frontière de la politique des classes rares (`<` contre `<=`) non plus.

## 4. Module par module

Convention : « survit » signifie « tous les tests actuels du module passent malgré la mutation ». Les identifiants (CB2, PA13...) renvoient au harnais de session ; chaque mutation est décrite en clair.

### 4.1 `cluster_bootstrap.py` (tests : `test_cluster_bootstrap.py`, 3 tests)

Ce que les tests tuent : regroupement par patient au lieu d'auteur (CB1), pas de rééchantillonnage (CB7), bornes inversées (CB6), tp compté en union (CB8).

Survivantes (preuves) :
- **CB2** `alpha = (1.0 - level) / 2.0` devient `(1.0 - level)` : IC à 90 % au lieu de 95 %. Survit parce que le test d'élargissement compare à un IC patients à 98,33 %.
- **CB3** classe absente : F1 = 1 au lieu de 0 quand `denom == 0` (ne se voit que si un système prédit la classe absente et pas l'autre).
- **CB4** `scored` ignoré (on score toutes les classes) : aucun test n'appelle `cluster_interval` avec une classe exclue (AUTRE), alors que `final_report` le fait toujours.
- **CB5** `multinomial(len(uniq) - 1, ...)` : un auteur de moins tiré par réplique.

Cas limites manquants (sondes exécutées sur la copie) :
- Un seul auteur : renvoie `(-22.42, -22.42, -22.42)`, un IC de largeur zéro, sans erreur ni avertissement. Deux auteurs : IC d'environ 2 points de large, sans alerte.
- `groups` de longueur différente de `truth` : ValueError numpy obscure (« array is not broadcastable »), pas de message métier.
- `scored` vide : `(nan, nan, nan)` sans erreur ; ensemble vide : IndexError.
- Pas de test d'une classe absente de la vérité, ni de classe prédite seulement par un système.

Tests à ajouter (validés : verts sur le code actuel, tuent CB2 à CB5 ; esquisses condensées) :

```python
def test_interval_matches_a_naive_replica_with_sklearn():
    truth, pa, pb, groups = _data()          # 12 auteurs de 8 patients, 3 classes
    scored, n_boot, seed = [0, 1], 300, 7     # classe 2 = « AUTRE » exclue
    uniq = sorted(set(groups))
    members = {g: np.flatnonzero(np.array(groups) == g) for g in uniq}
    weights = np.random.default_rng(seed).multinomial(len(uniq), np.full(len(uniq), 1 / len(uniq)), size=n_boot)
    def f1(p, rows):
        return f1_score(truth[rows], p[rows], labels=scored, average="macro", zero_division=0)
    diffs = []
    for w in weights:
        rows = np.concatenate([np.tile(members[g], int(k)) for g, k in zip(uniq, w, strict=True) if k])
        diffs.append(f1(pa, rows) - f1(pb, rows))
    lo, hi = np.percentile(diffs, [2.5, 97.5])
    d, lo_c, hi_c = cluster_interval(truth, pa, pb, scored, groups, n_boot=n_boot, seed=seed, level=0.95)
    assert (lo_c, hi_c) == pytest.approx((100 * lo, 100 * hi), abs=1e-9)

def test_a_scored_class_absent_from_truth_scores_zero_like_sklearn():
    truth, pa, pb, groups = _data()
    pa = pa.copy(); pa[::5] = 7              # A prédit la classe 7 (absente), B jamais
    d, *_ = cluster_interval(truth, pa, pb, [0, 1, 2, 7], groups, n_boot=50)
    exp = f1_score(truth, pa, labels=[0, 1, 2, 7], average="macro", zero_division=0) - f1_score(truth, pb, labels=[0, 1, 2, 7], average="macro", zero_division=0)
    assert d == pytest.approx(100 * exp, abs=1e-9)

def test_swapping_the_systems_negates_the_interval(): ...   # d2 == -d, lo2 == -hi, hi2 == -lo

def test_a_single_author_is_refused():    # échoue aujourd'hui (preuve) ; décision à prendre : seuil minimal d'auteurs
    with pytest.raises(ValueError):
        cluster_interval(truth, pa, pb, [0, 1, 2], ["a"] * len(truth), n_boot=50)
```

Mutations à garder en tête pour le jour où un outil automatique (mutmut) sera branché : CB2, CB4, CB5.

### 4.2 `paired.py` (tests : `test_paired.py`, 15 tests)

Points forts : McNemar exact comparé à statsmodels et scipy sur six tables, Holm comparé à statsmodels, permutation exacte comparée à scipy, F1 du bootstrap comparé à `metrics.macro_f1`, fausse alerte et puissance en simulation. Mutations tuées : min vers max et bilatéral vers unilatéral (PA1, PA2), monotonie de Holm (PA4), `>=` vers `>` dans la permutation (PA5), strates non rééchantillonnées (PA8, par le test statistique de fausse alerte seulement), `lo >= delta` (PA16), Bonferroni (PA17), F1 vers Jaccard (PA18).

Survivantes (preuves) :
- **PA3** `np.minimum(1.0, ...)` retiré de `holm_adjust` : survit. Les p ajustés du test valent au plus 0,2 et `[0.5, 0.9, 0.001]` donne 1,0 sans dépasser. Preuve par cas : `holm_adjust([0.5, 0.7, 0.9])` doit valoir `[1, 1, 1]`.
- **PA6** `(n + 1) / (n_perm + 1)` devient `n / n_perm` : survit (tolérance 0,01 pour 20 000 permutations). Le p Monte-Carlo peut alors valoir 0,0.
- **PA7** `MAX_EXACT_PERMUTATION = 20` relevé à 9999 : survit, aucun test du `ValueError`. Sans la garde, `product((-1, 1), repeat=n)` explose en mémoire.
- **PA13 / PA14** borne basse au percentile 5 (au lieu de 2,5) ou borne haute au 96,5 (au lieu de 97,5) : survivent. Le test contre scipy tolère 0,012 pour un écart-type du bootstrap d'environ 0,03. Un test de niveau doit comparer à l'approximation normale avec une tolérance de quelques centièmes d'erreur standard.
- **PA15** `hi < delta` devient `hi <= delta` : survit (aucun test à `hi == delta`).
- **PA12 / PA12b** graines de A (ou de B) toujours la première : survit. Le test « hiérarchique plus large que patients seuls » reste vrai si un seul côté est rééchantillonné.
- **PA10, PA19, PA20** `fp` calculé sans les poids, support non pondéré, dénominateur de l'exactitude `len(truth)` : survivent (PA19 et PA20 sont équivalentes sur le chemin stratifié de production, car les effectifs sont conservés ; elles ne l'étaient pas pour `stratify=False` avec des poids quelconques). Le chemin pondéré n'est jamais confronté à une réplique explicitement développée.

Cas limites manquants (sondes) :
- `paired_permutation_pvalue(np.array([]))` renvoie **0,0** (le plus significatif) avec des avertissements numpy : un échantillon vide devrait lever.
- `mcnemar_exact` avec des vecteurs de longueurs différentes : diffusion silencieuse (`only_b=1`, `p=1.0`).
- `holm_adjust` avec NaN : le NaN reste, les autres p sont ajustés avec le m complet, sans erreur.
- `bonferroni_level(0)` : ZeroDivisionError (acceptable) ; `hierarchical_bootstrap` avec `n_boot=0` : IndexError ; `level=1.5` : ValueError numpy ; indice de prédiction >= k : IndexError (acceptable, mais aucun test ne le fige).
- Nombres de graines différents entre A et B : accepté (voulu), non testé ; une graine unique avec `resample_seeds=True` : accepté, non testé.

Tests à ajouter (validés) :

```python
def test_holm_caps_adjusted_values_at_one():
    assert paired.holm_adjust(np.array([0.5, 0.7, 0.9])).tolist() == [1.0, 1.0, 1.0]

def test_exact_permutation_refuses_more_than_twenty_patients():
    with pytest.raises(ValueError, match="20"):
        paired.paired_permutation_pvalue(np.ones(21), n_perm=None)

def test_monte_carlo_permutation_p_value_is_never_zero():
    assert paired.paired_permutation_pvalue(np.ones(30), n_perm=50, rng=np.random.default_rng(0)) >= 1 / 51

def test_verdict_is_non_resolved_when_the_upper_bound_equals_delta():
    assert paired.verdict(-4.0, 2.0, delta=2.0) == "non résolu"

def test_percentile_interval_matches_the_normal_approximation_at_the_requested_level():
    rng = np.random.default_rng(0); n = 2000
    truth = np.zeros(n, dtype=int)
    a_ok, b_ok = rng.random(n) < 0.6, rng.random(n) < 0.5
    a, b = np.where(a_ok, 0, 1), np.where(b_ok, 0, 1)
    gaps = a_ok.astype(float) - b_ok.astype(float); se = gaps.std() / np.sqrt(n)
    res = paired.hierarchical_bootstrap(truth, a[None], b[None], 2, [0], metric="accuracy", stratify=False,
                                        resample_seeds=False, n_boot=20000, level=0.95, rng=np.random.default_rng(1))
    assert res.lo == pytest.approx(gaps.mean() - 1.96 * se, abs=0.07 * se)
    assert res.hi == pytest.approx(gaps.mean() + 1.96 * se, abs=0.07 * se)

@pytest.mark.parametrize("metric", ["macro_f1", "accuracy"])
def test_weighted_metric_equals_the_metric_on_the_expanded_sample(metric):   # tue PA10, PA19, PA20
    rng = np.random.default_rng(3)
    truth = rng.integers(0, 4, 40); pred = np.where(rng.random(40) < 0.6, truth, rng.integers(0, 4, 40))
    w = rng.integers(0, 4, size=(6, 40)); w[:, 0] += 1
    got = paired._metric_per_replicate(w, truth, pred, 4, [0, 1, 2], metric)
    for r in range(6):
        t, p = np.repeat(truth, w[r]), np.repeat(pred, w[r])
        exp = (t == p).mean() if metric == "accuracy" else f1_score(t, p, labels=[0, 1, 2], average="macro", zero_division=0)
        assert got[r] == pytest.approx(exp, abs=1e-12)

@pytest.mark.parametrize("side", ["a", "b"])
def test_interval_is_centred_on_the_seed_averaged_estimate(side):   # tue PA12 et PA12b
    # une graine de la recette qui varie est parfaite (exactitude 1) : une graine unique tirée déplacerait le centre
    ...  # assert abs((r.lo + r.hi) / 2 - r.estimate) < 0.2 * r.width

def test_stratified_weights_really_resample_every_class():
    w = paired.stratified_weights(np.array([0] * 40 + [1] * 30 + [2] * 20), 2000, np.random.default_rng(1))
    # variance de chaque colonne > 0,8 et moyenne 1 : une classe figée à 1 échoue
```

Tests à décider (échouent aujourd'hui, preuves de défaut) : l'échantillon vide pour la permutation doit lever (p = 0,0 aujourd'hui), longueurs différentes pour McNemar doivent lever.

### 4.3 `power_rule.py` (tests : `test_power_rule.py`, 7 tests)

Points forts : `pair_widths` est comparé à une réplique naïve avec scikit-learn **et le même flux de tirages** (tue le niveau 98,33, l'alpha, l'ordre des paires, la stratification aux effectifs du test).

Survivantes :
- **PR1** `np.mean(widths)` remplacé par `np.max(widths)` dans `mean_width` : survit. **PR2** `len(preds) < 3` remplacé par `< 4` : survit. Aucun test n'appelle `mean_width` avec trois graines ou plus.
- **PR5** `pooled_interval` avec alpha non divisé : survit ; **PR6** `pooled_interval` sans stratification : survit. Le test `pooled_width == pooled_interval` est une auto-cohérence (même fonction des deux côtés), et la décroissance avec n est trop large pour détecter ces fautes.
- Neutre : PR10 (fp := fn : le F1 est symétrique).

Faiblesses de noms et de tautologies : `test_pairs_follow_lexicographic_order_and_count` ne vérifie que `len == 3` (l'ordre n'est vérifié que de façon indirecte par la réplique) ; `test_threshold_is_two_delta` n'épingle qu'une constante, pas la règle `mean <= 4,0` (dans `scripts/rm17_power_rule.py`, non couverte ici). Cas limite : une classe de `test_counts` absente de `truth` donne un `ValueError: high <= 0` numpy brut.

Tests à ajouter (validés) :

```python
@pytest.mark.parametrize("n_seeds", [3, 4])
def test_mean_width_is_the_arithmetic_mean_of_the_pair_widths(n_seeds):
    truth, preds = _pool(n_seeds, np.random.default_rng(8))
    counts = {0: 6, 1: 4, 2: 3}
    widths = pair_widths(truth, preds, counts, [0, 1, 2], n_boot=100)
    got = mean_width(truth, preds, counts, [0, 1, 2], n_boot=100)
    assert got == pytest.approx(float(np.mean(widths))) and min(widths) < got < max(widths)

def test_pooled_interval_matches_a_naive_replica_at_the_default_level():
    # même flux (SEED), strates = np.unique(truth), F1 par scikit-learn, percentiles 100*alpha avec alpha = (1 - LEVEL) / 2
    ...
```

### 4.4 `conformal.py` (tests : `test_uncertainty.py`, partie conforme, 8 tests)

Mutations tuées : `(n+1)` vers `n` (CF1), sens du score LAC (CF2), `<=` vers `<` dans les variantes par classe et par groupe (CF7, CF8), Wilson centre (CF11), score de la classe prédite au lieu de la vraie (CF13, CF14).

Survivantes :
- **CF3** APS trié par ordre croissant ; **CF4** masse cumulée exclusive (classe non comprise) ; **CF5** gestion des égalités supprimée : survivent toutes les trois (voir constat 5). Valeur attendue : `[0.3, 0.6, 0.1]` donne `[0.9, 0.6, 1.0]` ; `[0.4, 0.4, 0.2]` donne `[0.8, 0.8, 1.0]` (sonde : le code actuel est correct).
- **CF6** `predict_sets` avec `<` au lieu de `<=` : survit (scores continus, jamais d'égalité avec le quantile).
- **CF9** Wilson par classe calculé avec k = n ; **CF10** `n` faux ; **CF12** bornes `[0, 1]` retirées de Wilson : survivent. `coverage_by_class_wilson` et `n` ne sont jamais vérifiés.
- Neutre : CF15.

Cas limites manquants (sondes) :
- `alpha = 1.0` renvoie le **maximum** des scores (10.0 pour 1..10), `alpha = 1.5` renvoie 5.0, `alpha < 0` ou `0` renvoie l'infini : aucune validation de `alpha` dans ]0, 1[.
- Probabilités NaN : `fit` renvoie un quantile fini et `predict_sets` produit des ensembles qui excluent la classe, sans erreur ; un score NaN dans `conformal_quantile` renvoie NaN (tous les ensembles deviennent vides).
- `evaluate([], [])` renvoie des NaN ; la classe absente de la calibration donne `inf` (testé), la famille sans exemple aussi (non testé).
- Le calcul flottant `ceil((n+1)(1-alpha))` : sur `alpha` de 0,01 à 0,99 et n jusqu'à 3000, 1738 couples donnent un rang trop grand de 1 (par exemple `alpha=0,18, n=149`), **toujours dans le sens prudent** ; aucun cas pour `alpha=0,10` ni `0,05`. Sans danger aujourd'hui (niveau 0,90), mais un test de propriété le figerait.

Tests à ajouter (validés) :

```python
def test_aps_scores_are_the_inclusive_cumulative_mass_in_descending_order():
    assert conformal._scores_all(np.array([[0.3, 0.6, 0.1]]), "aps")[0] == pytest.approx([0.9, 0.6, 1.0])
    assert conformal._scores_all(np.array([[0.4, 0.4, 0.2]]), "aps")[0] == pytest.approx([0.8, 0.8, 1.0])

def test_a_class_whose_score_equals_the_quantile_is_kept():
    p = np.array([[0.9, 0.1]])   # scores LAC 0.1 et 0.9
    assert conformal.predict_sets(p, 0.9) == [{0, 1}] and conformal.predict_sets(p, 0.5) == [{0}]
    assert conformal.predict_sets_by_class(p, {0: 0.9, 1: 0.9}) == [{0, 1}]
    assert conformal.predict_sets_by_group(p, {0: 0.9}, {0: 0, 1: 0}) == [{0, 1}]

def test_finite_sample_guarantee_holds_exactly_on_every_leave_one_out_split():
    values = np.arange(20, dtype=float)
    covered = sum(values[j] <= conformal.conformal_quantile(np.delete(values, j), 0.1) for j in range(20))
    assert 1 - 0.1 <= covered / 20 < 1 - 0.1 + 1 / 20 + 1e-9

def test_evaluate_reports_n_and_wilson_by_class_from_hits_and_counts():
    r = conformal.evaluate([{0}, {1}, {0}, {0}], np.array([0, 0, 1, 1]))
    assert r["n"] == 4 and r["coverage_by_class"] == {0: 0.5, 1: 0.0}
    assert r["coverage_by_class_wilson"][0] == pytest.approx(conformal.wilson(1, 2))

def test_wilson_stays_inside_zero_and_one_at_the_extremes():
    assert conformal.wilson(0, 10)[0] == 0.0 and conformal.wilson(10, 10)[1] == 1.0

def test_alpha_outside_the_open_unit_interval_is_refused():   # échoue aujourd'hui (preuve)
    with pytest.raises(ValueError):
        conformal.conformal_quantile(np.arange(1.0, 11.0), 1.5)

def test_nan_probabilities_are_refused():                    # échoue aujourd'hui (preuve)
    with pytest.raises(ValueError):
        conformal.fit(np.array([[0.5, 0.5], [np.nan, np.nan]]), np.array([0, 1]), 0.1)
```

### 4.5 `final_report.py` (tests : `test_final_report.py`, 4 tests)

C'est le module le moins protégé. Une seule mutation sur 21 est détectée (FR21, calibration prise sur la référence, par un `KeyError` parce que le test ne fournit que la clé `final`, pas par une assertion).

Survivantes (toutes) :
- Verdict : **FR1** `>=` au lieu de `>` ; **FR2** `<=` au lieu de `<` ; **FR17** `verdict(hi, lo, delta)`.
- `system_metrics` : **FR3** exactitude inversée (`!=`) ; **FR4** F1 par chapitre arrondi à 2 décimales ; **FR5** `n` = prédits au lieu du support ; **FR6** macro-F1 qui inclut la classe exclue. Aucun test ne lit `systemes`.
- `compare` : **FR7** IC patients avec A et B inversés et niveau 50 % ; **FR8** bornes patients inversées. Le test ne vérifie que `len(ic95_patients) == 2`.
- `conformal_report` : **FR9 et FR10** calibration (marginale, puis par famille) faite **sur le test** au lieu du développement : survivent, car le jouet est i.i.d. (couverture au moins aussi bonne) ; **FR11** couverture « minimale » devenue maximale (le test vérifie `>= 0,8`) ; **FR12** `niveau_vise = alpha` au lieu de `1 - alpha`.
- `abstention_table` : **FR13** garde les moins confiants ; **FR14** `round` remplacé par `int` ; **FR15** exactitude inversée. (`a["0.5"] >= a["1.0"]` n'est pas violé par ces mutations sur le jouet.)
- `full_report` : **FR16** `scored` = seulement AUTRE ; **FR18** final et référence inversés ; **FR19** sensibilité qui garde seulement les classes à retirer ; **FR20** `delta` publié à 0. Les étiquettes du test sont `["I", "II", "XVIII", "AUTRE"]` : XXI n'existe pas, donc « sans XVIII ni XXI » n'est jamais discriminant.

Cas limites (sondes) : `conformal_report` avec un test vide : ZeroDivisionError ; `verdict(5.0, 1.0, 2.0)` (bornes inversées) renvoie « gain confirmé » ; `verdict(nan, nan, 2.0)` renvoie « non résolu » (prudent) ; `abstention_table` sur 5 patients à couverture 0,5 traite 2 patients (arrondi bancaire de `round(2.5)`), à 0,7 en traite 4.

Observation de conception : le verdict primaire se lit sur l'IC 95 % par blocs d'auteurs (conforme à `PROTOCOLE_V2.md`, question primaire unique, IC 95 % non ajusté) ; le niveau 98,33 % de `bonferroni_level` n'entre pas dans `full_report`. Rien ne l'épingle : un test doit fixer `level = 0,95` pour le verdict.

Tests à ajouter (validés : verts aujourd'hui, tuent les 20 survivantes) :

```python
def test_verdict_boundaries_are_strict_on_both_sides():
    assert fr.verdict(2.0, 9.0, 2.0) == "non résolu" and fr.verdict(-3.0, 2.0, 2.0) == "non résolu"

def test_the_two_verdict_implementations_agree_on_a_grid():
    grid = [-5.0, 0.0, 1.9, 2.0, 2.1, 7.0]
    assert all(fr.verdict(lo, hi, 2.0) == paired.verdict(lo, hi, 2.0) for lo in grid for hi in grid if lo <= hi)

def test_system_metrics_on_a_hand_computed_example():
    truth = np.array([0, 0, 1, 1, 2, 2]); probs = _onehot([0, 1, 1, 1, 2, 0])
    m = fr.system_metrics(truth, probs, [0, 1, 2], ["a", "b", "c"])
    assert m["accuracy"] == 0.6667
    assert m["f1_par_chapitre"] == {"a": {"n": 2, "f1": 0.5}, "b": {"n": 2, "f1": 0.8}, "c": {"n": 2, "f1": 0.6667}}
    assert m["macro_f1"] == 0.6556
    assert fr.system_metrics(truth, probs, [0, 1], ["a", "b", "c"])["macro_f1"] == 0.65   # classe 2 exclue

def test_full_report_verdict_is_read_from_the_blocks_of_authors_interval(monkeypatch):
    monkeypatch.setattr(fr, "compare", lambda *a, **k: {"difference_points": 1.0, "ic95_blocs_auteurs": [-1.0, 5.0], "ic95_patients": [0.0, 2.0]})
    ...  # full_report(...)["question_primaire"]["verdict"] == "non résolu"

def test_conformal_report_is_calibrated_on_the_calibration_set_only():
    # calibration très sûre (p = 0,98 sur la vraie classe), test difficile (vraie classe à p = 0,3)
    # un seuil appris sur le développement ne couvre pas : couverture < 0,5 ; calibrer sur le test donnerait 0,9
    ...

def test_full_report_primary_question_orientation_delta_and_sensitivity():
    # final meilleur que la référence : « gain confirmé », delta == 2.0 ;
    # rôles échangés : « absence de gain utile » ;
    # sensibilité : « sans XVIII » == macro_f1 sur [0, 2], « sans XVIII ni XXI » == macro_f1 sur [0], avec des étiquettes ["I","XVIII","XXI","AUTRE"]
    ...

def test_abstention_keeps_the_most_confident_and_rounds_the_count():
    conf = np.array([0.9, 0.8, 0.7, 0.6, 0.5]); probs = np.stack([conf, 1 - conf], axis=1)
    truth = np.array([0, 0, 1, 0, 1])    # justes aux rangs 1, 2, 4
    out = fr.abstention_table(probs, truth, coverages=(1.0, 0.7, 0.6, 0.5))
    assert out["1.0"]["exactitude"] == 0.6 and out["0.6"]["n_traites"] == 3 and out["0.7"]["n_traites"] == 4 and out["0.5"]["n_traites"] == 2
```

### 4.6 `sealed.py` (tests : `test_sealed_access.py`, `test_sealed_two_steps.py`, 11 tests)

Points forts : marqueur exclusif (mode `x`), refus de la seconde ouverture, raison vide refusée, couverture des prédictions vérifiée **avant** le marqueur, marqueur conservé après un échec du calcul, répétition générale sans trace, aucun fichier `.tmp` résiduel, journal sans contenu. Mutations tuées : `x` vers `w`, couverture trop permissive sur les manquants, marqueur écrit après le calcul, prédictions non alignées en temps B, identifiants absents au temps A, raison vide.

Survivantes (preuves) :
- **SE2** `set(predictions) != set(ids)` devient « les ids sont inclus dans les prédictions » : des prédictions en trop sont acceptées. Aucun test avec une clé en plus.
- **SE6** (répétition) et **SE8** (ordre des lignes = ordre du tableau) : les données des tests (`FRAME`) sont dans l'ordre de `split["test"]`, donc un désalignement étiquettes/prédictions passe. Les prédictions sont passées dans l'ordre inverse, mais seulement pour le temps B et sans tableau dans un autre ordre.
- **SE9** `n_ids` du journal toujours 0 : le test ne vérifie que les clés.
- Équivalente : SE7 (`os.replace` vers `rename`). L'atomicité n'est pas testable sans injection de panne : le test vérifie seulement l'absence de `.tmp`.

Cas limites (sondes exécutées sur la copie) :
- **Identifiant du test absent du tableau au temps B** : `ConsumedWithoutResultError` avec **marqueur écrit** (test consommé pour une erreur de saisie). Même chose si `label_col` n'existe pas.
- **Identifiant dupliqué dans le tableau** : `.loc[ids]` renvoie 2 lignes pour 1 identifiant : `compute` reçoit `y` de longueur 2 et `p` de longueur 1, sans erreur.
- **Identifiant dupliqué dans `split["test"]`** : accepté, compté deux fois.
- Le détecteur de `test_no_other_module_reads_the_sealed_partition` (regex `\[\s*["']test["']\s*\]|\.test\b|sealed`) laisse passer `split.get("test")`, `split["te" + "st"]`, `split[k]`, `getattr(split, "test")` et `operator.itemgetter("test")(split)` (sondes). Le vrai verrou est le marqueur ; le détecteur est une aide statique, à présenter comme telle. Il ne parcourt pas `tests/` ni les notebooks.

Tests à ajouter (validés) :

```python
SPLIT = {"test": ["P4", "P2"], "folds": [["P1"], ["P3"]]}      # ordre différent de celui du tableau
PRED = {"P2": "p2", "P4": "p4"}

@pytest.mark.parametrize("rehearsal", [True, False])
def test_labels_and_predictions_are_both_aligned_on_the_order_of_the_test_ids(tmp_path, rehearsal):
    seen = {}
    sealed.sealed_labels_and_score(SPLIT, FRAME, "label", PRED, lambda y, p: seen.update(y=list(y), p=list(p)) or {}, marker=tmp_path / "m", reason="r", out_path=tmp_path / "o.json", rehearsal=rehearsal)
    assert seen == {"y": ["l4", "l2"], "p": ["p4", "p2"]}

def test_predictions_for_ids_outside_the_test_are_refused_before_the_marker(tmp_path): ...  # {**PRED, "P1": "x"}

def test_journal_records_the_number_of_ids(tmp_path): ...   # n_ids == 2

# Preuves Prove-It : ces trois tests ÉCHOUENT aujourd'hui (le marqueur est écrit avant la détection)
def test_a_test_id_missing_from_the_frame_is_refused_before_the_marker(tmp_path):
    with pytest.raises(ValueError):
        sealed.sealed_labels_and_score({"test": ["P2", "P9"]}, FRAME, "label", {"P2": "a", "P9": "b"}, compute, marker=tmp_path / "m", reason="r", out_path=tmp_path / "o.json")
    assert not (tmp_path / "m").exists()

def test_a_missing_label_column_is_refused_before_the_marker(tmp_path): ...    # KeyError, marqueur absent
def test_duplicate_ids_in_the_frame_are_refused(tmp_path): ...                  # ValueError
```

Correctif suggéré (à faire par le développeur, pas par moi) : appeler `_test_rows(split, frame)` et vérifier `label_col in frame.columns` et l'unicité des identifiants **avant** `open_sealed_test`, sans lire les étiquettes.

### 4.7 `freeze.py` (tests : `test_freeze.py`, 4 tests)

Tuées : doublons de runs (FZ2), permutation des empreintes (FZ5), `delta` (FZ6), `tfidf` absent (FZ7).

Survivantes :
- **FZ1** run non abouti accepté : survit (le code lève `non abouti`, aucun test).
- **FZ3** `CONFORMAL_LEVEL` 0,90 vers 0,95 ; **FZ4** couvertures d'abstention réduites à `(1.0,)` ; **FZ8** `secondaires` vidé : survivent. Ces valeurs sont **publiées dans le gel** ; seul `delta` est épinglé.
- Observation : `freeze.CONFORMAL_LEVEL` (0,90) et `final_report.conformal_report(alpha=0.10)` sont deux sources de vérité sans test qui les relie.

Cas limites (sondes) : `enc_seeds=()` et `lora_seeds=()` donnent un gel accepté avec `composition.encodeur == []` alors que `final` annonce « LoRA + encodeur + TF-IDF ». Un run sans `metrics.sha256` lève `KeyError` (échec franc, non testé). Le motif `*-{slug}.json` attrape aussi `…-essai-final-tfidf.json` et l'élève en doublon (refus prudent, voulu, non testé).

Tests à ajouter (validés) : refus d'un run `status != "ok"` ; épinglage de `niveau_conforme == 0.90`, des couvertures `[1.0, 0.9, 0.8, 0.7, 0.5]` et de `secondaires == ["E ensemble", "F LoRA"]` ; refus d'un gel sans graine (test qui échoue aujourd'hui, décision à prendre).

### 4.8 `budget.py` (tests : `test_budget.py`, 4 tests)

Tuées : `>=` vers `>` (BU3), tokenisation non comptée (BU6). Survivantes : **BU1** `BUDGET_HOURS` 90 vers 900 et **BU2** `ALERT_FRACTION` 0,8 vers 0,95 (le test de l'alerte utilise les constantes elles-mêmes, il est circulaire). Neutre : BU4. **BU5** (les durées négatives ignorées) est le correctif, pas une régression.

Cas limites (sondes) : une durée `NaN` (le JSON de Python l'accepte) donne un total NaN et `alert(nan)` vaut **False** : l'alerte se tait. Une durée négative **diminue** le total (`-1.0` h pour -3600 s). `True` compte pour 1 s. `"metrics": null` ou un JSON qui est une liste : AttributeError (échec franc ; mais voir « non vérifié » sur le code de sortie de `scripts/budget_alert.py`, où un plantage et une alerte pourraient se confondre). Registre vide : non testé (renvoie 0,0).

Tests à ajouter (validés) : `BUDGET_HOURS == 90.0`, `ALERT_FRACTION == 0.8`, `alert(71.99)` faux et `alert(72.0)` vrai en heures littérales ; registre vide ; NaN non propagé au total ; durée négative qui ne diminue pas le total (les deux derniers échouent aujourd'hui).

### 4.9 `tokenizer_guard.py` (tests : `test_tokenizer_guard.py`, `test_token_cache.py`, 13 cas)

Points forts : le fils tokenise sur un seul cœur (`sched_getaffinity`), plantage relancé puis abandonné, cache corrompu recalculé, un échec n'écrit rien dans le cache. Une mutation tuée : `max_len` retiré de la clé (TG5).

Survivantes (preuves) :
- **TG1** séparateur `\0` supprimé : `("tok", 16)` et `("tok1", 6)` produisent la même clé (collision) : un cache serait servi pour un autre `max_len`.
- **TG2** textes triés avant hachage : le cache renvoie des identifiants **dans l'ordre trié**, pas dans l'ordre des textes. Mutation grave pour un entraînement (désalignement texte/étiquette), aucun test sur l'ordre.
- **TG3** version de `transformers` retirée de la clé.
- **TG4** `range(1, attempts)` : une tentative de moins ; le message d'échec utilise la variable `attempts`, donc `match="3 essais"` reste vrai. Aucun compteur d'appels.
- **TG6** `except (UnpicklingError, EOFError)` sans `AttributeError, ValueError` : un cache périmé (classe disparue) ne serait plus rattrapé.

Cas limite : un cache dont la liste n'a pas la longueur des textes est **renvoyé tel quel** (aucune validation, test qui échoue aujourd'hui). Liste vide de textes non testée. Le test `test_sous_processus_donne_les_memes_identifiants...` compare le fils au calcul local qui **partage la même fonction de troncature** : il ne prouve pas la troncature (elle relève de `lora_train.truncate_head_tail`, hors périmètre).

Tests à ajouter (validés) : l'ordre des textes fait partie de la clé (`["aa","bbb"]` puis `["bbb","aa"]` : deux appels du fils, résultats `[[2],[3]]` puis `[[3],[2]]`) ; nom et longueur non confondables (`"tok"` + 16 contre `"tok1"` + 6) ; une autre version de `transformers` (monkeypatch de `tokenizer_guard.version`) donne un autre fichier ; `attempts=4` appelle le fils exactement 4 fois ; un pickle qui référence un attribut absent (`pickle.dumps(json.dumps).replace(b"dumps", b"dumpz")`) est recalculé.

### 4.10 `leakage.py` (tests : `test_leakage_lib.py`, `test_leakage.py`, 9 tests)

Points forts : chaque contrôle a un cas piégé ; `test_leakage.py` garde-fou « le fichier de paires n'est pas vide » et prouve qu'un découpage naïf casserait des paires. Tuées : auto-paires, union sans soustraction, inversions de `cross_partition`, hors-pli, source inconnue, seuil par défaut.

Survivantes (preuves) :
- **LK1** `jac >= threshold` devient `>` : survit. Une paire à Jaccard exactement 0,8 (`"abcdefgh"` et `"abcdefghi"` : 4 5-grammes communs sur 5) est signalée avec `>=` et pas avec `>` (sonde : `[('a','b',0.8)]`).
- **LK2** `ids[start + int(row)]` devient `ids[int(row)]` : survit. Avec 3 textes pour un bloc de 500, le second bloc n'est jamais exercé ; en production (milliers de textes) un identifiant décalé fabriquerait de fausses paires et en manquerait de vraies. Un test avec `monkeypatch.setattr(leakage, "_BLOCK", 2)` le tue.
- **LK3** 5-grammes remplacés par des 3-grammes ; **LK4** matrice non binaire (multiplicités) : survivent. **LK6** union-find `parent[a] = b` au lieu de `parent[find(a)] = find(b)` : survit (le test enchaîne `a-b`, `b-c` ; l'étoile `a-b`, `a-c` échoue avec le mutant).
- Neutre : LK12 (taille de bloc 1).

Cas limites (sondes) : deux textes **identiques** de moins de 5 caractères (`"ok"`, `"ok"`) ou vides ne produisent aucun 5-gramme : jamais signalés. Textes différant seulement par les accents : non signalés (choix de conception, à écrire). `clusters` avec un identifiant absent de `ids` : KeyError ; `check_out_of_fold` avec un identifiant sans entrée dans `teacher_trained_on` : KeyError (échecs francs). `test_leakage.py` : `pytestmark = skipif(not exists)` : sur un clone sans `data/`, les contrôles sur les partitions réelles passent **en silence** (0 vérification) ; à relier à un contrôle de CI qui exige leur exécution.

Tests à ajouter (validés) :

```python
def test_a_pair_exactly_at_the_threshold_is_reported():
    assert leakage.near_duplicate_pairs({"a": "abcdefgh", "b": "abcdefghi"}, threshold=0.8) == [("a", "b", 0.8)]

def test_the_similarity_uses_five_character_ngrams():
    assert leakage.near_duplicate_pairs({"a": "abcdefghij", "b": "abcdeXghij"}, threshold=0.2) == []   # 3-grammes : 0,45

def test_repeated_ngrams_count_once_so_a_repetitive_text_is_not_a_duplicate():
    assert leakage.near_duplicate_pairs({"a": "aaaaaaaaaa", "b": "aaaaabbbbb"}, threshold=0.8) == []

def test_pairs_found_in_later_blocks_carry_the_right_identifiers(monkeypatch):
    monkeypatch.setattr(leakage, "_BLOCK", 2)
    # 5 textes, la paire de quasi-doublons est en positions 3 et 4 (second et troisième bloc) : [("x3", "x4")]

def test_clusters_merge_a_star_of_pairs_through_the_first_member():
    c = leakage.clusters(["a", "b", "c", "d"], [("a", "b", 0.9), ("a", "c", 0.9)])
    assert c["a"] == c["b"] == c["c"] != c["d"]

def test_identical_short_texts_are_reported_as_duplicates():   # échoue aujourd'hui (preuve) ; décision de conception
    assert leakage.near_duplicate_pairs({"a": "ok", "b": "ok"}) != []
```

### 4.11 `splits.py` (tests : `test_splits.py`, `test_splits_real.py`, 11 + 4 tests)

Points forts : aucune partition partagée, déterminisme, quasi-doublons jamais séparés (groupes de 3), plis de contrôle sans auteur commun, `plant_leak` vérifié. Tuées : tolérance 10 fois plus large, plis de développement non stratifiés (SP7, après correction de mon harnais), test ignoré ou seuil `> 2` dans `check_no_overlap`, plis de contrôle par patient, 4 plis de test au lieu de 3, fraction de test 0,20, plis de développement non groupés par cluster.

Survivantes (preuves) :
- **SP1** `counts < min_count` devient `<=` (frontière de la politique des classes rares : une classe de 20 est conservée) ; **SP3** `>= LARGE_CLASS` devient `>` ; **SP4** `minimum = 0` (toute la branche des petites classes) ; **SP2** `abs(...)` retiré (le déficit n'est plus signalé) : survivent. `test_tolerance_check_flags_an_unbalanced_fold` ne vérifie que `assert check_tolerance(...)` non vide, déclenché par la branche des grandes classes.
- **SP6** `stratify=` retiré de `train_test_split` : survit (une classe de 5 % ne dévie pas assez sur un seul tirage pour dépasser `check_tolerance`).
- **SP10** `sorted(self.test)` retiré de `to_json` : survit (la signature SHA ne dépendrait plus de l'ordre des listes, le test compare deux appels identiques).

Cas limites (sondes) : un seul auteur ou deux auteurs : `ValueError` de scikit-learn (« n_splits=5 greater than the number of groups »), non figé par un test ; `check_tolerance` avec un pli vide : ZeroDivisionError, avec un identifiant inconnu : KeyError ; `apply_rare_class_policy` avec des NaN : les NaN restent NaN ; `check_no_overlap` ne regarde pas `control_folds` (un patient dans deux plis de contrôle est invisible : ces plis ne sont vérifiés que par le test sur la sortie de `make_splits`).

Tests à ajouter (validés) : frontière de 20 pour les classes rares ; message exact `test : classe small a 2 patients, minimum 3` et `pli 0 : classe small a 0 patients, minimum 2` ; classe de 50 patients traitée par proportion ; déficit signalé ; stratification (pour 4 graines, chaque classe à 1 patient près dans le test et dans chaque pli) ; hachage indépendant de l'ordre dans les listes ; erreur claire pour un seul auteur.

## 5. Tests qui passent sans rien vérifier d'utile

| Test | Pourquoi |
|---|---|
| `test_final_report::test_full_report_answers_the_primary_question_and_lists_secondaries_without_verdict` | Le verdict n'est vérifié que par appartenance à l'ensemble des trois valeurs ; ne peut échouer que sur une exception. Les clés de `sensibilite` sont vérifiées, pas les valeurs. |
| `test_final_report::test_compare_reports_a_positive_difference...` | `len(ic95_patients) == 2` ne vérifie ni l'ordre, ni le niveau, ni l'orientation de l'IC patients. |
| `test_final_report::test_conformal_and_abstention_are_consistent_on_the_toy_problem` | Seuils `>= 0,85` et `>= 0,8` ; `a["0.5"] >= a["1.0"]` ; i.i.d. : calibrer sur le test donnerait le même verdict. |
| `test_power_rule::test_pairs_follow_lexicographic_order_and_count` | Nom promet l'ordre, assertion `len == 3`. |
| `test_power_rule::test_threshold_is_two_delta` | Épingle une constante ; la règle (`<=` 4,0) est ailleurs. |
| `test_power_rule::test_pooled_interval_width_matches_pooled_width...` | Auto-cohérence : compare `pooled_interval` à `pooled_width` qui l'appelle. |
| `test_uncertainty::test_couverture_marginale_au_moins_le_niveau_vise_en_echangeable` | Passe pour tout score non conformité cohérent (garantie d'échangeabilité) : ne distingue ni LAC de n'importe quoi, ni APS exact d'APS faux. |
| `test_cluster_bootstrap::test_correlated_errors_within_groups_widen_the_interval` | Compare des niveaux différents (95 % contre 98,33 % par défaut) ; masque l'erreur de niveau (CB2). |
| `test_sealed_access::test_the_detector_would_catch_a_leaky_module` | Teste la regex sur une ligne choisie pour elle ; ne mesure pas les contournements. |
| `test_budget::test_alert_fires_at_eighty_percent_of_budget` | Utilise `BUDGET_HOURS * ALERT_FRACTION` : circulaire, passe avec n'importe quelles constantes. |
| `test_paired::test_bonferroni_level_for_three_comparisons...` | Réplique la formule du code ; ne passerait pas pour `m = 1` ou `m = 0` (non testés). |
| `test_leakage.py` et `test_splits_real.py` | `skipif` si `data/` est absent : un clone propre passe sans rien vérifier. |

## 6. Mutations équivalentes ou neutres (non comptées comme défauts)

SE7 (`os.replace` vers `Path.rename`), BU4 (`3600.0` vers `3600`), PR10 (fp := fn, F1 symétrique), PA9 et PA11 (ordre permuté au sein d'une classe ou des graines, même loi), LK12 (bloc de taille 1), CF15 (garde `k=0`), et BU5, qui est le correctif des durées négatives. Autres remarques d'honnêteté : PA8 n'est tuée que par le test statistique de fausse alerte (déterministe grâce aux graines, mais dépendant de la version de numpy), CF2 que par le test de la classe difficile, FR21 que par un plantage.

## 7. Priorités

- **Critique** (résultat publié ou irréversible) : `final_report` (verdict, métriques, calibration sur le développement, sensibilité, orientation) ; `sealed` (marqueur avant validation, alignement, doublons) ; `power_rule.mean_width`.
- **Élevé** : APS et frontière `<=` de `conformal` ; niveaux et percentiles de `cluster_bootstrap`, `paired` et `pooled_interval` ; asymétrie des graines ; clé de cache (ordre des textes) ; décalage de bloc de `leakage` ; branche des petites classes de `check_tolerance`.
- **Moyen** : constantes publiées de `freeze` et `budget` ; NaN, négatifs, échantillons vides, un seul auteur ; frontière des classes rares ; validation `alpha`.
- **Bas** : arrondi bancaire, messages d'erreur numpy bruts.

Règle de forme : le plancher du projet (`scripts/floor_guard.py`, expression `@pytest.mark.(skip|xfail)`) refuse `xfail`. Les tests « qui échouent aujourd'hui » ci-dessus doivent donc être écrits comme des tests ordinaires, vus en échec, puis suivis du correctif du code, ou précédés d'une décision sur le comportement voulu. Je n'ai utilisé `xfail` strict que dans ma copie de session, pour prouver qu'ils échouent aujourd'hui.

## 8. Ce que je n'ai pas pu vérifier

- Aucun résultat publié n'a été recalculé (pas de lecture d'étiquettes) : je ne peux pas dire si un défaut ci-dessus a touché G 0,8131 ou l'IC [+1,55 ; +12,62]. En particulier pour `sealed` : l'unicité des identifiants du test et du tableau réel n'a pas été contrôlée (pas d'accès à `data/`).
- `tests/test_leakage.py` et `tests/test_splits_real.py` n'ont pas été exécutés (ils lisent `data/`). Le SHA du découpage versionné, la présence du patient mis en quarantaine, l'absence de paires à cheval ne sont donc pas revérifiés.
- `make check`, `make check-fast`, mypy, ruff et la couverture de 97 % : non exécutés, non revérifiés. Mes esquisses n'ont pas été passées au linter du projet (j'ai évité `noqa` et `lambda` assignées dans le texte du rapport, mais les fichiers validés en session peuvent en contenir).
- Les scripts qui appellent ces modules (`scripts/rm17_power_rule.py`, `scripts/budget_alert.py`, `scripts/freeze_final.py`, `scripts/sealed_evaluation.py`, `scripts/compare_probs.py`) n'ont été lus que par extraits : la comparaison `mean <= 4,0`, le code de sortie de `budget_alert` (un plantage Python sort aussi avec le code 1, comme l'alerte à 80 %, à confirmer), l'ordre exact des appels dans `sealed_evaluation.py` ne sont pas revus.
- `tokenizer_child.py`, `lora_train.truncate_head_tail` et `special_affixes` ne sont pas revus ; le vrai défaut (course entre threads du tokenizer Rust) n'est pas reproductible par un test unitaire, seule la logique de relance, de cache et d'épinglage l'est. Les tests de `test_tokenizer_guard.py` (sous-processus réel) n'ont été exécutés que dans le dépôt (verts), pas mutés (TG1 à TG6 portent sur `test_token_cache.py`).
- Les 132 mutations sont écrites à la main (pas d'outil comme mutmut), et la classification « équivalente » repose sur mon raisonnement. Les tests de réplique (`power_rule`, `cluster_bootstrap`, `pooled_interval`) reposent sur le flux de tirages de numpy (`default_rng`, `multinomial`, `integers`), stable dans cet environnement mais non garanti entre versions majeures.
- Les mutations ont tourné sur une copie dans le dossier temporaire de session, sans `pyproject.toml` du projet (configuration `pythonpath` recréée). Seuls les fichiers de tests du module visé ont été rejoués pour chaque mutation, pas la suite complète ; une mutation tuée par un autre fichier de tests du dépôt n'apparaît pas ici comme tuée.
- Les 72 contre-épreuves ont été exécutées sur ma copie ; les fichiers de tests correspondants ne sont **pas** dans le dépôt (règle de la mission). Les esquisses ci-dessus sont condensées : plusieurs corps sont abrégés par `...` et doivent être complétés à l'écriture.
- Effets de bord dans le dépôt : les exécutions de tests y ont régénéré des `__pycache__` (ignorés par git) ; aucun autre fichier n'a été créé ou modifié par moi. Les fichiers modifiés visibles dans `git status` (`RESULTATS.md`, `roadmap_unifié.md`, etc.) ne viennent pas de cette revue.
