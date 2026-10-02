---
name: leakage-guard
description: Détecte les fuites de données avant qu'un score soit cru. À utiliser en créant un découpage train/val/test ou des plis, en générant des probabilités de professeur hors pli, en ajoutant des données synthétiques, pseudo-étiquetées ou externes, et quand un score paraît trop beau.
---

# Garde anti-fuite

Un score gonflé par une fuite est pire qu'un mauvais score : il est cru. Sur des petits jeux médicaux (DiaMED, 739 cas) et avec de la distillation, les fuites sont faciles et silencieuses.

## Les cinq contrôles

Chaque contrôle est un test `pytest` dans `tests/test_leakage.py`, rejoué à chaque changement de données ou de découpage.

1. **Test scellé** : le fichier de test a une empreinte SHA-256 consignée dans `PROTOCOLE.md`. Le test vérifie l'empreinte et qu'aucun identifiant du test n'apparaît dans un fichier d'entraînement, de validation, de pré-entraînement voisin, de pseudo-étiquetage ou de génération synthétique.
2. **Quasi-doublons** : textes normalisés (minuscules, espaces, ponctuation), puis MinHash ou n-grammes de caractères ; toute paire au-dessus du seuil fixé dans le protocole entre deux partitions différentes est un échec, listée avec ses identifiants.
3. **Strictement hors pli** : chaque probabilité de professeur utilisée pour distiller l'exemple `i` vient d'un professeur qui n'a pas vu `i`. Le test reconstruit la carte exemple → pli et la confronte aux métadonnées des fichiers de logits.
4. **Synthétique et pseudo-étiquettes** : un exemple généré à partir d'un exemple d'évaluation (amorce, paraphrase, cas « similaire ») est une fuite. Chaque exemple généré porte l'identifiant de sa source, et le test vérifie que les sources sont toutes dans l'entraînement du pli concerné.
5. **Réglages** : aucun hyperparamètre, seuil de calibration ou choix de point de départ n'est sélectionné sur le test scellé. Le test vérifie que le code de sélection ne charge que des partitions de validation.

**Terminé quand** les cinq tests passent au vert sur le découpage courant, et que tout échec a été corrigé à la source (jamais en relevant le seuil).

## Score trop beau

Un gain inattendu de plus de deux écarts-types déclenche d'abord ces cinq contrôles, ensuite seulement l'interprétation.
