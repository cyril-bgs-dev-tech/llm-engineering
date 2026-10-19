# À appliquer après la fin du lot RM-62 (N6), puis make check complet
1. scripts/lib/lot.sh : appliquer lot_sh.patch (conservation des sorties d'un essai mort) ; verser les 3 tests de essais_a_verser_dans_test_lot_sh.py dans tests/test_lot_sh.py (sans LOT_LIB).
2. tests/conftest.py : ajouter `import pytest` et le contenu de conftest_ajout.py (N42) ; lancer la suite complète, corriger chaque test qui casse sur le chemin à espaces (citer les chemins).
3. Lancer scripts/lora_author_calibration.py --register (fiche 2026-10-17-etalonnage-nouveaux-auteurs), appliquer son critère.
