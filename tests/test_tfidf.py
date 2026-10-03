import numpy as np

from llmft import tfidf

LABELS = ["a", "b", "c"]
TEXTS = ["alpha tumeur biopsie", "alpha tumeur kyste", "beta fracture femur", "beta fracture tibia", "gamma asthme toux", "gamma asthme dyspnee"] * 4
Y = ["a", "a", "b", "b", "c", "c"] * 4


def test_probas_alignees_sur_labels_et_somme_un():
    p = tfidf.fit_predict_proba(TEXTS, Y, ["alpha tumeur"], LABELS, c=10.0, ngram=(1, 1))
    assert p.shape == (1, 3)
    assert abs(p.sum() - 1) < 1e-9
    assert LABELS[int(p.argmax())] == "a"


def test_classe_absente_de_l_entrainement_garde_sa_colonne_a_zero():
    keep = [i for i, y in enumerate(Y) if y != "c"]
    p = tfidf.fit_predict_proba([TEXTS[i] for i in keep], [Y[i] for i in keep], ["gamma asthme"], LABELS, c=10.0, ngram=(1, 1))
    assert p.shape == (1, 3) and p[0, 2] == 0.0 and abs(p.sum() - 1) < 1e-9


def test_selection_egalite_exacte_va_au_c_le_plus_bas_puis_aux_unigrammes(monkeypatch):
    monkeypatch.setattr(tfidf, "GRID", [(1.0, (1, 1)), (10.0, (1, 1)), (10.0, (1, 2))])
    folds = np.array([i % 3 for i in range(len(Y))])
    # corpus parfaitement séparable : les trois configurations atteignent 1,0
    assert tfidf.select_config(TEXTS, Y, folds, val_fold=1, labels=LABELS, scored=LABELS) == (1.0, (1, 1))


def test_selection_ignore_le_pli_externe_absent_des_donnees_fournies():
    folds = np.array([i % 3 for i in range(len(Y))])
    keep = [i for i in range(len(Y)) if folds[i] != 2]  # le pli 2 joue l'externe : jamais transmis
    cfg = tfidf.select_config([TEXTS[i] for i in keep], [Y[i] for i in keep], folds[keep], val_fold=1, labels=LABELS, scored=LABELS)
    assert cfg in tfidf.GRID


def test_grille_fixee_a_huit_configurations():
    assert len(tfidf.GRID) == 8


def test_grille_v2_etend_c_vers_le_haut_sans_toucher_a_la_grille_v1():
    assert len(tfidf.GRID) == 8 and max(c for c, _ in tfidf.GRID) == 100.0
    assert max(c for c, _ in tfidf.GRID_V2) == 10000.0 and len(tfidf.GRID_V2) == 10


def test_selection_accepte_une_grille_explicite():
    folds = np.array([i % 3 for i in range(len(Y))])
    assert tfidf.select_config(TEXTS, Y, folds, val_fold=1, labels=LABELS, scored=LABELS, grid=[(10.0, (1, 1))]) == (10.0, (1, 1))


def test_poids_de_classe_equilibres_augmentent_la_probabilite_de_la_classe_rare():
    texts = ["alpha tumeur"] * 30 + ["beta fracture"] * 3 + ["alpha beta mixte"] * 3
    y = ["a"] * 30 + ["b"] * 3 + ["b"] * 3
    plain = tfidf.fit_predict_proba(texts, y, ["alpha beta mixte"], ["a", "b"], c=1.0, ngram=(1, 1))
    balanced = tfidf.fit_predict_proba(texts, y, ["alpha beta mixte"], ["a", "b"], c=1.0, ngram=(1, 1), class_weight="balanced")
    assert balanced[0, 1] > plain[0, 1]


def test_analyseur_de_caracteres_donne_des_probabilites_valides():
    p = tfidf.fit_predict_proba(TEXTS, Y, ["alphq tumeur"], LABELS, c=10.0, ngram=(3, 5), analyzer="char_wb")
    assert p.shape == (1, 3) and abs(p.sum() - 1) < 1e-9
