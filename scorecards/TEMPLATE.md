# Scorecard G-Px : modèle

Une note de 0 à 3 par catégorie Q1 à Q12, **une preuve par note**. Le vérificateur (`scripts/check_scorecards.py`, `make check`) contrôle la présence des champs, l'existence de l'artefact et son empreinte SHA-256 ; il ne prouve pas que la note est juste.

Échelle : 0 absent ; 1 amorcé, mesuré une fois ; 2 solide, reproductible avec sa commande ; 3 confirmé indépendamment.

Degrés d'indépendance (champ `independence_degree`, obligatoire pour une note 3) : `code` (un second code produit le même résultat), `données` (un autre jeu ou une autre partition), `méthode` (une autre méthode aboutit à la même conclusion), `personne ou contexte` (relecture en contexte neuf ou par Cyril), `reconstruction à froid` (rejeu depuis un clone ou un conteneur vierge). Une indépendance se déclare toujours avec son degré, jamais « vérifié » seul.

Champs d'un bloc (un bloc `yaml` par catégorie, dans l'ordre Q1 à Q12) :

```yaml
q: Q1
note: 2
requirement: "Ce que la catégorie exigeait à cette porte"
artifact: chemin/relatif/du/fichier
artifact_sha256: "<empreinte SHA-256 du fichier>"
command: "commande qui reproduit la preuve"
expected: "valeur attendue"
observed: "valeur observée"
date: "AAAA-MM-JJ"
residual_defect: "ce qui reste imparfait, ou aucun connu"
justification: "pourquoi cette note et pas la voisine"
# note 3 seulement :
# independent_confirmation: "qui ou quoi a confirmé"
# independence_degree: "personne ou contexte"
# note sous le plancher de la porte :
# remediation: "plan de rattrapage daté"
```
