# Errata de PROTOCOLE.md (hors fichier gelé)

Un erratum corrige un fait ou un chiffre de la description ; il **ne change aucune règle**. Les règles ne changent que par une nouvelle version du protocole (6.10, règle 4).

| Date | Section | Erratum |
|---|---|---|
| 2026-10-03 | 2 | « 3 exemples dans le test » est un minimum ; les effectifs réels du test sont dans `results/measures/splits_summary.json` (`test_class_counts` : 633 patients, XXII 4, XII 6, XXI 7, IV 9, V 9). |
| 2026-10-03 | 3 | Le test a été tiré puis **régénéré** après la correction de la section 4 ; l'empreinte du découpage actuel (`data/splits/parhaf_cim10_chapter.sha256`, commençant par 5c06b068) fait foi. |
| 2026-10-03 | ADR-006 | ADR-006 cite des plis de contrôle de 704 à 759 patients ; `splits_summary.json` donne 663 à 763 (valeur actuelle). |
| 2026-10-03 | 6.3 point 5 | Précision sans changement de règle (relevée par GLM, tables recalculées) : un vrai gain égal à δ est confirmé dans 0,83 % des cas et jugé « absence de gain utile » dans 0,83 % ; la probabilité de verdict résolu vaut donc **1,7 % à toute largeur**. |

| 2026-10-03 | 6.4 | « ce code n'existe pas encore » : le classement divergence ou panne existe depuis le 03/10/2026 (`src/llmft/failures.py`, `tests/test_failures.py`, cas piégés inclus) ; la tâche P1-19 garde ses cinq graines GPU à faire. Aucune règle changée. |
| 2026-10-03 | 6.8 | « Code requis avant RM-20 (pas encore écrit) » : les deux temps existent depuis le 03/10/2026 dans `src/llmft/sealed.py` (`sealed_inputs`, `sealed_labels_and_score`, `MARKER_PATH`, répétition générale par `rehearsal=True`, `tests/test_sealed_two_steps.py`). **Reste à faire** : consigner l'empreinte du marqueur à sa création, arrêter la liste `ALLOWED` et le nom du script d'évaluation avant de l'écrire, et exécuter la répétition générale sur les prédictions hors pli. |
