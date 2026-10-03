# Gabarit de rapport de résultat

À remplir pour toute sortie (page wiki, carte de modèle, texte de candidature). Chaque ligne a sa preuve (`claim-gate`).

## 1. Ce que le lecteur doit comprendre avant tout chiffre
- Le statut : **confirmatoire** (famille gelée H1 à H3, test scellé ouvert une fois) ou **EXPLORE** (un pli, une graine, aucun verdict).
- La valeur attendue d'avance d'un résultat « non résolu » : probabilité de verdict résolu d'environ 12 % à un gain réel de 3 points, 1,7 % à un gain égal à δ (protocole 6.3). « Non résolu » est un résultat attendu, ni un échec ni une victoire.

## 2. Estimand
- Test scellé : « nouveaux patients du même corpus », jamais groupé par auteur ; les patients du test partagent des auteurs avec le développement. Ce chiffre n'estime pas la généralisation à de nouveaux auteurs ; l'écart patient/auteur de RM-14 (+3,87 points [+1,27 ; +6,31], lecture non tranchée) est rapporté à côté.
- Chaque chiffre porte son périmètre : cinq plis ou pli 0, nombre de graines, nombre de patients.

## 3. Résultat
| Métrique | Valeur | Intervalle | Périmètre | `run_id` |
|---|---|---|---|---|
- Macro-F1 (17 chapitres), puis F1 pondérée et micro-F1, log loss équilibrée avec erreur-type.
- Comparaison appariée : verdict en trois valeurs (gain confirmé, absence de gain, non résolu), intervalle à 98,33 % pour la famille.

## 4. Incertitude
- Calibration (ECE globale et par classe), couverture conforme marginale et par classe avec intervalle de Wilson à 95 %, politique d'abstention : **mesurées pour le modèle rapporté**, jamais héritées d'un autre modèle (les chiffres du TF-IDF ne valent pas pour un LLM).
- Écart d'échangeabilité : calibration sur des prédictions hors pli de modèles entraînés sur 80 % du développement ; le test est prédit par un modèle entraîné sur 100 %.

## 5. Ce que nous ne savons pas
- Liste datée des lectures non tranchées (RM-14), des mesures manquantes (latence, quantification, robustesse du modèle rapporté), des sources non lues.
- Chapitres à moins de 10 patients au test : leurs F1 et couvertures sont non vérifiables individuellement.

## 6. Tableau de preuve
| Affirmation | Preuve | Statut (prouvé, reformulé, retiré) |
|---|---|---|
